import requests, json, time as t, src.Database as db
from config import api, lists
from src.User import User
from src.Tweet import Tweet

def get_rules(headers):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    rulesNumber = json.loads(json.dumps(response.json()))['meta']['result_count']
    print((" RÈGLES RÉCUPÉRÉES ({}) ".format(rulesNumber)).center(70,('=')))
    # print(json.dumps(response.json()))
    return response.json()

def delete_all_rules(headers, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    deletedRulesNumber = json.loads(json.dumps(response.json()))['meta']['summary']['deleted']
    print((" RÈGLES SUPPRIMÉES ({}) ".format(deletedRulesNumber)).center(70,('=')))
    # print(json.dumps(response.json()))

def createRulesFromLists():
    """Crée les règles pour l'API de Twitter en fonction des listes du fichier \"lists.py\""""
    lists_names = [i for i in dir(lists) if not i.startswith("__")]
    global_rules = []
    for i in lists_names:
        lst = getattr(lists, i)
        rule_words = []
        char_count = 0
        word_count = 0
        for j in lst:
            if char_count + len(j) + 4 >= 512 or word_count + len(str(j).split()) >= 30:
                str_lst = ""
                for k in rule_words:
                    str_lst += k + " OR "
                str_lst = str_lst[:-4]
                global_rules.append({"value": "({}) lang:fr -is:retweet -is:quote".format(str_lst),"tag": "{}".format(i)})
                char_count = 0
                word_count = 0
                rule_words = []
            rule_words.append(j)
            char_count += len(j) + 4
            word_count += len(str(j).split())
        if len(rule_words) != 0:
            str_lst = ""
            for k in rule_words:
                str_lst += k + " OR "
            str_lst = str_lst[:-4]
            global_rules.append({"value": "({}) lang:fr -is:retweet -is:quote".format(str_lst),"tag": "{}".format(i)})
    return global_rules

def set_rules(headers):
    # sample_rules = [
    #     # Les règles sont de la forme suivante :
    #     # {"value": "(mot1 OR mot2 OR mot3 OR ...) lang:fr -is:retweet -is:quote","tag": "nomDeLaRègle"},
    #     # La valeur "OR" permet de chercher le mot1 OU le mot2 OU le mot3...
    #     # "lang:fr" permet de récupérer seulement les tweets en français
    #     # -is:retweet permet de retirer les retweets
    #     # -is:quote permet de retirer les citations
    #     # "tag": "nomDeLaRègle" permet de donner un nom à notre règle (utilisé pour le 2e filtrage)
    #     {"value": "(gouine OR tarlouze OR tantouze OR sodomite OR pédé OR pd OR pédale OR tafiole OR tapette OR travelo OR lopette OR encule OR chbeb) lang:fr -is:retweet -is:quote","tag": "lgbtq"},
    #     {"value": "(nègre OR bougnoul OR chintoque OR melon OR bamboula OR youpin OR niakoué OR sale noir OR sale juif OR beurette OR beur OR babtou OR blédard OR métèque OR feuj OR boukak OR muzz) lang:fr -is:retweet -is:quote","tag": "racisme"},
    #     {"value": "(garage à bite OR pute OR sac à foutre OR pétasse OR pouffiasse OR pouffe OR cul OR nique OR salope OR petite bite OR chienne OR mal baisée OR chaudasse OR gaupe OR gueniche) lang:fr -is:retweet -is:quote","tag": "sexuel_misogyne"},
    #     {"value": "(conne OR connasse OR connard OR con OR counifle) lang:fr -is:retweet -is:quote","tag": "con"},
    #     {"value": "(ivrogne OR pochtronne OR clochard OR clodo OR plouc OR bouffon) lang:fr -is:retweet -is:quote","tag": "pejoratif"},
    #     {"value": "(grognasse OR trou du cul OR fdp OR fils de pute OR couille molle OR batard OR ta gueule OR abruti OR idiot OR imbécile OR enfoiré OR putain OR merde OR moins que rien OR ordure OR vas te faire OR casser la gueule) lang:fr -is:retweet -is:quote","tag": "banal"},
    #     {"value": "(brise couilles OR casse couille OR mange merde OR ntm OR orchidoclaste) lang:fr -is:retweet -is:quote","tag": "banal"},
    #     {"value": "(cotorep OR triso OR attardé OR mongol OR espèce d'handicapé OR autiste OR débile OR gogol) lang:fr -is:retweet -is:quote","tag": "devalorisant"},
    #     {"value": "(suicide toi) lang:fr -is:retweet -is:quote","tag": "suicide"},
    #     {"value": "(🖕 OR 🖕🏻 OR 🖕🏼 OR 🖕🏽 OR 🖕🏾 OR 🖕🏿) lang:fr -is:retweet -is:quote","tag": "emojis"},
    # ]
    sample_rules = createRulesFromLists()
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    createdRules = json.loads(json.dumps(response.json()))['meta']['summary']['created']
    validRules = json.loads(json.dumps(response.json()))['meta']['summary']['valid']
    print((" RÈGLES CRÉES ({} dont {} valides) ".format(createdRules,validRules)).center(70,('=')))
    # print(json.dumps(response.json()))

def get_stream(headers, showTweets, insertInDatabase):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?expansions=author_id,entities.mentions.username&tweet.fields=lang,created_at,possibly_sensitive", headers=headers, stream=True,
    )
    if response.status_code == 200:
        print((" CONNECTÉ AU STREAM ").center(70,('=')))
    else:
        print((" ERREUR LORS DE LA CONNEXION (code {}) ".format(response.status_code)).center(70,('=')))
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    tweetNumber = 0
    startTime = t.time()
    for response_line in response.iter_lines():
        if response_line:
            tweetNumber += 1
            tweet = Tweet()
            tweet.initializeFromStreamResponse(response_line)
            if showTweets:
                json_response = json.loads(response_line)
                print(json.dumps(json_response, indent=4, sort_keys=True, ensure_ascii=False))
            else:
                elapsedTime = round(t.time() - startTime,2)
                print("\rTweets récupérés : {} | Rythme : {} tweets/sec".format(tweetNumber, round(tweetNumber/elapsedTime,3)), end='')
            if insertInDatabase:
                db.insertNewTweet(tweet)


def start(showTweets:bool=False,insertInDatabase:bool=True,resetRules:bool=False):
    """Démarre le premier filtrage.\n
    showTweets : si True, affiche les tweets récupérés dans la console\n
    insertInDatabase : si True, insère les tweets dans la base de données\n
    resetRules : Si True, réinitialise les règles du filtrage.\n\n
    Limite API (stream) : 50 requêtes/15 mins | 2M tweets/mois"""
    headers = {"Authorization": "Bearer {}".format(api.bearer_token)}
    rules = get_rules(headers)
    if resetRules:
        delete_all_rules(headers, rules)
        set_rules(headers)
    get_stream(headers, showTweets, insertInDatabase)