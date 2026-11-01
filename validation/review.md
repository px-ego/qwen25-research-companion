# Local verification and review

Date: 2026-11-01 (Asia/Shanghai). Outcome: **Share with caveats**, within the scope of a research companion. The capability is L1, summary-level analysis and figure regeneration, as defined in [reproducibility.md](../reproducibility.md).

## Executed checks

The following commands were actually executed on Windows with Python 3.12.14. Private arguments below are displayed as placeholders; the real files were supplied for the owner-side check. See [local-checks.json](local-checks.json) for the machine-readable result and its exclusions.

```bash
python scripts/plot_results.py
python scripts/check_results.py --write-derived --paper path/to/final-manuscript.docx --audit-dir path/to/qwen25_audit --check-figures --report validation/local-checks.json
python scripts/check_results.py --check-figures
python -m pip check
git diff --cached --check
git remote -v
```

- The final manuscript's SHA-256, title, printed author, and every cell of its three tables matched the recorded source/transcriptions. Seventeen selected audit files matched their recorded SHA-256 hashes. The two included E1 excerpts matched their audit originals byte for byte.
- All 24 normalized result rows and 16 derived differences passed the included consistency checks. Eight E1 3B values matched Table 3. The two historical conflicts remain explicitly unresolved.
- Both plotting functions ran successfully. Four exports passed input/output hash checks, PNG signature/resolution checks, and exact SVG value-label checks. The plotting environment passed `pip check`.
- The portable check also ran with the bundled Python interpreter, without plotting packages or private-source arguments. This demonstrated that its default path uses only the standard library; it did not repeat source verification.
- Public text received the script's scoped private-information pattern screen and local Markdown file-link checks. A separate local comparison checked extracted server-path and connection-host tokens from the audit against the staged public payload, without recording those tokens here.
- The local Git whitespace check passed after standardizing authored text to LF. The staged file bytes were compared with the working files. Git has no configured remote. No commit, push, or public release was made.

## Visual and editorial review

The final PNG exports were inspected at their export size and in a 1,000-pixel-wide preview, including grayscale. The 1.5B figure is 2,160 × 1,404 pixels; the 3B figure is 2,160 × 1,152 pixels. Labels, axes, error bars, legends, and footnotes were readable without overlap after correcting the initial 1.5B caption spacing. Later text-export normalization left both PNG hashes unchanged, so those reviewed images remain the delivered images.

The 1.5B panels use the same explicitly focused 55-75% point-chart scale. Baseline circles, fine-tuned squares, reported sample SDs, and direct values distinguish the settings without relying on color. The 3B bars start at zero; hatching distinguishes baseline from fine-tuned results in grayscale. The chart states the single-run scope and does not invent error bars. SVG exports received structural/value-label checks; visual inspection used the PNG exports.

The README's research question, experimental design, changes, and qualifications were reviewed against the final manuscript. Early screenshot values do not appear in the primary result CSV or plot inputs. E4 proposals remain separate, and no new repository file is presented as recovered historical training code. Citation fields unsupported by the final manuscript remain unconfirmed.

## Delivered local payload

The repository contains 26 reviewable files, excluding Git metadata and ignored Python caches:

```text
.gitattributes
.gitignore
README.md
citation.md
provenance.md
reproducibility.md
requirements.txt
evidence/
  e1_3b_terminal_transcription.txt
  e1_early_mbpp_transcription.txt
  historical_discrepancies.csv
  paper_table_1.csv
  paper_table_2.csv
  paper_table_3.csv
  source_manifest.json
figures/
  1p5b_data_scale.png
  1p5b_data_scale.svg
  3b_before_after.png
  3b_before_after.svg
  figure_manifest.json
results/
  README.md
  changes_from_baseline.csv
  paper_results.csv
scripts/
  check_results.py
  plot_results.py
validation/
  local-checks.json
  review.md
```

Private extraction/QA helpers, previews, and the temporary authoring environment are outside this repository. The source audit and manuscript were read without modification. No framework, Docker configuration, CI workflow, training scaffold, or substitute historical evaluation implementation was introduced.

## Claims still unsupported

No historical training, checkpoint evaluation, per-seed statistics recomputation, task-level analysis, sampling reconstruction, decontamination audit, statistical-significance test, or causal task-alignment test was performed. Formal venue, publication year, DOI, and acceptance/publication status are unverified. A passing companion check does not establish any of those claims.
