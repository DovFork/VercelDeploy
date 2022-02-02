import os
import json
import subprocess
import yaml
import requests

token = os.environ["GIT_TOKEN"]
events = json.loads(os.environ["EVENTS"])

config_url = os.environ["CONFIG_URL"]
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
if os.getenv("AUTHORIZATION_TOKEN"):
    headers["Authorization"] = "token {}".format(
        os.getenv("AUTHORIZATION_TOKEN")
    )

res = requests.get(config_url, headers=headers).text
config = yaml.safe_load(res)

repo = {
    "full_name": events["repository"]["full_name"],
    "url": events["repository"]["clone_url"],
    "commit": events["commits"][0]["id"] if events["commits"] else None,
}

command = '''
git clone --depth 1 {} vercel
cd vercel
'''.format(f"https://{token}@" + repo["url"].lstrip("http://").lstrip("https://"))

if repo["commit"]:
    command += "\ngit reset --hard " + repo["commit"]

subprocess.run(command, shell=True, check=True, capture_output=False)
for cf in config["config"]:
    if repo["full_name"] == cf["name"]:
        with open("project_id", "w") as w:
            w.write(cf["project"])
