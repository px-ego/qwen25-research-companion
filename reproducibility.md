# Reproducibility scope

## Current capability

This companion reaches **L1: summary-level analysis and figure regeneration**. The levels below are local descriptions of capability, not an external certification.

| Level | Capability | Current status |
| --- | --- | --- |
| L0 | Read the reported experiment, results, sources, and limitations | Available |
| L1 | Recalculate differences and regenerate figures from manuscript summary tables | Available; locally executed |
| L2 | Rerun original model evaluation from identified checkpoints | Unavailable |
| L3 | Recreate the historical training runs and recompute their statistics | Unavailable |

The owner-side check compared all three included table transcriptions directly with the private final DOCX and checked its SHA-256. It also checked the selected audit-package files against the source manifest. Public readers can check internal table/CSV consistency and regenerate the figures. They cannot independently inspect the private originals from this repository alone.

## Commands and their scope

From the repository root, in an environment with Python 3.12:

```bash
python -m pip install -r requirements.txt
python scripts/check_results.py
python scripts/plot_results.py
python scripts/check_results.py --check-figures
```

The first check uses only Python's standard library. It checks the 24 result rows against the included manuscript tables, missing-versus-zero SDs, reported run counts, bounds, Plus/original ordering, 16 derived changes, the manuscript's 3B change row, eight matching E1 3B scores, and two unresolved historical discrepancies. It also screens repository text for selected private-information patterns and checks local Markdown file links.

The plotting command creates two PNGs, two SVGs, and a manifest of input/output hashes. The figure check verifies those hashes, PNG signatures/dimensions, and exact SVG value labels. Visual inspection is documented separately. None of these operations loads a model or executes generated benchmark solutions.

To regenerate the derived CSV after a source-reviewed correction:

```bash
python scripts/check_results.py --write-derived
```

Do not change manuscript transcriptions simply to make a check pass. Correct the controlling source and its metadata first, then propagate the correction to the normalized CSV, derived CSV, figures, prose, and validation records.

If the private originals are available, the optional owner-side command is:

```bash
python scripts/check_results.py --paper path/to/final-manuscript.docx --audit-dir path/to/qwen25_audit --check-figures --report validation/local-checks.json
```

The supplied manuscript must match the recorded hash. Source paths are not written into the receipt. Without these arguments, a passing run checks the included copies, not the private source documents. [local-checks.json](validation/local-checks.json) records the actual owner-side execution; [review.md](validation/review.md) records human-readable scope and visual review.

## Missing historical artifacts

| Missing artifact | Consequence |
| --- | --- |
| LoRA adapters, merged checkpoints, immutable base-model revisions, and checkpoint/result mapping | Original model scores cannot be rerun or tied independently to particular weights |
| Complete original training/export YAMLs and trainer logs/state | The exact launch configuration and successful completion of each run cannot be independently verified |
| Original HumanEval/MBPP generation scripts and common-import patch script | Prompt formatting, stop rules, extraction, imports, and execution behavior cannot be reconstructed faithfully |
| Per-seed scores and original task-level generations/evaluation JSON | The reported 1.5B means and sample SDs cannot be recomputed; paired task-level changes cannot be inspected |
| Training-data snapshot, dataset registration, sampled indices, ordering, and sampling records | Exact examples, subset nesting, composition changes, and the effects of seed/data-seed choices are unknown |
| Complete historical dependency lock, commits, model revisions, and benchmark/cache versions | Original training and evaluation environments cannot be recreated exactly |
| Decontamination scripts, matched-pair review, or cleaned-subset report | No completed contamination audit or contamination-free claim is supported |

The manuscript reports the original run plus variants using seeds 2024 and 3407. The original run's seed is not recovered; it must not be assumed to be 42. E4 seed generators and proposed YAMLs do not establish that their instructions were executed. A separate high-quality 15K configuration mentioned in the audit is not evidence for the ordinary 15K setting in the main results.

## Statistics and interpretation

- `n_runs=3` represents the manuscript's three trained-checkpoint evaluations at each fine-tuned 1.5B budget. It does not expose the underlying seed scores. The baseline and both 3B entries use `n_runs=1`.
- The manuscript reports sample SD, conventionally using an n-1 denominator. This repository transcribes that SD; it does not recompute it. A reported `0.00` SD is preserved. Empty SD cells mean unavailable or unreported, not zero.
- Derived changes are differences between printed two-decimal scores. They retain the source's rounding limits. No standard errors, confidence intervals, p-values, or inferred per-seed data are manufactured.
- Greedy decoding is reported by the manuscript. It does not, by itself, guarantee bitwise identity across unspecified software/hardware environments.
- The manuscript reports the same sanitization/import-patching pipeline for comparable checkpoints. Without its source and outputs, that consistency remains a reported method rather than a newly verified execution fact.

## Environment boundary and next evidence needed

The historical environment is reported as Python 3.11, PyTorch 2.11.0, CUDA 12.8, an NVIDIA GeForce RTX 5090, LLaMA-Factory, Transformers, and EvalPlus. These are E3 manuscript statements, not an environment reproduced here. No GPU training or inference was run for this companion.

`requirements.txt` pins the locally installed plotting dependencies. It is not a historical training lockfile, and validation on other operating systems or Python versions has not been performed. Figure hashes identify the current exports; different compatible environments may render different bytes.

To progress to L2, recover identified checkpoints, exact generation/post-processing/evaluation source, benchmark revisions, and task-level outputs. L3 additionally needs the training data and selection records, full launch configurations, original seeds, training logs, and all per-run results. A new implementation could support a new experiment, but would not recover the missing historical evidence.
