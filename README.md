# Visual Measurement App

A Python application for capturing photos, performing edge detection analysis, and detecting primitive geometric shapes using OpenCV and Tkinter.

## Features

- **Camera Integration**: Access your default camera for live preview and photo capture
- **Photo Capture Workflow**: Capture → Accept/Retake → Process workflow
- **Canny Edge Detection**: Adjustable parameters for edge detection analysis
- **Primitive Shape Detection**: Automatically detect lines, polygons, circles, and ellipses
- **Vector Data Export**: Export detected shapes as structured JSON data
- **Image File Support**: Load existing images from your computer
- **Save Functionality**: Save processed images and shape data to disk
- **Real-time Parameter Adjustment**: Adjust detection parameters with live preview

## Shape Detection Capabilities

### Supported Primitive Shapes:
- **Lines**: Using Hough Line Transform with probabilistic detection
- **Circles**: Using Hough Circle Transform with adjustable sensitivity
- **Polygons**: Triangles, quadrilaterals, pentagons, hexagons, etc.
- **Ellipses**: Fitted ellipses with eccentricity calculation (complete closed curves only)
- **Arcs**: Partial circles and elliptical arcs with start/end angles and arc length

### Vectorization Methods:
- **Contour Detection**: Finds connected edge components
- **Arc vs Closed Curve Analysis**: Distinguishes between partial arcs and complete shapes
- **Polygonal Approximation**: Douglas-Peucker algorithm for shape simplification
- **Hough Transforms**: Robust detection of lines and circles
- **Ellipse Fitting**: Least squares fitting for elliptical shapes (closed curves only)
- **Arc Fitting**: Least squares circle fitting for partial curves with angle calculation

## Requirements

- Python 3.7 or higher
- OpenCV (opencv-python)
- Pillow (PIL)
- NumPy
- Tkinter (usually included with Python)

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required packages:
   ```bash
   pip install opencv-python pillow numpy
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. **Using the Camera:**
   - Click "📷 Capture Photo" to take a picture
   - Choose "✓ Accept Photo" or "🔄 Retake Photo"
   - Once accepted, click "🔍 Apply Canny Edge Detection" to process

3. **Loading Image Files:**
   - Click "📁 Load Image File" to load an existing image
   - The image will be automatically set up for processing

5. **Detecting Shapes:**
   - After edge detection, click "🔺 Detect Primitive Shapes"
   - Adjust shape detection parameters as needed
   - View detected shapes overlaid on the original image

6. **Adjusting Parameters:**
   - Use the Low Threshold and High Threshold sliders to adjust edge detection sensitivity
   - Use shape detection sliders for line threshold, circle threshold, minimum area, and polygon epsilon
   - Enable "Apply Gaussian Blur" for noise reduction
   - Enable "Auto-update on parameter change" for real-time processing

7. **Saving and Exporting:**
   - Click "💾 Save Processed Image" to save the edge-detected image
   - Click "� Export Shape Data" to save detected shapes as JSON
   - Click "�🖼️ View Original" or "🔍 View Edge Detection" to toggle between views

## Controls

### Image Capture & Processing:
- **📷 Capture Photo**: Take a photo using the camera
- **✓ Accept Photo**: Accept the captured photo for processing
- **🔄 Retake Photo**: Discard current photo and capture a new one
- **🔍 Apply Canny Edge Detection**: Process the image with edge detection
- **📁 Load Image File**: Load an image from your computer

### Shape Detection:
- **� Detect Primitive Shapes**: Analyze edges and detect geometric shapes
- **🖼️ View Original**: Switch to original image view
- **🔍 View Edge Detection**: Switch to edge detection view
- **📊 Export Shape Data**: Save detected shapes as JSON data
- **💾 Save Processed Image**: Save the processed image to disk

## Parameters

### Canny Edge Detection:
- **Low Threshold**: Lower values detect more edges (including weak ones)
- **High Threshold**: Higher values detect only strong edges
- **Gaussian Blur**: Reduces noise before edge detection
- **Auto-update**: Automatically reprocess when parameters change

### Shape Detection:
- **Line Threshold**: Sensitivity for line detection (Hough transform votes)
- **Circle Threshold**: Sensitivity for circle detection (accumulator threshold)
- **Min Area**: Minimum contour area to consider for polygon detection
- **Poly Epsilon**: Approximation accuracy for polygon simplification (Douglas-Peucker)

## Technical Notes

- The application uses OpenCV for camera access and image processing
- Tkinter provides the GUI framework
- Images are automatically resized for display while preserving the original resolution for processing
- The app handles camera unavailability gracefully by allowing file-based operation

## Troubleshooting

- **Camera not working**: The app will display a warning and allow you to use image files instead
- **No edges detected**: Try adjusting the threshold values or enabling Gaussian blur
- **Performance issues**: The app runs at ~30 FPS for camera preview; disable auto-update for better performance when adjusting parameters

## Data Export Format

The shape detection exports data in JSON format containing:

```json
{
  "image_info": {
    "width": 800,
    "height": 600,
    "channels": 3
  },
  "detection_parameters": {
    "canny_low": 50,
    "canny_high": 150,
    "line_threshold": 50,
    "circle_threshold": 30,
    "min_area": 100,
    "poly_epsilon": 0.02
  },
  "shapes": [
    {
      "type": "line",
      "points": [[x1, y1], [x2, y2]],
      "length": 150.5,
      "angle": 45.0,
      "center": [x, y]
    },
    {
      "type": "circle",
      "center": [x, y],
      "radius": 50,
      "area": 7853.98,
      "circumference": 314.16
    },
    {
      "type": "polygon",
      "shape": "triangle",
      "vertices": 3,
      "points": [[x1,y1], [x2,y2], [x3,y3]],
      "area": 1000.0,
      "perimeter": 150.0,
      "center": [x, y],
      "solidity": 0.95
    },
    {
      "type": "ellipse",
      "center": [x, y],
      "axes": [major_axis, minor_axis],
      "angle": 30.0,
      "area": 5000.0,
      "eccentricity": 0.6
    },
    {
      "type": "arc",
      "center": [x, y],
      "radius": 45.5,
      "start_angle": 30.0,
      "end_angle": 150.0,
      "arc_length": 95.2,
      "start_point": [x1, y1],
      "end_point": [x2, y2],
      "chord_length": 78.5
    }
  ],
  "summary": {
    "total_shapes": 5,
    "lines": 1,
    "circles": 1,
    "polygons": 1,
    "ellipses": 1,
    "arcs": 1
  }
}
```

## Testing

A test image (`test_shapes.png`) is automatically created with various geometric shapes for testing the detection algorithms. You can create your own test image by running:

```bash
python create_test_image.py
```

## Future Enhancements

This app provides a foundation for measurement tools. Current vectorization enables:
- **Distance measurement calibration** using detected lines
- **Area calculations** from detected polygons and circles
- **Angular measurements** from line intersections
- **Regression model training** using the exported vector data
- **Shape fitting algorithms** (RANSAC, least squares)
- **Measurement annotation tools**
- **3D reconstruction** from multiple views
