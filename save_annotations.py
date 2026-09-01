import os


def save_edited_annotations(
    project_name,
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

    labels_dir = os.path.join("projects", project_name, "labels")
    os.makedirs(labels_dir, exist_ok=True)

    # Remove image extension
    image_name = os.path.splitext(image_filename)[0]

    label_path = os.path.join(
        labels_dir,
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

        # Check type
        anno_type = annotation.get("type", "rect")

        if anno_type == "rect":
            # Fabric canvas coordinates
            left = float(annotation.get("left", 0))
            top = float(annotation.get("top", 0))
            width = float(annotation.get("width", 0))
            height = float(annotation.get("height", 0))

            # Convert canvas coordinates back to original image coordinates
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
        
        elif anno_type == "polygon":
            points = annotation.get("points", [])
            if len(points) < 3:
                continue
            
            norm_points = []
            for p in points:
                x = p["x"] / scale
                y = p["y"] / scale
                
                x = max(0, min(x, image_width))
                y = max(0, min(y, image_height))
                
                norm_x = x / image_width
                norm_y = y / image_height
                
                norm_points.append(f"{norm_x:.6f} {norm_y:.6f}")
                
            points_str = " ".join(norm_points)
            yolo_lines.append(f"{class_id} {points_str}")

    # Overwrite old label file
    with open(label_path, "w") as file:

        for line in yolo_lines:
            file.write(line + "\n")

    return label_path, class_names