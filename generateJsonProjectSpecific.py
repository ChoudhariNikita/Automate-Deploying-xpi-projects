"""
This script is project-specific as it is designed to process and generate a JSON file 
containing details of projects following a specific naming convention (e.g., MCM_1, MCM_2, etc.). 
You can modify the script to include any other projects with a similar naming convention 
by adjusting the range or providing a list of project names.
"""

import json
import os

# Base directory path
base_dir = r"C:\Users\nchoudhari\Documents\magic\projects"

# Use current script directory to save the JSON file
script_dir = os.path.dirname(os.path.abspath(__file__))
aon_folder_path = script_dir  # Directly store in root folder (where script exists)

# List to hold project details
projects = []

# Iterate over all 50 projects
for i in range(1, 51):
    project_folder = f"MCM_{i}"
    docker_folder = f"Docker_MCM_{i}"
    project_dir = os.path.join(base_dir, project_folder, docker_folder)
    print(f"📁 Processing {project_folder} at: {project_dir}")

    # Paths
    hash_file_path = os.path.join(project_dir, "projectbuildhash.txt")
    context_path = os.path.join(project_dir, "env.ini")
    zip_path = os.path.join(project_dir, f"{project_folder}.zip")

    # Read project hash
    try:
        with open(hash_file_path, "r") as file:
            project_hash = file.read().strip()
    except FileNotFoundError:
        print(f"❌ Hash file not found for {project_folder}")
        project_hash = "N/A"

    # Validate essential files
    if not os.path.exists(zip_path) or not os.path.exists(context_path):
        print(f"⚠️ Required files missing for {project_folder}. Skipping...")
        continue

    # Create project dictionary
    project = {
        "projectname": project_folder,
        "projectzipfile": zip_path,
        "context": context_path,
        "projecthash": project_hash
    }

    projects.append(project)

# Save the JSON file in Desktop/Aon folder
output_file = os.path.join(aon_folder_path, "projects.json")
with open(output_file, "w") as json_file:
    json.dump(projects, json_file, indent=4)

print(f"\n✅ JSON file generated successfully at: {output_file}")
