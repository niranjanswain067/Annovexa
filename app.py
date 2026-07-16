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

    return render_template(
        "index.html"
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
                None

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
    # DISPLAY FIRST IMAGE
    # ======================================

    return render_template(

        "index.html",

        output_image=
            first_image[
                "output_image"
            ],

        detections=
            first_image[
                "detections"
            ],

        current_filename=
            first_image[
                "filename"
            ],

        current_index=
            current_image_index,

        total_images=
            len(batch_images)

    )


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


    # ======================================
    # GET DETECTION DATA
    # ======================================

    detections = image_data[
        "detections"
    ]


    # ======================================
    # DISPLAY SELECTED IMAGE
    # ======================================

    return render_template(

        "index.html",

        output_image=
            image_data[
                "output_image"
            ],

        detections=
            detections,

        current_filename=
            image_data[
                "filename"
            ],

        current_index=
            current_image_index,

        total_images=
            len(batch_images)

    )


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

    train_images_folder = os.path.join(
        EXPORT_FOLDER,
        "images",
        "train"
    )

    val_images_folder = os.path.join(
        EXPORT_FOLDER,
        "images",
        "val"
    )

    train_labels_folder = os.path.join(
        EXPORT_FOLDER,
        "labels",
        "train"
    )

    val_labels_folder = os.path.join(
        EXPORT_FOLDER,
        "labels",
        "val"
    )


    # Create all folders
    for folder in [

        train_images_folder,
        val_images_folder,
        train_labels_folder,
        val_labels_folder

    ]:

        os.makedirs(
            folder,
            exist_ok=True
        )


    # ======================================
    # PREPARE IMAGE LIST
    # ======================================

    dataset_images = batch_images.copy()


    # Randomize images before splitting
    random.shuffle(
        dataset_images
    )


    total_images = len(
        dataset_images
    )


    # ======================================
    # CALCULATE 80/20 SPLIT
    # ======================================

    # Special handling for one image
    if total_images == 1:

        train_images = dataset_images

        val_images = []


    else:

        # Calculate 80%
        train_count = int(
            total_images * 0.8
        )


        # Ensure at least one
        # training image
        train_count = max(
            1,
            train_count
        )


        # Ensure at least one
        # validation image
        train_count = min(
            train_count,
            total_images - 1
        )


        train_images = dataset_images[
            :train_count
        ]


        val_images = dataset_images[
            train_count:
        ]


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
    # COPY TRAIN DATA
    # ======================================

    train_image_count, train_label_count = (
        copy_dataset_items(

            train_images,

            train_images_folder,

            train_labels_folder

        )
    )


    # ======================================
    # COPY VALIDATION DATA
    # ======================================

    val_image_count, val_label_count = (
        copy_dataset_items(

            val_images,

            val_images_folder,

            val_labels_folder

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
            "train: images/train\n"
        )


        file.write(
            "val: images/val\n\n"
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
        "Training Images:",
        train_image_count
    )


    print(
        "Training Labels:",
        train_label_count
    )


    print(
        "Validation Images:",
        val_image_count
    )


    print(
        "Validation Labels:",
        val_label_count
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
# ==========================================
# ANNOTATION STATISTICS
# ==========================================

@app.route("/annotation_stats")
def annotation_stats():

    global batch_images
    global current_classes

    # Reload latest permanent classes
    current_classes = load_classes()

    # Create initial count
    class_counts = {
        class_name: 0
        for class_name in current_classes
    }

    total_annotations = 0


    # ======================================
    # CHECK LABELS FOR CURRENT BATCH
    # ======================================

    for image_data in batch_images:

        filename = image_data.get(
            "filename"
        )

        if not filename:
            continue


        # Get label filename
        image_name = os.path.splitext(
            filename
        )[0]

        label_path = os.path.join(
            LABEL_FOLDER,
            image_name + ".txt"
        )


        # Skip if label doesn't exist
        if not os.path.exists(
            label_path
        ):
            continue


        # ==================================
        # READ YOLO LABEL FILE
        # ==================================

        with open(
            label_path,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue


                parts = line.split()

                if len(parts) < 5:
                    continue


                try:

                    class_id = int(
                        parts[0]
                    )

                except ValueError:

                    continue


                # Check valid class ID
                if (
                    0 <= class_id
                    < len(current_classes)
                ):

                    class_name = (
                        current_classes[
                            class_id
                        ]
                    )

                    class_counts[
                        class_name
                    ] += 1

                    total_annotations += 1


    # ======================================
    # RETURN STATISTICS
    # ======================================

    return jsonify({

        "status":
            "success",

        "total_annotations":
            total_annotations,

        "class_counts":
            class_counts

    })
if __name__ == "__main__":
    print("Starting AI Auto Annotation Tool...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )