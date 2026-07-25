import os
from save_annotations import save_edited_annotations
from class_manager import load_classes, add_classes

# Mocking app.py state
annotations = [
    {"type": "rect", "class_name": "medicine bottle", "left": 100, "top": 100, "width": 200, "height": 200}
]

# Simulate save_labels route
annotation_classes = []
for annotation in annotations:
    class_name = annotation.get("class_name")
    if class_name:
        annotation_classes.append(class_name)

print("Before add_classes, classes.txt has:", load_classes())
current_classes = add_classes(annotation_classes)
print("After add_classes, current_classes is:", current_classes)

# Simulate save_edited_annotations
label_path, updated_classes = save_edited_annotations(
    annotations=annotations,
    image_filename="test_image.jpg",
    image_width=1000,
    image_height=1000,
    scale=0.5,
    class_names=current_classes
)

print("Saved label to:", label_path)
with open(label_path, "r") as f:
    print("Label file contents:")
    print(f.read())
