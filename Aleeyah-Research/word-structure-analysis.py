import pandas as pd
import re
from scipy.stats import chi2_contingency, mannwhitneyu


df = pd.read_csv("comments.csv", low_memory=False)
df['body'] = df['body'].astype(str).str.strip()

# Flag censored comments (TW/CW/NSFW markers)
df['is_censored'] = df['body'].str.contains(
    r'\b(?:TW|CW|NSFW)\b', 
    case=False, 
    na=False
)

# Precompute text features for all comments upfront
df['has_question_mark'] = df['body'].str.contains(r'\?', regex=True, na=False)
df['has_quotation_marks'] = df['body'].str.contains(r'[\"\'“”‘’]', regex=True, na=False)
df['has_brackets'] = df['body'].str.contains(r'\([^)]*\)', regex=True, na=False)
df['has_asterisk_pair'] = df['body'].str.contains(r'\*[^*]+\*', regex=True, na=False)
df['parentheses_count'] = df['body'].apply(lambda x: len(re.findall(r'\([^)]*\)', x)))
df['asterisk_phrase_count'] = df['body'].apply(lambda x: len(re.findall(r'\*[^*]+\*', x)))

# ------------------------------
# Analysis Functions
# ------------------------------
def analyze_group(group_df, group_label, subreddit):
    """Analyze and print statistics for a comment group (censored/uncensored)."""
    if group_df.empty:
        print(f"No {group_label} comments in {subreddit}")
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


# Main Analysis Loop

for subreddit in df['subreddit'].unique():
    print("\n" + "="*60)
    print(f"Analyzing r/{subreddit}")
    print("="*60)
    
    sub_df = df[df['subreddit'] == subreddit]
    censored = sub_df[sub_df['is_censored']]
    uncensored = sub_df[~sub_df['is_censored']]
    
    # Basic counts
    print(f"\nTotal Comments: {len(sub_df)}")
    print(f"Censored: {len(censored)} ({len(censored)/len(sub_df):.1%})")
    print(f"Uncensored: {len(uncensored)} ({len(uncensored)/len(sub_df):.1%})")
    
    # Group analysis
    analyze_group(censored, "Censored", subreddit)
    analyze_group(uncensored, "Uncensored", subreddit)
    
    # Statistical comparisons
    compare_groups(censored, uncensored, subreddit)
    