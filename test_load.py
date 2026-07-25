import os
import cv2
from class_manager import load_classes

label_path = r"labels\images_-_2026-07-25T131422.717.txt"
output_image = r"static\outputs\images_-_2026-07-25T131422.717.jpg"

try:
    permanent_classes = load_classes()
    print("Classes loaded:", len(permanent_classes))
    img = cv2.imread(output_image)
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
        print("Success:", saved_detections)
    else:
        print("Image is None")
except Exception as e:
    import traceback
    traceback.print_exc()
