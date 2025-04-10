import json
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL")
CUSTOMER = os.getenv("CUSTOMER", "magic")
ENVIRONMENT = os.getenv("ENVIRONMENT")

if not ACCESS_TOKEN:
    raise Exception("❌ ACCESS_TOKEN not found in .env file. Please check your .env setup.")

# Load project data
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, "projects.json")

if not os.path.exists(json_path):
    raise FileNotFoundError(f"❌ Project JSON file not found at: {json_path}")

with open(json_path, "r") as f:
    projects = json.load(f)

# Prepare log file
log_file = os.path.join(script_dir, "deployment_log.txt")

# Write header if file is new or empty
if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
    with open(log_file, "a") as log:
        log.write(f"{'Project Name':<20} {'Start Time':<25} {'End Time':<25} {'Duration(s)':<12} {'Status':<20}\n")
        log.write("-" * 100 + "\n")

WAIT_TIME = 60  # seconds
TIMEOUT_DURATION = 180  # 3 minutes

# Deployment loop
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
    start_time = time.time()

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
                "customer": CUSTOMER,
                "environment": ENVIRONMENT,
                "runOnExtrnlAgnt": "",
                "agentName": "",
                "runOnExtrnlCluster": ""
            }

            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "accept": "application/json"
            }

            response = requests.post(BASE_URL, headers=headers, files=files, data=data, timeout=TIMEOUT_DURATION)

            end_time = time.time()
            duration = end_time - start_time

            if response.status_code == 200:
                print(f"✅ {project_name} submitted successfully.")
                with open(log_file, "a") as log:
                    log.write(f"{project_name:<20} {time.ctime(start_time):<25} {time.ctime(end_time):<25} {duration:<12.2f} {'SUCCESS':<20}\n")
                print(f"⏳ Waiting {WAIT_TIME // 60} minutes before deploying next project...\n")
                time.sleep(WAIT_TIME)
                continue

    except requests.exceptions.Timeout:
        print(f"⏰ Timeout occurred while deploying {project_name}. Retrying once...")
        try:
            start_time_retry = time.time()
            with open(zip_path, "rb") as zip_file, open(context_path, "rb") as context_file:
                files = {
                    "projectzipfile": (os.path.basename(zip_path), zip_file),
                    "context": (os.path.basename(context_path), context_file)
                }

                response = requests.post(BASE_URL, headers=headers, files=files, data=data, timeout=TIMEOUT_DURATION)

                end_time_retry = time.time()
                duration_retry = end_time_retry - start_time_retry

                if response.status_code == 200:
                    print(f"✅ {project_name} submitted successfully on retry.")
                    with open(log_file, "a") as log:
                        log.write(f"{project_name:<20} {time.ctime(start_time_retry):<25} {time.ctime(end_time_retry):<25} {duration_retry:<12.2f} {'SUCCESS (RETRY)':<20}\n")
                    print(f"⏳ Waiting {WAIT_TIME // 60} minutes before deploying next project...\n")
                    time.sleep(WAIT_TIME)
                    continue
                else:
                    print(f"❌ {project_name} failed on retry. Status: {response.status_code}")
                    with open(log_file, "a") as log:
                        log.write(f"{project_name:<20} {'-':<25} {'-':<25} {'-':<12} {'FAILURE (RETRY)':<20}\n")

        except requests.exceptions.Timeout:
            print(f"⏰ Timeout occurred again while retrying {project_name}. Skipping...")
            with open(log_file, "a") as log:
                log.write(f"{project_name:<20} {'-':<25} {'-':<25} {'-':<12} {'TIMEOUT (RETRY)':<20}\n")

    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ Error deploying {project_name}: {e}")
        with open(log_file, "a") as log:
            log.write(f"{project_name:<20} {time.ctime(start_time):<25} {time.ctime(end_time):<25} {duration:<12.2f} {'ERROR':<20}\n")

print("\n🎯 Deployment script finished.")
