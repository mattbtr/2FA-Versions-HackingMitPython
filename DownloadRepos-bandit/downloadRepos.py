import os
import subprocess

repo_urls = [
    "https://github.com/mattbtr/HackingMitPython.git",
    "https://github.com/Hepha1stos/HackingWithPython.git"
]

clone_dir = "downloaded_repos"

os.makedirs(clone_dir, exist_ok=True)

for url in repo_urls:
    repo_name = url.split("/")[-1]
    subprocess.run(["git", "clone", url, f"{clone_dir}/{repo_name}"])
