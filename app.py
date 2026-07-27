from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    url_for,
    send_file
)

import os
import shutil
import random
from werkzeug.utils import secure_filename

from class_manager import add_classes, load_classes
from detector import detect_objects
from save_yolo import save_yolo_labels
from save_annotations import save_edited_annotations
from utils import results_to_json


# ==========================================
# CREATE FLASK APP
# ==========================================

app = Flask(__name__)


# ==========================================
# FOLDERS
# ==========================================

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = os.path.join(
    "static",
    "outputs"
)
LABEL_FOLDER = "labels"

EXPORT_FOLDER = "yolo_dataset"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

os.makedirs(
    LABEL_FOLDER,
    exist_ok=True
)


# ==========================================
# APPLICATION STATE
# ==========================================

# Permanent dataset classes
current_classes = load_classes()

# Stores all images in current batch
batch_images = []

# Current image being reviewed
current_image_index = 0


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    
    unique_classes = sorted(list(set(load_classes())))

    return render_template(
        "index.html",
        available_classes=unique_classes
    )


# ==========================================
# BATCH AUTO ANNOTATION
# ==========================================

@app.route(
    "/detect",
    methods=["POST"]
)
def detect():

    global batch_images
    global current_image_index
    global current_classes


    # ======================================
    # GET MULTIPLE IMAGES
    # ======================================

    images = request.files.getlist(
        "images"
    )


    images = [

        image

        for image in images

        if image and image.filename

    ]


    if not images:

        return (
            "No images selected."
        )


    # ======================================
    # GET DETECTION CLASSES
    # ======================================

    classes = request.form.get(
        "classes",
        ""
    )


    class_list = [

        class_name.strip()

        for class_name
        in classes.split(",")

        if class_name.strip()

    ]


    if not class_list:

        return (
            "Please enter at least "
            "one object class."
        )


    # ======================================
    # UPDATE PERMANENT CLASS LIST
    # ======================================

    current_classes = add_classes(
        class_list
    )


    print(
        "\n"
        "========================================"
    )

    print(
        "PERMANENT CLASS MAPPING"
    )

    print(
        "========================================"
    )


    for index, class_name in enumerate(
        current_classes
    ):

        print(
            f"{index} = {class_name}"
        )


    # ======================================
    # RESET PREVIOUS BATCH
    # ======================================

    batch_images = []

    current_image_index = 0


    total_images = len(
        images
    )


    print(

        f"\nStarting batch annotation "
        f"for {total_images} images..."

    )


    # ======================================
    # PROCESS EVERY IMAGE
    # ======================================

    for image_number, image in enumerate(
        images,
        start=1
    ):


        # ==================================
        # SECURE FILE NAME
        # ==================================

        filename = secure_filename(
            image.filename
        )


        if not filename:

            continue


        print(
            "\n"
            "----------------------------------------"
        )


        print(

            f"Processing Image "
            f"{image_number}/{total_images}"

        )


        print(
            "Filename:",
            filename
        )


        # ==================================
        # SAVE ORIGINAL IMAGE
        # ==================================

        image_path = os.path.join(

            UPLOAD_FOLDER,

            filename

        )


        image.save(
            image_path
        )


        # ==================================
        # RUN YOLO-WORLD
        # ==================================

        output_path, result = detect_objects(

            image_path,

            class_list

        )


        # ==================================
        # SAVE INITIAL YOLO LABELS
        # ==================================

        label_path = save_yolo_labels(

            result,

            image_path,

            class_list

        )


        print(

            "Label Saved:",

            label_path

        )


        # ==================================
        # CONVERT DETECTIONS TO JSON
        # ==================================

        detections = results_to_json(
            result
        )


        # ==================================
        # CREATE STATIC IMAGE URL
        # ==================================

        output_filename = os.path.basename(
            output_path
        )


        output_image = url_for(

            "static",

            filename=
                f"outputs/{output_filename}"

        )


        print(

            "Output Image URL:",

            output_image

        )


        # ==================================
        # STORE IMAGE DATA
        # ==================================

        batch_images.append({

            "filename":
                filename,

            "output_image":
                output_image,

            "detections":
                detections,

            "edited_annotations":
                None,

            "ai_fresh": True

        })


        print(

            "Detections:",

            len(detections)

        )


    # ======================================
    # CHECK BATCH
    # ======================================

    if not batch_images:

        return (
            "No valid images were processed."
        )


    # ======================================
    # OPEN FIRST IMAGE
    # ======================================

    current_image_index = 0


    first_image = batch_images[
        0
    ]


    print(
        "\n"
        "========================================"
    )

    print(
        "BATCH ANNOTATION COMPLETE"
    )

    print(

        "Total Images:",

        len(batch_images)

    )

    print(
        "========================================"
        "\n"
    )


    # ======================================
    # REDIRECT TO FIRST IMAGE
    # ======================================

    from flask import redirect
    return redirect(url_for("show_image", index=0))


