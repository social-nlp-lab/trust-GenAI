# Trust-TACL 2026 Dataset

Annotated dataset of **2,690 Reddit posts** with trust/distrust labels and fine-grained trust dimensions.

Use the hydration script below to fetch the original post content from Reddit.

## Dataset Availability

The dataset used in this study is publicly available on Zenodo:

https://zenodo.org/records/20331918

## Usage

### Install

```bash
pip install requests
```

### Run

```bash
python hydrate_reddit_posts.py sample_input.csv
```
Please refer to the Zenodo link above for the complete dataset. The provided `sample_input.csv` file contains the IDs of only 30 posts and is intended for demonstration purposes. Running the hydration script on this file will retrieve only those 30 Reddit posts.

The input CSV must have an `id` column containing Reddit post IDs. No API keys or Reddit account needed.

### Output

- **`hydrated_posts.csv`** — columns: `id`, `title`, `text`
- **`hydration_report.txt`** — summary of the run

Join `hydrated_posts.csv` with your input CSV on the `id` column to get the full annotated dataset.

## Notes

- Deleted/removed posts appear as `[DELETED_OR_UNAVAILABLE]` in the text column.
- If interrupted, re-run the same command — it resumes from where it left off.
- Requires Python 3.6+.

## Citation

For citation information for both the paper and dataset, please refer to the repository's main `README.md`

