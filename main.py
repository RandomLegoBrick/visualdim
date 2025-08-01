
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"


import ttkbootstrap as ttk
import cv2
from PIL import Image, ImageTk
import threading
from time import sleep

class MeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VisualDim 0.0.1")
        self.root.geometry("900x700")

        self.camera_running = False
        self.captured_image = None
        self.low_threshold = 40
        self.high_threshold = 150
        self.camera = None

    def start_camera(self):

        if not self.camera:
            self.camera = cv2.VideoCapture(1)

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)

        self.camera_running = True
        self.video_thread = threading.Thread(target=self.update_video_feed, daemon=True)
        self.video_thread.start()
    
    def stop_camera(self):
        self.camera_running = False

    def process_image(self):
        
        # Convert back to OpenCV format for Canny edge detection
        opencv_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Canny edge detection
        # Parameters: image, low_threshold, high_threshold

        opencv_gray = cv2.GaussianBlur(opencv_gray, (3,3), 0) 
        opencv_gray = cv2.bilateralFilter(opencv_gray, 9, 75, 75)

        edges = cv2.Canny(opencv_gray, self.low_threshold, self.high_threshold)
        
        # Remove small contours (noise from background)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        edges_clean = edges.copy()
        for contour in contours:
            if cv2.contourArea(contour) < 50:  # Remove small contours
                cv2.drawContours(edges_clean, [contour], -1, 0, -1)


        # Create a blank RGB image for drawing contours
        contour_img = cv2.cvtColor(edges_clean, cv2.COLOR_GRAY2RGB)
        contour_img[:] = 0  # Make it black

        # Draw contours in red with thickness 2

        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (0, 255, 255),
            (255, 0, 255),
        ]
        for i, contour in enumerate(contours):
            cv2.drawContours(contour_img, contours, i, colors[i%len(colors)], 2)

        # Convert edges back to RGBA for display
        # edges_rgba = cv2.cvtColor(contour_img, cv2.COLOR_GRAY2RGBA)
        captured_image = Image.fromarray(contour_img)

        captured_image = captured_image.resize((640, 512))
        photo_image = ImageTk.PhotoImage(image=captured_image)
        self.label_widget.configure(image=photo_image)
        self.label_widget.photo_image = photo_image

    def update_video_feed(self):
        while self.camera_running:
            if self.camera and self.camera.isOpened():
                
                success, self.frame = self.camera.read()

                if success:
                    
                    opencv_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)

                    captured_image = Image.fromarray(opencv_image).resize((640, 512))

                    photo_image = ImageTk.PhotoImage(image=captured_image)

                    self.label_widget.configure(image=photo_image)
                    self.label_widget.photo_image = photo_image
            
            sleep(0.1)  # ~10 FPS

        self.process_image()

    def on_low_threshold_change(self, value):
        self.low_threshold = int(float(value))
        if hasattr(self, 'frame') and self.frame is not None and not self.camera_running:
            self.process_image()

    def on_high_threshold_change(self, value):
        self.high_threshold = int(float(value))
        if hasattr(self, 'frame') and self.frame is not None and not self.camera_running:
            self.process_image()

    

    def run(self):

        self.root.bind('<Escape>', lambda e: app.quit())

        cameraFrame = ttk.Frame(self.root, width=600, height=600)
        
        self.label_widget = ttk.Label(cameraFrame, text="Press Open Camera to Begin...")
        self.label_widget.pack()

        cameraFrame.place(relx=0.5, rely=0.4, anchor='c')

        # Threshold sliders
        slider_frame = ttk.Frame(self.root)
        slider_frame.place(relx=0.02, rely=0.1)

        ttk.Label(slider_frame, text="Low Threshold:").pack()
        self.low_slider = ttk.Scale(slider_frame, from_=0, to=255, orient='horizontal', 
                                   value=self.low_threshold, command=self.on_low_threshold_change)
        self.low_slider.pack()

        ttk.Label(slider_frame, text="High Threshold:").pack()
        self.high_slider = ttk.Scale(slider_frame, from_=0, to=255, orient='horizontal', 
                                    value=self.high_threshold, command=self.on_high_threshold_change)
        self.high_slider.pack()

        startButton = ttk.Button(self.root, text="Open Camera", command=self.start_camera)
        startButton.place(relx=0.5-0.05, rely=0.8, anchor='c')

        startButton = ttk.Button(self.root, text="Capture", command=self.stop_camera)
        startButton.place(relx=0.5+0.05, rely=0.8, anchor='c')




if __name__ == "__main__":
    root = ttk.Window(themename="lumen")
    app = MeasurementApp(root)
    app.run()
    
    def on_closing():
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
