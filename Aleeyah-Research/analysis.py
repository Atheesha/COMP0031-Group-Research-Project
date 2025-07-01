import pandas as pd
import re
import json
import random
from scipy.stats import chi2_contingency, mannwhitneyu
from sentiment_analysis import analyze_phrase  # Import the sentiment analysis function

# Read and preprocess the data
df = pd.read_csv("comments.csv", low_memory=False)
df['body'] = df['body'].astype(str).str.strip()

# Enhanced pattern:
# - Word boundaries for TW, CW, NSFW (case-insensitive)
# - Allow bold (**TW**), hidden (e.g., >!TW!<), or plain
pattern = r'(\*\*(TW|CW|NSFW)\*\*|\>\!(TW|CW|NSFW)\!\<|\b(TW|CW|NSFW)\b)'

# Flag censored comments
df['is_censored'] = df['body'].str.contains(
    pattern,
    case=False,
    regex=True,
    na=False
)

# Precompute text features for all comments upfront
df['has_question_mark'] = df['body'].str.contains(r'\?', regex=True, na=False)
df['has_quotation_marks'] = df['body'].str.contains(r'[\"\'""'']', regex=True, na=False)
df['has_brackets'] = df['body'].str.contains(r'\([^)]*\)', regex=True, na=False)
df['has_asterisk_pair'] = df['body'].str.contains(r'\*[^*]+\*', regex=True, na=False)
df['parentheses_count'] = df['body'].apply(lambda x: len(re.findall(r'\([^)]*\)', x)))
df['asterisk_phrase_count'] = df['body'].apply(lambda x: len(re.findall(r'\*[^*]+\*', x)))

# ------------------------------
# Helper Functions for Sentiment
# ------------------------------
def extract_phrases(text: str) -> list:
    """
    Extract phrases enclosed in double quotes, parentheses, or asterisk pairs.
    """
    phrases = []
    # Extract phrases in parentheses
    phrases.extend(re.findall(r'\(([^)]*)\)', text))
    # Extract phrases in double quotes
    phrases.extend(re.findall(r'"([^"]+)"', text))
    # Extract phrases in asterisk pairs
    phrases.extend(re.findall(r'\*([^*]+)\*', text))
    return phrases

# ------------------------------
# Existing Analysis Functions
# ------------------------------
def analyze_group(group_df, group_label, subreddit):
    """Analyze and print statistics for a comment group (censored/uncensored)."""
    if group_df.empty:
        print(f"No {group_label} comments in r/{subreddit}")
        return
    
    total = len(group_df)
    stats = {
        'question_marks': group_df['has_question_mark'].sum(),
        'quotes': group_df['has_quotation_marks'].sum(),
        'brackets': group_df['has_brackets'].sum(),
        'asterisks': group_df['has_asterisk_pair'].sum(),
        'parentheses_total': group_df['parentheses_count'].sum(),
        'asterisk_total': group_df['asterisk_phrase_count'].sum()
    }
    
    print(f"\n--- {group_label} Comments in r/{subreddit} ---")
    print(f"Total: {total} comments")
    print(f"With question marks: {stats['question_marks']} ({stats['question_marks']/total:.1%})")
    print(f"With quotation marks: {stats['quotes']} ({stats['quotes']/total:.1%})")
    print(f"With brackets: {stats['brackets']} ({stats['brackets']/total:.1%})")
    print(f"With asterisk pairs: {stats['asterisks']} ({stats['asterisks']/total:.1%})")
    print(f"Avg parentheses phrases per comment: {stats['parentheses_total']/total:.2f}")
    print(f"Avg asterisk phrases per comment: {stats['asterisk_total']/total:.2f}")

def compare_groups(censored, uncensored, subreddit):
    """Compare censored vs. uncensored groups using statistical tests."""
    if censored.empty or uncensored.empty:
        print("Skipping tests: One group is empty")
        return
    
    # Chi-square tests for binary features
    binary_features = [
        ('has_question_mark', "Question Marks"),
        ('has_quotation_marks', "Quotation Marks"),
        ('has_brackets', "Brackets"),
        ('has_asterisk_pair', "Asterisk Pairs")
    ]
    
    print("\nFeature Association Tests (Censored vs. Uncensored):")
    for col, name in binary_features:
        cont_table = pd.crosstab(
            pd.concat([censored[col], uncensored[col]]),
            pd.concat([pd.Series(1, index=censored.index), 
                       pd.Series(0, index=uncensored.index)])
        )
        chi2, p, _, _ = chi2_contingency(cont_table)
        print(f"{name}: χ²={chi2:.2f}, p={p:.4f}")

    # Mann-Whitney U tests for count features
    count_features = [
        ('parentheses_count', "Parentheses Phrases"),
        ('asterisk_phrase_count', "Asterisk Phrases")
    ]
    
    for col, name in count_features:
        u_stat, p_val = mannwhitneyu(
            censored[col], 
            uncensored[col],
            alternative='two-sided'
        )
        print(f"{name}: U={u_stat:.0f}, p={p_val:.4f}")

def compute_group_stats(group_df):
    """Compute the percentage of comments with each textual feature for visualization."""
    total = len(group_df)
    if total == 0:
        return {
            "question_pct": 0,
            "quote_pct": 0,
            "parentheses_pct": 0,
            "asterisk_pct": 0
        }
    return {
        "question_pct": group_df['has_question_mark'].sum() / total,
        "quote_pct": group_df['has_quotation_marks'].sum() / total,
        "parentheses_pct": group_df['has_brackets'].sum() / total,
        "asterisk_pct": group_df['has_asterisk_pair'].sum() / total
    }

