#!/usr/bin/env python3
"""
sentiment_analysis.py

This module calculates the sentiment of a phrase using NLTK's VADER SentimentIntensityAnalyzer.
It provides the `analyze_phrase` function which returns a dictionary of sentiment scores.
"""

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Ensure the VADER lexicon is downloaded
nltk.download('vader_lexicon', quiet=True)

# Create a global instance of the sentiment analyzer
sia = SentimentIntensityAnalyzer()

def analyze_phrase(phrase: str) -> dict:
    """
    Analyze the sentiment of a phrase using VADER.
    
    Parameters:
        phrase (str): The phrase to analyze.
        
    Returns:
        dict: A dictionary with sentiment scores (e.g., 'neg', 'neu', 'pos', 'compound').
    """
    return sia.polarity_scores(phrase)

if __name__ == "__main__":
    import sys
    # If run directly, use command-line arguments or prompt for input.
    if len(sys.argv) > 1:
        phrase = " ".join(sys.argv[1:])
    else:
        phrase = input("Enter a phrase to analyze its sentiment: ")
    scores = analyze_phrase(phrase)
    print("Sentiment scores:", scores)
