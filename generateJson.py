import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Base directory where all projects are stored
base_dir = os.getenv("PROJECTS_DIR")

# Check if base_dir is set
if not base_dir:
    raise ValueError("Environment variable 'PROJECTS_DIR' is not set. Please check your .env file.")

# Use script directory to save the JSON
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "projects.json")

# Initialize project list
projects = []
# List of folder prefixes to ignore
ignore_prefixes = ["MCM_","FW_Step_FTP_Size","JDBC_MSSQL","XMLHasndling"]

# Loop through all folders in the base_dir
for project_folder in os.listdir(base_dir):
    # Skip folders starting with any prefix in ignore_prefixes
    if any(project_folder.startswith(prefix) for prefix in ignore_prefixes):
        print(f"⏩ Skipping folder: {project_folder}")
        continue

    project_path = os.path.join(base_dir, project_folder)

    if not os.path.isdir(project_path):
        continue  # skip files
        continue  # skip files

    # Look for a Docker_* subfolder
    docker_subfolder = None
    for sub in os.listdir(project_path):
        if sub.startswith("Docker_"):
            docker_subfolder = os.path.join(project_path, sub)
            break

    if not docker_subfolder or not os.path.isdir(docker_subfolder):
        print(f"❌ No Docker_* folder found in {project_folder}")
        continue

    print(f"📁 Processing: {project_folder} at {docker_subfolder}")

    # Construct paths
    hash_path = os.path.join(docker_subfolder, "projectbuildhash.txt")
    context_path = os.path.join(docker_subfolder, "env.ini")

    # Look for ZIP file inside Docker folder
    zip_file = None
    for file in os.listdir(docker_subfolder):
        if file.endswith(".zip"):
            zip_file = os.path.join(docker_subfolder, file)
            break

    if not zip_file or not os.path.exists(context_path):
        print(f"⚠️ Missing ZIP or env.ini for {project_folder}. Skipping.")
        continue

    # Read hash
    try:
        with open(hash_path, "r") as f:
            project_hash = f.read().strip()
    except FileNotFoundError:
        print(f"❌ Hash file missing for {project_folder}")
        project_hash = "N/A"

    # Add to project list
    projects.append({
        "projectname": project_folder,
        "projectzipfile": zip_file,
        "context": context_path,
        "projecthash": project_hash
    })

# Save to JSON
with open(output_path, "w") as f:
    json.dump(projects, f, indent=4)

print(f"\n✅ Project JSON generated at: {output_path}")
