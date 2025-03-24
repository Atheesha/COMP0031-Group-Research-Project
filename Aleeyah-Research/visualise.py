import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def create_stacked_feature_chart(all_results: dict):
    features = ['question_pct', 'quote_pct', 'parentheses_pct', 'asterisk_pct']
    labels = ['Questions', 'Quotes', 'Parentheses', 'Asterisks']
    subreddits = list(all_results.keys())
    x = np.arange(len(subreddits))
    bar_width = 0.35

    # Build data arrays (percentages)
    cens_data = np.array([
        [all_results[sub]['censored_results'].get(feat, 0) * 100 for feat in features]
        for sub in subreddits
    ])
    uncens_data = np.array([
        [all_results[sub]['uncensored_results'].get(feat, 0) * 100 for feat in features]
        for sub in subreddits
    ])

    fig, ax = plt.subplots(figsize=(12, 7))
    cens_bottom = np.zeros(len(subreddits))
    uncens_bottom = np.zeros(len(subreddits))

    for i, label in enumerate(labels):
        ax.bar(x - bar_width/2, cens_data[:, i], bar_width, bottom=cens_bottom, label=label)
        ax.bar(x + bar_width/2, uncens_data[:, i], bar_width, bottom=uncens_bottom)
        cens_bottom += cens_data[:, i]
        uncens_bottom += uncens_data[:, i]

    ax.set_xticks(x)
    ax.set_xticklabels(subreddits, rotation=45, ha='right')
    ax.set_xlabel('Subreddit', fontweight='bold')
    ax.set_ylabel('Percentage of Comments (%)', fontweight='bold')
    ax.set_title('Stacked Feature Distribution: Censored vs Uncensored by Subreddit', fontweight='bold')
    ax.legend(title='Feature')
    ax.set_ylim(0, 100)
    ax.grid(True, linestyle='--', alpha=0.7)

    os.makedirs('visualizations', exist_ok=True)
    plt.tight_layout()
    plt.savefig('visualizations/stacked_feature_comparison.png')
    plt.close()
    print('Created stacked feature comparison chart')

def create_sentiment_violin_plots(sentiment_results: dict):
    """
    Create violin plots for the raw sentiment scores.
    For each subreddit, two violin plots (censored and uncensored) are plotted side by side.
    """
    subreddits = list(sentiment_results.keys())
    n = len(subreddits)
    
    # Extract sentiment score lists for each subreddit
    cens_data = []
    uncens_data = []
    valid_subreddits = []
    valid_positions = []
    
    position_idx = 0
    for sub in subreddits:
        cens_scores = sentiment_results[sub].get("censored_sentiment_scores", [])
        uncens_scores = sentiment_results[sub].get("uncensored_sentiment_scores", [])
        
        # Only include subreddits where both datasets have at least 2 elements
        if len(cens_scores) >= 2 and len(uncens_scores) >= 2:
            cens_data.append(cens_scores)
            uncens_data.append(uncens_scores)
            valid_subreddits.append(sub)
            valid_positions.append(position_idx)
        position_idx += 1
    
    # If no valid data, create a simple message plot
    if not valid_subreddits:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Insufficient data for violin plots\n(Need at least 2 data points per group)",
                ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        os.makedirs('visualizations', exist_ok=True)
        plt.savefig('visualizations/sentiment_violin_plots.png')
        plt.close()
        print('Created placeholder for sentiment violin plots - insufficient data')
        return
    
    x = np.arange(len(valid_subreddits))
    width = 0.35  # separation between censored and uncensored groups
    pos_cens = x - width/2
    pos_uncens = x + width/2
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    vp_cens = ax.violinplot(cens_data, positions=pos_cens, widths=width, showmeans=True)
    vp_uncens = ax.violinplot(uncens_data, positions=pos_uncens, widths=width, showmeans=True)
    
    # Customize the violin colors
    for pc in vp_cens['bodies']:
        pc.set_facecolor('blue')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)
    for pc in vp_uncens['bodies']:
        pc.set_facecolor('orange')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)
    
    ax.set_xticks(x)
    ax.set_xticklabels(valid_subreddits, rotation=45, ha='right')
    ax.set_xlabel('Subreddit', fontweight='bold')
    ax.set_ylabel('Compound Sentiment Score', fontweight='bold')
    ax.set_title('Violin Plots of Compound Sentiment Scores\n(Censored vs. Uncensored Comments)', fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    cens_patch = mpatches.Patch(color='blue', label='Censored')
    uncens_patch = mpatches.Patch(color='orange', label='Uncensored')
    ax.legend(handles=[cens_patch, uncens_patch], title='Group')
    
    os.makedirs('visualizations', exist_ok=True)
    plt.tight_layout()
    plt.savefig('visualizations/sentiment_violin_plots.png')
    plt.close()
    print('Created sentiment violin plots')

def main():
    # Read feature results from all_results.json
    with open('all_results.json') as f:
        all_results = json.load(f)
    create_stacked_feature_chart(all_results)
    
    # Read sentiment results from sentiment_results.json
    with open('sentiment_results.json') as f:
        sentiment_results = json.load(f)
    create_sentiment_violin_plots(sentiment_results)

if __name__ == '__main__':
    main()