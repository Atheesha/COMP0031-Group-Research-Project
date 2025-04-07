import argparse
import pandas as pd
import os
from cogs import visualisation

# Argument parser
parser = argparse.ArgumentParser(description="Analyze Reddit posts and comments for mental health disclosures.")
parser.add_argument("mode", choices=["posts", "comments"], help="Choose which dataset to analyze")
parser.add_argument("-v", "--visualize", action="store_true", help="Enable visualization")

args = parser.parse_args()

# Define file paths
posts_path = os.path.abspath("./csv_files/posts.csv")
comments_path = os.path.abspath("./csv_files/comments.csv")
mental_health_lexicon_path = os.path.abspath("./csv_files/mentalhealth_lexicon.csv")
emotional_lexicon_path = os.path.abspath("./csv_files/emotion_lexicon.csv")

# Load lexicon data
mental_health_words = pd.read_csv(mental_health_lexicon_path).columns.tolist()
emotional_words = pd.read_csv(emotional_lexicon_path).columns.tolist()

# Function to count keyword appearances in text
def count_keywords(text, keywords):
    if pd.isna(text):
        return 0
    return sum(text.lower().count(word) for word in keywords)

# Analyze posts
def analyse_posts():
    print("Loading posts data...")
    posts = pd.read_csv(posts_path, dtype={"created_utc": "str"}, low_memory=False)
    
    posts["mental_health_count"] = posts["title"].apply(lambda x: count_keywords(x, mental_health_words)) + posts["selftext"].apply(lambda x: count_keywords(x, mental_health_words))
    posts["emotional_count"] = posts["title"].apply(lambda x: count_keywords(x, emotional_words)) + posts["selftext"].apply(lambda x: count_keywords(x, emotional_words))
    posts["disclosure_score"] = posts["mental_health_count"] + posts["emotional_count"]

    # Engagement analysis
    engagement = posts.groupby(["mental_health_count", "emotional_count"]).agg(
        avg_upvote_ratio=("upvote_ratio", "mean"),
        avg_comments=("num_comments", "mean"),
        avg_disclosure_score=("disclosure_score", "mean"),
        total_posts=("submission_id", "count")
    ).reset_index()

    print("Post Engagement Analysis:")
    print(engagement.sort_values(by="total_posts", ascending=False))

    # Most and least upvoted posts
    most_upvoted = posts.loc[posts["upvote_ratio"].idxmax(), ["mental_health_count", "emotional_count", "upvote_ratio", "num_comments", "title", "selftext"]]
    least_upvoted = posts.loc[posts["upvote_ratio"].idxmin(), ["mental_health_count", "emotional_count", "upvote_ratio", "num_comments", "title", "selftext"]]

    print("\nMost Upvoted Post:")
    print(most_upvoted)
    print("\nLeast Upvoted Post:")
    print(least_upvoted)

    # Filtering for trigger warning (TW, CW)
    tw_cw_posts = posts[posts["title"].str.contains(r'\b(?:TW|CW)\b', na=False, regex=True)]
    non_tw_cw_posts = posts[~posts["title"].str.contains(r'\b(?:TW|CW)\b', na=False, regex=True)]

    print("\nTrigger Warning (TW/CW) vs. Non-Trigger Warning Posts Analysis:")
    print("TW/CW Posts Avg Upvote Ratio:", tw_cw_posts["upvote_ratio"].mean())
    print("Non-TW/CW Posts Avg Upvote Ratio:", non_tw_cw_posts["upvote_ratio"].mean())
    print("TW/CW Posts Avg Disclosure Score:", tw_cw_posts["disclosure_score"].mean())
    print("Non-TW/CW Posts Avg Disclosure Score:", non_tw_cw_posts["disclosure_score"].mean())

    # Neutral vs Emotional/Mental Health Posts
    neutral_posts = posts[posts["disclosure_score"] == 0]
    emotional_mh_posts = posts[posts["disclosure_score"] > 0]

    print("\nNeutral vs Emotional/Mental Health Posts:")
    print("Neutral Posts - Avg Comment Count:", neutral_posts["num_comments"].mean())
    print("Neutral Posts - Avg Disclosure Score:", neutral_posts["disclosure_score"].mean())
    print("Emotional/MH Posts - Avg Comment Count:", emotional_mh_posts["num_comments"].mean())
    print("Emotional/MH Posts - Avg Disclosure Score:", emotional_mh_posts["disclosure_score"].mean())


    return posts  # Return dataframe for visualization if needed

# Analyze comments
def analyse_comments():
    print("Loading comments data...")
    comments = pd.read_csv(comments_path, dtype={"created_utc": "str"}, low_memory=False)

    comments["mental_health_count"] = comments["body"].apply(lambda x: count_keywords(x, mental_health_words))
    comments["emotional_count"] = comments["body"].apply(lambda x: count_keywords(x, emotional_words))
    comments["disclosure_score"] = comments["mental_health_count"] + comments["emotional_count"]

    comments["score"] = pd.to_numeric(comments["score"], errors="coerce")

    # Engagement analysis
    engagement = comments.groupby(["mental_health_count", "emotional_count"]).agg(
        avg_score=("score", "mean"),
        avg_disclosure_score=("disclosure_score", "mean"),
        total_comments=("comment_id", "count")
    ).reset_index()

    print("Comment Engagement Analysis:")
    print(engagement.sort_values(by="total_comments", ascending=False))

    # Filtering for trigger warning (TW, CW)
    tw_cw_comments = comments[comments["body"].str.contains(r'\b(?:TW|CW)\b', na=False, regex=True)]
    non_tw_cw_comments = comments[~comments["body"].str.contains(r'\b(?:TW|CW)\b', na=False, regex=True)]

    print("\nTrigger Warning (TW/CW) vs. Non-Trigger Warning Comments Analysis:")
    print("TW/CW Comments Avg Score:", tw_cw_comments["score"].mean())
    print("Non-TW/CW Comments Avg Score:", non_tw_cw_comments["score"].mean())
    print("TW/CW Comments Avg Disclosure Score:", tw_cw_comments["disclosure_score"].mean())
    print("Non-TW/CW Comments Avg Disclosure Score:", non_tw_cw_comments["disclosure_score"].mean())

    return comments  # Return dataframe for visualization if needed

# Run selected analysis
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Reddit mental health data.")
    parser.add_argument("option", choices=["posts", "comments"], help="Choose to analyze posts or comments.")
    parser.add_argument("-v", "--visualize", action="store_true", help="Show visualization.")

    args = parser.parse_args()

    if args.option == "posts":
        print("Analysing posts")
        posts = analyse_posts()  # Store the returned DataFrame
        if args.visualize:
            comments = pd.read_csv(comments_path, dtype={"created_utc": "str"}, low_memory=False)  # Load comments for visualization
            visualisation.plot_post_analysis(posts, comments)
    elif args.option == "comments":
        print("Analysing comments")
        comments = analyse_comments()  # Store the returned DataFrame
        if args.visualize:
            visualisation.plot_comment_analysis(comments)
    else:
        analyse_posts()
        analyse_comments()
