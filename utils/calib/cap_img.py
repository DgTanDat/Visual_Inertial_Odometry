# from picamera2 import Picamera2
# import cv2
# import numpy as np
# import os
# import time

# # Output directory and image counter
# output_dir = "calib_images"
# os.makedirs(output_dir, exist_ok=True)
# img_counter = 47

# # Initialize camera
# picam = Picamera2()
# config = picam.create_video_configuration(
#     main={"size": (640, 480), "format": "RGB888"},
#     controls={"FrameRate": 60}
# )
# picam.configure(config)
# picam.start()

# print("Press 'c' to capture calibration image, 'q' to quit.")

# try:
#     while True:
#         frame = picam.capture_array()

#         # Show camera feed
#         cv2.imshow("Pi Camera V3 - Calibration Mode", frame)

#         key = cv2.waitKey(1) & 0xFF

#         if key == ord('c'):
#             # Save image
#             img_counter += 1
#             filename = os.path.join(output_dir, f"calib_{img_counter:02d}.jpg")
#             cv2.imwrite(filename, frame)
#             print(f"Saved image: {filename}")

#         elif key == ord('q'):
#             break

# except KeyboardInterrupt:
#     print("Interrupted")

# # Cleanup
# picam.stop()
# cv2.destroyAllWindows()

# from picamera2 import Picamera2
# from libcamera import controls
# import cv2
# import numpy as np
# import os
# import time

# # Output directory and image counter
# output_dir = "calib_images1"
# os.makedirs(output_dir, exist_ok=True)
# img_counter = 0

# # Initialize camera
# picam = Picamera2()
# # configs = picam.sensor_modes

# # for mode in configs:
# #     print(mode)
# os.system("v4l2-ctl --set-ctrl wide_dynamic_range=1 -d /dev/v4l-subdev0")
# print("Setting HDR to ON")

# config = picam.create_video_configuration(
#     main={"size": (640, 480), "format": "RGB888"},
#     queue=False,
#     controls={"FrameRate": 30}
# )
# picam.configure(config)
# picam.set_controls({
#     "AfMode": controls.AfModeEnum.Continuous,
#     "AfSpeed": controls.AfSpeedEnum.Fast
# })
# picam.start()


# print("Press 'c' to capture calibration image, 'q' to quit.")

# # Variables for FPS calculation
# prev_time = time.time()
# fps = 0

# try:
#     while True:
#         # start_exe = time.perf_counter()
#         frame = picam.capture_array()
#         # end_exe = time.perf_counter()
#         # print("exe time: ", end_exe - start_exe)

#         # Calculate FPS
#         current_time = time.time()
#         fps = 1.0 / (current_time - prev_time)
#         prev_time = current_time

#         # Display FPS on the frame
#         cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#         # Show camera feed
#         cv2.imshow("Pi Camera V3 - Calibration Mode", frame)

#         key = cv2.waitKey(1) & 0xFF

#         if key == ord('c'):
#             # Save image
#             img_counter += 1
#             filename = os.path.join(output_dir, f"calib_{img_counter:02d}.jpg")
#             cv2.imwrite(filename, frame)
#             print(f"Saved image: {filename}")

#         elif key == ord('q'):
#             break

# except KeyboardInterrupt:
#     print("Interrupted")

# # Cleanup
# picam.stop()
# cv2.destroyAllWindows()
# print("Setting HDR to OFF")
# os.system("v4l2-ctl --set-ctrl wide_dynamic_range=0 -d /dev/v4l-subdev0")

from picamera2 import Picamera2
from libcamera import controls
import cv2
import numpy as np
import os
import time

# Output directory and image counter
output_dir = "calib_images1"
os.makedirs(output_dir, exist_ok=True)
img_counter = 0

# Initialize camera
picam = Picamera2()

print("Configuring camera with HDR-like settings...")

# Cấu hình video với định dạng RGB888 (phù hợp với OpenCV) và độ phân giải nhỏ
config = config = picam.create_video_configuration(
    main={"size": (640, 480), "format": "RGB888"},
    queue=False,
    controls={
        # "AfMode": 1,
        # "AeEnable": True,
        # "NoiseReductionMode": 2,
        "FrameRate": 60,
        "ExposureTime": 10000,
        # "AnalogueGain": 5
    }
)

picam.configure(config)
picam.start()

print("Camera started. Press 'c' to capture calibration image, 'q' to quit.")

# Variables for FPS calculation
prev_time = time.time()
fps = 0

try:
    while True:
        frame = picam.capture_array()

        # Calculate FPS
        current_time = time.time()
        fps = 1.0 / (current_time - prev_time)
        prev_time = current_time

        # Display FPS on the frame
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show camera feed
        cv2.imshow("Pi Camera V3 - Calibration Mode", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            img_counter += 1
            filename = os.path.join(output_dir, f"calib_{img_counter:02d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Saved image: {filename}")

        elif key == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted")

# Cleanup
picam.stop()
cv2.destroyAllWindows()
print("Camera stopped.")
