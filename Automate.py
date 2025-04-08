import json
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get token from environment
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL")

if not ACCESS_TOKEN:
    raise Exception("❌ ACCESS_TOKEN not found in .env file. Please check your .env setup.")

# Load project data from 'projects.json' in the current directory
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "projects.json")

if not os.path.exists(json_path):
    raise FileNotFoundError(f"❌ Project JSON file not found at: {json_path}")

with open(json_path, "r") as f:
    projects = json.load(f)

# Create a deployment log file in the same directory
log_file = os.path.join(script_dir, "deployment_log.txt")

# Delay between deployments in seconds (e.g., 1 minutes = 60 seconds)
WAIT_TIME = 60

# Begin deployment loop
for project in projects:
    zip_path = project["projectzipfile"]
    context_path = project["context"]
    project_hash = project["projecthash"]
    project_name = project["projectname"]

    if not os.path.exists(zip_path):
        print(f"❌ ZIP file missing for {project_name}: {zip_path}")
        continue

    if not os.path.exists(context_path):
        print(f"❌ Context file (env.ini) missing for {project_name}: {context_path}")
        continue

    print(f"\n🚀 Deploying {project_name}...")

    try:
        with open(zip_path, "rb") as zip_file, open(context_path, "rb") as context_file:
            files = {
                "projectzipfile": (os.path.basename(zip_path), zip_file),
                "context": (os.path.basename(context_path), context_file)
            }

            data = {
                "state": "start",
                "projectname": project_name,
                "projecthash": project_hash,
                "customer": "magic",
                "environment": "magic",
                "runOnExtrnlAgnt": "",
                "agentName": "",
                "runOnExtrnlCluster": ""
            }

            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "accept": "application/json"
            }

            # Make POST request with timeout (2 minutes)
            response = requests.post(BASE_URL, headers=headers, files=files, data=data, timeout=120)

            if response.status_code == 200:
                print(f"✅ {project_name} submitted successfully.")
                with open(log_file, "a") as log:
                    log.write(f"[SUCCESS] {project_name} submitted at {time.ctime()}\n")
                print(f"⏳ Waiting {WAIT_TIME // 60} minutes before deploying next project...\n")
                time.sleep(WAIT_TIME)
            else:
                print(f"❌ {project_name} failed. Status: {response.status_code}")
                print("🔴 Response:", response.text)
                with open(log_file, "a") as log:
                    log.write(f"[FAILURE] {project_name} failed with status {response.status_code} at {time.ctime()}\n")

    except requests.exceptions.Timeout:
        print(f"⏰ Timeout occurred while deploying {project_name}")
        with open(log_file, "a") as log:
            log.write(f"[TIMEOUT] {project_name} timed out at {time.ctime()}\n")

    except Exception as e:
        print(f"❌ Error deploying {project_name}: {e}")
        with open(log_file, "a") as log:
            log.write(f"[ERROR] {project_name} error: {str(e)} at {time.ctime()}\n")

print("\n🎯 Deployment script finished.")
