import sqlite3
from typing import List
from src.User import User
from src.Tweet import Tweet
from datetime import datetime, timedelta
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
    if score:
        c.execute("""UPDATE tweets SET score = ? WHERE id = ?""",(score,tweetID))
        conn.commit()
    else:
        c.execute("""UPDATE tweets SET score = ? WHERE id = ?""",(None,tweetID))
        conn.commit()
    return None

def getTopAuthors(results_number:int = 10) -> List[User]:
    """Renvoie une liste des auteurs qui apparaissent le plus dans la base de données.\n\n
    Nombre d'auteurs par défaut : 10"""
    lst = []
    c.execute("""SELECT auteurs.id, auteurs.username, auteurs.lien, COUNT(*) as nbTweets FROM auteurs,tweets WHERE auteur = auteurs.id GROUP BY auteurs.id ORDER BY nbTweets DESC LIMIT ?""",(results_number,))
    result = c.fetchall()
    for i in result:
        lst.append(User(None,None,i[1],i[0],i[3]))
    return lst

def insertNewTweet(tweet:Tweet) -> None:
    """Insère le tweet (et l'auteur si il n'existe pas) dans la base de données."""
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