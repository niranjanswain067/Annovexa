from ultralytics import YOLO
import cv2
import os
import shutil

# Load model once when the application starts
model = YOLO("models/yolov8s-world.pt")


def detect_objects(image_path, class_names):
    """
    image_path : path of uploaded image
    class_names : list like ['bottle','chair','table']
    """

    # Tell YOLO-World which objects to detect
    model.set_classes(class_names)

    # Run inference on CPU
    results = model.predict(
        source=image_path,
        conf=0.25,
        device="cpu",
        verbose=False
    )

    result = results[0]

    output_path = os.path.join("static", "outputs", os.path.basename(image_path))

    annotated = result.plot()

    shutil.copy(image_path, output_path)

    return output_path, result