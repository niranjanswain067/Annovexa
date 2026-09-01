import os

def get_class_file_path(project_name):
    return os.path.join("projects", project_name, "classes.txt")


def load_classes(project_name):

    class_file = get_class_file_path(project_name)
    if not os.path.exists(class_file):
        return []

    with open(
        class_file,
        "r",
        encoding="utf-8"
    ) as file:

        classes = [
            line.strip()
            for line in file
            if line.strip()
        ]

    return classes


def save_classes(project_name, classes):

    class_file = get_class_file_path(project_name)
    os.makedirs(os.path.dirname(class_file), exist_ok=True)

    with open(
        class_file,
        "w",
        encoding="utf-8"
    ) as file:

        for class_name in classes:

            file.write(
                class_name + "\n"
            )


def add_classes(project_name, new_classes):

    classes = load_classes(project_name)

    for class_name in new_classes:

        class_name = class_name.strip()

        if (
            class_name and
            class_name not in classes
        ):

            classes.append(
                class_name
            )

    save_classes(project_name, classes)

    return classes


def get_class_id(project_name, class_name):

    classes = load_classes(project_name)

    if class_name not in classes:

        classes.append(
            class_name
        )

        save_classes(project_name, classes)

    return classes.index(
        class_name
    )