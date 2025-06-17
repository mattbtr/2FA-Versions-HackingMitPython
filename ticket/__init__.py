# __init__.py = Initialisierung App --> hier wird sie konfiguiert und mit Erweiterungen versehen 

# Flask importieren
from flask import Flask, session
# für Datenbankzugriff
from flask_sqlalchemy import SQLAlchemy
# Flask Instanz erstellt und in "app" gespeichert
app = Flask(__name__)

# Secret Key für Nutzung von Sessions!! --> Nicht öffentlich machen in Repo in Praxis
app.secret_key = 'hello'

# Konfiguration um auf Datenbank Zugriff zu erhalten (Anmeldedaten)
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql+pymysql://ticketdb_user:Heute0000@127.0.0.1/ticketdb"

# Deaktiviert unnötige Event-Tracking-Logs (Performance-Optimierung)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# in Variable db wird DAtnbankzugriff-Instanz bzw Zugriff gespeichert
db = SQLAlchemy(app)

# Wozu?
# !! Import ist notwendig, damit Flask(die Flask-App-Instanz) die Decorators (@app.route(...)) registriert !!
# Beim Import werden Routen registriert
# !! Wenn nciht gemacht wird, weiß Flask-App nichts von den Routen
from ticket import routes

