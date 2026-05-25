# =============================================================
# Reddit Post Hydration Script for the Trust-TACL 2026 Dataset
# (Using requests — no API keys or credentials needed)
# =============================================================
#
# This script retrieves the original Reddit post content using
# the post IDs in the shared dataset CSV. It produces an output
# CSV with three columns: id, title, and content (post body).
# The input CSV only needs an "id" column; titles are fetched
# directly from Reddit.
#
# Per Reddit's Terms of Service, the full text of posts cannot
# be redistributed directly. Instead, we share post IDs and
# annotations, and this script allows you to reconstruct the
# original post text by fetching it from Reddit's public JSON
# endpoint.
#
# ----- HOW TO USE (2 steps) -----
#
# Step 1: Install the required Python library:
#
#     pip install requests
#
# Step 2: Run the script with the input CSV file:
#
#     python hydrate_reddit_posts.py your_dataset.csv
#
# That's it. No API keys, credentials, or Reddit account needed.
# The output will be saved as "hydrated_posts.csv".
#
# ----- NOTES -----
#
# - Posts that have been deleted or removed since the dataset was
#   collected will be marked as [DELETED_OR_UNAVAILABLE].
# - The script pauses between requests to respect Reddit's rate
#   limits. For 2,690 posts this takes a few hours.
# - If the script is interrupted, you can re-run it and it will
#   skip posts that were already fetched.
# - Requires Python 3.6+.
# - See README.md for more details.
# =============================================================

import csv
import os
import sys
import time

try:
    import requests
except ImportError:
    print("requests is not installed. Please run:  pip install requests")
    sys.exit(1)


OUTPUT_FILE = "hydrated_posts.csv"
REPORT_FILE = "hydration_report.txt"

HEADERS = {
    "User-Agent": "TrustTACL2026Hydration/1.0 (academic research dataset rehydration)"
}


def fetch_post(post_id):
    """Fetch a Reddit submission by its ID using Reddit's public JSON endpoint."""
    url = f"https://www.reddit.com/comments/{post_id}.json"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 429:
            return None, None, "rate_limited"
        if response.status_code != 200:
            return None, None, f"HTTP {response.status_code}"
        data = response.json()
        post_data = data[0]["data"]["children"][0]["data"]
        title = post_data.get("title", "")
        selftext = post_data.get("selftext", "")
        if selftext in ("[deleted]", "[removed]"):
            return None, None, "deleted/removed"
        return title, selftext, None
    except Exception as e:
        return None, None, str(e)


def load_already_fetched(output_file):
    """Load IDs already fetched from a previous partial run."""
    fetched = {}
    if not os.path.exists(output_file):
        return fetched
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["content"] != "[DELETED_OR_UNAVAILABLE]":
                    fetched[row["id"]] = row
    except Exception:
        pass
    return fetched


def main():
    # Get input file from command line
    if len(sys.argv) != 2:
        print("Usage: python hydrate_reddit_posts.py <input_csv_file>")
        print("Example: python hydrate_reddit_posts.py your_dataset.csv")
        sys.exit(1)

    input_file = sys.argv[1]

    start_time = time.time()

    print("=" * 60)
    print("  Reddit Post Hydration - Trust-TACL 2026 Dataset")
    print("=" * 60)
    print()

    # Read input CSV
    print(f"Reading posts from: {input_file}")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except UnicodeDecodeError:
        with open(input_file, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    total = len(rows)
    print(f"Found {total} posts to fetch.\n")

    # Check for previously fetched posts (resume support)
    already_fetched = load_already_fetched(OUTPUT_FILE)
    if already_fetched:
        print(f"Found {len(already_fetched)} previously fetched posts, skipping those.\n")

    # Fetch each post
    hydrated = []
    deleted_posts = []       # posts that were deleted/removed on Reddit
    other_failed_posts = []  # posts that failed for non-rate-limit reasons (e.g. HTTP errors)
    successful = 0
    skipped = 0
    total_rate_limits = 0

    for i, row in enumerate(rows):
        post_id = row["id"]

        # Skip if already fetched in a previous run
        if post_id in already_fetched:
            hydrated.append(already_fetched[post_id])
            skipped += 1
            successful += 1
            continue

        # Fetch with retry — if rate-limited, keep waiting and retrying
        # The script will NEVER give up due to rate limiting
        wait_time = 30
        fetched_title, selftext, error = fetch_post(post_id)
        while error == "rate_limited":
            total_rate_limits += 1
            print(f"  [{i+1}/{total}] Rate limited, waiting {wait_time}s and retrying...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 300)  # double wait each time, max 5 min
            fetched_title, selftext, error = fetch_post(post_id)

        if error == "deleted/removed":
            print(f"  [{i+1}/{total}] DELETED  id={post_id}")
            hydrated.append({
                "id": post_id,
                "title": "",
                "content": "[DELETED_OR_UNAVAILABLE]",
            })
            deleted_posts.append(post_id)
        elif error:
            print(f"  [{i+1}/{total}] FAILED  id={post_id}  ({error})")
            hydrated.append({
                "id": post_id,
                "title": "",
                "content": "[DELETED_OR_UNAVAILABLE]",
            })
            other_failed_posts.append((post_id, error))
        else:
            successful += 1
            hydrated.append({
                "id": post_id,
                "title": fetched_title,
                "content": selftext,
            })
            if (i + 1) % 50 == 0 or (i + 1) == total:
                print(f"  [{i+1}/{total}] fetched")

        # 6-second pause to respect Reddit's unauthenticated rate limits
        time.sleep(6.0)

    # Write output CSV
    print(f"\nSaving results to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "content"])
        writer.writeheader()
        writer.writerows(hydrated)

    elapsed = time.time() - start_time
    minutes, seconds = divmod(int(elapsed), 60)

    # Print summary
    print(f"\nDone! Total time: {minutes}m {seconds}s")
    print(f"  Successfully retrieved: {successful}/{total}")
    print(f"  Deleted/removed:        {len(deleted_posts)}")
    print(f"  Other failures:         {len(other_failed_posts)}")
    print(f"  Rate limit retries:     {total_rate_limits}")
    if skipped:
        print(f"  Skipped (from resume):  {skipped}")

    # Write report file
    print(f"\nWriting report to: {REPORT_FILE}")
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  Hydration Report - Trust-TACL 2026 Dataset\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Input file:             {input_file}\n")
        f.write(f"Output file:            {OUTPUT_FILE}\n")
        f.write(f"Total time:             {minutes}m {seconds}s\n\n")
        f.write(f"Total posts:            {total}\n")
        f.write(f"Successfully retrieved: {successful}\n")
        f.write(f"Deleted/removed:        {len(deleted_posts)}\n")
        f.write(f"Other failures:         {len(other_failed_posts)}\n")
        f.write(f"Rate limit retries:     {total_rate_limits}\n")
        if skipped:
            f.write(f"Skipped (from resume):  {skipped}\n")

        if deleted_posts:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"  Deleted/Removed Post IDs ({len(deleted_posts)})\n")
            f.write(f"{'=' * 60}\n")
            for pid in deleted_posts:
                f.write(f"  {pid}\n")

        if other_failed_posts:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"  Other Failed Post IDs ({len(other_failed_posts)})\n")
            f.write(f"{'=' * 60}\n")
            for pid, reason in other_failed_posts:
                f.write(f"  {pid}  ({reason})\n")


if __name__ == "__main__":
    main()
