# Results data dictionary

`paper_results.csv` contains 24 rows at the grain **model × fine-tuning budget × benchmark**. Values come exclusively from final-manuscript Tables 2 and 3. `evidence_class=E3` identifies the basis; `artifact_origin=POST_HOC` identifies the newly authored file.

| Column | Meaning |
| --- | --- |
| `model` | Full instruction-model name; baseline already means an Instruct model |
| `training_samples` | Additional fine-tuning samples: 0, 5000, 10000, or 15000; zero denotes baseline |
| `condition` | `baseline` or `lora_sft` |
| `benchmark` | HumanEval, HumanEval+, MBPP, or MBPP+; no aggregate score |
| `pass_at_1_pct` | Printed pass@1 score on a 0-100 percentage scale; a mean for fine-tuned 1.5B rows |
| `sample_sd_pp` | Printed sample SD in percentage points; empty when unreported, including all single-evaluation rows |
| `n_runs` | Number of checkpoint evaluations summarized, as reported: 3 for fine-tuned 1.5B, otherwise 1; not recovered seed IDs or repeated inference draws |
| `summary_type` | `mean_sample_sd` or `single_evaluation` |
| `evidence_class` | `E3`, meaning manuscript-reported rather than newly measured |
| `source_id`, `source_table` | `FINAL_MANUSCRIPT` and Table 2 or 3; see the source manifest |
| `artifact_origin` | `POST_HOC`; no row represents a new training/evaluation run |

`changes_from_baseline.csv` contains 16 rows, one per non-baseline result. `change_pp = comparison_pass_at_1_pct - baseline_pass_at_1_pct`, calculated with decimal arithmetic at the manuscript's printed precision. Positive changes are numerical increases, not significance findings.

`comparison_sample_sd_pp` is copied from the fine-tuned summary, not estimated uncertainty for the difference. `comparison_n_runs` preserves the comparison's reported run count. `artifact_origin=POST_HOC_DERIVED` marks the calculation. There is no inferred baseline SD, pooled SD, confidence interval, or per-seed reconstruction.

All CSV files use UTF-8, comma delimiters, a header row, decimal points, and empty fields for missing SDs. The evidence table snapshots retain literal source cells such as `65.85 ± 0.00`; the normalized results keep the numeric components separate. The historical discrepancy CSV is excluded from the plot inputs.
