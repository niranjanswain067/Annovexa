from ultralytics import YOLO
import cv2
import os
import shutil

# Load segmentation model
model = YOLO("models/yolov8s-seg.pt")


def detect_objects(image_path, class_names):
    """
    image_path : path of uploaded image
    class_names : list like ['bottle','chair','table']
    """

    # Find IDs for requested COCO classes
    requested_ids = []
    for cls_name in class_names:
        for idx, name in model.names.items():
            if name.lower() == cls_name.lower():
                requested_ids.append(idx)

    # Run inference on CPU
    # Filter by classes if any valid COCO classes were requested
    if requested_ids:
        results = model.predict(
            source=image_path,
            conf=0.25,
            classes=requested_ids,
            device="cpu",
            verbose=False
        )
    else:
        results = model.predict(
            source=image_path,
            conf=0.25,
            device="cpu",
            verbose=False
        )

    result = results[0]

    output_path = os.path.join("static", "outputs", os.path.basename(image_path))

    # The frontend uses Fabric.js to draw over the clean image
    shutil.copy(image_path, output_path)

    return output_path, result