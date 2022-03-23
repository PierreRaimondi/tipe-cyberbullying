import src.Database as db, src.Filtering as Filtering, src.Stream as Stream, src.UserLookup as UserLookup, src.Stats as Stats, src.Search as Search
from src.Tweet import Tweet
from src.User import User
from config import api, lists

# Une documentation plus précise est disponible dans le fichier "README.md"

#       Lancer le premier filtrage :
# Stream.start()

#       Lancer le second filtrage :
# Filtering.start()

#       Statistiques :
# Stats.general()
# Stats.tweetsNumberInAList()
# Stats.authorsWithMoreThanXTweets()
# Stats.topAuthorsUsernames()
# Stats.topAuthorsSensitiveTweetsPercentage()

#       Affichage des tweets
# Search.random()
# Search.byID()
# Search.byListName()
# Search.byText()
# Search.byScore()
# Search.byAuthor()