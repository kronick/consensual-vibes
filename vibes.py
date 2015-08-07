#coding=utf-8
from flask import Flask, request, url_for, redirect, render_template, jsonify, json, session
import os, subprocess, random
import sqlite3
import printer
import time

app = Flask(__name__)


@app.route("/info")
def info():
    return request.headers["host"]

@app.route("/")
def index():
    if isCaptivePortal(request):
        print "CAPTIVE PORTAL DETECTED"
        return "<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>"
    #elif u"vib.es" not in request.headers["Host"]:
        #return redirect("http://xn--yh8hry.vib.es/")
    elif u"vibes.local" not in request.headers["Host"]:
        return redirect("http://vibes.local/")


    games = [game[:-3] for game in os.listdir("games") if game.endswith(".db")]

    return render_template("choose_game.html", games=games)

@app.route("/<game>", methods=["GET"])
def load_game(game):
    return render_template("login.html", game=game)

    #return redirect("http://disk.cactus:2000/swipe")

    # if request.headers["host"] != u"disk.cactus":
    #     return render_template("redirect.html", url="http://disk.cactus/")


@app.route("/<game>/swipe")
def swipe(game):
    return render_template("swipe.html", game=game)


@app.route("/<game>/words/things", methods=["POST"])
def addthing(game):
    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("INSERT INTO words(word, type) VALUES(?, ?)", (request.form["word"], "thing"))
        db.commit()
    return "OK"    

@app.route("/<game>/words/modifiers", methods=["POST"])
def addmodifier(game):
    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute("INSERT INTO words(word, type) VALUES(?, ?)", (request.form["word"], "modifier"))
        db.commit()
    return "OK"    

@app.route("/newgame", methods=["GET"])
def show_create_game_form():
    return render_template("create_game.html")

@app.route("/massgame", methods=["GET"])
def show_create_masss_game_form():
    return render_template("create_mass_game.html")

@app.route("/massgame", methods=["POST"])
def create_mass_game():

    players = request.form["players"]
    groups = [[l.strip() for l in g.split("\n") if l.strip() is not u""] for g in players.split("---") if g.strip() is not u""]

    things = [l.strip() for l in request.form["things"].split("\n") if l is not ""]
    modifiers = [l.strip() for l in request.form["modifiers"].split("\n") if l is not ""]

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    i = 0
    print groups
    for users in groups:
        game = u"{} {}".format(request.form["name"], letters[i])
        i+=1


        with sqlite3.connect("games/{}.db".format(game)) as db:
            cursor = db.cursor()

            cursor.execute("DROP TABLE IF EXISTS words")
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS phrases")
            cursor.execute("DROP TABLE IF EXISTS ratings")
            cursor.execute("DROP TABLE IF EXISTS notifications")
                    
            cursor.execute("pragma foreign_keys = on")

            cursor.execute("CREATE TABLE words(word, type)")

            cursor.execute("CREATE TABLE users(name PRIMARY KEY UNIQUE)")
            cursor.execute("CREATE TABLE phrases(id INTEGER PRIMARY KEY AUTOINCREMENT, a,b)")
            cursor.execute('''
                CREATE TABLE ratings(phrase_id INTEGER KEY, user_name, rating INTEGER,
                                    FOREIGN KEY(phrase_id) REFERENCES phrases(id),
                                    FOREIGN KEY(user_name) REFERENCES users(name), CONSTRAINT unq UNIQUE(phrase_id, user_name))
            ''')
            for u in users:
                cursor.execute("INSERT INTO users (name) VALUES(?)", (u,))

            cursor.execute('''
                CREATE TABLE notifications(id INTEGER PRIMARY KEY AUTOINCREMENT, user_name,
                                           read INTEGER DEFAULT 0, text,
                                           FOREIGN KEY(user_name) REFERENCES users(name))
            ''')

            print u"Inserting {} things and {} modifiers into the database.".format(len(things), len(modifiers))
            for t in things:
                cursor.execute("INSERT INTO words (word, type) VALUES(?,?)", (t, "thing"))
            for a in modifiers:
                cursor.execute("INSERT INTO words (word, type) VALUES(?,?)", (a, "modifier"))
            
            db.commit()    

    return redirect(url_for("index"))

