import pandas as pd
import matplotlib.pyplot as plt
import sys
from datetime import datetime, timedelta

# Load datasets with proper dtype handling
posts = pd.read_csv("./csv_files/posts.csv", dtype={"created_utc": "str"}, low_memory=False)
comments = pd.read_csv("./csv_files/comments.csv", dtype={"created_utc": "str"}, low_memory=False)

# Convert timestamps to datetime safely
posts["created_utc"] = pd.to_numeric(posts["created_utc"], errors="coerce")
posts = posts.dropna(subset=["created_utc"])
posts["created_utc"] = posts["created_utc"].astype(int)
posts["created_utc"] = pd.to_datetime(posts["created_utc"], unit="s")

comments["created_utc"] = pd.to_numeric(comments["created_utc"], errors="coerce")
comments = comments.dropna(subset=["created_utc"])
comments["created_utc"] = comments["created_utc"].astype(int)
comments["created_utc"] = pd.to_datetime(comments["created_utc"], unit="s")

# Function to round time to the nearest 30 minutes
def round_to_nearest_30(dt):
    new_minute = (dt.minute // 30) * 30
    if dt.minute % 30 >= 15:  # If closer to the next 30-minute mark, round up
        new_minute += 30
    return dt.replace(minute=new_minute % 60, second=0, microsecond=0)

# Extract rounded hh:mm from created_utc
posts["created_time"] = posts["created_utc"].apply(round_to_nearest_30).dt.strftime("%H:%M")

# Identify repeat posters (users with multiple disclosures)
repeat_posters = posts[posts["disclosure_post"] == 1].groupby("author").filter(lambda x: len(x) > 1)

# Fix edited column handling
repeat_posters["edited"] = repeat_posters["edited"].replace({"FALSE": False, "TRUE": True}).astype(bool)

# Track engagement trends over time
engagement_trends = repeat_posters.groupby(["created_utc"]).agg(
    {"num_comments": "sum", "score": "mean"}
).reset_index()

# Track edit/delete behavior of repeat posters
edit_trends = repeat_posters.groupby("created_utc")["edited"].sum().reset_index()

# Output summary
summary = pd.DataFrame({
    "avg_score": repeat_posters.groupby("author")["score"].mean(),
    "total_comments": repeat_posters.groupby("author")["num_comments"].sum(),
    "num_edits": repeat_posters.groupby("author")["edited"].sum()
})

# Group metrics by created time
aggregated_trends = posts.groupby("created_time").agg(
    disclosure_post=("disclosure_post", "sum"),
    upvote_ratio=("upvote_ratio", "mean"),
    num_comments=("num_comments", "sum")
).reset_index()

def plot_graph(option="engagement"):
    plt.figure(figsize=(10, 5))
    
    if option == "engagement":
        plt.plot(engagement_trends["created_utc"], engagement_trends["num_comments"], marker='o', linestyle='-', label="Comments", color='blue')
        plt.plot(engagement_trends["created_utc"], engagement_trends["score"], marker='s', linestyle='-', label="Score", color='green')
        plt.ylabel("Engagement Metrics")
        plt.title("Engagement Trends for Repeat Posters")
    elif option == "edits":
        plt.plot(edit_trends["created_utc"], edit_trends["edited"], marker='o', linestyle='-', color='red', label="Edits")
        plt.ylabel("Number of Edits")
        plt.title("Editing Behavior of Repeat Posters")
    elif option == "upvote_ratio":
        plt.bar(aggregated_trends["created_time"], aggregated_trends["upvote_ratio"], color='purple')
        plt.xlabel("Time (hh:mm)")
        plt.ylabel("Average Upvote Ratio")
        plt.title("Upvote Ratio by Time of Post Creation (Rounded to 30 min)")
        plt.xticks(rotation=90)
    elif option == "disclosures":
        plt.bar(aggregated_trends["created_time"], aggregated_trends["disclosure_post"], color='orange')
        plt.xlabel("Time (hh:mm)")
        plt.ylabel("Number of Disclosures")
        plt.title("Disclosures by Time of Post Creation (Rounded to 30 min)")
        plt.xticks(rotation=90)
    
    plt.xlabel("Date" if option not in ["upvote_ratio", "disclosures"] else "Time (hh:mm)")
    plt.xticks(rotation=45)
    plt.legend() if option not in ["upvote_ratio", "disclosures"] else None
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "cli":
        if sys.argv[2] == "edits":
            if "-o" in sys.argv:
                column = sys.argv[sys.argv.index("-o") + 1]
                print(summary.sort_values(column, ascending=False))
            else:
                print(summary.sort_values("num_edits", ascending=False))
        elif sys.argv[2] == "engagement":
            if "-o" in sys.argv:
                column = sys.argv[sys.argv.index("-o") + 1]
                print(summary.sort_values(column, ascending=False))
            else:
                print(summary.sort_values("total_comments", ascending=False))
        elif sys.argv[2] == "disclosures":
            if "-o" in sys.argv:
                column = sys.argv[sys.argv.index("-o") + 1]
                print(aggregated_trends.sort_values(column, ascending=False))
            else:
                print(aggregated_trends)
        else:
            print("Invalid option. Use 'cli edits', 'cli engagement', or 'cli disclosures'")
    elif len(sys.argv) > 1:
        if sys.argv[1] == "edits":
            plot_graph("edits")
        elif sys.argv[1] == "engagement":
            plot_graph("engagement")
        elif sys.argv[1] == "upvote_ratio":
            plot_graph("upvote_ratio")
        elif sys.argv[1] == "disclosures":
            plot_graph("disclosures")
        else:
            print("Invalid option. Use 'edits', 'engagement', 'upvote_ratio', or 'disclosures'")
    else:
        plot_graph("engagement")