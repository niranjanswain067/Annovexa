// ==========================================
// GLOBAL VARIABLES
// ==========================================

let addMode = false;

let imageScale = 1;
let originalImageWidth = 0;
let originalImageHeight = 0;

let startX = 0;
let startY = 0;

let tempRect = null;

// Track whether user has changed annotations
let hasUnsavedChanges = false;

// Prevent initial YOLO boxes from being
// counted as user changes
let canvasLoadingComplete = false;


// ==========================================
// CREATE FABRIC CANVAS
// ==========================================

const canvas = new fabric.Canvas("canvas", {
    selection: true
});

const imgElement =
    document.getElementById("sourceImage");


// ==========================================
// LOAD IMAGE
// ==========================================

fabric.Image.fromURL(
    imgElement.src,
    function (img) {

        // Save original image dimensions
        originalImageWidth = img.width;
        originalImageHeight = img.height;


        // Calculate scale
        imageScale = Math.min(
            canvas.width / img.width,
            canvas.height / img.height
        );

        const scale = imageScale;


        // Scale background image
        img.scale(scale);


        // Set image as canvas background
        canvas.setBackgroundImage(
            img,
            canvas.renderAll.bind(canvas),
            {
                originX: "left",
                originY: "top"
            }
        );


        // ==================================
        // CREATE YOLO DETECTION BOXES
        // ==================================

        detections.forEach(det => {

            const rect =
                new fabric.Rect({

                    left:
                        det.x1 * scale,

                    top:
                        det.y1 * scale,

                    width:
                        (det.x2 - det.x1)
                        * scale,

                    height:
                        (det.y2 - det.y1)
                        * scale,

                    fill:
                        "rgba(255, 0, 0, 0.05)",

                    stroke:
                        "red",

                    strokeWidth:
                        2,

                    cornerColor:
                        "blue",

                    transparentCorners:
                        false,

                    hasRotatingPoint:
                        false,

                    lockRotation:
                        true,

                    objectCaching:
                        false

                });


            // Store annotation information
            rect.className =
                det.class_name;

            rect.confidence =
                det.confidence;


            // Add annotation
            canvas.add(rect);

        });


        canvas.renderAll();


        // ==================================
        // INITIAL LOADING FINISHED
        // ==================================

        // Initial YOLO boxes should not
        // count as unsaved changes.

        canvasLoadingComplete = true;

        hasUnsavedChanges = false;

    }
);


// ==========================================
// DELETE SELECTED BOX
// ==========================================

document
.getElementById("deleteBox")
.onclick = function () {

    const obj =
        canvas.getActiveObject();


    if (!obj) {

        alert(
            "Please select an annotation."
        );

        return;

    }


    canvas.remove(obj);

    canvas.discardActiveObject();

    canvas.renderAll();


    // Mark as changed
    hasUnsavedChanges = true;

};


// ==========================================
// ADD BOX BUTTON
// ==========================================

document
.getElementById("addBoxBtn")
.onclick = function () {

    addMode = true;

    // Prevent selecting existing boxes
    canvas.selection = false;

    canvas.discardActiveObject();

    canvas.defaultCursor =
        "crosshair";

    canvas.renderAll();

};


// ==========================================
// MOUSE DOWN
// START DRAWING NEW BOX
// ==========================================

canvas.on(
    "mouse:down",
    function (opt) {

        if (!addMode) {
            return;
        }


        const pointer =
            canvas.getPointer(opt.e);


        startX = pointer.x;
        startY = pointer.y;


        tempRect =
            new fabric.Rect({

                left:
                    startX,

                top:
                    startY,

                width:
                    0,

                height:
                    0,

                fill:
                    "rgba(0, 255, 0, 0.10)",

                stroke:
                    "green",

                strokeWidth:
                    2,

                selectable:
                    false,

                evented:
                    false

            });


        canvas.add(
            tempRect
        );

    }
);


// ==========================================
// MOUSE MOVE
// DRAW NEW BOX
// ==========================================

canvas.on(
    "mouse:move",
    function (opt) {

        if (
            !addMode ||
            !tempRect
        ) {
            return;
        }


        const pointer =
            canvas.getPointer(opt.e);


        // Support drawing
        // in any direction

        const left =
            Math.min(
                startX,
                pointer.x
            );

        const top =
            Math.min(
                startY,
                pointer.y
            );

        const width =
            Math.abs(
                pointer.x -
                startX
            );

        const height =
            Math.abs(
                pointer.y -
                startY
            );


        tempRect.set({

            left:
                left,

            top:
                top,

            width:
                width,

            height:
                height

        });


        canvas.renderAll();

    }
);


// ==========================================
// MOUSE UP
// FINISH NEW BOX
// ==========================================

