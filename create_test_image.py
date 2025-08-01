#!/usr/bin/env python3
"""
Create a test image with various geometric shapes for testing the shape detection
"""
import cv2
import numpy as np

def create_test_image():
    # Create a blank white image
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Draw some shapes in black for good edge detection
    
    # Rectangle
    cv2.rectangle(img, (50, 50), (200, 150), (0, 0, 0), 3)
    
    # Complete circle
    cv2.circle(img, (350, 100), 60, (0, 0, 0), 3)
    
    # Triangle
    triangle_pts = np.array([[500, 50], [450, 150], [550, 150]], np.int32)
    cv2.polylines(img, [triangle_pts], True, (0, 0, 0), 3)
    
    # Complete ellipse
    cv2.ellipse(img, (150, 300), (80, 50), 30, 0, 360, (0, 0, 0), 3)
    
    # Pentagon
    center = (350, 300)
    radius = 70
    pentagon_pts = []
    for i in range(5):
        angle = i * 2 * np.pi / 5 - np.pi/2
        x = int(center[0] + radius * np.cos(angle))
        y = int(center[1] + radius * np.sin(angle))
        pentagon_pts.append([x, y])
    pentagon_pts = np.array(pentagon_pts, np.int32)
    cv2.polylines(img, [pentagon_pts], True, (0, 0, 0), 3)
    
    # Hexagon
    center = (550, 300)
    radius = 60
    hexagon_pts = []
    for i in range(6):
        angle = i * 2 * np.pi / 6
        x = int(center[0] + radius * np.cos(angle))
        y = int(center[1] + radius * np.sin(angle))
        hexagon_pts.append([x, y])
    hexagon_pts = np.array(hexagon_pts, np.int32)
    cv2.polylines(img, [hexagon_pts], True, (0, 0, 0), 3)
    
    # Some lines
    cv2.line(img, (100, 450), (300, 500), (0, 0, 0), 3)
    cv2.line(img, (400, 450), (600, 480), (0, 0, 0), 3)
    cv2.line(img, (50, 520), (200, 520), (0, 0, 0), 3)
    
    # Another complete circle
    cv2.circle(img, (650, 100), 40, (0, 0, 0), 3)
    
    # Complete oval/ellipse
    cv2.ellipse(img, (500, 500), (100, 40), 45, 0, 360, (0, 0, 0), 3)
    
    # Add some arcs (partial circles/ellipses)
    # Arc 1: Quarter circle (90 degrees)
    cv2.ellipse(img, (100, 200), (50, 50), 0, 0, 90, (0, 0, 0), 3)
    
    # Arc 2: Half circle (180 degrees) 
    cv2.ellipse(img, (250, 200), (40, 40), 0, 45, 225, (0, 0, 0), 3)
    
    # Arc 3: Three-quarter circle (270 degrees) - this might still be detected as circle
    cv2.ellipse(img, (400, 200), (35, 35), 0, 30, 300, (0, 0, 0), 3)
    
    # Arc 4: Elliptical arc
    cv2.ellipse(img, (700, 200), (60, 30), 45, 60, 180, (0, 0, 0), 3)
    
    # Arc 5: Small arc
    cv2.ellipse(img, (600, 350), (25, 25), 0, 120, 240, (0, 0, 0), 3)
    
    # Arc 6: Large arc spanning less than 180 degrees
    cv2.ellipse(img, (150, 450), (80, 80), 0, 220, 40, (0, 0, 0), 3)
    
    return img

def main():
    # Create test image
    test_img = create_test_image()
    
    # Save the image
    cv2.imwrite('test_shapes.png', test_img)
    print("Test image 'test_shapes.png' created successfully!")
    print("This image contains:")
    print("- Rectangles")
    print("- Complete circles") 
    print("- Triangles")
    print("- Complete ellipses")
    print("- Pentagon")
    print("- Hexagon")
    print("- Lines")
    print("- Arcs (partial circles and ellipses)")
    print("\nLoad this image in the Visual Measurement App to test shape detection!")
    print("Arcs should now be detected as partial curves instead of complete circles/ellipses!")

if __name__ == "__main__":
    main()