# ==========================================
# OPEN IMAGE FROM BATCH
# ==========================================

@app.route(
    "/image/<int:index>"
)
def show_image(index):

    global batch_images
    global current_image_index


    # ======================================
    # CHECK BATCH
    # ======================================

    if not batch_images:

        return (

            "No batch images found. "
            "Please upload images again."

        )


    # ======================================
    # VALIDATE INDEX
    # ======================================

    if (

        index < 0

        or

        index >= len(
            batch_images
        )

    ):

        return (
            "Invalid image index."
        )


    # ======================================
    # UPDATE CURRENT IMAGE
    # ======================================

    current_image_index = index


    image_data = batch_images[
        current_image_index
    ]


    detections = image_data[
        "detections"
    ]

    # ======================================
    # LOAD SAVED LABELS IF THEY EXIST
    # ======================================
    
    import os
    import cv2
    from class_manager import load_classes

    image_name = os.path.splitext(os.path.basename(image_data["filename"]))[0]
    label_path = os.path.join("labels", f"{image_name}.txt")

    if os.path.exists(label_path) and not image_data.get("ai_fresh"):
        try:
            permanent_classes = load_classes()
            local_image_path = image_data["output_image"].lstrip("/")
            img = cv2.imread(local_image_path)
            if img is not None:
                img_h, img_w = img.shape[:2]
                saved_detections = []
                with open(label_path, "r") as f:
                    for line in f.readlines():
                        parts = line.strip().split()
                        if len(parts) == 5:
                            class_id = int(parts[0])
                            cx = float(parts[1])
                            cy = float(parts[2])
                            nw = float(parts[3])
                            nh = float(parts[4])
                            
                            class_name = permanent_classes[class_id] if class_id < len(permanent_classes) else "Unknown"
                            
                            w = nw * img_w
                            h = nh * img_h
                            x1 = (cx * img_w) - (w / 2)
                            y1 = (cy * img_h) - (h / 2)
                            x2 = x1 + w
                            y2 = y1 + h
                            
                            saved_detections.append({
                                "class_id": class_id,
                                "class_name": class_name,
                                "confidence": 1.0,
                                "x1": x1,
                                "y1": y1,
                                "x2": x2,
                                "y2": y2
                            })
                        elif len(parts) > 5 and len(parts) % 2 == 1:
                            class_id = int(parts[0])
                            class_name = permanent_classes[class_id] if class_id < len(permanent_classes) else "Unknown"
                            
                            polygon = []
                            min_x = float('inf')
                            min_y = float('inf')
                            max_x = float('-inf')
                            max_y = float('-inf')
                            
                            for i in range(1, len(parts), 2):
                                px = float(parts[i]) * img_w
                                py = float(parts[i+1]) * img_h
                                polygon.append({"x": px, "y": py})
                                
                                if px < min_x: min_x = px
                                if px > max_x: max_x = px
                                if py < min_y: min_y = py
                                if py > max_y: max_y = py
                                
                            saved_detections.append({
                                "class_id": class_id,
                                "class_name": class_name,
                                "confidence": 1.0,
                                "x1": min_x,
                                "y1": min_y,
                                "x2": max_x,
                                "y2": max_y,
                                "polygon": polygon
                            })
                
                # Update local variable passed to template
                detections = saved_detections
                # Update the dictionary so it stays cached
                image_data["detections"] = saved_detections
        except Exception as e:
            print("Error loading saved labels:", e)

    # ======================================
    # COLLECT ALL UNIQUE CLASSES FOR DROPDOWN
    # ======================================
    all_classes = set(load_classes())
    for img_data in batch_images:
        if img_data.get("detections"):
            for det in img_data["detections"]:
                if det.get("class_name"):
                    all_classes.add(det["class_name"])
    
    unique_classes = sorted(list(all_classes))

    # ======================================
    # DISPLAY SELECTED IMAGE
    # ======================================

    return render_template(
        "index.html",
        output_image=image_data["output_image"],
        detections=detections,
        current_filename=image_data["filename"],
        current_index=current_image_index,
        total_images=len(batch_images),
        available_classes=unique_classes
    )