# NEW: Function to compute the proportion of comments with any binary feature
def compute_binary_feature_prop(group_df):
    """Compute the proportion of comments that have at least one binary feature."""
    total = len(group_df)
    if total == 0:
        return 0
    # Check if any binary feature is True for each comment
    binary_present = group_df[['has_question_mark', 'has_quotation_marks', 'has_brackets', 'has_asterisk_pair']].any(axis=1)
    return binary_present.sum() / total

# Function to get exactly 50 sentiment scores for each group
def get_fifty_sentiment_scores(group_df, phrase_type="censored"):
    """
    Extract exactly 50 phrases from comments and analyze their sentiment.
    If not enough phrases are available in the initial sample, the function
    progressively increases sample size until 50 phrases are found or all
    comments are exhausted.
    """
    all_phrases = []
    all_sentiment_scores = []
    
    # Skip if group is empty
    if group_df.empty:
        print(f"No {phrase_type} comments available")
        return []
    
    # First try: sample a reasonable number of comments to extract phrases
    initial_sample_size = min(100, len(group_df))
    comment_sample = group_df.sample(n=initial_sample_size, random_state=42)
    
    # Extract all phrases from this sample
    for comment in comment_sample['body']:
        phrases = extract_phrases(comment)
        all_phrases.extend(phrases)
    
    # If we don't have enough phrases, keep sampling more comments
    remaining_df = group_df[~group_df.index.isin(comment_sample.index)]
    sample_increment = 50
    
    while len(all_phrases) < 50 and not remaining_df.empty:
        sample_size = min(sample_increment, len(remaining_df))
        additional_sample = remaining_df.sample(n=sample_size)
        remaining_df = remaining_df[~remaining_df.index.isin(additional_sample.index)]
        
        for comment in additional_sample['body']:
            additional_phrases = extract_phrases(comment)
            all_phrases.extend(additional_phrases)
    
    # Shuffle all collected phrases and take up to 50
    random.seed(42)
    random.shuffle(all_phrases)
    selected_phrases = all_phrases[:50]
    
    # Get sentiment scores for selected phrases
    for phrase in selected_phrases:
        if phrase.strip():  # Ensure phrase is not empty
            compound = analyze_phrase(phrase).get("compound", 0)
            all_sentiment_scores.append(compound)
    
    actual_count = len(all_sentiment_scores)
    print(f"Analyzed {actual_count} {phrase_type} phrases for sentiment")
    
    # If we couldn't get 50 phrases, duplicate some to reach 50
    # This ensures we always have 50 data points for visualization
    if 0 < actual_count < 50:
        print(f"WARNING: Could only find {actual_count} {phrase_type} phrases. Duplicating some to reach 50.")
        multiplier = 50 // actual_count + 1
        duplicated_scores = all_sentiment_scores * multiplier
        all_sentiment_scores = duplicated_scores[:50]
    
    return all_sentiment_scores

# ------------------------------
# Main Analysis Loop & Sentiment Output
# ------------------------------
all_results = {}
sentiment_results = {}  # Dictionary to store raw sentiment scores

for subreddit in df['subreddit'].unique():
    print("\n" + "="*60)
    print(f"Analyzing r/{subreddit}")
    print("="*60)
    
    sub_df = df[df['subreddit'] == subreddit]
    censored = sub_df[sub_df['is_censored']]
    uncensored = sub_df[~sub_df['is_censored']]
    
    # Basic counts
    total_comments = len(sub_df)
    censored_count = len(censored)
    uncensored_count = len(uncensored)
    print(f"\nTotal Comments: {total_comments}")
    if total_comments > 0:
        print(f"Censored: {censored_count} ({censored_count/total_comments:.1%})")
        print(f"Uncensored: {uncensored_count} ({(total_comments - censored_count)/total_comments:.1%})")
    else:
        print("Censored: 0 (N/A)")
        print("Uncensored: 0 (N/A)")
    
    # Group analysis
    analyze_group(censored, "Censored", subreddit)
    analyze_group(uncensored, "Uncensored", subreddit)
    
    # Statistical comparisons
    compare_groups(censored, uncensored, subreddit)
    
    # Compute percentages for visualization
    censored_stats = compute_group_stats(censored)
    uncensored_stats = compute_group_stats(uncensored)
    censorship_rate = censored_count / total_comments if total_comments else 0
    
    all_results[subreddit] = {
        "censored_results": censored_stats,
        "uncensored_results": uncensored_stats,
        "censorship_rate": censorship_rate
    }
    
    # NEW: Compute and print binary feature proportions
    censored_binary_pct = compute_binary_feature_prop(censored)
    uncensored_binary_pct = compute_binary_feature_prop(uncensored)
    print(f"\nSUBREDDIT {subreddit} CENSORED HAS {censored_binary_pct:.1%} BINARY FEATURES AND UNCENSORED HAS {uncensored_binary_pct:.1%} BINARY FEATURES")
    
    # ------------------------------
    # Extract Raw Sentiment Scores - EXACTLY 50 for each group if possible
    # ------------------------------
    print("\nExtracting sentiment data for phrases...")
    censored_sentiments = get_fifty_sentiment_scores(censored, "censored")
    uncensored_sentiments = get_fifty_sentiment_scores(uncensored, "uncensored")
    
    sentiment_results[subreddit] = {
        "censored_sentiment_scores": censored_sentiments,
        "uncensored_sentiment_scores": uncensored_sentiments
    }
    
    # NEW: Print :AK at the end of each subreddit's analysis
    print(":AK")

# Write overall feature results to JSON file
with open("all_results.json", "w") as f:
    json.dump(all_results, f, indent=2)

# Write raw sentiment results to a new JSON file
with open("sentiment_results.json", "w") as f:
    json.dump(sentiment_results, f, indent=2)

print("\nOverall analysis complete.")
print("Results saved to 'all_results.json' and 'sentiment_results.json'.")
