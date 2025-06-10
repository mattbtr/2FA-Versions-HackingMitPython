import os
import subprocess

repos_path = "downloaded_repos"

for repo_name in os.listdir(repos_path):
    repo_path = os.path.join(repos_path, repo_name)
    print(f"\n🔍 Scanning {repo_name} with Bandit...\n")
    subprocess.run(["bandit", "-r", repo_path])
