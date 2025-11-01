import cv2
from flask import Flask, Response
import time

app = Flask(__name__)

def generate_frames():
    # Use cv2.VideoCapture to access the webcam. The '0' indicates the first camera.
    camera = cv2.VideoCapture(0)  

    if not camera.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        # Read a frame from the camera.
        success, frame = camera.read()  
        if not success:
            break
        else:
            # Encode the frame as a JPEG image.
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            # Convert the buffer to bytes.
            frame_bytes = buffer.tobytes()

            # Yield the frame in the format required for the HTTP response.
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        # Optional: Add a small delay to control the frame rate.
        time.sleep(0.04)  # ~25 fps

    camera.release()

@app.route('/video_feed')
def video_feed():
    # Return the stream of frames as a multipart response.
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Run the Flask application.
    app.run(host='192.168.1.114', port=5000, threaded=True)