canvas.on(
    "mouse:up",
    function () {

        if (
            !addMode ||
            !tempRect
        ) {
            return;
        }


        // Prevent very small boxes
        if (
            tempRect.width < 5 ||
            tempRect.height < 5
        ) {

            canvas.remove(
                tempRect
            );

            tempRect = null;

            addMode = false;

            canvas.selection =
                true;

            canvas.defaultCursor =
                "default";

            canvas.renderAll();

            return;

        }


        // Ask for class name
        const className =
            prompt(
                "Enter Class Name:"
            );


        if (
            className &&
            className.trim() !== ""
        ) {

            tempRect.set({

                selectable:
                    true,

                evented:
                    true,

                stroke:
                    "red",

                fill:
                    "rgba(255, 0, 0, 0.05)",

                cornerColor:
                    "blue",

                transparentCorners:
                    false,

                lockRotation:
                    true,

                objectCaching:
                    false

            });


            tempRect.className =
                className.trim();


            // Manual annotation
            // has no confidence
            tempRect.confidence =
                null;


            canvas.setActiveObject(
                tempRect
            );


            // User added a real box
            hasUnsavedChanges =
                true;

        }

        else {

            // User cancelled
            canvas.remove(
                tempRect
            );

        }


        // Reset drawing mode
        tempRect = null;

        addMode = false;

        canvas.selection =
            true;

        canvas.defaultCursor =
            "default";

        canvas.renderAll();

    }
);


// ==========================================
// EDIT CLASS
// ==========================================

document
.getElementById("editClassBtn")
.onclick = function () {

    const obj =
        canvas.getActiveObject();


    if (
        !obj ||
        obj.type !== "rect" ||
        !obj.className
    ) {

        alert(
            "Please select a bounding box first."
        );

        return;

    }


    const newClassName =
        prompt(
            "Edit Class Name:",
            obj.className
        );


    // User cancelled
    if (
        newClassName === null
    ) {
        return;
    }


    const cleanedClassName =
        newClassName.trim();


    if (
        cleanedClassName === ""
    ) {

        alert(
            "Class name cannot be empty."
        );

        return;

    }


    // Don't mark as changed if
    // class name is exactly the same
    if (
        cleanedClassName ===
        obj.className
    ) {

        return;

    }


    // Update class
    obj.className =
        cleanedClassName;


    // Remove old AI confidence
    obj.confidence =
        null;


    // Mark unsaved
    hasUnsavedChanges =
        true;


    canvas.renderAll();

};


// ==========================================
// COLLECT ANNOTATIONS
// ==========================================

function collectAnnotationData() {

    const annotations = [];


    canvas
    .getObjects()
    .forEach(obj => {


        // Annotation rectangles
        if (
            obj.type === "rect" &&
            obj.className
        ) {

            annotations.push({

                class_name:
                    obj.className,

                left:
                    obj.left,

                top:
                    obj.top,

                width:
                    obj.width *
                    obj.scaleX,

                height:
                    obj.height *
                    obj.scaleY

            });

        }

    });


    return {

        annotations:
            annotations,

        image_width:
            originalImageWidth,

        image_height:
            originalImageHeight,

        scale:
            imageScale

    };

}


// ==========================================
// SAVE LABELS FUNCTION
// ==========================================

function saveLabels(
    goToNext = false
) {

    const data =
        collectAnnotationData();


    console.log(
        "Saving:",
        data
    );


    fetch(
        "/save_labels",
        {

            method:
                "POST",

            headers: {

                "Content-Type":
                    "application/json"

            },

            body:
                JSON.stringify(data)

        }
    )

    .then(response => {

        if (!response.ok) {

            throw new Error(
                "Failed to save labels."
            );

        }

        return response.json();

    })

    .then(data => {


        // ==================================
        // CHECK SAVE STATUS
        // ==================================

        if (
            data.status !==
            "success"
        ) {

            alert(
                data.message ||
                "Error saving labels."
            );

            return;

        }


        console.log(
            "Labels Saved:",
            data
        );


        // ==================================
        // MARK AS SAVED
        // ==================================

        hasUnsavedChanges = false;
        loadDatasetProgress();
        loadAnnotationStatistics();


        // ==================================
        // SAVE & NEXT
        // ==================================

        if (goToNext) {

            const currentIndex =
                data.current_index;

            const totalImages =
                data.total_images;


            if (
                currentIndex <
                totalImages - 1
            ) {

                const nextIndex =
                    currentIndex + 1;


                // Navigate after saving
                window.location.href =
                    "/image/" +
                    nextIndex;

            }

            else {

                alert(
                    "All images have been reviewed!"
                );

            }

        }


        // ==================================
        // NORMAL SAVE
        // ==================================

        else {

            alert(
                "YOLO Labels Saved Successfully!"
            );

        }

    })

    .catch(error => {

        console.error(
            "Save Error:",
            error
        );

        alert(
            "Failed to save labels."
        );

    });

}


// ==========================================
// SAVE LABELS BUTTON
// ==========================================

const saveLabelsBtn =
    document.getElementById(
        "saveLabels"
    );


if (saveLabelsBtn) {

    saveLabelsBtn.onclick =
        function () {

            saveLabels(
                false
            );

        };

}


// ==========================================
// SAVE & NEXT BUTTON
// ==========================================

