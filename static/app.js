// ==========================================
// GLOBAL VARIABLES
// ==========================================

let addMode = false;
let polygonMode = false;

let imageScale = 1;
let originalImageWidth = 0;
let originalImageHeight = 0;

let startX = 0;
let startY = 0;

let tempRect = null;
let polygonPoints = [];
let polygonLines = [];

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

            // 1. Draw Bounding Box
            const rect = new fabric.Rect({
                left: det.x1 * scale,
                top: det.y1 * scale,
                width: (det.x2 - det.x1) * scale,
                height: (det.y2 - det.y1) * scale,
                fill: (det.polygon && det.polygon.length > 0) ? "transparent" : "rgba(255, 0, 0, 0.05)",
                stroke: "green",
                strokeWidth: 2,
                cornerColor: "blue",
                transparentCorners: false,
                lockRotation: true,
                objectCaching: false
            });
            
            rect.className = det.class_name;
            rect.confidence = det.confidence;
            
            if (det.polygon && det.polygon.length > 0) {
                rect.isAuxiliary = true;
            }
            canvas.add(rect);

            // 2. Draw Polygon Mask
            if (det.polygon && det.polygon.length > 0) {
                const scaledPoints = det.polygon.map(p => ({
                    x: p.x * scale,
                    y: p.y * scale
                }));

                const poly = new fabric.Polygon(scaledPoints, {
                    fill: "rgba(255, 165, 0, 0.4)", // orange tint like screenshot
                    stroke: "transparent",
                    cornerColor: "blue",
                    transparentCorners: false,
                    lockRotation: true,
                    objectCaching: false
                });
                poly.className = det.class_name;
                poly.confidence = det.confidence;
                
                // Link polygon and rect together so deleting one deletes the other
                poly.linkedObj = rect;
                rect.linkedObj = poly;
                
                canvas.add(poly);
            }

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

    // If the selected object has a linked polygon/rect, delete it too
    if (obj.linkedObj) {
        canvas.remove(obj.linkedObj);
    }
    
    // Fallback: search canvas for any object linking to this one
    canvas.getObjects().forEach(o => {
        if (o.linkedObj === obj) {
            canvas.remove(o);
        }
    });

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
    polygonMode = false;

    // Prevent selecting existing boxes
    canvas.selection = false;

    canvas.discardActiveObject();

    canvas.defaultCursor =
        "crosshair";

    canvas.renderAll();

};

// ==========================================
// ADD POLYGON BUTTON
// ==========================================

document
.getElementById("addPolygonBtn")
.onclick = function () {

    polygonMode = true;
    addMode = false;

    canvas.selection = false;
    canvas.discardActiveObject();
    canvas.defaultCursor = "crosshair";
    
    // Clear any partial polygon
    polygonPoints = [];
    polygonLines.forEach(item => canvas.remove(item));
    polygonLines = [];

    canvas.renderAll();
};


// ==========================================
// MOUSE DOWN
// START DRAWING NEW BOX
// ==========================================

