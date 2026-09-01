import os
import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. State Management
state_code = """
# ==========================================
# APPLICATION STATE
# ==========================================

project_sessions = {}

def get_session(project_name):
    if project_name not in project_sessions:
        from class_manager import load_classes
        project_sessions[project_name] = {
            "batch_images": [],
            "current_image_index": 0,
            "current_classes": load_classes(project_name)
        }
    return project_sessions[project_name]
"""
content = re.sub(r'# ==========================================\n# APPLICATION STATE.*?(?=# ==========================================)', state_code + "\n\n", content, flags=re.DOTALL)


# 2. Folders
# We remove global folders and just use dynamic ones, but we'll comment them out
folder_code = """
# ==========================================
# FOLDERS (Now scoped to projects)
# ==========================================

def get_project_folders(project_name):
    base = os.path.join("projects", project_name)
    return {
        "uploads": os.path.join(base, "uploads"),
        "outputs": os.path.join(base, "outputs"),
        "labels": os.path.join(base, "labels"),
        "export": os.path.join(base, "yolo_dataset")
    }
"""
content = re.sub(r'# ==========================================\n# FOLDERS.*?(?=# ==========================================)', folder_code + "\n\n", content, flags=re.DOTALL)


# 3. Home Route
home_code = """
# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    os.makedirs("projects", exist_ok=True)
    projects = [d for d in os.listdir("projects") if os.path.isdir(os.path.join("projects", d))]
    return render_template("dashboard.html", projects=projects)

@app.route("/create_project", methods=["POST"])
def create_project():
    from flask import request, redirect
    project_name = request.form.get("project_name", "").strip()
    if project_name:
        folders = get_project_folders(project_name)
        for f in folders.values():
            os.makedirs(f, exist_ok=True)
    return redirect("/")

@app.route("/delete_project", methods=["POST"])
def delete_project():
    from flask import request, jsonify
    import shutil
    data = request.get_json(silent=True)
    project_name = data.get("project_name", "")
    if project_name:
        proj_dir = os.path.join("projects", project_name)
        if os.path.exists(proj_dir):
            shutil.rmtree(proj_dir)
            if project_name in project_sessions:
                del project_sessions[project_name]
    return jsonify({"status": "success"})

@app.route("/project/<project_name>")
def project_home(project_name):
    from class_manager import load_classes
    unique_classes = sorted(list(set(load_classes(project_name))))
    return render_template("index.html", available_classes=unique_classes, project_name=project_name)

@app.route("/project/<project_name>/outputs/<filename>")
def serve_output(project_name, filename):
    import os
    from flask import send_from_directory
    return send_from_directory(os.path.abspath(os.path.join("projects", project_name, "outputs")), filename)
"""
content = re.sub(r'# ==========================================\n# HOME PAGE.*?(?=# ==========================================)', home_code + "\n\n", content, flags=re.DOTALL)


# 4. Update Global variables in functions (global batch_images, current_image_index, current_classes)
# We'll replace lines like:
# global batch_images
# global current_image_index
# global current_classes
# with:
# session = get_session(project_name)
# batch_images = session["batch_images"]
# current_image_index = session["current_image_index"]
# current_classes = session["current_classes"]

def replace_globals(match):
    return """
    session = get_session(project_name)
    batch_images = session["batch_images"]
    current_image_index = session["current_image_index"]
    current_classes = session["current_classes"]
"""
content = re.sub(r'\n\s*global batch_images\n\s*global current_image_index\n\s*global current_classes\n', replace_globals, content)
content = re.sub(r'\n\s*global batch_images\n\s*global current_image_index\n', replace_globals, content)
content = re.sub(r'\n\s*global batch_images\n', replace_globals, content)

# Update Route Signatures to accept project_name
content = re.sub(r'@app.route\(\n\s*"/detect"', r'@app.route("/project/<project_name>/detect"', content)
content = re.sub(r'def detect\(\):', r'def detect(project_name):', content)

content = re.sub(r'@app.route\(\n\s*"/image/<int:index>"\n\)', r'@app.route("/project/<project_name>/image/<int:index>")', content)
content = re.sub(r'def show_image\(index\):', r'def show_image(project_name, index):', content)

content = re.sub(r'@app.route\("/bulk_rename", methods=\["POST"\]\)', r'@app.route("/project/<project_name>/bulk_rename", methods=["POST"])', content)
content = re.sub(r'def bulk_rename\(\):', r'def bulk_rename(project_name):', content)

content = re.sub(r'@app.route\(\n\s*"/save_labels"', r'@app.route("/project/<project_name>/save_labels"', content)
content = re.sub(r'def save_labels\(\):', r'def save_labels(project_name):', content)

content = re.sub(r'@app.route\("/export_dataset"\)', r'@app.route("/project/<project_name>/export_dataset")', content)
content = re.sub(r'def export_dataset\(\):', r'def export_dataset(project_name):', content)

