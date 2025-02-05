import os
import shutil
import requests

def clear_directory(directory):
    """Delete all files and subdirectories in the given directory."""
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete subdirectory
            else:
                os.remove(file_path)  # Delete file

def fetch_java_files_from_github(repo_name, output_dir, token):
    # Clear the source and bin directories before fetching new files
    clear_directory(output_dir)
    clear_directory("C:\\Users\\hatvi\\spotbugs\\bin")  # Add your bin folder path

    # Construct GitHub API URL
    url = f"https://api.github.com/repos/{repo_name}/contents"
    
    headers = {
        "Authorization": f"token {token}"
    }

    # Fetch the repository contents
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repository contents: {response.status_code} - {response.text}")

    content = response.json()

    # Filter Java files
    java_files = []

    for item in content:
        if item['type'] == 'file' and item['name'].endswith('.java'):
            # Fetch the content of each Java file
            java_file_content = requests.get(item['download_url']).text
            java_files.append({
                'filename': item['name'],
                'content': java_file_content  # Add content of the file
            })

    if not java_files:
        print("No Java files found.")
        raise Exception("No Java files found in the repository.")

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save each Java file to the output directory
    for java_file in java_files:
        file_path = os.path.join(output_dir, java_file['filename'])

        # Save the content to a file in the output directory
        with open(file_path, 'w') as f:
            f.write(java_file['content'])

        print(f"Saved file: {file_path}")

    return java_files  # Return the files with both filename and content

if __name__ == "__main__":
    # GitHub repository details
    repo_name = "havtik28/BugDetectorSystem"  # Replace with your repo
    # Directory to save the .java files
    output_dir = "C:\\Users\\hatvi\\spotbugs\\src"
    # Replace with your GitHub Personal Access Token
    access_token = "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"

    # Fetch Java files and save them locally
    fetch_java_files_from_github(repo_name, output_dir, access_token)
