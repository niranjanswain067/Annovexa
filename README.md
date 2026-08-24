# Annovexa - AI-Powered Computer Vision Annotation Platform

Annovexa is a next-generation AI-powered image and video annotation platform designed to simplify dataset creation for machine learning and computer vision. It combines AI-assisted auto-annotation with an intuitive manual editor, allowing students, researchers, startups, and enterprises to build high-quality datasets significantly faster than manual workflows.

---

## 🚀 Key Features

### Image & Video Processing
- **Image Upload:** Upload single, multiple, or bulk image batches.
- **Video Annotation:** Upload video files (`.mp4`, `.avi`, `.mov`) and automatically extract frames for sequential processing.
- **Batch Processing:** Seamlessly navigate and review large sets of images and video frames.

### AI-Powered Detection (YOLO-World)
- **Dynamic Class Prompting:** Type the objects you want to detect (e.g., "person, car, dog") and YOLO-World will automatically find them.
- **Auto-Bounding Boxes:** Instantly generates bounding boxes and segmentation masks for recognized objects before manual review.

### Interactive Annotation Editor
- **Fabric.js Canvas:** Smooth, interactive, and responsive annotation drawing.
- **Full Editing:** Add, move, resize, and delete bounding boxes and polygons.
- **Bulk Rename:** Intelligently rename classes across the entire dataset globally.

### Dataset Management
- **Dataset Export:** Instantly export your progress as a ready-to-use YOLO dataset with an 80/20 train/validation split (includes `data.yaml`).
- **Dashboard Progress:** Keep track of annotation statistics (total, reviewed, and remaining items) in real-time.

---

## 🏗️ Architecture & Tech Stack

- **Frontend:** HTML, Vanilla CSS, JavaScript, Fabric.js (Canvas UI)
- **Backend:** Flask (Python)
- **AI Engine:** Ultralytics YOLO (`yolov8s-seg.pt`)
- **Computer Vision Utilities:** OpenCV (`cv2`) for video frame extraction.

---

## 📂 Folder Structure

```
Annovexa/
├── app.py                  # Main Flask application and API routing
├── detector.py             # YOLO-World AI detection logic
├── save_annotations.py     # Canvas coordinates to YOLO format translator
├── save_yolo.py            # Automatic label saving script
├── class_manager.py        # Centralized class and ID management
├── utils.py                # Detection to JSON utilities
├── requirements.txt        # Python dependencies
├── templates/              # HTML files (index.html)
├── static/                 # CSS, JavaScript (app.js), and generated output images
├── uploads/                # Local storage for uploaded files and extracted video frames
├── labels/                 # Local storage for generated YOLO .txt label files
└── yolo_dataset/           # Generated ZIP exports for dataset downloads
```

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/niranjanswain067/Annovexa.git
   cd Annovexa
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Annovexa requires PyTorch and OpenCV. Ensure your system supports them).*

4. **Run the Application:**
   ```bash
   python app.py
   ```

5. **Open in Browser:**
   Navigate to `http://localhost:5000` or `http://127.0.0.1:5000`

---

## 📖 Usage Guide

1. **Upload Data:** Drag and drop images or videos into the left-hand sidebar upload zone.
2. **Set Classes:** Type a comma-separated list of the objects you wish to detect (e.g., `car, traffic light, pedestrian`).
3. **Auto-Annotate:** Click **Auto Annotate**. The AI will process your files and extract frames from videos (1 frame/sec).
4. **Review & Edit:** The main workspace will load. Use the tools to add missing boxes, correct mistakes, or delete false positives.
5. **Save & Next:** Click **Save & Next** to lock in the annotations for the current frame/image and proceed to the next one.
6. **Export:** Once the dataset progress shows 100%, click **Download YOLO Dataset** to get your zipped, formatted dataset.

---

## 📝 License
*(Add your license information here)*