# ==========================================
# BULK RENAME CLASSES ACROSS DATASET
# ==========================================

@app.route("/bulk_rename", methods=["POST"])
def bulk_rename():
    global batch_images
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "No data received."}), 400
        
    old_class = data.get("from_class", "").strip().lower()
    new_class = data.get("to_class", "").strip().lower()
    
    if not old_class or not new_class:
        return jsonify({"status": "error", "message": "Missing class names."}), 400
        
    from class_manager import load_classes, save_classes
    classes = load_classes()
    
    # Create a lower-case map of existing classes
    classes_lower = [c.lower() for c in classes]
    
    if old_class not in classes_lower:
        # If it's not in classes.txt, maybe it's just in memory. Let's just update memory.
        old_id = -1
    else:
        old_id = classes_lower.index(old_class)
    
    new_id = -1
    if old_id != -1:
        if new_class not in classes_lower:
            # Easy case: just rename it in classes.txt
            classes[old_id] = new_class
            save_classes(classes)
            new_id = old_id
        else:
            # Merge case: new class already exists. Find its ID and replace old_id with new_id in all .txt files
            new_id = classes_lower.index(new_class)
            import os
            labels_dir = "labels"
            if os.path.exists(labels_dir):
                for filename in os.listdir(labels_dir):
                    if filename.endswith(".txt"):
                        filepath = os.path.join(labels_dir, filename)
                        with open(filepath, "r") as f:
                            lines = f.readlines()
                        
                        changed = False
                        new_lines = []
                        for line in lines:
                            parts = line.strip().split()
                            if parts and int(parts[0]) == old_id:
                                parts[0] = str(new_id)
                                new_lines.append(" ".join(parts) + "\n")
                                changed = True
                            else:
                                new_lines.append(line)
                                
                        if changed:
                            with open(filepath, "w") as f:
                                f.writelines(new_lines)
                                
    # Now update batch_images in memory
    for image_data in batch_images:
        if image_data.get("detections"):
            for det in image_data["detections"]:
                if det.get("class_name", "").lower() == old_class:
                    det["class_name"] = new_class
                    if new_id != -1:
                        det["class_id"] = new_id
                    
    return jsonify({"status": "success", "message": f"Renamed '{old_class}' to '{new_class}' globally."})


# ==========================================
# SAVE EDITED ANNOTATIONS
# ==========================================

