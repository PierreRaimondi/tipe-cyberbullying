import src.Database as db, time as t
from config import lists
from src.Tweet import Tweet

# Score à partir duquel on garde les tweets
minScore = 40

def createTweetScore(tweet:Tweet,showOutput:bool = False) -> float:
    """Attribue à un tweet son score.\n
    Renvoie le score et modifie également le tweet (tweet.score)."""
    assert type(tweet) == Tweet, "tweet doit être de type \"Tweet\""
    text = tweet.text
    score = 0
    wordNumber = 0
    # Remplace la mention dans le tweet par {mention}
    if tweet.tagged_users:
        if len(tweet.tagged_users) > 0:
            for i in tweet.tagged_users:
                text = text.replace(str(i), '{mention}')
    # Filtrage
    if tweet.matching_rules:
        for i in tweet.matching_rules:
            lst = getattr(lists, i)
            for j in lst:
                if j in text:
                    wordValue = getattr(lists, i)[j]
                    score += text.count(j) * wordValue
                    wordNumber += text.count(j)
                    if showOutput == True:
                        print(f"Tweet {tweet.db_ID} : \"{j}\" ({wordValue}) détecté {text.count(j)} fois ({i})")
    else:
        lists_names = [i for i in dir(lists) if not i.startswith("__")]
        for i in lists_names:
            lst = getattr(lists, i)
            for j in lst:
                if j in text:
                    wordValue = getattr(lists, i)[j]
                    score += text.count(j) * wordValue
                    wordNumber += text.count(j)
                    if showOutput == True:
                        print(f"Tweet {tweet.db_ID} : \"{j}\" ({wordValue}) détecté {text.count(j)} fois ({i})")
        
    # Attribution du score
    if wordNumber == 0:
        finalScore = 0
    else:
        finalScore = score/wordNumber
    tweet.score = finalScore
    return finalScore


def filterTweet(tweet:Tweet) -> int:
    """Filtre le tweet dans la base de données.\n
    Renvoie 1 si le tweet a été gardé, et 0 si le tweet a été supprimé."""
    assert type(tweet) == Tweet, "tweet doit être de type \"Tweet\""
    if tweet.score != None and tweet.db_ID != None:
        if tweet.score < minScore:
            db.deleteTweet(tweet)
            return 0
        else:
            db.updateScore(tweet.db_ID,tweet.score)
            return 1

def start(showOutput:bool = False) -> None:
    """Lance le second filtrage"""
    startTime = t.time()
    print((" LANCEMENT DU SECOND FILTRAGE ").center(70,('=')))
    print("\n")
    totalTweets = 0
    deletedTweets = 0
    tweet, tweetNumber, filteredTweets = db.getTweetWithoutScore(), db.getTweetsNumberWithoutScore(), 0    
    while tweet != None:
        totalTweets += 1
        createTweetScore(tweet,showOutput)
        result = filterTweet(tweet)
        filteredTweets += 1
        print(f"\rFiltrage des tweets... {round((filteredTweets/tweetNumber)*100,1)}%", end='')
        if result == 0:
            deletedTweets += 1
        tweet = db.getTweetWithoutScore()
    print("")
    print("Suppression des auteurs...")
    deletedAuthors = db.deleteAuthors()
    endTime = t.time()
    print("\n")
    print((f" SECOND FILTRAGE TERMINÉ EN {round(endTime-startTime,2)} SECONDES ").center(70,('=')))
    print((f" {totalTweets} TWEETS FILTRÉS ").center(70,('=')))
    if totalTweets == 0:
        tweetRatio = 100
    else:
        tweetRatio = round(((totalTweets-deletedTweets)/totalTweets)*100,2)
    print((f" DONT {totalTweets-deletedTweets} CONSERVÉS ({tweetRatio}%) ET {deletedTweets} SUPPRIMÉS ").center(70,('=')))
    print((f" {deletedAuthors} AUTEURS SUPPRIMÉS ").center(70,('=')))
    return None