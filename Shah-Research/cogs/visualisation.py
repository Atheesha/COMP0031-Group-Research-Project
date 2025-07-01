import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load datasets
posts = pd.read_csv(r"C:\Users\shahk\Documents\UCL\Y3\COMP0031 - Group Research\python\csv_files\posts.csv", dtype={"created_utc": "str"}, low_memory=False)
comments = pd.read_csv(r"C:\Users\shahk\Documents\UCL\Y3\COMP0031 - Group Research\python\csv_files\comments.csv", dtype={"created_utc": "str"}, low_memory=False)

# Load lexicons
mental_health_lexicon = pd.read_csv(r"C:\Users\shahk\Documents\UCL\Y3\COMP0031 - Group Research\python\csv_files\mentalhealth_lexicon.csv")
emotional_lexicon = pd.read_csv(r"C:\Users\shahk\Documents\UCL\Y3\COMP0031 - Group Research\python\csv_files\emotion_lexicon.csv")

# Convert lexicon CSVs into lists of words
mental_health_words = mental_health_lexicon.columns.tolist()
emotional_words = emotional_lexicon.columns.tolist()

# Function to count keyword appearances in text
def count_keywords(text, keywords):
    if pd.isna(text):
        return 0
    return sum(text.lower().count(word) for word in keywords)

# Apply keyword analysis to posts and comments
posts["mental_health_count"] = posts["title"].apply(lambda x: count_keywords(x, mental_health_words)) + posts["selftext"].apply(lambda x: count_keywords(x, mental_health_words))
posts["emotional_count"] = posts["title"].apply(lambda x: count_keywords(x, emotional_words)) + posts["selftext"].apply(lambda x: count_keywords(x, emotional_words))
posts["disclosure_score"] = posts["mental_health_count"] + posts["emotional_count"]

comments["mental_health_count"] = comments["body"].apply(lambda x: count_keywords(x, mental_health_words))
comments["emotional_count"] = comments["body"].apply(lambda x: count_keywords(x, emotional_words))
comments["disclosure_score"] = comments["mental_health_count"] + comments["emotional_count"]

# Convert score column to numeric
comments["score"] = pd.to_numeric(comments["score"], errors="coerce")

def plot_post_analysis(posts, comments):
    """Visualizes post-related data."""

    plt.figure(figsize=(12, 6))
    sns.histplot(posts["disclosure_score"], bins=30, kde=True, color="blue", label="Posts")
    sns.histplot(comments["disclosure_total"], bins=30, kde=True, color="red", label="Comments")
    plt.xlabel("Disclosure Score")
    plt.ylabel("Frequency")
    plt.title("Distribution of Disclosure Scores in Posts and Comments")
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=posts["disclosure_score"], y=posts["upvote_ratio"], alpha=0.5)
    plt.xlabel("Disclosure Score")
    plt.ylabel("Upvote Ratio")
    plt.title("Disclosure Score vs. Upvote Ratio")
    plt.show()

def plot_comment_analysis(comments):
    """Visualizes comment-related data."""

    tw_cw_comments = comments[comments["body"].str.contains(r'\b(?:TW|CW)\b', na=False, regex=True)]
    non_tw_cw_comments = comments[~comments["body"].str.contains(r'\b(?:TW|CW)\b', na=False, regex=True)]

    tw_cw_comments["type"] = "TW/CW"
    non_tw_cw_comments["type"] = "Non-TW/CW"
    combined = pd.concat([tw_cw_comments, non_tw_cw_comments])

    plt.figure(figsize=(10, 6))
    sns.violinplot(x="type", y="score", data=combined)
    plt.xlabel("Type")
    plt.ylabel("Comment Score")
    plt.title("Distribution of Comment Scores for TW/CW vs. Non-TW/CW")
    plt.show()
