import cv2
import numpy as np
import os
import glob
import argparse
import pickle

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Camera calibration using chessboard images")
parser.add_argument("--chessboard-size", type=str, default="7x5", help="Chessboard size as WIDTHxHEIGHT (e.g., 6x4)")
parser.add_argument("--square-size", type=float, default=3.0, help="Size of each square (arbitrary unit)")
parser.add_argument("--input-dir", type=str, default="calib_images1", help="Directory containing calibration images")
parser.add_argument("--calib-file", type=str, default="calibration_data.pkl", help="File to save calibration results")
args = parser.parse_args()

# Chessboard configuration
chessboard_size = tuple(map(int, args.chessboard_size.split('x')))
square_size = args.square_size
input_dir = args.input_dir
calib_file = args.calib_file

# Prepare object points (3D coordinates of chessboard corners)
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * square_size

# Initialize lists for calibration
obj_points = []  # 3D points in real world
img_points = []  # 2D points in image plane
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)  # For corner refinement

# Load images from the input directory
image_files = glob.glob(os.path.join(input_dir, "*.jpg"))
if not image_files:
    print(f"No images found in {input_dir}")
    exit(1)

print(f"Found {len(image_files)} images in {input_dir}")

# Process each image
for img_path in image_files:
    img = cv2.imread(img_path)
    if img is None:
        print(f"Failed to load image: {img_path}")
        continue

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        # Refine corners
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        obj_points.append(objp)
        img_points.append(corners)
        print(f"Chessboard detected in {img_path}")
    else:
        print(f"No chessboard detected in {img_path}")

# Perform calibration if enough valid images
if len(obj_points) >= 5:
    print("\nStarting camera calibration...")
    try:
        # Get image size from the first valid image
        img_size = gray.shape[::-1]

        # Calibrate camera
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_points, img_points, img_size, None, None
        )

        # Calculate reprojection error
        mean_error = 0
        for i in range(len(obj_points)):
            imgpoints2, _ = cv2.projectPoints(obj_points[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(img_points[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error
        mean_error /= len(obj_points)

        print(f"Calibration successful!")
        print(f"Reprojection error: {mean_error:.4f} pixels")
        print(f"Camera matrix:\n{mtx}")
        print(f"Distortion coefficients:\n{dist}")

        # Save calibration data
        calib_data = {
            "camera_matrix": mtx,
            "distortion_coefficients": dist,
            "reprojection_error": mean_error,
            "image_size": img_size
        }
        try:
            with open(calib_file, 'wb') as f:
                pickle.dump(calib_data, f)
            print(f"Calibration data saved to {calib_file}")
        except Exception as e:
            print(f"Error saving calibration data: {e}")

        # Undistort a sample image (last valid image)
        if image_files:
            sample_img = cv2.imread(image_files[-1])
            if sample_img is not None:
                h, w = sample_img.shape[:2]
                new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
                undistorted = cv2.undistort(sample_img, mtx, dist, None, new_camera_mtx)
                output_path = os.path.join(input_dir, "undistorted_sample.jpg")
                cv2.imwrite(output_path, undistorted)
                print(f"Saved undistorted sample image as {output_path}")
            else:
                print("Could not load sample image for undistortion")

    except Exception as e:
        print(f"Error during calibration: {e}")
else:
    print(f"Not enough valid images ({len(obj_points)}) for calibration. Need at least 5.")

print(f"\nProcessed {len(image_files)} images, {len(obj_points)} valid for calibration. Done!")