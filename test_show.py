from app import app, batch_images
from flask import render_template
import os

with app.app_context():
    # Setup mock data
    batch_images.clear()
    batch_images.append({
        "filename": "download_1.jpeg",
        "output_image": "/static/outputs/download_1.jpeg",
        "detections": [{"class_name": "bottle", "confidence": 0.48, "x1": 0, "y1": 0, "x2": 100, "y2": 100}]
    })
    
    with app.test_request_context('/image/0'):
        # Simulate show_image
        import app as app_module
        app_module.current_image_index = 0
        response = app_module.show_image(0)
        print("Detections inside response:")
        for line in response.split('\n'):
            if 'const detections' in line:
                print(line.strip())
