from cs50 import SQL

db = SQL("sqlite:///xfiesta.db")

interests = [
    "Travel", "Music",
    "Gaming", "Reading",
    "Cooking", "Hiking",
    "Photography", "Movies",
    "Sports", "Art", "Technology",
    "Fashion", "Fitness",
    "Food", "Nature",
    "Pets", "Science",
    "History", "Writing", "Dancing"]

for interest in interests:
    db.execute("INSERT INTO interests(interest) VALUES(?);", interest)

print("Done :D")