import sqlite3
from classes.User import User
from classes.Tweet import Tweet
from datetime import datetime, timedelta
from config import lists
conn = sqlite3.connect('./database.db')
c = conn.cursor()

def getRandomTweet() -> Tweet:
    """Renvoie un tweet de la base de données aléatoirement.\n\n
    Si aucun résultat : renvoie un None."""
    c.execute("""SELECT tweets.*, auteurs.username as author_username FROM tweets JOIN auteurs ON auteurs.id = tweets.auteur ORDER BY RANDOM() LIMIT 1""")
    result = c.fetchone()
    if not(result):
        tweet = None
    else:
        if (result[6] == '1'):
            possibly_sensitive = True
        else:
            possibly_sensitive = False
        if (result[5] != ''):
            tagged_users = result[5].split(",")
        else:
            tagged_users = []
        tweet = Tweet(date=result[1],text=result[2],author_username=result[9],db_authorID=result[3],matching_rules=result[4].split(","),possibly_sensitive=possibly_sensitive,tagged_users=tagged_users,score=result[8],db_tweetID=result[0])
    return tweet

def getTweetById(tweetID:int) -> Tweet:
    """Renvoie le tweet correspondant à l'ID donné dans la base de données.\n\n
    Si aucun résultat : renvoie un None."""
    assert type(tweetID) == int, "tweetID doit être de type \"int\""
    c.execute("""SELECT tweets.*, auteurs.username as author_username FROM tweets JOIN auteurs ON auteurs.id = tweets.auteur WHERE tweets.id = ?""", (tweetID,))
    result = c.fetchone()
    if not(result):
        tweet = None
    else:
        tweet = Tweet()
        if (result[6] == '1'):
            possibly_sensitive = True
        else:
            possibly_sensitive = False
        if (result[5] != ''):
            tagged_users = result[5].split(",")
        else:
            tagged_users = []
        tweet = Tweet(date=result[1],text=result[2],author_username=result[9],db_authorID=result[3],matching_rules=result[4].split(","),possibly_sensitive=possibly_sensitive,tagged_users=tagged_users,score=result[8],db_tweetID=result[0])
    return tweet

def getTweetWithoutScore() -> Tweet:
    """Renvoie un tweet de la base de données qui n'a pas de score.\n\n
    Si aucun résultat : renvoie un None."""
    c.execute("""SELECT tweets.*, auteurs.username as author_username FROM tweets JOIN auteurs ON auteurs.id = tweets.auteur AND tweets.score IS NULL LIMIT 1""")
    result = c.fetchone()
    if not(result):
        tweet = None
    else:
        tweet = Tweet()
        if (result[6] == '1'):
            possibly_sensitive = True
        else:
            possibly_sensitive = False
        tagged_users = []
        if (result[5] != ''):
            tagged_users = result[5].split(",")
        else:
            tagged_users = []
        tweet = Tweet(date=result[1],text=result[2],author_username=result[9],db_authorID=result[3],matching_rules=result[4].split(","),possibly_sensitive=possibly_sensitive,tagged_users=tagged_users,db_tweetID=result[0])
    return tweet

def updateScore(tweetID:int, score:float = None) -> None:
    """Change le score du tweet ayant l'ID indiqué dans la base de données.\n\n
    Si aucun score est entré, change la valeur en \"NULL\""""
    assert type(tweetID) == int, "tweetID doit être de type \"int\""
    if score:
        c.execute("""UPDATE tweets SET score = ? WHERE id = ?""",(score,tweetID))
        conn.commit()
    else:
        c.execute("""UPDATE tweets SET score = ? WHERE id = ?""",(None,tweetID))
        conn.commit()
    return None

def getTopAuthors(results_number:int = 10) -> list:
    """Renvoie une liste des auteurs qui apparaissent le plus dans la base de données.\n\n
    Nombre d'auteurs par défaut : 10"""
    assert type(results_number) == int, "results_number doit être de type \"int\""
    lst = []
    c.execute("""SELECT auteurs.id, auteurs.username, auteurs.lien, COUNT(*) as nbTweets FROM auteurs,tweets WHERE auteur = auteurs.id GROUP BY auteurs.id ORDER BY nbTweets DESC LIMIT ?""",(results_number,))
    result = c.fetchall()
    for i in result:
        lst.append(User(None,None,i[1],i[0],i[3]))
    return lst

