# Trust-TACL 2026 Dataset

Annotated dataset of **2,690 Reddit posts** with trust/distrust labels and fine-grained trust dimensions.

Per Reddit's Terms of Service, post text cannot be redistributed directly. We share post IDs and annotations in a CSV file. Use the hydration script below to fetch the original post content from Reddit.

## Usage

### Install

```bash
pip install requests
```

### Run

```bash
python hydrate_reddit_posts.py your_dataset.csv
```

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

```
[Citation TBD]
```
