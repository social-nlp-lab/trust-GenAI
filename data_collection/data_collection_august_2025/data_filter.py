import pandas as pd
import glob
import os
import re
import csv

# Load keywords and build regex patterns
keywords_patterns = []
with open("keywords.txt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            keyword, case_sensitive, kw_type = line.split("|")
        except ValueError:
            continue
        case_sensitive = case_sensitive.lower() == "yes"

        if kw_type == "type_1":  
            pattern = r"\b" + re.escape(keyword.rstrip("*")) + r"\w*"
        elif kw_type == "type_2":  
            pattern = r"\b" + r"\s+".join(map(re.escape, keyword.split())) + r"\b"
        elif kw_type == "type_3":  
            pattern = r"\b" + re.escape(keyword) + r"\b"
        else:
            continue

        regex = re.compile(pattern, 0 if case_sensitive else re.IGNORECASE)
        keywords_patterns.append((regex, keyword))

# Folders
input_folder = "input_jsonl"
output_folder = "output_csvs"
os.makedirs(output_folder, exist_ok=True)

# Keyword matching
def matches_keywords(text):
    if pd.isna(text) or not text.strip():
        return False
    return any(regex.search(text) for regex, _ in keywords_patterns)

# Process JSONL files
for file_path in glob.glob(os.path.join(input_folder, "*.jsonl")):
    print("Processing:", file_path)
    try:
        df = pd.read_json(file_path, lines=True)
    except Exception as e:
        print("Failed to read:", file_path, e)
        continue

    required_cols = ["author", "selftext"]
    if not all(col in df.columns for col in required_cols):
        print(f"Missing columns in {file_path}, skipping")
        continue

    df = df[~df["author"].isin(["[removed]", "[deleted]", ""])]
    df = df[~df["selftext"].isin(["[removed]", "[deleted]", ""])]

    if "title" not in df.columns:
        df["title"] = ""

    mask = df["title"].apply(matches_keywords) | df["selftext"].apply(matches_keywords)
    filtered = df.loc[mask, ["id", "author", "subreddit", "created_utc", "title", "selftext"]]

    filtered["selftext"] = filtered["selftext"].str.replace(r"[\r\n]+", " ", regex=True)

    out_file = os.path.join(output_folder, os.path.basename(file_path).replace(".jsonl", ".csv"))
    filtered.to_csv(out_file, index=False)
    print(f"Saved {len(filtered)} rows to {out_file}")
