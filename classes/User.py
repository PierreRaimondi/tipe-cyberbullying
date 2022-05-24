import requests, json
from config import api

class User:
    """Défini l'auteur d'un tweet"""
    def __init__(self,id:str = None,name:str = None,username:str = None,db_authorID:int = None,db_tweetNumber:int = None):
        self.id = id
        self.name = name
        self.username = username
        self.db_ID = db_authorID
        self.db_tweetNumber = db_tweetNumber

    def getTwitterID(self) -> int:
        """Renvoie l'ID Twitter de l'utilisateur.\n\n
        Limite API : 300 requêtes/15min"""
        if not(self.username):
            raise Exception("Pas de nom d'utilisateur défini")
        usernames = "usernames="+str(self.username)
        user_fields = "user.fields=description,created_at"
        url = f"https://api.twitter.com/2/users/by?{usernames}&{user_fields}"
        headers = {"Authorization": f"Bearer {api.bearer_token}"}
        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            print((f" ERREUR LORS DE LA CONNEXION (code {response.status_code}) ").center(70,('=')))
            raise Exception(
                f"Request returned an error: {response.status_code} {response.text}"
            )
        jsonResponse = json.loads(json.dumps(response.json()))
        if ('errors' in jsonResponse):
            print((" ERREUR API ").center(70,('=')))
            raise Exception(jsonResponse['errors'][0]['detail'])
        return int(jsonResponse['data'][0]["id"])

    def isBanned(self) -> bool:
        """Renvoie le status du bannissement de l'utilisateur.\n
        True : l'utilisateur est banni.\n
        False : l'utilisateur n'est pas banni.\n\n
        Limite API : 300 requêtes/15min"""
        if not(self.username):
            raise Exception("Pas de nom d'utilisateur défini")
        usernames = "usernames="+str(self.username)
        user_fields = "user.fields=description"
        url = f"https://api.twitter.com/2/users/by?{usernames}&{user_fields}"
        headers = {"Authorization": f"Bearer {api.bearer_token}"}
        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            print((f" ERREUR LORS DE LA CONNEXION (code {response.status_code}) ").center(70,('=')))
            raise Exception(
                f"Request returned an error: {response.status_code} {response.text}"
            )
        jsonResponse = json.loads(json.dumps(response.json()))
        if ('errors' in jsonResponse):
                return True
        return False