content = re.sub(r'@app.route\("/progress"\)', r'@app.route("/project/<project_name>/progress")', content)
content = re.sub(r'def dataset_progress\(\):', r'def dataset_progress(project_name):', content)


# 5. Fix route redirects
content = re.sub(r'return redirect\(url_for\("show_image", index=0\)\)', r'return redirect(url_for("show_image", project_name=project_name, index=0))', content)

# 6. Fix UPLOAD_FOLDER -> folders["uploads"]
content = re.sub(r'file_path = os.path.join\(UPLOAD_FOLDER, filename\)', r'folders = get_project_folders(project_name)\n        file_path = os.path.join(folders["uploads"], filename)', content)
content = re.sub(r'frame_path = os.path.join\(UPLOAD_FOLDER, frame_filename\)', r'frame_path = os.path.join(folders["uploads"], frame_filename)', content)
content = re.sub(r'UPLOAD_FOLDER', r'get_project_folders(project_name)["uploads"]', content)
content = re.sub(r'LABEL_FOLDER', r'get_project_folders(project_name)["labels"]', content)
content = re.sub(r'EXPORT_FOLDER', r'get_project_folders(project_name)["export"]', content)

# 7. Output image static url logic inside detect()
# Original: output_image = url_for("static", filename=f"outputs/{output_filename}")
# New: output_image = url_for("serve_output", project_name=project_name, filename=output_filename)
content = re.sub(r'url_for\(\n\s*"static",\n\s*filename=\n\s*f"outputs/\{output_filename\}"\n\s*\)', r'url_for("serve_output", project_name=project_name, filename=output_filename)', content)

# 8. Render template in show_image needs project_name
content = re.sub(r'available_classes=unique_classes\n\s*\)', r'available_classes=unique_classes,\n        project_name=project_name\n    )', content)

# 9. Function calls that need project_name
content = re.sub(r'add_classes\(\n\s*class_list\n\s*\)', r'add_classes(project_name, class_list)', content)
content = re.sub(r'add_classes\(\n\s*annotation_classes\n\s*\)', r'add_classes(project_name, annotation_classes)', content)
content = re.sub(r'detect_objects\(\n\s*image_path,\n\s*class_list\n\s*\)', r'detect_objects(project_name, image_path, class_list)', content)
content = re.sub(r'save_yolo_labels\(\n\s*result,\n\s*image_path,\n\s*class_list\n\s*\)', r'save_yolo_labels(project_name, result, image_path, class_list)', content)
content = re.sub(r'save_edited_annotations\(\n\s*annotations=', r'save_edited_annotations(\n            project_name=project_name,\n            annotations=', content)

# save_classes and load_classes
content = re.sub(r'load_classes\(\)', r'load_classes(project_name)', content)
content = re.sub(r'save_classes\(classes\)', r'save_classes(project_name, classes)', content)

# In show_image, labels dir is now projects/project_name/labels
content = re.sub(r'label_path = os.path.join\("labels", f"\{image_name\}.txt"\)', r'label_path = os.path.join("projects", project_name, "labels", f"{image_name}.txt")', content)
content = re.sub(r'labels_dir = "labels"', r'labels_dir = os.path.join("projects", project_name, "labels")', content)

# Save session state changes
# Since batch_images, current_image_index, current_classes are local refs now, we need to save them back or modify them in place.
# Actually, lists (batch_images) and dicts (session) are mutable so modifying `batch_images` in place (append) works.
# But assignments like `current_image_index = 0` only change the local variable. We must do `session["current_image_index"] = 0`
content = re.sub(r'\n\s*current_image_index = 0\n', r'\n    session["current_image_index"] = 0\n    current_image_index = 0\n', content)
content = re.sub(r'\n\s*current_image_index = index\n', r'\n    session["current_image_index"] = index\n    current_image_index = index\n', content)
content = re.sub(r'\n\s*batch_images = \[\]\n', r'\n    session["batch_images"] = []\n    batch_images = session["batch_images"]\n', content)
content = re.sub(r'\n\s*current_classes = add_classes', r'\n    session["current_classes"] = add_classes', content)
content = re.sub(r'\n\s*current_classes = \(\n\s*updated_classes\n\s*\)', r'\n    session["current_classes"] = updated_classes\n    current_classes = session["current_classes"]', content)
content = re.sub(r'\n\s*current_classes = load_classes\(project_name\)\n', r'\n    session["current_classes"] = load_classes(project_name)\n    current_classes = session["current_classes"]\n', content)

# We can remove the reset_workspace route completely since we have delete_project
content = re.sub(r'# ==========================================\n# RESET WORKSPACE.*?# ==========================================\n# DATASET PROGRESS', r'# ==========================================\n# DATASET PROGRESS', content, flags=re.DOTALL)


# Delete old variables
content = re.sub(r'UPLOAD_FOLDER = "uploads".*?os.makedirs\(\n\s*LABEL_FOLDER,\n\s*exist_ok=True\n\)', '', content, flags=re.DOTALL)


with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