canvas.on(
    "mouse:down",
    function (opt) {

        if (addMode) {
            const pointer =
                canvas.getPointer(opt.e);

            startX = pointer.x;
            startY = pointer.y;

            tempRect =
                new fabric.Rect({
                    left: startX,
                    top: startY,
                    width: 0,
                    height: 0,
                    fill: "rgba(0, 255, 0, 0.10)",
                    stroke: "green",
                    strokeWidth: 2,
                    selectable: false,
                    evented: false
                });

            canvas.add(tempRect);
        } else if (polygonMode) {
            const pointer = canvas.getPointer(opt.e);
            polygonPoints.push({ x: pointer.x, y: pointer.y });
            
            const circle = new fabric.Circle({
                radius: 3,
                fill: 'red',
                left: pointer.x,
                top: pointer.y,
                originX: 'center',
                originY: 'center',
                selectable: false,
                evented: false
            });
            canvas.add(circle);
            polygonLines.push(circle);
            
            if (polygonPoints.length > 1) {
                const prev = polygonPoints[polygonPoints.length - 2];
                const line = new fabric.Line([prev.x, prev.y, pointer.x, pointer.y], {
                    stroke: 'red',
                    strokeWidth: 2,
                    selectable: false,
                    evented: false
                });
                canvas.add(line);
                polygonLines.push(line);
            }
        }
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
// DOUBLE CLICK
// FINISH NEW POLYGON
// ==========================================

canvas.on('mouse:dblclick', function(opt) {
    if (polygonMode && polygonPoints.length > 2) {
        // Create polygon
        const poly = new fabric.Polygon(polygonPoints, {
            fill: "rgba(255, 0, 0, 0.05)",
            stroke: "red",
            strokeWidth: 2,
            selectable: true,
            evented: true,
            cornerColor: "blue",
            transparentCorners: false,
            lockRotation: true,
            objectCaching: false
        });
        
        // Remove temporary lines and circles
        polygonLines.forEach(item => canvas.remove(item));
        polygonLines = [];
        polygonPoints = [];
        
        canvas.add(poly);
        canvas.setActiveObject(poly);
        
        polygonMode = false;
        canvas.selection = true;
        canvas.defaultCursor = "default";
        canvas.renderAll();
        
        const className = prompt("Enter Class Name:");
        if (className && className.trim() !== "") {
            poly.className = className.trim();
            poly.confidence = null;
            hasUnsavedChanges = true;
        } else {
            canvas.remove(poly);
        }
    }
});


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
        (obj.type !== "rect" && obj.type !== "polygon") ||
        !obj.className
    ) {

        alert(
            "Please select a bounding box or mask first."
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
        
    // Also update linked object if it exists
    if (obj.linkedObj) {
        obj.linkedObj.className = cleanedClassName;
        obj.linkedObj.confidence = null;
    }


    // Mark unsaved
    hasUnsavedChanges =
        true;


    // Redraw canvas with new text
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

        if (obj.isAuxiliary) return;

        // Annotation rectangles
        if (
            obj.type === "rect" &&
            obj.className
        ) {

            annotations.push({
                type: "rect",
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

        } else if (
            obj.type === "polygon" &&
            obj.className
        ) {
            
            const matrix = obj.calcTransformMatrix();
            const absolutePoints = obj.points.map(function(p) {
                return fabric.util.transformPoint({ x: p.x, y: p.y }, matrix);
            });
            
            annotations.push({
                type: "polygon",
                class_name: obj.className,
                points: absolutePoints
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
        "/project/" + PROJECT_NAME + "/save_labels",
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
                    "/project/" + PROJECT_NAME + "/image/" +
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

            // Skip auxiliary objects (like the transparent rect behind a polygon)
            if (obj.isAuxiliary) {
                return;
            }

            // Only annotation rectangles and polygons
            if (
                (obj.type !== "rect" && obj.type !== "polygon") ||
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
                    top +
                    boundingRect.height;

            }


            // Background
            ctx.fillStyle =
                "rgba(0, 128, 0, 0.8)";


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
                15

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

    fetch("/project/" + PROJECT_NAME + "/progress")

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



// Load dashboard when page opens
loadDatasetProgress();


// ==========================================
// BULK RENAME CLASSES
// ==========================================

document.getElementById("bulkRenameBtn")?.addEventListener("click", function() {
    const fromClass = document.getElementById("rename-from").value.trim();
    const toClass = document.getElementById("rename-to").value.trim();
    
    if (!fromClass || !toClass) {
        alert("Please enter both the original and new class names.");
        return;
    }
    
    const btn = document.getElementById("bulkRenameBtn");
    const originalText = btn.innerHTML;
    btn.innerHTML = 'Renaming...';
    btn.disabled = true;

    fetch("/project/" + PROJECT_NAME + "/bulk_rename", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ from_class: fromClass, to_class: toClass })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            hasUnsavedChanges = false;
            window.location.reload();
        } else {
            alert("Error: " + data.message);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    })
    .catch(err => {
        alert("Failed to reach server.");
        console.error(err);
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
});

