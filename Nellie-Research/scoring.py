import csv
import re
from operator import itemgetter
pronouns = ["i","me","myself","mine"]

def medicationPosts(posts):
        with open('medication_names.csv', newline='', encoding='utf-8-sig') as mednames:
                medicationNames = []
                reader = csv.reader(mednames, delimiter=',')
                for row in reader:
                        medicationNames.extend(row)
        counter = 0
        for row in posts:
                for medication in medicationNames:
                        if ((medication) in row['selftext'] or (" "+medication) in row['title']):
                                print("the following contains:", medication)
                                #print(row["title"]," ",row["selftext"])
                                #print("---------------------------------------")
                                counter += 1
                                break
        print(counter, "posts detected")

def medicationComments(comments):
        with open('medication_names.csv', newline='', encoding='utf-8-sig') as mednames:
                medicationNames = []
                reader = csv.reader(mednames, delimiter=',')
                for row in reader:
                        medicationNames.extend(row)
        counter = 0
        for row in comments:
                #for medication in medicationNames:
                if ('azona' in row['body']):
                #if re.search(rf'\b{re.escape(medication)}\b', row['body'], re.IGNORECASE):
                        #print("the following contains:", medication)
                        print(row["body"])
                        #print("---------------------------------------")
                        counter += 1
                        #break
        print(counter, "comments detected")

def keywordSearch(text):
        words = re.findall(r'\b\w+\b', text.lower()) 
        length = len(words)
        if length < 5:
                return 0
        matches = sum(2 for word in words if word in mhLexicon)
        matches += sum(1 for word in words if word in emLexicon)
        if(matches != 0):
                matches += sum(1 for word in words if word in pronouns)
                factor = min(length / 100, 1)
                return ((matches / length) * (1 + factor))
        else:
                return 0

with open('mentalhealth_lexicon.csv', newline='', encoding='utf-8-sig') as file:
        content = file.read() 
        mhLexicon = set(word.lower() for word in content.split(','))  

with open('emotion_lexicon.csv', newline='', encoding='utf-8-sig') as file:
        content = file.read() 
        emLexicon = set(word.lower() for word in content.split(',')) 

ranked = []
seen = set()
with open('sanitisedPosts.csv', newline='', encoding='utf-8-sig') as csvfile:
        postReader = csv.DictReader(csvfile, delimiter=',')
        for row in postReader:
                if row['submission_id'] not in seen:
                        seen.add(row['submission_id'])
                        text = row['title'] + " " + row['selftext']
                        score = keywordSearch(text)
                        if score > 0:
                                #print("found a score of:", score)
                                ranked.append({"score": score, 
                                        "submission_id": row['submission_id'], 
                                        "author": row['author'], 
                                        "subreddit": row['subreddit'], 
                                        "body": text})

print("DONE W POSTS")

with open('sanitisedComments.csv', newline='', encoding='utf-8-sig') as csvfile:
        commentReader = csv.DictReader(csvfile, delimiter=',')
        for row in commentReader:
                if row['comment_id'] not in seen:
                        seen.add(row['comment_id'])
                        score = keywordSearch(row['body'])
                        if score > 0:
                                #print("found a score of:", score)
                                ranked.append({"score": score, 
                                        "submission_id": row['comment_id'], 
                                        "author": row['author'], 
                                        "subreddit": row['subreddit'], 
                                        "body": row['body']})
                        

print("DONE W COMMENTS")

ranked.sort(key=itemgetter('score'), reverse=True)

with open('backupResults.csv', mode='w', newline='', encoding='utf-8-sig') as output:
    fieldnames = ["score","submission_id", "author", "subreddit", "body"]
    postWriter = csv.DictWriter(output, fieldnames=fieldnames)
    postWriter.writeheader()
    postWriter.writerows(ranked)

print("DONE W SORTING")
