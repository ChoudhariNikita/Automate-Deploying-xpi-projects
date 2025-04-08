import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get base directory from environment variable
base_dir = os.getenv("PROJECTS_DIR")
if not base_dir:
    raise EnvironmentError("PROJECTS_DIR environment variable not set.")

# Define the source project folder name
original_project_name = "JDBC_MSSQL"
src_dir = Path(base_dir) / original_project_name

# Validate source directory
if not src_dir.exists():
    raise FileNotFoundError(f"Source directory not found: {src_dir}")

# Create 10 copies with renamed zip files
for i in range(1, 11):
    new_project_name = f"{original_project_name}_{i}"
    dest_dir = Path(base_dir) / new_project_name

    # Clean up if already exists
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    # Copy the whole project folder
    shutil.copytree(src_dir, dest_dir)

    # Find docker_jdbc_mssql* subfolder
    docker_folder = next(dest_dir.glob("docker_jdbc_mssql*"), None)
    if docker_folder and docker_folder.is_dir():
        # Find and rename the zip file that contains 'jdbc_mssql'
        for zip_file in docker_folder.glob("*.zip"):
            if "jdbc_mssql" in zip_file.name.lower():
                new_zip_name = docker_folder / f"{new_project_name}.zip"
                zip_file.rename(new_zip_name)
                break
    else:
        print(f"No docker_jdbc_mssql* folder found in {dest_dir}")
