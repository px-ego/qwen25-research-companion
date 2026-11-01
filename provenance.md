# Evidence and provenance

The final author-provided DOCX controls the research title, reported protocol, and primary result values. It is identified by SHA-256 in [source_manifest.json](evidence/source_manifest.json). The audit package supplies historical transcriptions and the inventory of missing artifacts. Neither source type is elevated into an independently rerun experiment.

## Evidence classes and artifact origin

The audit's E labels describe the kind of historical evidence, not a numerical confidence scale.

| Label | Meaning here | Permitted use |
| --- | --- | --- |
| E1 | User-provided terminal output or screenshot preserved in an audit transcription | Support the specific visible command/output/value; no guarantee of complete logs or immutable checkpoint identity |
| E2 | Preserved historical source/config text, sometimes only a partial grep excerpt | Support visible fields only; no inference of a complete configuration or successful run |
| E3 | Author statements and, separately, the final manuscript's reported summaries | State what the author reports; final tables control this companion's primary results |
| E4 | Historical assistant-proposed scripts, commands, or configurations | Document a proposal; no proof of execution or training success |
| E5 | Inference from incomplete information | No recovered code or execution claim is based on it |
| POST_HOC | Artifacts authored for this companion on 2026-11-01 | Analysis, presentation, and checks on preserved evidence; no new model observations |

Evidence class and file origin are separate. For example, the normalized results CSV is a new post-hoc artifact whose numbers have an E3 basis. An included E1 transcription is an audit-preserved copy of historical user output, not a recovered native evaluation JSON file.

## Included material

| Repository files | Basis and transformation |
| --- | --- |
| `evidence/paper_table_1.csv`, `paper_table_2.csv`, `paper_table_3.csv` | Post-hoc literal transcriptions of all cells in final-manuscript Tables 1-3 (E3); checked against the DOCX XML |
| `results/paper_results.csv` | Post-hoc normalization of Tables 2-3; means and SDs in separate numeric columns; no inferred seed rows |
| `results/changes_from_baseline.csv` | Post-hoc decimal subtraction of the printed table values |
| `evidence/e1_3b_terminal_transcription.txt` | Byte-identical copy of the audit's short, connection-free 3B terminal transcription (E1); eight values agree with Table 3 |
| `evidence/e1_early_mbpp_transcription.txt` | Byte-identical copy of an earlier short MBPP output (E1); retained to expose the conflicting earlier value |
| `evidence/historical_discrepancies.csv` | Post-hoc comparison of two conflicting historical values against final-paper values; unresolved causes |
| `evidence/source_manifest.json` | Post-hoc source IDs, safe relative locators, evidence classes, byte sizes, and SHA-256 hashes |
| `scripts/`, `figures/`, all Markdown, `requirements.txt`, `.gitignore`, `.gitattributes`, `validation/` | New companion code, exports, documentation, and actual execution/review records; not historical training assets |

The manifest hashes identify the supplied local source bytes. They do not authenticate when the historical experiments ran, certify the underlying results, or make unavailable originals publicly inspectable. Audit documents are themselves a later compilation; E1/E3/E4 describe their underlying content.

## Conflicts retained rather than merged

| Scope | Earlier preserved value | Final-paper value | Treatment |
| --- | ---: | ---: | --- |
| 1.5B baseline, MBPP+ | 58.20% in an early screenshot transcription | 58.73% in Table 2 | A 0.53 pp difference; use 58.73% in primary results; source of discrepancy unresolved |
| 3B baseline, MBPP+ | 0.632, or 63.20%, in an early terminal report | 63.76% in Table 3 and the later full 3B terminal summary | A 0.56 pp difference; use 63.76% in primary results; source of discrepancy unresolved |

These differences cannot be dismissed as rounding. Different runs or extraction paths are possible explanations, not established facts. The early 1.5B screenshot is a separate single-run record and does not replace the final three-run summaries. Its aggregate score is not propagated.

Existing figures or scripts outside this companion may use earlier 1.5B values. They were not imported. Both new plots read only the final-paper normalized CSV, and the figure manifest records the input hashes.

## E4 proposals and missing source

The private audit contains proposed 3B train/export YAMLs, 3B evaluation commands, a 1.5B seed-config generator, and a proposed batch evaluation script. They remain E4 in the source manifest. They are not copied into an executable training interface and were not run for this companion.

A historical file listing with matching names or byte sizes does not prove byte-identical content or execution. Partial E1/E2 configuration grep output supports only the displayed fields. Original evaluation and patching scripts, checkpoints, per-seed results, and sampling records remain missing as detailed in [reproducibility.md](reproducibility.md).

## Public-content boundary

The full audit, environment notes, server connection details, machine-specific paths, temporary signed download URLs, review forms, and full manuscript are excluded. Only selected result/configuration metadata and the two short connection-free terminal transcriptions are included. Source locators in the manifest are relative paths inside the audit package, not server paths.

All authored text and SVG files were screened for selected private-information patterns. PNGs were generated from the curated result CSV. This is a scoped content review, not a general security certification or a training-data contamination audit. The repository was prepared and reviewed locally without a public GitHub remote or publication.

## Bibliographic boundary

The final manuscript verifies the title and the author string. Its body/header/footer supply no confirmed venue, DOI, publication year, or formal publication status. A local review form is not a proceedings record. Directory names and template metadata are not bibliographic evidence. [citation.md](citation.md) therefore leaves those fields unconfirmed and provides only a clearly labeled manuscript reference.
