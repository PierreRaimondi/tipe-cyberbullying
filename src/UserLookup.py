import requests
import json
from config import api
from src.User import User
from src.Tweet import Tweet
import src.Filtering as Filtering

# Limite de tweets a récupérer (min : 5)
tweetLimit = 500

# Score minimum pour conserver le tweet
minScore = 30


tweetNumber = 0
canContinue = True
tweetsList = []

def apiRequest(userID:int, pagination_token=None):
    """Recherche les tweets de l'utilisateur (dans une limite de 100 tweets), et les ajoute dans la variable "tweetsList".\n
    "pagination_token" permet d'afficher les 100 tweets d'après.\n
    Renvoie le next_token, s'il existe, None sinon.\n\n
    Limite API : 1500 requêtes/15 mins | 2M tweets/mois"""
    url = "https://api.twitter.com/2/users/{}/tweets".format(userID)
    params = {"max_results": 100, "tweet.fields": "lang,created_at,possibly_sensitive", "expansions": "author_id,entities.mentions.username"}
    if (pagination_token):
        params["pagination_token"] = pagination_token
    headers = {"Authorization": "Bearer {}".format(api.bearer_token)}
    response = requests.request("GET", url, headers=headers, params=params)
    if response.status_code != 200:
        print((" ERREUR LORS DE LA CONNEXION (code {}) ".format(response.status_code)).center(70,('=')))
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    json_response = json.loads(json.dumps(response.json()))
    # print(json.dumps(json_response, indent=4, ensure_ascii=False, sort_keys=True))
    if 'data' in json_response:
        for i in json_response['data']:
            tweet = Tweet()
            tweet.initializeFromUserResponse(json.dumps(i).encode('utf-8'))
            global tweetNumber
            global tweetLimit
            if tweetNumber < tweetLimit:
                tweetsList.append(tweet)
                tweetNumber += 1
            else:
                break
        if not('next_token' in json_response['meta']):
            global canContinue
            canContinue = False
            return None
        else:
            return json_response['meta']['next_token']
    else:
        canContinue = False
        return None


def getTweets(user:User, showOutput:bool = False) -> None:
    """Démarre l"analyse de l'utilisateur.\n
    Récupère tous ses tweets (dans la limite définie), et les stocke dans la liste \"tweetsList\""""
    global tweetsList, tweetNumber, canContinue
    tweetsList = []
    tweetNumber = 0
    canContinue = True
    if showOutput:
        print((f" ANALYSE DE \"{user.username}\" ").center(70,('=')))
        print("\n")
        print("Récupération de l'ID...")
    twitterID = user.getTwitterID()
    if showOutput:
        print(f"\rRécupération des tweets ({tweetNumber})...", end='')
    while tweetNumber < tweetLimit and canContinue:
        next_token = apiRequest(twitterID)
        if showOutput:
            print(f"\rRécupération des tweets ({tweetNumber})...", end='')
        if next_token != None:
            apiRequest(twitterID, next_token)
            if showOutput:
                print(f"\rRécupération des tweets ({tweetNumber})...", end='')
    if showOutput:
        print("\nRécupération des tweets terminée !")
    return tweetsList
    

def getSensitiveTweetPercentage(user:User) -> float:
    """Renvoie le pourcentage de tweets haineux de l'utilisateur"""
    getTweets(user)
    scoreList = [Filtering.createTweetScore(e) for e in tweetsList]
    list_ = [e for e in scoreList if e >= minScore]
    if len(scoreList) != 0:
        tweetRatio = round((len(list_)/len(scoreList))*100,2)
    else:
        tweetRatio = 0
    return tweetRatio