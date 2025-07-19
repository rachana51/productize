import cv2
import numpy as np
import os
from glob import glob

# Define input and output directories
input_folder = 'C:\Users\racha\Downloads\New folder (2)\project22\Task2\input-images'     # Change if needed
output_folder = './output'

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Get all 'before' images (excluding '~2' ones)
before_images = sorted(glob(os.path.join(input_folder, '1.jpg')))
before_images = [img for img in before_images if '1~2' not in img]

def highlight_changes(before_path, after_path, output_path):
    before = cv2.imread(before_path)
    after = cv2.imread(after_path)

    # Convert to grayscale
    gray_before = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    # Compute absolute difference
    diff = cv2.absdiff(gray_before, gray_after)

    # Threshold the difference
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Dilate the thresholded image to fill in gaps
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    # Find contours in the difference image
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding boxes on the 'after' image
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h > 500:  # Ignore small changes/noise
            cv2.rectangle(after, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Save output
    cv2.imwrite(output_path, after)

# Process all image pairs
for before_path in before_images:
    after_path = before_path.replace('3.jpg', '3~2.jpg')
    if os.path.exists(after_path):
        filename = os.path.basename(before_path).replace('5.jpg', '5.jpg')
        output_path = os.path.join(output_folder, filename)
        highlight_changes(before_path, after_path, output_path)
        print(f"Processed: {filename}")

print("Change detection completed. Results saved in the 'output' folder.")
