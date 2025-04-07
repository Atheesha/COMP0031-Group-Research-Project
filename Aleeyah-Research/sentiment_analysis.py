#!/usr/bin/env python3
"""
sentiment_analysis.py

This script calculates the sentiment of an input phrase using NLTK's VADER SentimentIntensityAnalyzer.
If run as a script, it will prompt the user for a phrase or accept command-line arguments.
"""

import sys
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download the VADER lexicon if not already available (quietly)
nltk.download('vader_lexicon', quiet=True)

def analyze_phrase(phrase: str) -> dict:
    """
    Analyze the sentiment of a phrase using VADER.

    Parameters:
        phrase (str): The input phrase.

    Returns:
        dict: A dictionary with sentiment scores (negative, neutral, positive, compound).
    """
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(phrase)
    return scores

def main():
    # Check for a phrase passed via command-line arguments; otherwise, prompt the user.
    if len(sys.argv) > 1:
        phrase = " ".join(sys.argv[1:])
    else:
        phrase = input("Enter a phrase to analyze its sentiment: ")

    # Calculate sentiment scores for the given phrase.
    scores = analyze_phrase(phrase)

    # Print the results.
    print("\nSentiment Analysis Results:")
    for k, v in scores.items():
        print(f"{k.capitalize()}: {v}")

if __name__ == "__main__":
    main()
