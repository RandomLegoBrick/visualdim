import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import time
import os

class MeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Measurement App")
        self.root.geometry("900x700")
        
        # Camera and image variables
        self.cap = None
        self.current_frame = None
        self.captured_image = None
        self.processed_image = None
        self.camera_running = False
        self.camera_index = 0
        
        # Shape detection variables
        self.detected_shapes = []
        self.shapes_image = None
        
        # Image display size
        self.display_width = 640
        self.display_height = 480
        
        self.setup_ui()
        self.start_camera()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create menu bar
        self.setup_menu_bar()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Visual Measurement App", 
                               font=("Arial", 18, "bold"), bootstyle="primary")
        title_label.grid(row=0, column=0, pady=(0, 15))
        
        # Camera preview frame
        camera_frame = ttk.LabelFrame(main_frame, text="Camera Preview / Image Display", 
                                     padding=10, bootstyle="info")
        camera_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        camera_frame.columnconfigure(0, weight=1)
        camera_frame.rowconfigure(0, weight=1)
        
        # Camera display label
        self.camera_label = ttk.Label(camera_frame, text="Starting camera...", 
                                     background="black", foreground="white",
                                     font=("Arial", 12))
        self.camera_label.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons frame
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", 
                                       padding=10, bootstyle="secondary")
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # First row of buttons
        buttons_frame1 = ttk.Frame(controls_frame)
        buttons_frame1.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Capture button
        self.capture_btn = ttk.Button(buttons_frame1, text="Capture Photo", 
                                     command=self.capture_photo, state="disabled",
                                     bootstyle="success", width=15)
        self.capture_btn.grid(row=0, column=0, padx=5)
        
        # Accept button
        self.accept_btn = ttk.Button(buttons_frame1, text="✓ Accept Photo", 
                                    command=self.accept_photo, state="disabled",
                                    bootstyle="primary", width=15)
        self.accept_btn.grid(row=0, column=1, padx=5)
        
        # Retake button
        self.retake_btn = ttk.Button(buttons_frame1, text="Retake Photo", 
                                    command=self.retake_photo, state="disabled",
                                    bootstyle="warning", width=15)
        self.retake_btn.grid(row=0, column=2, padx=5)
        
        # Second row of buttons
        buttons_frame2 = ttk.Frame(controls_frame)
        buttons_frame2.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Process button
        self.process_btn = ttk.Button(buttons_frame2, text="Apply Canny Edge Detection", 
                                     command=self.process_image, state="disabled",
                                     bootstyle="info", width=25)
        self.process_btn.grid(row=0, column=0, padx=5)
        
        # Detect shapes button
        self.detect_shapes_btn = ttk.Button(buttons_frame2, text="Detect Primitive Shapes", 
                                           command=self.detect_shapes, state="disabled",
                                           bootstyle="dark", width=25)
        self.detect_shapes_btn.grid(row=0, column=1, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", 
                                     padding=10, bootstyle="light")
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.status_label = ttk.Label(status_frame, text="Starting camera...",
                                     font=("Arial", 10), bootstyle="secondary")
        self.status_label.grid(row=0, column=0)
        
        # Canny parameters frame
        params_frame = ttk.LabelFrame(main_frame, text="Canny Edge Detection Parameters", 
                                     padding=10, bootstyle="warning")
        params_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(3, weight=1)
        
        # Low threshold
        ttk.Label(params_frame, text="Low Threshold:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.low_threshold = tk.IntVar(value=50)
        low_scale = ttk.Scale(params_frame, from_=0, to=255, variable=self.low_threshold, 
                             orient="horizontal", bootstyle="warning")
        low_scale.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.low_label = ttk.Label(params_frame, text="50", width=5, 
                                  bootstyle="inverse-warning")
        self.low_label.grid(row=0, column=2, padx=5)
        
        # High threshold
        ttk.Label(params_frame, text="High Threshold:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, sticky="w")
        self.high_threshold = tk.IntVar(value=150)
        high_scale = ttk.Scale(params_frame, from_=0, to=255, variable=self.high_threshold, 
                              orient="horizontal", bootstyle="warning")
        high_scale.grid(row=0, column=4, padx=5, sticky=(tk.W, tk.E))
        self.high_label = ttk.Label(params_frame, text="150", width=5, 
                                   bootstyle="inverse-warning")
        self.high_label.grid(row=0, column=5, padx=5)
        
        # Additional processing options
        options_frame = ttk.Frame(params_frame)
        options_frame.grid(row=1, column=0, columnspan=6, pady=10, sticky=(tk.W, tk.E))
        
        # Gaussian blur checkbox
        self.use_blur = tk.BooleanVar(value=True)
        blur_check = ttk.Checkbutton(options_frame, text="Apply Gaussian Blur", 
                                   variable=self.use_blur, bootstyle="warning-round-toggle")
        blur_check.grid(row=0, column=0, padx=10)
        
        # Auto-update checkbox
        self.auto_update = tk.BooleanVar(value=False)
        auto_check = ttk.Checkbutton(options_frame, text="Auto-update on parameter change", 
                                   variable=self.auto_update, bootstyle="info-round-toggle")
        auto_check.grid(row=0, column=1, padx=10)
        
        # Bind threshold changes to update labels and auto-process
        self.low_threshold.trace('w', self.on_threshold_change)
        self.high_threshold.trace('w', self.on_threshold_change)
        
        # Shape Detection parameters frame
        shape_params_frame = ttk.LabelFrame(main_frame, text="Shape Detection Parameters", 
                                           padding=10, bootstyle="success")
        shape_params_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        shape_params_frame.columnconfigure(1, weight=1)
        shape_params_frame.columnconfigure(3, weight=1)
        
        # Line detection parameters
        ttk.Label(shape_params_frame, text="Line Threshold:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.line_threshold = tk.IntVar(value=50)
        line_scale = ttk.Scale(shape_params_frame, from_=10, to=200, variable=self.line_threshold, 
                              orient="horizontal", bootstyle="success")
        line_scale.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        self.line_label = ttk.Label(shape_params_frame, text="50", width=5, 
                                   bootstyle="inverse-success")
        self.line_label.grid(row=0, column=2, padx=5)
        
        # Circle detection parameters
        ttk.Label(shape_params_frame, text="Circle Threshold:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, sticky="w")
        self.circle_threshold = tk.IntVar(value=30)
        circle_scale = ttk.Scale(shape_params_frame, from_=10, to=100, variable=self.circle_threshold, 
                                orient="horizontal", bootstyle="success")
        circle_scale.grid(row=0, column=4, padx=5, sticky=(tk.W, tk.E))
        self.circle_label = ttk.Label(shape_params_frame, text="30", width=5, 
                                     bootstyle="inverse-success")
        self.circle_label.grid(row=0, column=5, padx=5)
        
        # Minimum contour area
        ttk.Label(shape_params_frame, text="Min Area:", 
                 font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, sticky="w")
        self.min_area = tk.IntVar(value=100)
        area_scale = ttk.Scale(shape_params_frame, from_=50, to=1000, variable=self.min_area, 
                              orient="horizontal", bootstyle="success")
        area_scale.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E))
        self.area_label = ttk.Label(shape_params_frame, text="100", width=5, 
                                   bootstyle="inverse-success")
        self.area_label.grid(row=1, column=2, padx=5)
        
        # Polygon approximation epsilon
        ttk.Label(shape_params_frame, text="Poly Epsilon:", 
                 font=("Arial", 10, "bold")).grid(row=1, column=3, padx=5, sticky="w")
        self.poly_epsilon = tk.DoubleVar(value=0.02)
        epsilon_scale = ttk.Scale(shape_params_frame, from_=0.01, to=0.1, variable=self.poly_epsilon, 
                                 orient="horizontal", bootstyle="success")
        epsilon_scale.grid(row=1, column=4, padx=5, sticky=(tk.W, tk.E))
        self.epsilon_label = ttk.Label(shape_params_frame, text="0.02", width=5, 
                                      bootstyle="inverse-success")
        self.epsilon_label.grid(row=1, column=5, padx=5)
        
        # Bind shape parameter changes
        self.line_threshold.trace('w', self.on_shape_param_change)
        self.circle_threshold.trace('w', self.on_shape_param_change)
        self.min_area.trace('w', self.on_shape_param_change)
        self.poly_epsilon.trace('w', self.on_shape_param_change)
    
    def setup_menu_bar(self):
        """Setup the menu bar with dropdown menus"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Image File", command=self.load_image_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save Processed Image", command=self.save_processed_image, state="disabled")
        file_menu.add_command(label="Export Shape Data", command=self.export_shapes, state="disabled")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="View Original", command=self.view_original, state="disabled")
        view_menu.add_command(label="View Edge Detection", command=self.view_edges, state="disabled")
        
        # Store menu references for state management
        self.file_menu = file_menu
        self.view_menu = view_menu
    
    def on_threshold_change(self, *args):
        """Handle threshold slider changes"""
        self.low_label.config(text=str(self.low_threshold.get()))
        self.high_label.config(text=str(self.high_threshold.get()))
        
        # Auto-update if enabled and we have a captured image
        if self.auto_update.get() and self.captured_image is not None:
            self.process_image()
    
    def on_shape_param_change(self, *args):
        """Handle shape detection parameter changes"""
        self.line_label.config(text=str(self.line_threshold.get()))
        self.circle_label.config(text=str(self.circle_threshold.get()))
        self.area_label.config(text=str(self.min_area.get()))
        self.epsilon_label.config(text=f"{self.poly_epsilon.get():.2f}")
        
        # Auto-update if enabled and we have processed edges
        if self.auto_update.get() and self.processed_image is not None:
            self.detect_shapes()
    
    def start_camera(self):
        """Initialize and start the camera"""
        try:
            # Suppress OpenCV warnings
            cv2.setLogLevel(1)  # Only show errors
            
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                raise Exception(f"Could not open camera {self.camera_index}")
            
            # Set camera resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.display_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.display_height)
            
            self.camera_running = True
            self.capture_btn.config(state="normal")
            self.status_label.config(text="Camera ready - Click 'Capture Photo' to take a picture")
            
            # Start video feed thread
            self.video_thread = threading.Thread(target=self.update_video_feed, daemon=True)
            self.video_thread.start()
            
        except Exception as e:
            messagebox.showwarning("Camera Warning", 
                                 f"Camera not available: {str(e)}\nYou can still load image files using 'Load Image File' button.")
            self.status_label.config(text="No camera - Use 'Load Image File' to work with existing images")
    
    def update_video_feed(self):
        """Update the video feed in the GUI"""
        while self.camera_running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame.copy()
                    
                    # Convert frame for display
                    self.display_image(frame)
            
            time.sleep(0.03)  # ~30 FPS
    
    def display_image(self, image, is_bgr=True):
        """Display an image in the camera label"""
        try:
            # Convert BGR to RGB if needed
            if is_bgr and len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Resize to fit display
            h, w = image_rgb.shape[:2]
            if w > self.display_width or h > self.display_height:
                scale = min(self.display_width/w, self.display_height/h)
                new_w, new_h = int(w*scale), int(h*scale)
                image_resized = cv2.resize(image_rgb, (new_w, new_h))
            else:
                image_resized = image_rgb
            
            # Convert to PIL Image and then to PhotoImage
            pil_image = Image.fromarray(image_resized)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update the camera label
            self.camera_label.configure(image=photo, text="")
            self.camera_label.image = photo
            
        except Exception as e:
            print(f"Error displaying image: {e}")
    
    def capture_photo(self):
        """Capture the current frame"""
        if self.current_frame is not None:
            self.captured_image = self.current_frame.copy()
            
            # Stop video feed and show captured image
            self.camera_running = False
            
            # Display captured image
            self.display_image(self.captured_image)
            
            # Update button states
            self.capture_btn.config(state="disabled")
            self.accept_btn.config(state="normal")
            self.retake_btn.config(state="normal")
            
            self.status_label.config(text="Photo captured - Accept or retake the photo")
        else:
            messagebox.showwarning("Capture Error", "No frame available to capture")
    
    def accept_photo(self):
        """Accept the captured photo and enable processing"""
        if self.captured_image is not None:
            self.accept_btn.config(state="disabled")
            self.retake_btn.config(state="disabled")
            self.process_btn.config(state="normal")
            
            # Update menu states
            self.view_menu.entryconfig("🖼️ View Original", state="normal")
            
            self.status_label.config(text="Photo accepted - Click 'Apply Canny Edge Detection' to analyze")
        else:
            messagebox.showwarning("Accept Error", "No photo to accept")
    
    def retake_photo(self):
        """Retake the photo by restarting the camera"""
        self.captured_image = None
        self.processed_image = None
        
        # Restart camera if available
        if self.cap and self.cap.isOpened():
            self.camera_running = True
            self.video_thread = threading.Thread(target=self.update_video_feed, daemon=True)
            self.video_thread.start()
        
        # Update button states
        self.capture_btn.config(state="normal" if self.cap and self.cap.isOpened() else "disabled")
        self.accept_btn.config(state="disabled")
        self.retake_btn.config(state="disabled")
        self.process_btn.config(state="disabled")
        self.detect_shapes_btn.config(state="disabled")
        
        # Update menu states
        self.file_menu.entryconfig("💾 Save Processed Image", state="disabled")
        self.file_menu.entryconfig("📄 Export Shape Data", state="disabled")
        self.view_menu.entryconfig("🖼️ View Original", state="disabled")
        self.view_menu.entryconfig("🔍 View Edge Detection", state="disabled")
        
        self.status_label.config(text="Ready for new capture")
    
    def load_image_file(self):
        """Load an image file from disk"""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=file_types
        )
        
        if file_path:
            try:
                # Load image
                image = cv2.imread(file_path)
                if image is None:
                    raise Exception("Could not load image file")
                
                # Stop camera if running
                self.camera_running = False
                
                # Set as captured image
                self.captured_image = image
                
                # Display the image
                self.display_image(image)
                
                # Update button states
                self.capture_btn.config(state="disabled")
                self.accept_btn.config(state="disabled")
                self.retake_btn.config(state="normal")
                self.process_btn.config(state="normal")
                
                # Update menu states
                self.view_menu.entryconfig("🖼️ View Original", state="normal")
                
                self.status_label.config(text=f"Image loaded: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load image: {str(e)}")
    
    def process_image(self):
        """Process the accepted image with Canny edge detection"""
        if self.captured_image is not None:
            try:
                # Convert to grayscale
                gray = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2GRAY)
                
                # Apply Gaussian blur if enabled
                if self.use_blur.get():
                    processed = cv2.GaussianBlur(gray, (5, 5), 0)
                else:
                    processed = gray
                
                # Apply Canny edge detection
                low_thresh = self.low_threshold.get()
                high_thresh = self.high_threshold.get()
                
                # Ensure high threshold is greater than low threshold
                if high_thresh <= low_thresh:
                    high_thresh = low_thresh + 50
                    self.high_threshold.set(high_thresh)
                
                edges = cv2.Canny(processed, low_thresh, high_thresh)
                
                # Store processed image (keep as single channel for saving)
                self.processed_image = edges
                
                # Convert to RGB for display
                edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                
                # Display processed image
                self.display_image(edges_rgb, is_bgr=False)
                
                # Enable buttons and menu items
                self.detect_shapes_btn.config(state="normal")
                self.file_menu.entryconfig("💾 Save Processed Image", state="normal")
                
                blur_text = "with blur" if self.use_blur.get() else "without blur"
                self.status_label.config(text=f"Canny edge detection applied {blur_text} (Low: {low_thresh}, High: {high_thresh})")
                
            except Exception as e:
                messagebox.showerror("Processing Error", f"Failed to process image: {str(e)}")
        else:
            messagebox.showwarning("Processing Error", "No image to process")
    
    def view_original(self):
        """Switch back to viewing the original captured image"""
        if self.captured_image is not None:
            self.display_image(self.captured_image)
            self.status_label.config(text="Viewing original image")
    
    def save_processed_image(self):
        """Save the processed image to disk"""
        if self.processed_image is not None:
            file_types = [
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
            
            file_path = filedialog.asksaveasfilename(
                title="Save processed image",
                defaultextension=".png",
                filetypes=file_types
            )
            
            if file_path:
                try:
                    cv2.imwrite(file_path, self.processed_image)
                    self.status_label.config(text=f"Processed image saved: {os.path.basename(file_path)}")
                    messagebox.showinfo("Save Success", f"Image saved successfully to:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save image: {str(e)}")
        else:
            messagebox.showwarning("Save Error", "No processed image to save")
    
    def detect_shapes(self):
        """Detect primitive shapes in the edge-detected image"""
        if self.processed_image is None:
            messagebox.showwarning("Detection Error", "No edge-detected image available. Please run Canny edge detection first.")
            return
        
        try:
            # Clear previous detections
            self.detected_shapes = []
            
            # Create a copy of the original image for drawing shapes
            result_image = self.captured_image.copy()
            
            # Detect lines using Hough Line Transform
            lines = self.detect_lines()
            
            # Detect circles using Hough Circle Transform
            circles = self.detect_circles()
            
            # Detect polygons and other shapes using contour analysis
            polygons, ellipses, arcs = self.detect_contour_shapes()
            
            # Draw all detected shapes on the result image
            self.draw_shapes_on_image(result_image, lines, circles, polygons, ellipses, arcs)
            
            # Store the result and display it
            self.shapes_image = result_image
            self.display_image(result_image)
            
            # Enable menu items
            self.view_menu.entryconfig("🔍 View Edge Detection", state="normal")
            self.file_menu.entryconfig("📄 Export Shape Data", state="normal")
            
            # Update status
            total_shapes = len(lines) + len(circles) + len(polygons) + len(ellipses) + len(arcs)
            self.status_label.config(text=f"Shapes detected: {len(lines)} lines, {len(circles)} circles, {len(polygons)} polygons, {len(ellipses)} ellipses, {len(arcs)} arcs")
            
        except Exception as e:
            messagebox.showerror("Detection Error", f"Failed to detect shapes: {str(e)}")
    
    def detect_lines(self):
        """Detect lines using Hough Line Transform"""
        lines = []
        
        # Parameters from UI
        threshold = self.line_threshold.get()
        
        # Detect lines using HoughLinesP (Probabilistic Hough Transform)
        detected_lines = cv2.HoughLinesP(
            self.processed_image,
            rho=1,                    # Distance resolution in pixels
            theta=np.pi/180,          # Angle resolution in radians
            threshold=threshold,      # Minimum votes required
            minLineLength=30,         # Minimum line length
            maxLineGap=10            # Maximum gap between line segments
        )
        
        if detected_lines is not None:
            for line in detected_lines:
                x1, y1, x2, y2 = line[0]
                # Calculate line properties
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                angle = np.degrees(np.arctan2(y2-y1, x2-x1))
                
                line_data = {
                    'type': 'line',
                    'points': [(x1, y1), (x2, y2)],
                    'length': length,
                    'angle': angle,
                    'center': ((x1+x2)/2, (y1+y2)/2)
                }
                lines.append(line_data)
                self.detected_shapes.append(line_data)
        
        return lines
    
    def detect_circles(self):
        """Detect circles using Hough Circle Transform"""
        circles = []
        
        # Parameters from UI
        param2 = self.circle_threshold.get()
        
        # Convert processed image to grayscale if needed
        gray = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2GRAY)
        if self.use_blur.get():
            gray = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles
        detected_circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,                     # Inverse ratio of accumulator resolution
            minDist=20,              # Minimum distance between circle centers
            param1=50,               # Upper threshold for edge detection
            param2=param2,           # Accumulator threshold for center detection
            minRadius=5,             # Minimum circle radius
            maxRadius=200            # Maximum circle radius
        )
        
        if detected_circles is not None:
            detected_circles = np.round(detected_circles[0, :]).astype("int")
            for (x, y, r) in detected_circles:
                circle_data = {
                    'type': 'circle',
                    'center': (x, y),
                    'radius': r,
                    'area': np.pi * r * r,
                    'circumference': 2 * np.pi * r
                }
                circles.append(circle_data)
                self.detected_shapes.append(circle_data)
        
        return circles
    
    def detect_contour_shapes(self):
        """Detect polygons, ellipses, and arcs using contour analysis"""
        polygons = []
        ellipses = []
        arcs = []
        
        # Find contours from the edge image
        contours, _ = cv2.findContours(self.processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area
        min_area = self.min_area.get()
        epsilon_factor = self.poly_epsilon.get()
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            # Approximate contour to polygon
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Get contour properties
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            
            # Check if this is likely an arc/partial curve
            is_arc = self.is_contour_arc(contour, approx)
            
            # Classify based on number of vertices and properties
            num_vertices = len(approx)
            
            if is_arc:
                # Handle as an arc
                arc_data = self.fit_arc_to_contour(contour)
                if arc_data:
                    arcs.append(arc_data)
                    self.detected_shapes.append(arc_data)
            elif num_vertices >= 5 and solidity > 0.85:
                # Check if it's a complete ellipse/circle (closed curve)
                if self.is_closed_curve(contour):
                    # Fit ellipse to complete curve
                    if len(contour) >= 5:
                        try:
                            ellipse = cv2.fitEllipse(contour)
                            (center_x, center_y), (width, height), angle = ellipse
                            
                            ellipse_data = {
                                'type': 'ellipse',
                                'center': (int(center_x), int(center_y)),
                                'axes': (width/2, height/2),
                                'angle': angle,
                                'area': area,
                                'eccentricity': self.calculate_eccentricity(width, height)
                            }
                            ellipses.append(ellipse_data)
                            self.detected_shapes.append(ellipse_data)
                        except:
                            pass  # Skip if ellipse fitting fails
                else:
                    # Treat as an arc
                    arc_data = self.fit_arc_to_contour(contour)
                    if arc_data:
                        arcs.append(arc_data)
                        self.detected_shapes.append(arc_data)
            else:
                # Classify as polygon
                shape_name = self.classify_polygon(num_vertices)
                
                # Calculate polygon properties
                moments = cv2.moments(contour)
                if moments["m00"] != 0:
                    cx = int(moments["m10"] / moments["m00"])
                    cy = int(moments["m01"] / moments["m00"])
                else:
                    cx, cy = 0, 0
                
                polygon_data = {
                    'type': 'polygon',
                    'shape': shape_name,
                    'vertices': num_vertices,
                    'points': [tuple(point[0]) for point in approx],
                    'area': area,
                    'perimeter': cv2.arcLength(contour, True),
                    'center': (cx, cy),
                    'solidity': solidity
                }
                polygons.append(polygon_data)
                self.detected_shapes.append(polygon_data)
        
        return polygons, ellipses, arcs
    
    def is_contour_arc(self, contour, approx):
        """Determine if a contour represents an arc rather than a closed shape"""
        # Check if the contour endpoints are far apart (indicating an open curve)
        if len(contour) < 10:
            return False
        
        # Get start and end points
        start_point = contour[0][0]
        end_point = contour[-1][0]
        
        # Calculate distance between endpoints
        endpoint_distance = np.sqrt((start_point[0] - end_point[0])**2 + (start_point[1] - end_point[1])**2)
        
        # Calculate the perimeter
        perimeter = cv2.arcLength(contour, False)  # Open contour
        
        # If endpoints are far apart relative to the contour length, it's likely an arc
        if perimeter > 0:
            endpoint_ratio = endpoint_distance / perimeter
            # If endpoints are more than 10% of perimeter apart, consider it an arc
            if endpoint_ratio > 0.1:
                return True
        
        # Also check curvature consistency (arcs have relatively consistent curvature)
        curvature_variance = self.calculate_curvature_variance(contour)
        return curvature_variance < 0.5  # Low variance indicates consistent curvature
    
    def is_closed_curve(self, contour):
        """Check if a contour represents a closed curve (circle/ellipse)"""
        if len(contour) < 10:
            return False
        
        # Get start and end points
        start_point = contour[0][0]
        end_point = contour[-1][0]
        
        # Calculate distance between endpoints
        endpoint_distance = np.sqrt((start_point[0] - end_point[0])**2 + (start_point[1] - end_point[1])**2)
        
        # If endpoints are very close, it's a closed curve
        return endpoint_distance < 10  # pixels
    
    def calculate_curvature_variance(self, contour):
        """Calculate variance in curvature along the contour"""
        if len(contour) < 6:
            return float('inf')
        
        curvatures = []
        for i in range(2, len(contour) - 2):
            # Get three consecutive points
            p1 = contour[i-2][0]
            p2 = contour[i][0]
            p3 = contour[i+2][0]
            
            # Calculate curvature using the cross product method
            v1 = np.array([p2[0] - p1[0], p2[1] - p1[1]])
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
            
            # Normalize vectors
            v1_norm = np.linalg.norm(v1)
            v2_norm = np.linalg.norm(v2)
            
            if v1_norm > 0 and v2_norm > 0:
                v1 = v1 / v1_norm
                v2 = v2 / v2_norm
                
                # Calculate angle between vectors
                cross_product = np.cross(v1, v2)
                curvature = abs(cross_product)
                curvatures.append(curvature)
        
        if len(curvatures) > 1:
            return np.var(curvatures)
        return 0
    
    def fit_arc_to_contour(self, contour):
        """Fit an arc to a contour and return arc parameters"""
        if len(contour) < 5:
            return None
        
        try:
            # Fit a circle to the contour points
            contour_points = contour.reshape(-1, 2).astype(np.float32)
            
            # Use least squares circle fitting
            center, radius = self.fit_circle_least_squares(contour_points)
            
            if radius <= 0 or radius > 1000:  # Invalid radius
                return None
            
            # Calculate arc parameters
            start_point = contour[0][0]
            end_point = contour[-1][0]
            
            # Calculate start and end angles
            start_angle = np.degrees(np.arctan2(start_point[1] - center[1], start_point[0] - center[0]))
            end_angle = np.degrees(np.arctan2(end_point[1] - center[1], end_point[0] - center[0]))
            
            # Normalize angles to [0, 360]
            start_angle = (start_angle + 360) % 360
            end_angle = (end_angle + 360) % 360
            
            # Calculate arc length
            angle_diff = end_angle - start_angle
            if angle_diff < 0:
                angle_diff += 360
            
            # If the arc spans more than 270 degrees, it might be a nearly complete circle
            if angle_diff > 270:
                return None  # Treat as ellipse instead
            
            arc_length = (angle_diff / 360) * 2 * np.pi * radius
            
            arc_data = {
                'type': 'arc',
                'center': (int(center[0]), int(center[1])),
                'radius': float(radius),
                'start_angle': float(start_angle),
                'end_angle': float(end_angle),
                'arc_length': float(arc_length),
                'start_point': tuple(start_point),
                'end_point': tuple(end_point),
                'chord_length': float(np.sqrt((end_point[0] - start_point[0])**2 + (end_point[1] - start_point[1])**2))
            }
            
            return arc_data
            
        except Exception as e:
            print(f"Error fitting arc: {e}")
            return None
    
    def fit_circle_least_squares(self, points):
        """Fit a circle to points using least squares method"""
        if len(points) < 3:
            return (0, 0), 0
        
        # Convert to numpy array
        points = np.array(points)
        
        # Set up the least squares system
        # Circle equation: (x-a)² + (y-b)² = r²
        # Expanding: x² + y² - 2ax - 2by + (a² + b² - r²) = 0
        # Linear form: -2ax - 2by + c = -(x² + y²)
        
        A = np.column_stack([
            -2 * points[:, 0],  # -2x
            -2 * points[:, 1],  # -2y
            np.ones(len(points))  # 1
        ])
        
        b = -(points[:, 0]**2 + points[:, 1]**2)
        
        try:
            # Solve the least squares problem
            solution = np.linalg.lstsq(A, b, rcond=None)[0]
            
            center_x = solution[0]
            center_y = solution[1]
            c = solution[2]
            
            # Calculate radius: r² = a² + b² - c
            radius_squared = center_x**2 + center_y**2 - c
            radius = np.sqrt(max(0, radius_squared))
            
            return (center_x, center_y), radius
            
        except np.linalg.LinAlgError:
            # Fallback to simple centroid if least squares fails
            center = np.mean(points, axis=0)
            distances = np.sqrt(np.sum((points - center)**2, axis=1))
            radius = np.mean(distances)
            return tuple(center), radius
    
    def classify_polygon(self, vertices):
        """Classify polygon based on number of vertices"""
        if vertices == 3:
            return "triangle"
        elif vertices == 4:
            return "quadrilateral"
        elif vertices == 5:
            return "pentagon"
        elif vertices == 6:
            return "hexagon"
        else:
            return f"{vertices}-gon"
    
    def calculate_eccentricity(self, width, height):
        """Calculate eccentricity of an ellipse"""
        a = max(width, height) / 2
        b = min(width, height) / 2
        if a == 0:
            return 0
        return np.sqrt(1 - (b**2 / a**2))
    
    def draw_shapes_on_image(self, image, lines, circles, polygons, ellipses, arcs):
        """Draw detected shapes on the image with different colors"""
        
        # Draw lines in red
        for line in lines:
            pt1, pt2 = line['points']
            cv2.line(image, pt1, pt2, (0, 0, 255), 2)
            # Draw line center
            center = (int(line['center'][0]), int(line['center'][1]))
            cv2.circle(image, center, 3, (0, 0, 255), -1)
        
        # Draw circles in green
        for circle in circles:
            center = circle['center']
            radius = circle['radius']
            cv2.circle(image, center, radius, (0, 255, 0), 2)
            cv2.circle(image, center, 2, (0, 255, 0), -1)
        
        # Draw polygons in blue
        for polygon in polygons:
            points = np.array(polygon['points'], np.int32)
            cv2.polylines(image, [points], True, (255, 0, 0), 2)
            # Draw center
            center = polygon['center']
            cv2.circle(image, center, 3, (255, 0, 0), -1)
        
        # Draw ellipses in cyan
        for ellipse in ellipses:
            center = ellipse['center']
            axes = (int(ellipse['axes'][0]), int(ellipse['axes'][1]))
            angle = ellipse['angle']
            cv2.ellipse(image, center, axes, angle, 0, 360, (255, 255, 0), 2)
            cv2.circle(image, center, 2, (255, 255, 0), -1)
        
        # Draw arcs in magenta
        for arc in arcs:
            center = arc['center']
            radius = int(arc['radius'])
            start_angle = arc['start_angle']
            end_angle = arc['end_angle']
            
            # Draw the arc
            cv2.ellipse(image, center, (radius, radius), 0, start_angle, end_angle, (255, 0, 255), 2)
            
            # Draw center point
            cv2.circle(image, center, 2, (255, 0, 255), -1)
            
            # Draw start and end points
            start_point = arc['start_point']
            end_point = arc['end_point']
            cv2.circle(image, start_point, 4, (255, 0, 255), -1)
            cv2.circle(image, end_point, 4, (255, 0, 255), -1)
            
            # Draw radius lines to show the arc extent
            cv2.line(image, center, start_point, (255, 0, 255), 1)
            cv2.line(image, center, end_point, (255, 0, 255), 1)
    
    def view_edges(self):
        """Switch to viewing the edge-detected image"""
        if self.processed_image is not None:
            edges_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_GRAY2RGB)
            self.display_image(edges_rgb, is_bgr=False)
            self.status_label.config(text="Viewing edge detection result")
    
    def export_shapes(self):
        """Export detected shape data to a JSON file"""
        if not self.detected_shapes:
            messagebox.showwarning("Export Error", "No shapes detected to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export shape data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import json
                
                # Prepare export data
                export_data = {
                    'image_info': {
                        'width': self.captured_image.shape[1],
                        'height': self.captured_image.shape[0],
                        'channels': self.captured_image.shape[2]
                    },
                    'detection_parameters': {
                        'canny_low': self.low_threshold.get(),
                        'canny_high': self.high_threshold.get(),
                        'line_threshold': self.line_threshold.get(),
                        'circle_threshold': self.circle_threshold.get(),
                        'min_area': self.min_area.get(),
                        'poly_epsilon': self.poly_epsilon.get()
                    },
                    'shapes': self.detected_shapes,
                    'summary': {
                        'total_shapes': len(self.detected_shapes),
                        'lines': len([s for s in self.detected_shapes if s['type'] == 'line']),
                        'circles': len([s for s in self.detected_shapes if s['type'] == 'circle']),
                        'polygons': len([s for s in self.detected_shapes if s['type'] == 'polygon']),
                        'ellipses': len([s for s in self.detected_shapes if s['type'] == 'ellipse']),
                        'arcs': len([s for s in self.detected_shapes if s['type'] == 'arc'])
                    }
                }
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                self.status_label.config(text=f"Shape data exported: {os.path.basename(file_path)}")
                messagebox.showinfo("Export Success", f"Shape data exported successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export shape data: {str(e)}")
    
    def cleanup(self):
        """Clean up resources when closing the app"""
        self.camera_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    # Create ttkbootstrap window with theme
    root = ttk.Window(themename="lumen")
    app = MeasurementApp(root)
    
    # Handle window closing
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()