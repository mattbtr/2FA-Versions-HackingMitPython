# Import der Variable "app" aus __init__.py --> importiert die Flask-App-Instanz
from ticket import app

if __name__ == "__main__":
# Wenn app.py direkt gestartet wird, dann "__main__"
# Wenn app.py importiert wird, dann "dateiname" (hier: "run")
    app.run(debug=True, host="0.0.0.0", port=5000)          

# bisher aufgerufen unter: http://127.0.0.1:5000 als Standard

# Mit Zusatz von: host= 0.0.0.0 und port 5000 damit man burpe verwendet, um echte ip adresse zu erhalten mit proxy