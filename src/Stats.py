import src.Database as db
import src.UserLookup as UserLookup

def general():
    """Renvoie le nombre total de tweets et d'auteurs dans la base de données"""
    return (db.getTotalTweetsNumber(), db.getTotalAuthorsNumber())

def authorsWithMoreThanXTweets(tweetsNumber:int = 1):
    """Renvoie le nombre d'auteurs apparaissant au moins "tweetsNumber" fois dans la base de données."""
    return db.getAuthorCountWithMoreThanXTweets(tweetsNumber)

def tweetsNumberInAList(list:str):
    """Renvoie le nombre de tweets correspondant à une liste particulière.\n
    Choix possibles :\n
    lgbtq, racisme, sexuel_misogyne, con, pejoratif, banal, devalorisant, suicide, emojis"""
    return db.getTweetsNumberByList(list)

def topAuthorsUsernames(authorsNumber:int = 10,showTweetsNumber:bool = False):
    """Renvoie la liste des noms d'utilisateurs des auteurs qui apparaissent le plus de fois dans notre base de données.\n
    authorsNumber : le nombre d'auteurs à afficher.\n
    showTweetsNumber : affiche également le nombre de tweets dans la base de données de cet auteur."""
    top = db.getTopAuthors(authorsNumber)
    if showTweetsNumber:
        return [(e.username, e.db_tweetNumber) for e in top]
    else:
        return [e.username for e in top]

def topAuthorsSensitiveTweetsPercentage(authorsNumber:int = 10):
    """Renvoie le pourcentage des tweets haineux des auteurs qui apparaissent le plus de fois dans notre base de données.\n
    authorsNumber : le nombre d'auteurs à afficher"""
    return [(e.username,UserLookup.getSensitiveTweetPercentage(e)) if not(e.isBanned()) else (e.username, 'BANNI') for e in db.getTopAuthors(authorsNumber)]