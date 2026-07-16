def results_to_json(result):

    detections = []

    boxes = result.boxes

    names = result.names

    for box in boxes:

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        detections.append({

            "class_id": int(box.cls),

            "class_name": names[int(box.cls)],

            "confidence": float(box.conf),

            "x1": x1,

            "y1": y1,

            "x2": x2,

            "y2": y2

        })

    return detections