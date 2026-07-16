import os

CLASS_FILE = "classes.txt"


def load_classes():

    if not os.path.exists(CLASS_FILE):
        return []

    with open(
        CLASS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        classes = [
            line.strip()
            for line in file
            if line.strip()
        ]

    return classes


def save_classes(classes):

    with open(
        CLASS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for class_name in classes:

            file.write(
                class_name + "\n"
            )


def add_classes(new_classes):

    classes = load_classes()

    for class_name in new_classes:

        class_name = class_name.strip()

        if (
            class_name and
            class_name not in classes
        ):

            classes.append(
                class_name
            )

    save_classes(classes)

    return classes


def get_class_id(class_name):

    classes = load_classes()

    if class_name not in classes:

        classes.append(
            class_name
        )

        save_classes(classes)

    return classes.index(
        class_name
    )