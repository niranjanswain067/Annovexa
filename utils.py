def results_to_json(result):

    detections = []

    boxes = result.boxes

    names = result.names

    # Check if masks exist
    if result.masks is not None:
        masks = result.masks.xy
    else:
        masks = [None] * len(boxes)

    for box, mask in zip(boxes, masks):

        x1, y1, x2, y2 = box.xyxy[0].tolist()
        
        polygon = None
        if mask is not None and len(mask) > 0:
            polygon = [{"x": float(pt[0]), "y": float(pt[1])} for pt in mask]

        detections.append({

            "class_id": int(box.cls),

            "class_name": names[int(box.cls)],

            "confidence": float(box.conf),

            "x1": x1,

            "y1": y1,

            "x2": x2,

            "y2": y2,
            
            "polygon": polygon

        })

    return detections