@app.route("/newgame", methods=["POST"])
def create_game():
    game = request.form["name"]
    users = [l.strip() for l in request.form["players"].split("\n") if l is not ""]
    things = [l.strip() for l in request.form["things"].split("\n") if l is not ""]
    modifiers = [l.strip() for l in request.form["modifiers"].split("\n") if l is not ""]

    with sqlite3.connect("games/{}.db".format(game)) as db:
        cursor = db.cursor()

        cursor.execute("DROP TABLE IF EXISTS words")
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS phrases")
        cursor.execute("DROP TABLE IF EXISTS ratings")
        cursor.execute("DROP TABLE IF EXISTS notifications")
                
        cursor.execute("pragma foreign_keys = on")

        cursor.execute("CREATE TABLE words(word, type)")

        cursor.execute("CREATE TABLE users(name PRIMARY KEY UNIQUE)")
        cursor.execute("CREATE TABLE phrases(id INTEGER PRIMARY KEY AUTOINCREMENT, a,b)")
        cursor.execute('''
            CREATE TABLE ratings(phrase_id INTEGER KEY, user_name, rating INTEGER,
                                FOREIGN KEY(phrase_id) REFERENCES phrases(id),
                                FOREIGN KEY(user_name) REFERENCES users(name), CONSTRAINT unq UNIQUE(phrase_id, user_name))
        ''')
        for u in users:
            cursor.execute("INSERT INTO users (name) VALUES(?)", (u,))

        cursor.execute('''
            CREATE TABLE notifications(id INTEGER PRIMARY KEY AUTOINCREMENT, user_name,
                                       read INTEGER DEFAULT 0, text,
                                       FOREIGN KEY(user_name) REFERENCES users(name))
        ''')

        print u"Inserting {} things and {} modifiers into the database.".format(len(things), len(modifiers))
        for t in things:
            cursor.execute("INSERT INTO words (word, type) VALUES(?,?)", (t, "thing"))
        for a in modifiers:
            cursor.execute("INSERT INTO words (word, type) VALUES(?,?)", (a, "modifier"))
        
        db.commit()

    return redirect(url_for("load_game", game=game))


@app.route("/<game>/words/rebuild", defaults={"rebuild_all": False})
@app.route("/<game>/rebuild", defaults={"rebuild_all": True})
def rebuild(game, rebuild_all):
    # Load words from JSON config files
    with open("games/{}_words.json".format(game)) as words_file:
        words_json = json.load(words_file)
        things     = words_json["things"]
        modifiers  = words_json["modifiers"]

    with open("games/{}_users.json".format(game)) as users_file:
        users_json = json.load(users_file)
        users = users_json["users"]


    with sqlite3.connect("games/{}.db".format(game)) as db:
        cursor = db.cursor()

        cursor.execute("DROP TABLE IF EXISTS words")
        if rebuild_all:
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS phrases")
            cursor.execute("DROP TABLE IF EXISTS ratings")
            cursor.execute("DROP TABLE IF EXISTS notifications")
                
        cursor.execute("pragma foreign_keys = on")

        cursor.execute("CREATE TABLE words(word, type)")

        if rebuild_all:
            cursor.execute("CREATE TABLE users(name PRIMARY KEY UNIQUE)")
            cursor.execute("CREATE TABLE phrases(id INTEGER PRIMARY KEY AUTOINCREMENT, a,b)")
            cursor.execute('''
                CREATE TABLE ratings(phrase_id INTEGER KEY, user_name, rating INTEGER,
                                    FOREIGN KEY(phrase_id) REFERENCES phrases(id),
                                    FOREIGN KEY(user_name) REFERENCES users(name), CONSTRAINT unq UNIQUE(phrase_id, user_name))
            ''')
            for u in users:
                cursor.execute("INSERT INTO users (name) VALUES(?)", (u,))

            cursor.execute('''
                CREATE TABLE notifications(id INTEGER PRIMARY KEY AUTOINCREMENT, user_name,
                                           read INTEGER DEFAULT 0, text,
                                           FOREIGN KEY(user_name) REFERENCES users(name))
            ''')

        print u"Inserting {} things and {} modifiers into the database.".format(len(things), len(modifiers))
        for t in things:
            cursor.execute("INSERT INTO words (word, type) VALUES(?,?)", (t, "thing"))
        for a in modifiers:
            cursor.execute("INSERT INTO words (word, type) VALUES(?,?)", (a, "modifier"))
        
        db.commit()
    return "Database rebuilt!"

