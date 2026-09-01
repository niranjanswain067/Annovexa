import os
import shutil

def migrate():
    default_proj = os.path.join("projects", "default")
    
    # Check if we have legacy data
    has_legacy = False
    legacy_folders = ["uploads", "static/outputs", "labels", "yolo_dataset"]
    legacy_files = ["classes.txt"]

    for f in legacy_folders + legacy_files:
        if os.path.exists(f):
            has_legacy = True
            break
            
    if not has_legacy:
        print("No legacy data found. Skipping migration.")
        return
        
    print("Migrating legacy data to 'default' project...")
    os.makedirs(os.path.join(default_proj, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(default_proj, "outputs"), exist_ok=True)
    os.makedirs(os.path.join(default_proj, "labels"), exist_ok=True)
    os.makedirs(os.path.join(default_proj, "yolo_dataset"), exist_ok=True)
    
    # Move uploads
    if os.path.exists("uploads"):
        for f in os.listdir("uploads"):
            shutil.move(os.path.join("uploads", f), os.path.join(default_proj, "uploads", f))
        shutil.rmtree("uploads")
        
    # Move outputs
    if os.path.exists("static/outputs"):
        for f in os.listdir("static/outputs"):
            shutil.move(os.path.join("static/outputs", f), os.path.join(default_proj, "outputs", f))
        shutil.rmtree("static/outputs")
        
    # Move labels
    if os.path.exists("labels"):
        for f in os.listdir("labels"):
            shutil.move(os.path.join("labels", f), os.path.join(default_proj, "labels", f))
        shutil.rmtree("labels")
        
    # Move yolo_dataset
    if os.path.exists("yolo_dataset"):
        for f in os.listdir("yolo_dataset"):
            src = os.path.join("yolo_dataset", f)
            dst = os.path.join(default_proj, "yolo_dataset", f)
            if os.path.isdir(src):
                if os.path.exists(dst): shutil.rmtree(dst)
                shutil.move(src, dst)
            else:
                shutil.move(src, dst)
        shutil.rmtree("yolo_dataset")
        
    # Move classes.txt
    if os.path.exists("classes.txt"):
        shutil.move("classes.txt", os.path.join(default_proj, "classes.txt"))
        
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