@app.route(
    "/save_labels",
    methods=["POST"]
)
def save_labels():

    global batch_images
    global current_image_index
    global current_classes


    # ======================================
    # CHECK CURRENT BATCH
    # ======================================

    if not batch_images:

        return jsonify({

            "status":
                "error",

            "message":
                "No batch images found."

        }), 400


    # ======================================
    # VALIDATE CURRENT IMAGE INDEX
    # ======================================

    if (

        current_image_index < 0

        or

        current_image_index >= len(
            batch_images
        )

    ):

        return jsonify({

            "status":
                "error",

            "message":
                "Invalid current image."

        }), 400


    # ======================================
    # GET CURRENT IMAGE
    # ======================================

    current_image_data = batch_images[
        current_image_index
    ]


    current_image = current_image_data[
        "filename"
    ]


    # ======================================
    # GET JSON DATA
    # ======================================

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "status":
                "error",

            "message":
                "No annotation data received."

        }), 400


    # ======================================
    # GET ANNOTATIONS
    # ======================================

    annotations = data.get(

        "annotations",

        []

    )


    if not isinstance(
        annotations,
        list
    ):

        return jsonify({

            "status":
                "error",

            "message":
                "Annotations must be a list."

        }), 400


    # ======================================
    # GET IMAGE INFORMATION
    # ======================================

    try:

        image_width = float(

            data.get(
                "image_width",
                0
            )

        )


        image_height = float(

            data.get(
                "image_height",
                0
            )

        )


        scale = float(

            data.get(
                "scale",
                1
            )

        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "status":
                "error",

            "message":
                "Invalid image information."

        }), 400


    # ======================================
    # VALIDATE IMAGE DIMENSIONS
    # ======================================

    if (

        image_width <= 0

        or

        image_height <= 0

    ):

        return jsonify({

            "status":
                "error",

            "message":
                "Invalid image dimensions."

        }), 400


    if scale <= 0:

        return jsonify({

            "status":
                "error",

            "message":
                "Invalid image scale."

        }), 400


    # ======================================
    # COLLECT ANNOTATION CLASSES
    # ======================================

    annotation_classes = []


    for annotation in annotations:


        if not isinstance(
            annotation,
            dict
        ):

            continue


        class_name = annotation.get(
            "class_name"
        )


        if class_name:


            class_name = str(
                class_name
            ).strip()


            if class_name:

                annotation_classes.append(
                    class_name
                )


    # ======================================
    # UPDATE PERMANENT CLASS LIST
    # ======================================

    current_classes = add_classes(
        annotation_classes
    )


    # ======================================
    # SAVE EDITED YOLO LABELS
    # ======================================

    label_path, updated_classes = (

        save_edited_annotations(

            annotations=
                annotations,

            image_filename=
                current_image,

            image_width=
                image_width,

            image_height=
                image_height,

            scale=
                scale,

            class_names=
                current_classes

        )

    )


    current_classes = (
        updated_classes
    )


    # ======================================
    # STORE EDITED ANNOTATIONS
    # ======================================

    batch_images[
        current_image_index
    ]["edited_annotations"] = (
        annotations
    )
    
    batch_images[
        current_image_index
    ]["ai_fresh"] = False


    # ======================================
    # TERMINAL OUTPUT
    # ======================================

    print(

        "\n"
        "========== SAVED YOLO LABELS =========="

    )


    print(

        "Image:",

        current_image

    )


    print(

        "Image Number:",

        current_image_index + 1,

        "/",

        len(batch_images)

    )


    print(

        "Label File:",

        label_path

    )


    print(

        "Total Annotations:",

        len(annotations)

    )


    print(
        "\nPermanent Class Mapping:"
    )


    for index, class_name in enumerate(
        current_classes
    ):

        print(
            f"{index} = {class_name}"
        )


    print(
        "========================================"
        "\n"
    )


    # ======================================
    # RETURN SUCCESS
    # ======================================

    return jsonify({

        "status":
            "success",

        "message":
            "YOLO labels saved successfully.",

        "label_path":
            label_path,

        "current_image":
            current_image,

        "current_index":
            current_image_index,

        "total_images":
            len(batch_images),

        "classes":
            current_classes

    })


# ==========================================
# EXPORT YOLO DATASET
# 80% TRAIN / 20% VALIDATION
# ==========================================

