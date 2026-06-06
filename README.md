# TACL Pipeline Notebook

This repository contains the organized analysis notebook for the TACL project on trust and distrust in Reddit discourse about Generative AI / Large Language Models.

The main notebook is:

TACL_GitHub_Repo.ipynb

The notebook has been reorganized into a clearer research pipeline while preserving the original code logic. Each code cell includes its original cell index so that the cleaned notebook can still be traced back to the uploaded working notebook.

## What the Notebook Does

The notebook supports the full analysis workflow:

1. Loads and prepares the manually annotated ground-truth dataset.
2. Evaluates Task 1 classification models for four labels:
   - Trust
   - Distrust
   - Both
   - Neither
3. Evaluates Task 2 models for trust/distrust dimensions.
4. Runs or loads full-corpus Task 1 batch predictions.
5. Runs or loads full-corpus Task 2 batch predictions.
6. Analyzes dimension frequencies, co-occurrences, and temporal patterns.
7. Extracts and analyzes trustor and reason categories.
8. Includes later TACL editorial/revision experiments.

## Notebook Organization

The cleaned notebook is structured as follows:

0. Imports, API configuration, and global utilities
1. Load and prepare the manually annotated ground-truth data
2. Task 1 classification: Trust / Distrust / Both / Neither
3. Task 2 dimension extraction on manually annotated data
4. Annotation agreement, dimension prevalence, and performance relationships
5. Full-corpus data preparation and Task 1 batch labeling
6. Full-corpus Task 2 batch labeling
7. Analyze full-corpus Task 2 dimension results
8. Reason and trustor extraction
9. TACL editorial / revision experiments
10. Final data-sharing export
11. Remaining unclassified/diagnostic cells


### CSV files
Required datasets shared on Zenodo

### Full rerun mode

Use this mode only if you want to rerun LLM inference and batch jobs.

You will need:

1. The manually annotated data file.
2. The full-corpus Reddit CSV files.
3. API credentials for relevant providers.
4. OpenAI Batch API access.
5. Enough time and budget for model inference.


## Notes for Reproducibility

- Run cells sequentially within each section.
- API/batch cells can be skipped if cached CSV outputs are available.
- Several cells save intermediate files that later sections reload.
- The cleaned notebook preserves original cell indices in metadata for traceability.
- Some later cells are revision/diagnostic experiments rather than core pipeline steps.


## Contact

For questions about the project or notebook, contact ap3943@drexel.edu.
