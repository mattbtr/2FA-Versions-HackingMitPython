import os
import zipfile
import subprocess
import re

ZIP_DIR = "downloads"
EXTRACT_DIR = "repos"
RESULTS_DIR = "analysis_results"

# 1. Extrahiere alle ZIPs
def extract_all_zips():
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    for zip_file in os.listdir(ZIP_DIR):
        if zip_file.endswith(".zip"):
            zip_path = os.path.join(ZIP_DIR, zip_file)
            extract_path = os.path.join(EXTRACT_DIR, zip_file.replace(".zip", ""))
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            print(f"[+] Extrahiert: {zip_file}")

# 2. Führe Bandit aus
def run_bandit_on_all():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    for project_dir in os.listdir(EXTRACT_DIR):
        full_path = os.path.join(EXTRACT_DIR, project_dir)
        if os.path.isdir(full_path):
            result_file = os.path.join(RESULTS_DIR, f"{project_dir}_bandit.txt")
            with open(result_file, 'w') as f:
                subprocess.run(["bandit", "-r", full_path], stdout=f, stderr=subprocess.DEVNULL)
            print(f"[+] Bandit ausgeführt für: {project_dir}")

# 3. Suche nach hardcodierten Passwörtern mit Regex
def search_password_patterns():
    pattern = re.compile(r'(?i)(password|passwd|pwd)\s*=\s*[\'"].+[\'"]')
    for project_dir in os.listdir(EXTRACT_DIR):
        full_path = os.path.join(EXTRACT_DIR, project_dir)
        for root, _, files in os.walk(full_path):
            for file in files:
                if file.endswith(".py"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                        for lineno, line in enumerate(f, 1):
                            if pattern.search(line):
                                print(f"[!] Möglicherweise hartkodiertes Passwort gefunden in {file}:{lineno}")
                                print(f"    → {line.strip()}")

if __name__ == "__main__":
    extract_all_zips()
    run_bandit_on_all()
    search_password_patterns()
