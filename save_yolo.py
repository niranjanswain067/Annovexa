import os

from class_manager import add_classes, load_classes


def save_yolo_labels(
    project_name,
    result,
    image_path,
    detection_classes
):

    """
    Save YOLO-World detection results using
    permanent class IDs from classes.txt.

    Parameters:
        result:
            YOLO-World detection result.

        image_path:
            Path of the detected image.

        detection_classes:
            Classes given to YOLO-World for detection.
            Example:
            ["vase", "table", "flower"]
    """

    # ==========================================
    # CREATE LABELS FOLDER
    # ==========================================

    labels_dir = os.path.join("projects", project_name, "labels")
    os.makedirs(
        labels_dir,
        exist_ok=True
    )

    # ==========================================
    # GET IMAGE NAME
    # ==========================================

    image_name = os.path.splitext(
        os.path.basename(image_path)
    )[0]


    # ==========================================
    # CREATE LABEL FILE PATH
    # ==========================================

    label_path = os.path.join(
        labels_dir,
        image_name + ".txt"
    )


    # ==========================================
    # ADD DETECTION CLASSES TO PERMANENT LIST
    # ==========================================

    add_classes(
        project_name,
        detection_classes
    )


    # Load permanent classes
    permanent_classes = load_classes(project_name)


    # ==========================================
    # GET DETECTED BOXES & MASKS
    # ==========================================

    boxes = result.boxes
    
    if hasattr(result, "masks") and result.masks is not None:
        masks = result.masks.xyn
    else:
        masks = [None] * len(boxes)


    # ==========================================
    # SAVE YOLO LABELS
    # ==========================================

    with open(
        label_path,
        "w",
        encoding="utf-8"
    ) as file:

        for box, mask in zip(boxes, masks):

            # ----------------------------------
            # Get YOLO-Seg COCO class ID
            # ----------------------------------

            coco_class_id = int(
                box.cls.item()
            )


            # ----------------------------------
            # Convert COCO ID to class name
            # ----------------------------------
            
            if coco_class_id not in result.names:
                continue

            class_name = result.names[coco_class_id]


            # ----------------------------------
            # Get permanent class ID
            # ----------------------------------

            if class_name not in permanent_classes:

                print(
                    "Warning: Class not found:",
                    class_name
                )

                continue


            permanent_class_id = (
                permanent_classes.index(
                    class_name
                )
            )

            # ----------------------------------
            # Write YOLO annotation (Box Only)
            # ----------------------------------

            x, y, w, h = box.xywhn[0].tolist()
            file.write(
                f"{permanent_class_id} "
                f"{x:.6f} "
                f"{y:.6f} "
                f"{w:.6f} "
                f"{h:.6f}\n"
            )


    print(
        "YOLO labels saved using "
        "permanent class IDs:",
        label_path
    )


    return label_path