def insertNewTweet(tweet:Tweet) -> None:
    """Insère le tweet (et l'auteur si il n'existe pas) dans la base de données."""
    assert type(tweet) == Tweet, "tweet doit être de type \"tweet\""
    c.execute("""SELECT * FROM auteurs WHERE username = ?""",(tweet.author.username,))
    authorResult = c.fetchone()
    if not(authorResult): # L'auteur n'existe pas
        c.execute('''INSERT INTO auteurs(username, lien) VALUES (?,?)''',(tweet.author.username,'https://twitter.com/'+tweet.author.username))
        conn.commit()
        c.execute("""SELECT * FROM auteurs WHERE username = ?""",(tweet.author.username,))
        authorID = c.fetchone()[0]
    else:
        authorID = authorResult[0]
    date = str(datetime.strptime(tweet.date, '%Y-%m-%dT%H:%M:%S.000Z') + timedelta(hours=2))
    tweetLink = "https://twitter.com/"+tweet.author.username+'/status/'+tweet.id
    if (tweet.tagged_users):
        tagged_users = ','.join(tweet.tagged_users)
    else:
        tagged_users = ''
    c.execute('''INSERT INTO tweets(date, tweet, auteur, detecte, mentionne, sensible, lien) VALUES (?,?,?,?,?,?,?)''',(date,tweet.text,authorID,','.join(tweet.matching_rules),tagged_users,tweet.possibly_sensitive,tweetLink))
    conn.commit()
    return None

def deleteTweet(tweet:Tweet) -> None:
    """Supprime un tweet de la base de données."""
    assert type(tweet) == Tweet, "tweet doit être de type \"tweet\""
    if (tweet.db_ID):
        c.execute("""DELETE FROM tweets WHERE id = ?""",(tweet.db_ID,))
        conn.commit()
    return None

def deleteAuthors() -> int:
    """Supprime les auteurs n'ayant aucun tweet associé.\n
    Renvoie le nombre d'auteurs supprimés."""
    deletedAuthors = 0
    c.execute("""SELECT auteurs.*, COUNT(tweets.id) AS "nbTweets" FROM auteurs LEFT JOIN tweets ON auteurs.id = tweets.auteur GROUP BY auteurs.id HAVING nbTweets = 0""")
    authors = c.fetchall()
    for i in authors:
        c.execute("""DELETE FROM auteurs WHERE id = ?""",(i[0],))
        conn.commit()
        deletedAuthors += 1
    return deletedAuthors

def getTotalTweetsNumber() -> int:
    """Renvoie le nombre total de tweets dans la base de données"""
    c.execute("""SELECT COUNT(*) FROM tweets""")
    result = c.fetchone()
    return result[0]

def getTotalAuthorsNumber() -> int:
    """Renvoie le nombre total d'auteurs dans la base de données"""
    c.execute("""SELECT COUNT(*) FROM auteurs""")
    result = c.fetchone()
    return result[0]

def getAuthorCountWithMoreThanXTweets(tweetNumber:int = 0):
    c.execute("""SELECT COUNT(*) FROM (SELECT auteurs.id, COUNT(tweets.id) as nbTweets FROM auteurs, tweets WHERE tweets.auteur = auteurs.id GROUP BY auteurs.id HAVING nbTweets >= ?);""",(tweetNumber,))
    result = c.fetchone()
    return result[0]

def getTweetsNumberByList(list:str):
    """Renvoie le nombre de tweets correspondant à une liste particulière.\n
    \"list\" doit être une des listes du fichier \"lists.py\""""
    c.execute("""SELECT COUNT(*) FROM tweets WHERE detecte LIKE ?""",("%"+str(list)+"%",))
    result = c.fetchone()
    return result[0]

def getTweetsNumberByWord(word:str):
    """Renvoie le nombre de tweets contenant un mot ou une expression.\n
    \"word\" : mot ou expression à chercher."""
    c.execute("""SELECT COUNT(*) FROM tweets WHERE tweet LIKE ?""",("%"+str(word)+"%",))
    result = c.fetchone()
    return result[0]

def getTweetsbyList(list:str, limit:int=5):
    """Renvoie une liste des tweets correspondant à la liste choisie."""
    lists_names = [i for i in dir(lists) if not i.startswith("__")]
    assert list in lists_names, f"list doit être parmi les choix suivants : {', '.join(lists_names)}"
    c.execute("""SELECT tweets.*, auteurs.username as author_username FROM tweets JOIN auteurs ON auteurs.id = tweets.auteur AND detecte LIKE ? ORDER BY RANDOM() LIMIT ?""",("%"+str(list)+"%",limit))
    results = c.fetchall()
    tweets = []
    for result in results:
        tweet = Tweet()
        if (result[6] == '1'):
            possibly_sensitive = True
        else:
            possibly_sensitive = False
        tagged_users = []
        if (result[5] != ''):
            tagged_users = result[5].split(",")
        else:
            tagged_users = []
        tweet = Tweet(date=result[1],text=result[2],author_username=result[9],db_authorID=result[3],matching_rules=result[4].split(","),possibly_sensitive=possibly_sensitive,tagged_users=tagged_users,score=result[8],db_tweetID=result[0])
        tweets.append(tweet)
    return tweets

def getTweetsByText(text:str, limit:int=1):
    """Renvoie une liste des tweets contenant le texte."""
    c.execute("""SELECT tweets.*, auteurs.username as author_username FROM tweets JOIN auteurs ON auteurs.id = tweets.auteur AND tweet LIKE ? ORDER BY RANDOM() LIMIT ?""",("%"+str(text)+"%",limit))
    results = c.fetchall()
    tweets = []
    for result in results:
        tweet = Tweet()
        if (result[6] == '1'):
            possibly_sensitive = True
        else:
            possibly_sensitive = False
        tagged_users = []
        if (result[5] != ''):
            tagged_users = result[5].split(",")
        else:
            tagged_users = []
        tweet = Tweet(date=result[1],text=result[2],author_username=result[9],db_authorID=result[3],matching_rules=result[4].split(","),possibly_sensitive=possibly_sensitive,tagged_users=tagged_users,score=result[8],db_tweetID=result[0])
        tweets.append(tweet)
    return tweets

def getTweetsByScore(score:float, limit:int=1):
    """Renvoie une liste des tweets ayant un score précis."""
    c.execute("""SELECT tweets.*, auteurs.username as author_username FROM tweets JOIN auteurs ON auteurs.id = tweets.auteur AND score = ? ORDER BY RANDOM() LIMIT ?""",(score,limit))
    results = c.fetchall()
    tweets = []
    for result in results:
        tweet = Tweet()
        if (result[6] == '1'):
            possibly_sensitive = True
        else:
            possibly_sensitive = False
        tagged_users = []
        if (result[5] != ''):
            tagged_users = result[5].split(",")
        else:
            tagged_users = []
        tweet = Tweet(date=result[1],text=result[2],author_username=result[9],db_authorID=result[3],matching_rules=result[4].split(","),possibly_sensitive=possibly_sensitive,tagged_users=tagged_users,score=result[8],db_tweetID=result[0])
        tweets.append(tweet)
    return tweets

def getTweetsByAuthorUsername(username:float, limit:int=1):
    """Renvoie une liste des tweets d'un auteur précis."""
    c.execute("""SELECT tweets.*, auteurs.username as author_username FROM tweets JOIN auteurs ON auteurs.id = tweets.auteur AND author_username = ? ORDER BY RANDOM() LIMIT ?""",(username,limit))
    results = c.fetchall()
    tweets = []
    for result in results:
        tweet = Tweet()
        if (result[6] == '1'):
            possibly_sensitive = True
        else:
            possibly_sensitive = False
        tagged_users = []
        if (result[5] != ''):
            tagged_users = result[5].split(",")
        else:
            tagged_users = []
        tweet = Tweet(date=result[1],text=result[2],author_username=result[9],db_authorID=result[3],matching_rules=result[4].split(","),possibly_sensitive=possibly_sensitive,tagged_users=tagged_users,score=result[8],db_tweetID=result[0])
        tweets.append(tweet)
    return tweets

def getTweetsNumberWithoutScore():
    """Renvoie le nombre de tweets qui n'a pas de score."""
    c.execute("""SELECT COUNT(*) FROM tweets WHERE score IS NULL""")
    results = c.fetchone()
    return results[0]