import src.Database as db
from src.Tweet import Tweet

def afficher(tweet:Tweet):
    """Affiche le tweet"""
    print(f" Tweet #{tweet.db_ID} ({tweet.date}) ".center(80,('=')))
    print(f"{tweet.author.username} : {tweet.text}")
    print(f" Détecté : {', '.join(tweet.matching_rules)} | Score : {tweet.score} ".center(80,('=')))
    return None    

def random():
    """Affiche un tweet aléatoire"""
    afficher(db.getRandomTweet())
    return None

def byID(id:int):
    """Affiche le tweet ayant l'ID demandé.
    \"id\" : ID du tweet a afficher."""
    tweet = db.getTweetById(id)
    if tweet:
        afficher(tweet)
    else:
        print("Aucun tweet trouvé")
    return None

def byListName(list:str, limit:int=1):
    """Affiche des tweets détectés dans une liste particulière.\n
    \"list\" : liste à chercher.\n
    \"limit\" : nombre de tweets à afficher."""
    tweets = db.getTweetsbyList(list,limit)
    if not(tweets):
        print("Aucun tweet trouvé")
    else:
        for i in tweets:
            afficher(i)
            print("\n")
    return None

def byText(text:str, limit:int=1):
    """Affiche des tweets contenant un mot ou une expression particulière.\n
    \"text\" : texte à chercher.\n
    \"limit\" : nombre de tweets à afficher."""
    tweets = db.getTweetsByText(text,limit)
    if not(tweets):
        print("Aucun tweet trouvé")
    else:
        for i in tweets:
            afficher(i)
            print("\n")
    return None

def byScore(score:float, limit:int=1):
    """Affiche des tweets ayant un score précis.\n
    \"score\" : score à chercher.\n
    \"limit\" : nombre de tweets à afficher."""
    tweets = db.getTweetsByScore(score,limit)
    if not(tweets):
        print("Aucun tweet trouvé")
    else:
        for i in tweets:
            afficher(i)
            print("\n")
    return None

def byAuthor(username:float, limit:int=1):
    """Affiche les tweets d'un auteur précis.\n
    \"username\" : nom d'utilisateur de l'auteur à chercher.\n
    \"limit\" : nombre de tweets à afficher."""
    tweets = db.getTweetsByAuthorUsername(username,limit)
    if not(tweets):
        print("Aucun tweet trouvé")
    else:
        for i in tweets:
            afficher(i)
            print("\n")
    return None