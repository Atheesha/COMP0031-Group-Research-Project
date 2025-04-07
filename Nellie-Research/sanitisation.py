import csv
import re

def sanitise():
        # create dictionary of relevant, sanitised posts
        with open('posts.csv', newline='', encoding='utf-8-sig') as csvfile, \
        open('sanitisedPosts.csv', mode='w', newline='', encoding='utf-8-sig') as output:
                postReader = csv.DictReader(csvfile, delimiter=',')
                fieldnames = ["submission_id", "author", "subreddit", "title", "selftext"]
                postWriter = csv.DictWriter(output, fieldnames=fieldnames)
                postWriter.writeheader()
                for row in postReader:
                        if(row['selftext'] == "[deleted]" or row['selftext'] == "[removed]"):
                                continue
                        words = re.findall(r'\b\w+\b', row['selftext'].lower()) 
                        length = len(words)
                        if(length < 3):
                                continue
                        else:
                                rowDict = {}
                                rowDict.update({"submission_id": row['submission_id']})
                                rowDict.update({"author": row['author']})
                                rowDict.update({"subreddit": row['subreddit']})
                                rowDict.update({"title": row['title']})
                                rowDict.update({"selftext": row['selftext']})
                                postWriter.writerow(rowDict)
        print("finished with posts\n")
        with open('comments.csv', newline='', encoding='utf-8-sig') as csvfile, \
        open('sanitisedComments.csv', mode='w', newline='', encoding='utf-8-sig') as output:
                commentReader = csv.DictReader(csvfile, delimiter=',')
                fieldnames = ["comment_id", "parent_id", "author", "subreddit", "body"]
                commentWriter = csv.DictWriter(output, fieldnames=fieldnames)
                commentWriter.writeheader()
                for row in commentReader:
                        words = re.findall(r'\b\w+\b', row['body'].lower()) 
                        length = len(words)
                        if(length < 3):
                                continue
                        else:
                                rowDict = {}
                                rowDict.update({"comment_id": row['comment_id']})
                                rowDict.update({"parent_id": row['parent_id']})
                                rowDict.update({"author": row['author']})
                                rowDict.update({"subreddit": row['subreddit']})
                                rowDict.update({"body": row['body']})
                                commentWriter.writerow(rowDict)
        print("finished with comments\n") 

sanitise()



