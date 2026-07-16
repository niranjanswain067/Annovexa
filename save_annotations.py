import os


def save_edited_annotations(
    annotations,
    image_filename,
    image_width,
    image_height,
    scale,
    class_names
):
    """
    Convert Fabric.js canvas coordinates to YOLO format
    and save them to a TXT file.
    """

    os.makedirs("labels", exist_ok=True)

    # Remove image extension
    image_name = os.path.splitext(image_filename)[0]

    label_path = os.path.join(
        "labels",
        image_name + ".txt"
    )

    yolo_lines = []

    for annotation in annotations:

        class_name = annotation.get("class_name")

        # Skip annotations without valid classes
        if not class_name:
            continue

        # Create class ID
        if class_name not in class_names:
            class_names.append(class_name)

        class_id = class_names.index(class_name)

        # Fabric canvas coordinates
        left = float(annotation["left"])
        top = float(annotation["top"])
        width = float(annotation["width"])
        height = float(annotation["height"])

        # Convert canvas coordinates back to
        # original image coordinates
        left = left / scale
        top = top / scale
        width = width / scale
        height = height / scale

        # Prevent coordinates from going outside image
        left = max(0, min(left, image_width))
        top = max(0, min(top, image_height))

        width = max(
            0,
            min(width, image_width - left)
        )

        height = max(
            0,
            min(height, image_height - top)
        )

        # Skip invalid boxes
        if width <= 1 or height <= 1:
            continue

        # Convert XYWH to YOLO normalized format
        center_x = (left + width / 2) / image_width
        center_y = (top + height / 2) / image_height

        norm_width = width / image_width
        norm_height = height / image_height

        yolo_lines.append(
            f"{class_id} "
            f"{center_x:.6f} "
            f"{center_y:.6f} "
            f"{norm_width:.6f} "
            f"{norm_height:.6f}"
        )

    # Overwrite old label file
    with open(label_path, "w") as file:

        for line in yolo_lines:
            file.write(line + "\n")

    return label_path, class_names