@app.route("/<game>/matches.json", methods=["GET"], defaults={"format": "json"})
@app.route("/<game>/matches", methods=["GET"], defaults={"format": "html"})
@app.route("/<game>/matches/print", methods=["GET"], defaults={"format": "print"})
def get_matches(game, format):
    matches = []
    good_ones = []
    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        # Get number of users
        cursor.execute("SELECT name FROM users")
        n_users = len(cursor.fetchall())

        cursor.execute("SELECT DISTINCT phrase_id FROM ratings WHERE rating > 0")
        rated = [r["phrase_id"] for r in cursor.fetchall()]
        for id in rated:
            cursor.execute("SELECT * FROM ratings WHERE phrase_id = ?", (id,))
            rating = sum([r["rating"] for r in cursor.fetchall()])
            if rating > 1:
                # Get the record for this phrase
                cursor.execute("SELECT * FROM phrases WHERE id is ?", (id,))
                result = cursor.fetchone()
                phrase = {"a": result["a"], "b": result["b"], "id":result["id"]}
                if rating >= n_users:               # Match is defined as everyone agrees
                    matches.append(phrase)
                #elif rating >= n_users / 2.0:    # Good ones is defined as more than half users agree
                elif rating == n_users - 1:
                    good_ones.append(phrase)

    if format is "html":
        return render_template("matches.html", game=game, matches=matches, good_ones=good_ones)
    elif format is "json":
        return jsonify(game=game, matches=matches, good_ones=good_ones)
    elif format is "print":

        print u"Printing {} matches...".format(len(matches))
        printer.printHeader()
        time.sleep(.5)
        for m in matches:
            printer.printMatch(m["a"], m["b"])
            time.sleep(1)

        return "OK"



@app.route("/<game>/phrase", methods=["GET"])
def generate(game):
    if not session.has_key("user"):
        return redirect(url_for("login", game=game))

    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        # Check if there are any ratings waiting with this user
        if random.random() < 0.25:
            cursor.execute("SELECT * FROM ratings WHERE user_name is ? AND rating is 0", (session['user'],))
            waiting_phrases = cursor.fetchall()
            if len(waiting_phrases) > 0:
                cursor.execute("SELECT * FROM phrases WHERE id is ?", (waiting_phrases[0]["phrase_id"],))
                phrase = cursor.fetchone()
                if phrase is not None:
                    print u"RETURNING WAITING PHRASE {} + {}".format(phrase["a"], phrase["b"])
                    return jsonify(a=phrase["a"], b=phrase["b"], id=phrase["id"])

        # Create a new phrase, add it to the database, serve it to the user
        cursor.execute("SELECT * FROM words WHERE type is 'thing'")
        things = [w["word"] for w in cursor.fetchall()]

        cursor.execute("SELECT * FROM words WHERE type is 'modifier'")
        modifiers = [w["word"] for w in cursor.fetchall()]

        a_has_modifier = True if random.random() < 0.4 else False
        b_has_modifier = True if random.random() < 0.4 else False

        a = random.choice(things)
        b = random.choice(things)
        if a_has_modifier:
            a = u"{} {}".format(random.choice(modifiers), a)
        if b_has_modifier:
            b = u"{} {}".format(random.choice(modifiers), b)

        # Add this to the database
        cursor.execute("INSERT INTO phrases(a,b) VALUES(?,?)", (a,b))
        db.commit()
    return jsonify(a=a, b=b, id=cursor.lastrowid)

@app.route("/<game>/phrase/<int:phrase_id>/rating", methods=["POST"])
def rate(game, phrase_id):
    if not session.has_key("user"):
        return redirect(url_for("login", game=game))

    user = session['user']
    rating = int(request.form["rating"])

    print u"Rating from user {}: {}".format(user,rating)

    positive = 0
    negative = 0

    # if rating > 0:
    #     subprocess.Popen("aplay -B 100000 swipe_right.wav", shell=True)
    # else:
    #     subprocess.Popen("aplay -B 100000 swipe_left.wav", shell=True)

    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()    

        # Add or update a rating for this phrase and user
        cursor.execute("INSERT OR REPLACE INTO ratings(phrase_id, user_name, rating) VALUES(?,?,?)", (phrase_id, user, rating))
        cursor.execute("SELECT * FROM users WHERE name is not ?", (user,))
        other_users = [u["name"] for u in cursor.fetchall()]

        if rating > 0:
            positive += 1
        elif rating < 0:
            negative += 1

        for u in other_users:
            # See if a rating already exists for this user
            cursor.execute("SELECT * FROM ratings WHERE user_name is ? AND phrase_id is ?", (u,phrase_id))
            result = cursor.fetchone()
            if not result and rating > 0:
                # Create a 0 entry for all other users in the rating table if this is a positive rating
                # That way they will see it soon
                cursor.execute("INSERT INTO ratings(phrase_id, user_name, rating) VALUES(?,?,?)", (phrase_id, u, 0))
            elif result:
                if result["rating"] > 0:
                    positive += 1
                else:
                    negative += 1
        db.commit()

            
            
            

        # Create notifications as needed
        if rating > 0 and positive >= (len(other_users)+1):
            # IT'S A MATCH
            #subprocess.Popen("aplay -B 100000 match.wav", shell=True)

            cursor.execute("SELECT * FROM phrases WHERE id is ?", (phrase_id,))
            result = cursor.fetchone()
            
            printer.printMatch(result["a"], result["b"])
            
            other_users.append(session['user']) # Make sure to notify this user, too
            for u in other_users:
                #create_notification(u, "It's a match: {} + {}".format(result["a"], result["b"]))
                create_notification(game, u, render_template("match_notification.html", game=game, a=result["a"], b=result["b"], message=u"👍 It's a match!"))

        elif rating < 0 and positive >= (len(other_users)):
            # YOU KILLED THE VIBE
            #subprocess.Popen("aplay -B 100000 deadvibe.wav", shell=True)

            cursor.execute("SELECT * FROM phrases WHERE id is ?", (phrase_id,))
            result = cursor.fetchone()


            other_users.append(session['user']) # Make sure to notify this user, too
            for u in other_users:
                #create_notification(u, "It's a match: {} + {}".format(result["a"], result["b"]))
                if u is session['user']:
                    who = "YOU"
                else:
                    who = session['user'].upper()
                create_notification(game, u, render_template("match_notification.html", game=game, a=result["a"], b=result["b"], message=u"😰 {} KILLED THE VIBE".format(who)))
        #elif rating > 0 and positive >= (len(other_users) / 2.0):
        elif rating > 0 and positive == (len(other_users)):
            # GENERATING ENERGY
            #subprocess.Popen("aplay -B 200000 feelingit.wav", shell=True)

            cursor.execute("SELECT * FROM phrases WHERE id is ?", (phrase_id,))
            result = cursor.fetchone()
            other_users.append(session['user']) # Make sure to notify this user, too
            for u in other_users:
                #create_notification(u, "It's a match: {} + {}".format(result["a"], result["b"]))
                if u is session['user']:
                    who = "YOU"
                else:
                    who = session['user'].upper()
                create_notification(game, u, render_template("match_notification.html", game=game,  a=result["a"], b=result["b"], message=u"🌵 We're feeling this vibe:".format(who)))

    return get_rating(game, phrase_id) 

@app.route("/<game>/phrase/<int:phrase_id>/rating", methods=["GET"])
def get_rating (game, phrase_id):
    if not session.has_key("user"):
        return redirect(url_for("login", game=game))

    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()    
        cursor.execute("SELECT * FROM ratings WHERE phrase_id is ?", (phrase_id,))    
        ratings = {}
        for r in cursor.fetchall():
            ratings[r["user_name"]] = r["rating"]

        return jsonify(ratings=ratings)

@app.route("/<game>/notifications/test")
def create_bogus_notification(game):
    return create_notification(game=game, user="Sam", text="This is an alert")

def create_notification(game, user, text):
    with sqlite3.connect("games/{}.db".format(game)) as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO notifications(user_name, text) VALUES(?,?)", (user, text))
        db.commit()
        return "OK"

    return "ERROR"

@app.route("/<game>/notifications/unread", methods=["GET"], defaults={"all": False})
@app.route("/<game>/notifications", methods=["GET"], defaults={"all": True})
def get_notifications(game, all):
    if not session.has_key("user"):
        return redirect(url_for("login", game=game))

    # Look in the database and return new notifications for the user
    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        if all:
            cursor.execute("SELECT id,text,read FROM notifications WHERE user_name is ?", (session["user"],))
        else:
            cursor.execute("SELECT id,text,read FROM notifications WHERE user_name is ? AND read is 0", (session["user"],))

        notifications = [{"id": n["id"], "read": n["read"], "text": n["text"]} for n in cursor.fetchall()]

        return jsonify(notifications=notifications)

@app.route("/<game>/notifications/read", methods=["POST", "GET"])
def read_all_notifications(game):
    if not session.has_key("user"):
        return redirect(url_for("login", game=game))

    with sqlite3.connect("games/{}.db".format(game)) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE notifications SET read=1 WHERE user_name is ?", (session["user"],))
        db.commit()
    
        return str(cursor.rowcount) # 1 if successful, 0 if not

@app.route("/<game>/notifications/<int:id>/read", methods=["POST", "GET"])
def read_notification(game, id):
    if not session.has_key("user"):
        return redirect(url_for("login", game=game))

    with sqlite3.connect("games/{}.db".format(game)) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE notifications SET read=1 WHERE id=? AND user_name is ? AND read=0", (id,session["user"]))
        db.commit()
    
        return str(cursor.rowcount) # 1 if successful, 0 if not

@app.route("/<game>/users", methods=["GET"])
def userlist(game):
    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()    
        cursor.execute("SELECT * FROM users")
        users = [u["name"] for u in cursor.fetchall()]

    current = ""
    if session.has_key("user"):
        current = session["user"]

    return jsonify(users=users, loggedin=current)

@app.route("/login", methods=["GET"])
def render_login():
    return "Please login."

@app.route("/<game>/login", methods=["POST"])
def login(game):
    user = request.form['user']
    with sqlite3.connect("games/{}.db".format(game)) as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users")
        users = [u["name"] for u in cursor.fetchall()]

        print users
        cursor.execute("SELECT * FROM users WHERE name is ?", (user,))
        results = cursor.fetchall()
        if len(results) > 0:
            session['user'] = user
            print u"User {} logged in.".format(user)
            return "OK"
        else:
            print u"USER DOES NOT EXIST: {}".format(user)
            return "USER DOES NOT EXIST"

@app.errorhandler(404)
def notfound(error):
    return redirect(url_for('index'))

def isCaptivePortal(request):
    user_agent = request.headers["User-Agent"]
    host = request.headers["Host"
    ]
    CP_ALLOWED_HOSTS = ["captive.apple.com"]
    CP_ALLOWED_AGENTS = ["CaptiveNetworkSupport"]

    if host in CP_ALLOWED_HOSTS:
        return True

    for agent in CP_ALLOWED_AGENTS:
        if agent in user_agent:
            return True

    return False

app.secret_key = "the ambulance chasers of venture capital"
app.debug = True
if __name__ == '__main__':
    printer.init()
    printer.printHeader()
    #subprocess.call("amixer cset numid=5 26,0", shell=True)
    # subprocess.call("cp *.wav /tmp/", shell=True)
    #subprocess.Popen("aplay -B 100000 welcome.wav", shell=True)
    app.run(host='0.0.0.0', threaded=True, port=8000)


