import csv
import re

options ="1: explicit mh disclosure\n" \
        "2: low mood disclosure\n" \
        "3: incorrect/ambiguous\n" \
        "u: undo"

fieldnames = ["score","submission_id", "author", "subreddit", "body"]
filenames = ["mhDisclosure.csv", "lmDisclosure.csv", "incorrect.csv"]

sorted = [[] for _ in range(3)]
toDelete = []
counter = 0

with open('mentalhealth_lexicon.csv', newline='', encoding='utf-8-sig') as file:
        content = file.read() 
        mhLexicon = set(word.lower() for word in content.split(','))  

with open('emotion_lexicon.csv', newline='', encoding='utf-8-sig') as file:
        content = file.read() 
        emLexicon = set(word.lower() for word in content.split(',')) 

def deleteSorted(filename):
    remaining = []
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['submission_id'] not in toDelete:
                remaining.append(row)
    
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(remaining)

def writeResults():
    index = 0
    for file in filenames:
        with open(file, mode='a', newline='', encoding='utf-8-sig') as resultFile:
            postWriter = csv.DictWriter(resultFile, fieldnames=fieldnames)
            postWriter.writerows(sorted[index])
        index += 1

def printMessage(text):
    contains = set()
    words = re.findall(r'\b\w+\b', text.lower()) 
    for word in words:
        if word in mhLexicon: contains.add(word)
        if word in emLexicon: contains.add(word)

    print("\nSORT THIS MESSAGE (contains:",contains,":\n")
    print(text)
    print("---------\n"+options+"\n")

def selectOption(choice, row, prevRow, prevChoice):
        global counter, toDelete, sorted
        if choice.isdigit() and 1 <= int(choice) <= len(filenames):
            sorted[int(choice) - 1].append(row)
            toDelete.append(row['submission_id'])
            print("sorted successfully")
            counter += 1
        elif (choice == "u" or choice == "undo"):
            if prevChoice:
                    sorted[prevChoice - 1].pop()
                    toDelete.pop()
                    counter -= 1
                    printMessage(prevRow['body'])
                    choice = input()
                    selectOption(choice, prevRow, None, None)
                    printMessage(row['body'])
                    choice = input()
                    selectOption(choice, row, None, None)
            else:
                print("no previous choice")
                printMessage(row['body'])
                choice = input()
                selectOption(choice, row, prevChoice, prevRow)
        elif choice == "quit":
            return
        else:
                print("skipped")

def classify(filename):
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
            textReader = csv.DictReader(csvfile, delimiter=',')
            prevChoice = None
            prevRow = None
            for row in textReader:
                printMessage(row['body'])
                choice = input()
                if choice == "quit":
                    break
                else:
                    selectOption(choice, row, prevRow, prevChoice)
                    if choice.isdigit() and 1 <= int(choice) <= len(filenames):
                        prevChoice = int(choice)
                        prevRow = row
                    elif choice == "quit":
                        break

    print("sorted", counter, "posts, writing results")
    deleteSorted(filename)
    writeResults()


classify('results.csv')



                    