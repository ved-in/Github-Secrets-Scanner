import os
import zipfile
import shutil

ZIP_DIR = "downloads"
EXTRACT_DIR = "extracts"
os.makedirs(EXTRACT_DIR, exist_ok=True)

for f in os.listdir(EXTRACT_DIR):
    path = os.path.join(EXTRACT_DIR, f)
    if os.path.isdir(path):
        shutil.rmtree(path)


def extract_repo_zip(zip_file):
    folder_name = zip_file.rsplit(".", 1)[0]
    folder_path = os.path.join(EXTRACT_DIR, folder_name)

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    os.makedirs(folder_path)

    zip_path = os.path.join(ZIP_DIR, zip_file)
    with zipfile.ZipFile(zip_path, "r") as zip_obj:
        zip_obj.extractall(folder_path)

    print(f"Extracted {zip_file} : {folder_path}")


def extract_all_repos():
    zip_files = [f for f in os.listdir(ZIP_DIR) if f.endswith(".zip")]

    if not zip_files:
        print("No zip files found to extract")
        return

    for zip_file in zip_files:
        extract_repo_zip(zip_file)


if __name__ == "__main__":
    print("Extracting all downloaded GitHub repo zips")
    extract_all_repos()