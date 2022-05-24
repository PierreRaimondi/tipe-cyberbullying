import json
from classes.User import User

class Tweet:
    """Défini un Tweet"""
    def __init__(self,id:str = None,date:str = None,text:str = None,author_id:str = None,author_name:str = None,author_username:str = None,db_authorID:int = None,matching_rules:list = None,possibly_sensitive: bool = None,tagged_users:list = None,score:float = None,db_tweetID:int = None):
        """Initialise un nouveau tweet.\n\n
        Possibilité de ne mettre aucun argument (pour une initialisation avec la réponse de l'API par exemple."""
        self.id = id
        self.date = date
        self.text = text
        self.author = User(author_id, author_name, author_username, db_authorID)
        self.matching_rules = matching_rules
        self.possibly_sensitive = possibly_sensitive
        self.tagged_users = tagged_users
        self.score = score
        self.db_ID = db_tweetID

    def initializeFromStreamResponse(self, response:bytes):
        """Initialise le tweet en passant par la réponse de l'API de Twitter (Stream).\n
        La réponse doit être en format JSON."""
        json_response = json.loads(response)
        self.id = json_response['data']['id']
        self.date = json_response['data']['created_at']
        self.text = json_response['data']['text']
        author_id = json_response['includes']['users'][0]['id']
        author_name = json_response['includes']['users'][0]['name']
        author_username = json_response['includes']['users'][0]['username']
        self.author = User(author_id, author_name, author_username)
        self.matching_rules = [element['tag'] for element in json_response['matching_rules']]
        self.possibly_sensitive = json_response['data']['possibly_sensitive']
        if 'mentions' in json_response['data']['entities']:
            self.tagged_users = [element['username'] for element in json_response['data']['entities']['mentions']]

    def initializeFromUserResponse(self, response:bytes):
        """Initialise le tweet en passant par la réponse de l'API de Twitter (UserLookup).\n
        La réponse doit être en format JSON."""
        json_response = json.loads(response)
        self.id = json_response['id']
        self.date = json_response['created_at']
        self.text = json_response['text']
        self.possibly_sensitive = json_response['possibly_sensitive']
        if 'entities' in json_response:
            if 'mentions' in json_response['entities']:
                self.tagged_users = [element['username'] for element in json_response['entities']['mentions']]