const saveAndNextBtn =
    document.getElementById(
        "saveAndNextBtn"
    );


if (saveAndNextBtn) {

    saveAndNextBtn.onclick =
        function () {

            saveLabels(
                true
            );

        };

}


// ==========================================
// DRAW CLASS LABELS ABOVE BOXES
// ==========================================

canvas.on(
    "after:render",
    function () {

        const ctx =
            canvas.getContext();


        canvas
        .getObjects()
        .forEach(obj => {


            // Only annotation rectangles
            if (
                obj.type !== "rect" ||
                !obj.className
            ) {
                return;
            }


            // Get transformed coordinates
            // so label follows moved boxes
            const boundingRect =
                obj.getBoundingRect();


            const left =
                boundingRect.left;

            const top =
                boundingRect.top;


            // Class label
            let label =
                obj.className;


            // Add AI confidence
            if (
                obj.confidence !== null &&
                obj.confidence !== undefined
            ) {

                label +=
                    " " +
                    Number(
                        obj.confidence
                    ).toFixed(2);

            }


            ctx.font =
                "14px Arial";


            const textWidth =
                ctx.measureText(
                    label
                ).width;


            const padding =
                5;

            const labelHeight =
                22;


            let labelTop =
                top -
                labelHeight;


            if (
                labelTop < 0
            ) {

                labelTop =
                    top;

            }


            // Background
            ctx.fillStyle =
                "red";


            ctx.fillRect(

                left,

                labelTop,

                textWidth +
                padding * 2,

                labelHeight

            );


            // Text
            ctx.fillStyle =
                "white";


            ctx.fillText(

                label,

                left +
                padding,

                labelTop +
                16

            );

        });

    }
);


// ==========================================
// TRACK BOX MOVEMENT / RESIZING
// ==========================================

canvas.on(
    "object:modified",
    function (event) {

        const obj =
            event.target;


        if (
            canvasLoadingComplete &&
            obj &&
            obj.className
        ) {

            hasUnsavedChanges =
                true;

        }

    }
);


// ==========================================
// TRACK ADDED BOXES
// ==========================================

canvas.on(
    "object:added",
    function (event) {

        const obj =
            event.target;


        // Only count completed
        // annotation boxes.
        //
        // Ignore initial YOLO loading
        // and temporary drawing boxes.

        if (
            canvasLoadingComplete &&
            obj &&
            obj.className
        ) {

            hasUnsavedChanges =
                true;

        }

    }
);


// ==========================================
// TRACK REMOVED BOXES
// ==========================================

canvas.on(
    "object:removed",
    function (event) {

        const obj =
            event.target;


        // Only real annotation boxes
        // count as changes.
        //
        // This prevents cancelled
        // temporary boxes from triggering
        // an unnecessary warning.

        if (
            canvasLoadingComplete &&
            obj &&
            obj.className
        ) {

            hasUnsavedChanges =
                true;

        }

    }
);


// ==========================================
// WARN BEFORE LEAVING PAGE
// ==========================================

window.addEventListener(
    "beforeunload",
    function (event) {

        if (
            hasUnsavedChanges
        ) {

            event.preventDefault();

            // Required by browsers
            // for the standard warning
            event.returnValue = "";

        }

    }
);

// ==========================================
// LOAD DATASET PROGRESS
// ==========================================

function loadDatasetProgress() {

    fetch("/progress")

    .then(response => response.json())

    .then(data => {

        document.getElementById(
            "totalImages"
        ).textContent = data.total;

        document.getElementById(
            "reviewedImages"
        ).textContent = data.reviewed;

        document.getElementById(
            "remainingImages"
        ).textContent = data.remaining;

        document.getElementById(
            "progressPercentage"
        ).textContent =
            data.percentage + "%";

        document.getElementById(
            "progressBarFill"
        ).style.width =
            data.percentage + "%";

    })

    .catch(error => {

        console.error(
            "Progress Error:",
            error
        );

    });

}


// ==========================================
// LOAD ANNOTATION STATISTICS
// ==========================================

function loadAnnotationStatistics() {

    fetch("/annotation_stats")

    .then(response => response.json())

    .then(data => {

        if (data.status !== "success") {
            return;
        }


        const container =
            document.getElementById(
                "classStatistics"
            );


        const totalElement =
            document.getElementById(
                "totalAnnotations"
            );


        if (
            !container ||
            !totalElement
        ) {
            return;
        }


        // Clear old statistics
        container.innerHTML = "";


        // Display every class
        Object.entries(
            data.class_counts
        ).forEach(
            ([className, count]) => {

                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "stat-item";


                item.innerHTML = `

                    <span>
                        ${className}
                    </span>

                    <strong>
                        ${count}
                    </strong>

                `;


                container.appendChild(
                    item
                );

            }
        );


        // Total annotations
        totalElement.textContent =
            data.total_annotations;

    })

    .catch(error => {

        console.error(
            "Statistics Error:",
            error
        );

    });

}

// Load dashboard when page opens
loadDatasetProgress();
loadAnnotationStatistics();