@app.route("/export_dataset")
def export_dataset():

    global batch_images
    global current_classes

    # ======================================
    # CHECK DATASET
    # ======================================

    if not batch_images:

        return (
            "No dataset available to export.",
            400
        )


    # Reload permanent classes
    current_classes = load_classes()


    # ======================================
    # REMOVE OLD EXPORT FOLDER
    # ======================================

    if os.path.exists(EXPORT_FOLDER):

        shutil.rmtree(
            EXPORT_FOLDER
        )


    # ======================================
    # CREATE YOLO FOLDER STRUCTURE
    # ======================================

    images_folder = os.path.join(
        EXPORT_FOLDER,
        "images"
    )

    labels_folder = os.path.join(
        EXPORT_FOLDER,
        "labels"
    )

    # Create all folders
    for folder in [
        images_folder,
        labels_folder
    ]:
        os.makedirs(
            folder,
            exist_ok=True
        )


    # ======================================
    # PREPARE IMAGE LIST
    # ======================================

    dataset_images = batch_images.copy()
    total_images = len(dataset_images)


    # ======================================
    # FUNCTION TO COPY IMAGE + LABEL
    # ======================================

    def copy_dataset_items(
        image_list,
        destination_images,
        destination_labels
    ):

        copied_images = 0
        copied_labels = 0


        for image_data in image_list:


            filename = image_data[
                "filename"
            ]


            # ==================================
            # COPY IMAGE
            # ==================================

            source_image = os.path.join(
                UPLOAD_FOLDER,
                filename
            )


            destination_image = os.path.join(
                destination_images,
                filename
            )


            if os.path.exists(
                source_image
            ):

                shutil.copy2(
                    source_image,
                    destination_image
                )

                copied_images += 1


            # ==================================
            # FIND LABEL
            # ==================================

            image_name = os.path.splitext(
                filename
            )[0]


            label_filename = (
                image_name +
                ".txt"
            )


            source_label = os.path.join(
                LABEL_FOLDER,
                label_filename
            )


            destination_label = os.path.join(
                destination_labels,
                label_filename
            )


            # ==================================
            # COPY LABEL
            # ==================================

            if os.path.exists(
                source_label
            ):

                shutil.copy2(
                    source_label,
                    destination_label
                )

                copied_labels += 1


            else:

                # Empty label means
                # image contains no objects

                open(
                    destination_label,
                    "w",
                    encoding="utf-8"
                ).close()


        return (
            copied_images,
            copied_labels
        )


    # ======================================
    # COPY ALL DATA
    # ======================================

    image_count, label_count = (
        copy_dataset_items(
            dataset_images,
            images_folder,
            labels_folder
        )
    )


    # ======================================
    # CREATE classes.txt
    # ======================================

    classes_path = os.path.join(
        EXPORT_FOLDER,
        "classes.txt"
    )


    with open(
        classes_path,
        "w",
        encoding="utf-8"
    ) as file:


        for class_name in current_classes:

            file.write(
                class_name +
                "\n"
            )


    # ======================================
    # CREATE data.yaml
    # ======================================

    yaml_path = os.path.join(
        EXPORT_FOLDER,
        "data.yaml"
    )


    with open(
        yaml_path,
        "w",
        encoding="utf-8"
    ) as file:


        file.write(
            "path: .\n"
        )


        file.write(
            "train: images\n"
        )


        file.write(
            "val: images\n\n"
        )


        file.write(
            "names:\n"
        )


        for class_id, class_name in enumerate(
            current_classes
        ):


            safe_class_name = (
                class_name.replace(
                    "'",
                    "''"
                )
            )


            file.write(

                f"  {class_id}: "
                f"'{safe_class_name}'\n"

            )


    # ======================================
    # REMOVE OLD ZIP
    # ======================================

    zip_filename = (
        EXPORT_FOLDER +
        ".zip"
    )


    if os.path.exists(
        zip_filename
    ):

        os.remove(
            zip_filename
        )


    # ======================================
    # CREATE ZIP
    # ======================================

    zip_path = shutil.make_archive(

        EXPORT_FOLDER,

        "zip",

        EXPORT_FOLDER

    )


    # ======================================
    # TERMINAL OUTPUT
    # ======================================

    print(
        "\n"
        "========== DATASET EXPORTED =========="
    )


    print(
        "Total Images:",
        total_images
    )


    print(
        "Copied Images:",
        image_count
    )


    print(
        "Copied Labels:",
        label_count
    )


    print(
        "Classes:",
        len(current_classes)
    )


    print(
        "ZIP:",
        zip_path
    )


    print(
        "======================================\n"
    )


    # ======================================
    # SEND ZIP TO BROWSER
    # ======================================

    return send_file(

        os.path.abspath(
            zip_path
        ),

        as_attachment=True,

        download_name=
            "yolo_dataset.zip"

    )

# ==========================================
# RESET WORKSPACE
# ==========================================

@app.route("/reset_workspace", methods=["POST"])
def reset_workspace():
    global batch_images
    global current_image_index
    global current_classes
    
    import shutil
    import os

    # Folders to clear
    folders_to_clear = ["uploads", "static/outputs", "labels", "yolo_dataset"]
    
    for folder in folders_to_clear:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")
            
            # If it's the yolo_dataset folder, we can delete the folder itself
            if folder == "yolo_dataset":
                try:
                    os.rmdir(folder)
                except:
                    pass
                    
    # Delete specific files
    files_to_delete = ["classes.txt", "yolo_dataset.zip"]
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass
            
    # Reset globals
    batch_images = []
    current_image_index = 0
    current_classes = []
    
    return jsonify({"status": "success"})


# ==========================================
# DATASET PROGRESS
# ==========================================

@app.route("/progress")
def dataset_progress():

    global batch_images

    total_images = len(batch_images)

    reviewed_images = 0

    # Count images that have been saved/reviewed
    for image_data in batch_images:

        if image_data.get(
            "edited_annotations"
        ) is not None:

            reviewed_images += 1

    remaining_images = (
        total_images - reviewed_images
    )

    if total_images > 0:

        progress_percentage = round(
            (
                reviewed_images
                / total_images
            ) * 100
        )

    else:

        progress_percentage = 0


    # Debug output
    print(
        "Dataset Progress:",
        reviewed_images,
        "/",
        total_images
    )


    return jsonify({

        "total":
            total_images,

        "reviewed":
            reviewed_images,

        "remaining":
            remaining_images,

        "percentage":
            progress_percentage

    })

if __name__ == "__main__":
    print("Starting AI Auto Annotation Tool...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )