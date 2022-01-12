from requests.api import get
from config import lists
import src.Database as db
from src.User import User
from src.Tweet import Tweet
import time as t

# Score à partir duquel on garde les tweets
minScore = 40

def createTweetScore(tweet:Tweet,showOutput:bool = False) -> float:
    """Attribue à un tweet son score.\n
    Renvoie le score et modifie également le tweet (tweet.score)."""
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
                        print("Tweet {} : \"{}\" ({}) détecté {} fois ({})".format(tweet.db_ID,j,wordValue,text.count(j),i))
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
                        print("Tweet {} : \"{}\" ({}) détecté {} fois ({})".format(tweet.db_ID,j,wordValue,text.count(j),i))
        
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
    tweet = db.getTweetWithoutScore()
    print("Filtrage des tweets...")
    while tweet != None:
        totalTweets += 1
        createTweetScore(tweet,showOutput)
        result = filterTweet(tweet)
        if result == 0:
            deletedTweets += 1
        tweet = db.getTweetWithoutScore()
    print("Suppression des auteurs...")
    deletedAuthors = db.deleteAuthors()
    endTime = t.time()
    print("\n")
    print((" SECOND FILTRAGE TERMINÉ EN {} SECONDES ".format(round(endTime-startTime,2))).center(70,('=')))
    print((" {} TWEETS FILTRÉS ".format(totalTweets)).center(70,('=')))
    if totalTweets == 0:
        tweetRatio = 100
    else:
        tweetRatio = round(((totalTweets-deletedTweets)/totalTweets)*100,2)
    print((" DONT {} CONSERVÉS ({}%) ET {} SUPPRIMÉS ".format(totalTweets-deletedTweets,tweetRatio,deletedTweets)).center(70,('=')))
    print((" {} AUTEURS SUPPRIMÉS ".format(deletedAuthors)).center(70,('=')))
    return None