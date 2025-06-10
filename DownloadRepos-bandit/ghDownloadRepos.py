import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# GitHub-Repo URL (nicht die .git-URL!)
REPO_PAGE_URL = "https://github.com/mattbtr/HackingMitPython"

# Download-Verzeichnis
DOWNLOAD_DIR = os.path.abspath("downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def setup_driver():
    try:
        options = Options()
        #options.add_argument("--headless=new")  # Headless-Modus
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("prefs", {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

        logging.info("Starte Chrome WebDriver...")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        return driver
    except WebDriverException as e:
        logging.error(f"WebDriver konnte nicht initialisiert werden: {e}")
        raise

def download_repo_zip(driver, repo_url):
    try:
        logging.info(f"Öffne Repository-Seite: {repo_url}")
        driver.get(repo_url)
        time.sleep(2)  # Warte, bis Seite geladen ist

        logging.info("Suche 'Code'-Button...")
        #code_button = driver.find_element(By.XPATH, "//summary[contains(@class, 'get-repo-select-menu')]")
        code_button = driver.find_element(By.XPATH, "//button[contains(., 'Code')]")
        code_button.click()
        time.sleep(1)

        logging.info("Suche 'Download ZIP'-Link...")
        download_link = driver.find_element(By.XPATH, "//a[.//span[text()='Download ZIP']]")
        download_url = download_link.get_attribute("href")
        logging.info(f"Download-Link gefunden: {download_url}")

        logging.info("Starte den Download...")
        driver.get(download_url)

        # Warte auf Download
        time.sleep(5)
        logging.info(f"Download abgeschlossen. ZIP sollte nun im Ordner '{DOWNLOAD_DIR}' liegen.")

    except NoSuchElementException as e:
        logging.error("Ein benötigtes Element wurde auf der Seite nicht gefunden.")
        logging.error(e)
    except TimeoutException as e:
        logging.error("Timeout beim Laden der Seite oder beim Zugriff auf Elemente.")
        logging.error(e)
    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

def main():
    driver = setup_driver()
    try:
        download_repo_zip(driver, REPO_PAGE_URL)
    finally:
        driver.quit()
        logging.info("Browser geschlossen.")

if __name__ == "__main__":
    main()
