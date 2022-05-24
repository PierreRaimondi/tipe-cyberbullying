import classes.Database as db, classes.UserLookup as UserLookup
from config import lists

def general(readable:bool = True):
    """Renvoie le nombre total de tweets et d'auteurs dans la base de données"""
    if readable:
        print(f"La base de données contient {db.getTotalTweetsNumber()} tweets et {db.getTotalAuthorsNumber()} auteurs.")
        return None
    else:
        return (db.getTotalTweetsNumber(), db.getTotalAuthorsNumber())

def authorsWithMoreThanXTweets(tweetsNumber:int = 1, readable:bool = True):
    """Renvoie le nombre d'auteurs apparaissant au moins "tweetsNumber" fois dans la base de données."""
    assert type(tweetsNumber) == int, "tweetsNumber doit être de type \"int\""
    if readable:
        print(f"{db.getAuthorCountWithMoreThanXTweets(tweetsNumber)} auteurs apparaissent au moins {tweetsNumber} fois dans la base de données.")
        return None
    else:
        return db.getAuthorCountWithMoreThanXTweets(tweetsNumber)

def tweetsNumberInAList(list:str, readable:bool = True):
    """Renvoie le nombre de tweets correspondant à une liste particulière.\n
    \"list\" doit être une des listes du fichier \"lists.py\""""
    lists_names = [i for i in dir(lists) if not i.startswith("__")]
    assert list in lists_names, f"list doit être parmi les choix suivants : {', '.join(lists_names)}"
    if readable:
        print(f"{db.getTweetsNumberByList(list)} tweets correspondent à la liste \"{list}\".")
        return None
    else:
        return db.getTweetsNumberByList(list)

def topAuthorsUsernames(authorsNumber:int = 10,showTweetsNumber:bool = False, readable:bool = True):
    """Renvoie la liste des noms d'utilisateurs des auteurs qui apparaissent le plus de fois dans notre base de données.\n
    authorsNumber : le nombre d'auteurs à afficher.\n
    showTweetsNumber : affiche également le nombre de tweets dans la base de données de cet auteur."""
    assert type(authorsNumber) == int, "authorsNumber doit être de type \"int\""
    top = db.getTopAuthors(authorsNumber)
    if readable:
        nb = 0
        if showTweetsNumber:
            for i in [(e.username, e.db_tweetNumber) for e in top]:
                nb += 1
                print(f"{nb} - {i[0]} apparaît {i[1]} fois.")
            return None
        else:
            for i in [e.username for e in top]:
                nb += 1
                print(f"{nb} - {i}")
            return None
    else:
        if showTweetsNumber:
            return [(e.username, e.db_tweetNumber) for e in top]
        else:
            return [e.username for e in top]

def topAuthorsSensitiveTweetsPercentage(authorsNumber:int = 10, readable:bool = True):
    """Renvoie le pourcentage des tweets haineux des auteurs qui apparaissent le plus de fois dans notre base de données.\n
    authorsNumber : le nombre d'auteurs à afficher"""
    assert type(authorsNumber) == int, "authorsNumber doit être de type \"int\""
    if readable:
        nb = 0
        for i in [(e.username,UserLookup.getSensitiveTweetPercentage(e)) if not(e.isBanned()) else (e.username, 'BANNI') for e in db.getTopAuthors(authorsNumber)]:
            nb += 1
            if (i[1]) == "BANNI":
                print(f"{nb} - {i[0]} est banni.")
            else:
                print(f"{nb} - {i[1]}% des derniers tweets de {i[0]} sont potentiellement haineux.")
        return None
    else:
        return [(e.username,UserLookup.getSensitiveTweetPercentage(e)) if not(e.isBanned()) else (e.username, 'BANNI') for e in db.getTopAuthors(authorsNumber)]

def tweetsWithWord(word:str, readable:bool = True):
    """Renvoie le nombre de tweets contenant un mot ou une expression.\n
    \"word\" : mot ou expression à chercher"""
    if readable:
        print(f"La base de données contient {db.getTweetsNumberByWord(word)} tweets contenant \"{str(word)}\".")
        return None
    else:
        return db.getTweetsNumberByWord(word)