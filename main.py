import src.Database as db, src.Filtering as Filtering, src.Stream as Stream, src.UserLookup as UserLookup, src.Stats as Stats
from src.Tweet import Tweet
from src.User import User
from config import api, lists

# Pour démarrer le premier filtrage
# (Pour l'arrêter, il faut interrompre le programme)

# Stream.start()

# Pour démarrer le second filtrage

# Filtering.start()

# Pour récupérer les 10 personnes qui apparaissent le plus de fois dans notre base

# top = db.getTopAuthors()
# print([e.username for e in top])


# TESTS

# test = User(username="tony84fils2pute")
# UserLookup.getSensitiveTweetPercentage(test)
# [(e.username,UserLookup.getSensitiveTweetPercentage(e)) if not(e.isBanned()) else (e.username, 'BANNI') for e in db.getTopAuthors(10)]