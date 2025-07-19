import cv2
import numpy as np
import os

# Paths to the input images
thermal_path = r"C:\Users\racha\OneDrive\Desktop\project11\Task1\DJI_20250530123037_0003_Z.JPG"
rgb_path = r"C:\Users\racha\OneDrive\Desktop\project11\Task1\DJI_20250530123037_0003_AT.JPG"

# Read the thermal and RGB images
thermal_img = cv2.imread(thermal_path)
rgb_img = cv2.imread(rgb_path)

# Resize thermal image to match RGB image size (optional but helps with alignment)
thermal_img = cv2.resize(thermal_img, (rgb_img.shape[1], rgb_img.shape[0]))

# Convert images to grayscale for feature detection
gray_thermal = cv2.cvtColor(thermal_img, cv2.COLOR_BGR2GRAY)
gray_rgb = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)

# Use ORB detector to find keypoints and descriptors
orb = cv2.ORB_create(5000)
kp1, des1 = orb.detectAndCompute(gray_thermal, None)
kp2, des2 = orb.detectAndCompute(gray_rgb, None)

# Match descriptors using BFMatcher
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)

# Sort matches by distance (lower is better)
matches = sorted(matches, key=lambda x: x.distance)
good_matches = matches[:50]

# Extract matched keypoints
src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

# Estimate homography matrix
H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

# Warp thermal image to align with RGB image
aligned_thermal = cv2.warpPerspective(thermal_img, H, (rgb_img.shape[1], rgb_img.shape[0]))

# Blend aligned thermal with RGB (use transparency for overlay)
overlay = cv2.addWeighted(rgb_img, 0.6, aligned_thermal, 0.4, 0)

# Save output
output_path =r"C:\Users\racha\OneDrive\Desktop\project11\Task1\DJI_20250530123037_0003_Z.JPG"
cv2.imwrite(output_path, overlay)

print(f"Overlay saved to: {output_path}")
