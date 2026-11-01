"""Check a post-hoc research companion. This does not run model evaluation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("Qwen2.5-Coder-1.5B-Instruct", "Qwen2.5-Coder-3B-Instruct")
BENCHMARKS = ("HumanEval", "HumanEval+", "MBPP", "MBPP+")
FIELDS = [
    "model", "training_samples", "condition", "benchmark", "pass_at_1_pct",
    "sample_sd_pp", "n_runs", "summary_type", "evidence_class", "source_id",
    "source_table", "artifact_origin",
]
CHANGE_FIELDS = [
    "model", "training_samples", "benchmark", "baseline_pass_at_1_pct",
    "comparison_pass_at_1_pct", "change_pp", "comparison_sample_sd_pp",
    "comparison_n_runs", "source_id", "artifact_origin",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        require(all(None not in r and None not in r.values() for r in rows),
                f"Malformed CSV: {Path(path).name}")
        return reader.fieldnames, rows


def read_matrix(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        return list(csv.reader(stream))


def write_csv(path, fields, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(value):
    result = Decimal(value)
    require(result.is_finite(), "Non-finite result")
    return result


def normalized_from_snapshots():
    """Normalize the literal Table 2/3 snapshots, preserving missing SDs."""
    rows = []
    for model, table_number in zip(MODELS, (2, 3)):
        matrix = read_matrix(ROOT / f"evidence/paper_table_{table_number}.csv")
        require(matrix[0][1:] == list(BENCHMARKS), "Unexpected table benchmarks")
        settings = (0, 5000, 10000, 15000) if table_number == 2 else (0, 15000)
        require(len(matrix) == (5 if table_number == 2 else 4), "Unexpected table rows")
        expected_labels = ["0 (baseline)", "5K", "10K", "15K"] if table_number == 2 else ["Baseline", "15K fine-tuned"]
        for source_row, samples, label in zip(matrix[1:], settings, expected_labels):
            require(source_row[0] == label and len(source_row) == 5, "Unexpected table setting")
            multi_run = table_number == 2 and samples > 0
            for benchmark, cell in zip(BENCHMARKS, source_row[1:]):
                parts = [p.strip() for p in cell.split("±")]
                require(len(parts) == (2 if multi_run else 1), "Missing or invented SD")
                rows.append(dict(zip(FIELDS, [
                    model, str(samples), "baseline" if samples == 0 else "lora_sft",
                    benchmark, f"{number(parts[0]):.2f}",
                    f"{number(parts[1]):.2f}" if multi_run else "",
                    "3" if multi_run else "1",
                    "mean_sample_sd" if multi_run else "single_evaluation",
                    "E3", "FINAL_MANUSCRIPT", str(table_number), "POST_HOC",
                ])))
    return rows


def derive_changes(rows):
    index = {(r["model"], r["training_samples"], r["benchmark"]): r for r in rows}
    changes = []
    for row in rows:
        if row["training_samples"] == "0":
            continue
        base = index[(row["model"], "0", row["benchmark"])]
        changes.append(dict(zip(CHANGE_FIELDS, [
            row["model"], row["training_samples"], row["benchmark"],
            base["pass_at_1_pct"], row["pass_at_1_pct"],
            f'{number(row["pass_at_1_pct"]) - number(base["pass_at_1_pct"]):.2f}',
            row["sample_sd_pp"], row["n_runs"], "FINAL_MANUSCRIPT", "POST_HOC_DERIVED",
        ])))
    return changes


def load_results():
    fields, rows = read_csv(ROOT / "results/paper_results.csv")
    require(fields == FIELDS, "Unexpected results schema")
    require(rows == normalized_from_snapshots(), "Results differ from manuscript table snapshots")
    keys = [(r["model"], r["training_samples"], r["benchmark"]) for r in rows]
    require(len(rows) == 24 and len(set(keys)) == 24, "Missing or duplicate results")
    for row in rows:
        require(0 <= number(row["pass_at_1_pct"]) <= 100, "Score outside [0, 100]")
        if row["sample_sd_pp"]:
            require(0 <= number(row["sample_sd_pp"]) <= 100, "Invalid SD")
    index = {key: row for key, row in zip(keys, rows)}
    for row in rows:
        if row["benchmark"].endswith("+"):
            original = index[(row["model"], row["training_samples"], row["benchmark"][:-1])]
            require(number(row["pass_at_1_pct"]) <= number(original["pass_at_1_pct"]),
                    "Plus score exceeds its original-suite score")
    # Table 3 prints its own change row: an additional source-level arithmetic check.
    printed_changes = read_matrix(ROOT / "evidence/paper_table_3.csv")[-1]
    require(printed_changes[0] == "Change", "Missing manuscript change row")
    derived_3b = [r for r in derive_changes(rows) if r["model"] == MODELS[1]]
    require([number(v) for v in printed_changes[1:]] ==
            [number(r["change_pp"]) for r in derived_3b], "Table 3 arithmetic mismatch")
    return rows


def check_e1_and_discrepancies(rows):
    text = (ROOT / "evidence/e1_3b_terminal_transcription.txt").read_text(encoding="utf-8")
    values = re.findall(r"(?:base|plus) pass@1:\s*(\d+(?:\.\d+)?)", text)
    paper_3b = [r["pass_at_1_pct"] for r in rows if r["model"] == MODELS[1]]
    require([number(v) for v in values] == [number(v) for v in paper_3b], "E1/3B table mismatch")
    _, conflicts = read_csv(ROOT / "evidence/historical_discrepancies.csv")
    require(len(conflicts) == 2, "Expected two documented historical discrepancies")
    expected = [(MODELS[0], "58.20", "58.73", "0.53"),
                (MODELS[1], "63.20", "63.76", "0.56")]
    for conflict, (model, early, final, gap) in zip(conflicts, expected):
        require(conflict["model"] == model and conflict["benchmark"] == "MBPP+",
                "Unexpected historical discrepancy identity")
        require([number(conflict[k]) for k in ("earlier_pass_at_1_pct", "final_paper_pass_at_1_pct", "gap_pp")] ==
                [number(v) for v in (early, final, gap)], "Historical discrepancy value mismatch")
        require(number(final) - number(early) == number(gap), "Historical discrepancy arithmetic mismatch")
    early_text = (ROOT / "evidence/e1_early_mbpp_transcription.txt").read_text(encoding="utf-8")
    require(re.search(r"mbpp\+.*?0\.632", early_text, re.S), "Missing earlier E1 MBPP+ value")


def extract_docx(path):
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
    # Read w:t explicitly; other XML text includes field codes and is not table content.
    def content(element):
        return "".join(t.text or "" for t in element.findall(".//w:t", ns)).strip()
    body = document.find("w:body", ns)
    paragraphs = [content(p) for p in body.findall("w:p", ns) if content(p)]
    tables = [[[content(cell) for cell in row.findall("w:tc", ns)]
               for row in table.findall("w:tr", ns)] for table in body.findall("w:tbl", ns)]
    return paragraphs, tables


def check_originals(paper, audit_dir, manifest):
    checked = []
    if paper:
        record = next(s for s in manifest["sources"] if s["source_id"] == "FINAL_MANUSCRIPT")
        require(sha256(paper) == record["sha256"], "Final manuscript SHA-256 mismatch")
        paragraphs, tables = extract_docx(paper)
        require(paragraphs[0] == manifest["paper_metadata"]["title"], "Manuscript title mismatch")
        require(paragraphs[1].rstrip("*").strip() == manifest["paper_metadata"]["author_as_printed"],
                "Manuscript author mismatch")
        require(len(tables) == 3, "Unexpected manuscript table count")
        for i, table in enumerate(tables, 1):
            require(table == read_matrix(ROOT / f"evidence/paper_table_{i}.csv"),
                    f"Table {i} snapshot differs from original DOCX")
        checked.append({"check": "original_manuscript", "status": "passed", "tables": 3,
                        "scope": "Byte identity, title, author and all table cells; not experimental rerun"})
    if audit_dir:
        records = [s for s in manifest["sources"] if s["location_kind"] == "audit_relative"]
        for record in records:
            path = audit_dir / record["reference"]
            require(sha256(path) == record["sha256"], f'Audit source hash mismatch: {record["source_id"]}')
            if record.get("included_copy"):
                require(path.read_bytes() == (ROOT / record["included_copy"]).read_bytes(),
                        "Included E1 transcription differs from audit source")
        _, early = read_csv(audit_dir / "recovered/results/early_screenshot_E1.csv")
        require(number(early[0]["MBPP_plus"]) == Decimal("58.2"), "Earlier screenshot value mismatch")
        checked.append({"check": "audit_source_hashes", "status": "passed", "sources": len(records),
                        "scope": "Audit-package transcriptions and documents; no E4 execution"})
    return checked


def check_figures(rows):
    manifest = json.loads((ROOT / "figures/figure_manifest.json").read_text(encoding="utf-8"))
    for relative, digest in manifest["inputs_sha256"].items():
        require(sha256(ROOT / relative) == digest, "Stale figure input: " + relative)
    for relative, digest in manifest["outputs_sha256"].items():
        path = ROOT / relative
        require(sha256(path) == digest, "Figure hash mismatch: " + relative)
        if path.suffix == ".png":
            data = path.read_bytes()
            require(data[:8] == b"\x89PNG\r\n\x1a\n", "Invalid PNG")
            width, height = struct.unpack(">II", data[16:24])
            require(width >= 1200 and height >= 700, "Figure resolution too low")
        else:
            root = ET.fromstring(path.read_text(encoding="utf-8"))
            texts = Counter("".join(e.itertext()) for e in root.iter() if e.tag.endswith("}text"))
            model = MODELS[0] if "1p5b" in path.name else MODELS[1]
            expected = Counter(
                r["pass_at_1_pct"] + (" ± " + r["sample_sd_pp"] if r["sample_sd_pp"] else "")
                for r in rows if r["model"] == model)
            require(not (expected - texts), "Figure is missing exact source value labels")
    require(len(manifest["outputs_sha256"]) == 4, "Expected two PNG and two SVG charts")


def check_public_files():
    """A bounded pattern screen, not a general security certification."""
    patterns = [
        r"(?i)\b[a-z]:[\\/]", r"/(?:root|home|autodl-tmp|autodl-pub)/",
        r"(?i)\b(?:ssh|scp|sftp)\s+", r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        r"(?i)[?&](?:x-amz-[a-z-]+|signature|sig|token|se|sp|sv)=",
        r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,})",
        r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    ]
    count = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(p in {".git", ".venv", "__pycache__"} for p in path.relative_to(ROOT).parts):
            continue
        if path.suffix in {".png", ".pyc"}:
            continue
        text = path.read_text(encoding="utf-8")
        require(not any(re.search(p, text) for p in patterns),
                "Potential private information in " + path.relative_to(ROOT).as_posix())
        if path.suffix == ".md":
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                if not target.startswith(("https://", "http://", "#")):
                    require((path.parent / target.split("#")[0]).is_file(), "Broken local Markdown link")
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", type=Path, help="Private final DOCX; read only")
    parser.add_argument("--audit-dir", type=Path, help="Private audit-package directory; read only")
    parser.add_argument("--write-derived", action="store_true", help="Regenerate the derived changes CSV")
    parser.add_argument("--check-figures", action="store_true")
    parser.add_argument("--report", type=Path, help="Write a JSON execution receipt; source paths omitted")
    args = parser.parse_args()
    rows = load_results()
    if args.write_derived:
        write_csv(ROOT / "results/changes_from_baseline.csv", CHANGE_FIELDS, derive_changes(rows))
    fields, changes = read_csv(ROOT / "results/changes_from_baseline.csv")
    require(fields == CHANGE_FIELDS and changes == derive_changes(rows), "Derived changes CSV mismatch")
    check_e1_and_discrepancies(rows)
    manifest = json.loads((ROOT / "evidence/source_manifest.json").read_text(encoding="utf-8"))
    checks = [
        {"check": "included_tables_and_normalized_results", "status": "passed", "rows": len(rows)},
        {"check": "derived_changes_and_table3_arithmetic", "status": "passed", "rows": len(changes)},
        {"check": "e1_3b_concordance_and_historical_conflicts", "status": "passed", "matching_scores": 8, "unresolved_conflicts": 2},
    ]
    checks += check_originals(args.paper, args.audit_dir, manifest)
    if args.check_figures:
        check_figures(rows)
        checks.append({"check": "figure_hashes_inputs_png_headers_svg_labels", "status": "passed", "files": 4})
    screened = check_public_files()
    checks.append({"check": "public_text_patterns_and_local_markdown_links", "status": "passed", "text_files": screened})
    report = {
        "status": "passed_within_stated_scope",
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "artifact_origin": "POST_HOC", "python": sys.version.split()[0], "checks": checks,
        "private_sources_supplied": {"final_manuscript": bool(args.paper), "audit_package": bool(args.audit_dir)},
        "not_checked": ["historical training", "checkpoint evaluation", "per-seed statistics recomputation",
                        "data sampling or decontamination", "publication metadata beyond supplied manuscript"],
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
