from flask import Flask, render_template, request, jsonify
import os
import subprocess
import json
from fetchcode import fetch_java_files_from_github
from spotbugs import compile_java_files, run_spotbugs_analysis, parse_spotbugs_xml, display_spotbugs_issues
import shutil

app = Flask(__name__)

# Load SpotBugs descriptions from JSON
with open("bug_descriptions.json", "r") as f:
    bug_descriptions = json.load(f)

# Clear the directory (delete files and subdirectories)
def clear_directory(directory):
    """Delete all files and subdirectories in the given directory."""
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete subdirectory
            else:
                os.remove(file_path)  # Delete file

@app.route('/')
def index():
    return render_template('index.html')  # Show the input form

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get the GitHub repository URL from the form
    repo_url = request.form.get('repo_url')

    if not repo_url:
        return jsonify({"error": "No repository URL provided"}), 400

    # Extract repository name from URL
    repo_name = repo_url.split('github.com/')[1]

    # Define the output directories
    output_dir = "src"
    bin_dir = "bin"
    spotbugs_report_path = "spotbugs_report.xml"

    # Clear the source and bin directories before fetching new files
    clear_directory(output_dir)
    clear_directory(bin_dir)

    # Fetch the Java files from the GitHub repo
    try:
        files = fetch_java_files_from_github(
            repo_name, output_dir, "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")  # Use actual token
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not files or len(files) == 0:
        return jsonify({"error": "No Java files found in the repository"}), 404

    # Compile the Java files
    try:
        compile_java_files(output_dir, bin_dir)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Compilation failed: {e}"}), 500

    # Run SpotBugs analysis
    try:
        run_spotbugs_analysis(bin_dir, spotbugs_report_path)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"SpotBugs analysis failed: {e}"}), 500

    # Parse SpotBugs XML report
    try:
        spotbugs_issues = parse_spotbugs_xml(spotbugs_report_path)
    except Exception as e:
        return jsonify({"error": f"Error parsing SpotBugs report: {e}"}), 500

    # Return the bug results along with the code files
    return jsonify({
        "files": files,  # Send the code files to the frontend
        "bugs": spotbugs_issues
    })

if __name__ == '__main__':
    app.run(debug=True)
