# CV_LP_project 

This repository contains a series of computer vision scripts designed to **count people in real-time** across one or multiple cameras. The project evolved from basic frame difference detection to YOLO-based tracking, timer-enabled snapshots, Flask video streaming, and finally a **multi-camera GUI people counter**.  

> **Note:** All IP addresses, passwords, and camera information have been anonymized to protect sensitive data.

---

## Table of Contents
1. [Simple Difference-Based Detection](#simple-difference-based-detection)
2. [YOLO Single Camera People Counter](#yolo-single-camera-people-counter)
3. [YOLO Timer-Based People Counter](#yolo-timer-based-people-counter)
4. [Flask Video Stream](#flask-video-stream)
5. [Multi-Camera GUI People Counter](#multi-camera-gui-people-counter)

---

## Simple Difference-Based Detection

### Overview
This is the **first iteration** of the people counting system. It detects motion by calculating the **difference between consecutive frames**, followed by thresholding and contour detection. People are counted when their movement crosses a predefined reference line.

**Highlights and Characteristics:**
- Extremely lightweight; runs on low-power devices.
- Detects **moving objects** without the need for complex models.
- Allows quick prototyping of a counting system.

**Example Workflow:**
1. Capture a few initial frames to normalize lighting conditions.
```python
first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
first_frame = cv2.GaussianBlur(first_frame, (21, 21), 0)
```
2. Convert frames to grayscale and blur to reduce noise.
```python
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (21, 21), 0)
```
3. Calculate the absolute difference between the first frame and the current frame.
```python
delta = cv2.absdiff(first_frame, gray)
thresh = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]
```
4. Apply dilation and find contours to detect moving objects.
```python
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
```
5. Count objects whose centroids cross the reference line.
```python
for c in contours:
    if cv2.contourArea(c) > min_area:
        cx = int((x + x + w) / 2)
        if cx > line_x: count_exit += 1
```

### Lessons Learned
- Sensitive to **lighting changes and shadows**; initial frames help reduce false positives.
- Thresholds and minimum contour area need **empirical tuning**.
- Simple and effective for testing but not robust for multi-camera or complex environments.

[Link to full script](Scripts/simple_difference_detection.py)

---

## YOLO Single Camera People Counter

### Overview
The next step introduces **YOLOv8 nano**, enabling robust people detection and tracking in a single camera feed. Persistent IDs allow accurate counting of entries and exits using centroid tracking.

**Highlights and Characteristics:**
- Real-time **object detection** using YOLO.
- Persistent **tracking IDs** prevent double-counting.
- Simple **vertical line** counting method.
- Can save snapshots of detected people crossing the line.

**Example Workflow:**
1. Open camera feed and read frames.
```python
ret, frame = cap.read()
```
2. Use YOLO to detect people (class 0).
```python
results = model.track(frame, persist=True, classes=[0])
```
3. Draw bounding boxes and centroids for each person.
```python
for track_id, box in zip(results[0].boxes.id, results[0].boxes.xyxy):
    x1, y1, x2, y2 = box
    center_x = (x1 + x2) // 2
```
4. Track the X-coordinate of each centroid across frames.
5. Count as "entry" or "exit" when centroids cross the vertical reference line.
```python
if prev_x < line_x and curr_x >= line_x:
    out_count += 1
```

### Lessons Learned
- YOLO improves detection accuracy compared to simple frame differencing.
- Centroid-based tracking is essential to maintain correct counts.
- Single-camera setup is easier for testing, but multi-camera setups require further integration.

[Link to full script](Scripts/yolo_single_camera.py)

---

## YOLO Timer-Based People Counter

### Overview
This variation adds **timers for each detected object**. When a person is detected, a timer starts. After the timer expires, a snapshot of the person is automatically saved. Useful for **monitoring areas or generating evidence for people entering/exiting**.

**Highlights and Characteristics:**
- Timer runs independently for each detected person using **Python threading**.
- Snapshots are saved after the timer expires.
- Keeps track of multiple people concurrently without freezing the video feed.

**Example Workflow:**
1. Detect and track people using YOLO as in the previous script.
2. For each new person ID, start a timer in a separate thread.
```python
threading.Thread(target=countdown, args=(15, track_id)).start()
```
3. Store remaining time for each active timer in a dictionary.
4. When a timer reaches zero, save a snapshot.
```python
def countdown(seconds, track_id):
    time.sleep(seconds)
    save_snapshot(track_id)
```
5. Clean up inactive timers and maintain the last few frames for smooth tracking.

### Lessons Learned
- Threading ensures that timers do not block the main video feed.
- Timer-based snapshots allow automated capture of events.
- Concurrent snapshot saving must be carefully handled to avoid conflicts.

[Link to full script](Scripts/yolo_timer_counter.py)

---

## Flask Video Stream

### Overview
This script streams video from a **USB camera or similar device** using Flask. It enables remote monitoring via a web browser, which is particularly useful for **Raspberry Pi deployments** or lightweight setups.

**Highlights and Characteristics:**
- Real-time streaming of camera frames over HTTP.
- Accessible from any device on the network.
- Supports simple web-based monitoring.

**Example Workflow:**
1. Capture frames from a USB camera using OpenCV.
```python
camera = cv2.VideoCapture(0)
ret, frame = camera.read()
```
2. Encode frames as JPEG and yield them in a multipart HTTP response.
```python
ret, buffer = cv2.imencode('.jpg', frame)
yield (b'--frame\r\n'
       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
```
3. Serve the video stream on a Flask endpoint.
```python
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
```

### Lessons Learned
- Flask provides a simple interface for live streaming.
- Frame encoding and HTTP streaming must be efficient to maintain smooth playback.
- Works best for **single-camera lightweight monitoring**, complementing detection scripts.

[Link to full script](Scripts/flask_video_stream.py)

---

## Multi-Camera GUI People Counter

### Overview
This is the **crowning jewel** of the project. It integrates all previous techniques into a **user-friendly multi-camera GUI**, combining YOLOv8 detection, persistent centroid tracking, threaded updates, and live entry/exit counters.

Users can select cameras dynamically, and the GUI handles multiple feeds in parallel without freezing. This design allows the system to monitor **different areas simultaneously**—perfect for warehouses, offices, or events—while remaining fully responsive.

**Highlights and Characteristics with Conceptual Explanations:**
- **Dynamic camera selection via GUI**: Users choose which camera feed to monitor from menus.
```python
selectcam("LavaBotas")
```
- **Threaded updates for smooth GUI operation**: Each feed runs in a thread, preventing the interface from freezing.
```python
threading.Thread(target=start_feed).start()
```
- **Real-time tracking and counts**: YOLO detects people, centroids are computed, and crossing events update entry/exit counts live.
```python
if prev_x < line_x and curr_x >= line_x:
    out_count += 1
```
- **Highly scalable for multiple areas**: Cameras are stored in a dictionary. Adding a new camera is as simple as updating the dictionary—no changes to the main logic are required.
```python
Cam_dict = {"adm": "Ti", "prod": "LavaBotas", "new_area": "NewCameraIP"}
```
- **Modular structure**: GUI, detection, tracking, and threading are separate modules, making the system maintainable and extensible.
- **Integration of YOLO detection into Tkinter**: Bounding boxes, centroids, and counts are displayed directly on the live feed.
```python
video_label.config(image=ImageTk.PhotoImage(Image.fromarray(frame)))
```

**Example Workflow:**
1. User selects a camera from the GUI menus.
2. A new thread starts to handle the live feed for that camera.
3. YOLO detects people and assigns persistent IDs.
4. Centroids are tracked to detect crossing events.
5. Entry/exit counts update in real-time.
6. GUI displays live video with bounding boxes, centroids, and counts, all without freezing.

### Lessons Learned
- Threading ensures smooth video updates and responsive GUI operation.
- Persistent IDs maintain accurate counting across frames.
- Modular camera dictionary allows **easy addition of new camera feeds**.
- A GUI provides usability for non-technical operators while retaining flexibility for advanced monitoring.
- Multi-camera threaded architecture is key to scaling from a single feed to multiple areas simultaneously.

[Link to full script](Scripts/multi_camera_gui_counter.py)
