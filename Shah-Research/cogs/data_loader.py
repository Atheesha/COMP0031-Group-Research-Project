import pandas as pd
import numpy as np

def load_data():
    # Load posts CSV
    posts = pd.read_csv("csv_files/posts.csv", dtype={
        "author": str, 
        "created_utc": str,  
        "edited": str,  
        "submission_id": str, 
        "num_comments": "Int64", 
        "permalink": str, 
        "score": "Int64", 
        "selftext": str, 
        "subreddit": str, 
        "title": str, 
        "upvote_ratio": float, 
        "disclosure_post": "Int64",
        "disclosure_title": "Int64",
        "disclosure_total": str  # Read as string initially
    }, low_memory=False)

    # Load comments CSV
    comments = pd.read_csv("csv_files/comments.csv", dtype={
        "author": str, 
        "body": str, 
        "created_utc": str,  
        "comment_id": str, 
        "edited": str, 
        "is_submitter": str, 
        "link_id": str, 
        "permalink": str, 
        "parent_id": str, 
        "score": "Int64", 
        "subreddit": str, 
        "disclosure_total": str  # Read as string initially
    }, low_memory=False)

    # Convert 'disclosure_total' to numeric, coercing errors to NaN (non-numeric values)
    comments["disclosure_total"] = pd.to_numeric(comments["disclosure_total"], errors="coerce")

    # Optionally, handle the NaN values by filling them with a specific number or leaving as NaN
    # comments["disclosure_total"].fillna(0, inplace=True)  # Uncomment to replace NaNs with 0

    return posts, comments
