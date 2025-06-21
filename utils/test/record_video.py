from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()

video_config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(video_config)

picam2.start()
time.sleep(1)

# VideoWriter vẫn cần khung hình 3 kênh (BGR), nên ta sẽ convert ngược lại để lưu
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (640, 480))

print("Recording grayscale video... Press 'q' to stop.")

while True:
    frame = picam2.capture_array()
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # # Convert grayscale back to BGR to save (AVI requires 3 channels)
    # gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    out.write(gray)

    # Show grayscale preview
    cv2.imshow("Grayscale Preview", gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

out.release()
cv2.destroyAllWindows()
picam2.stop()
print("Video saved as 'output.avi'")
