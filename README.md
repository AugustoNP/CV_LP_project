# CV_LP_project

![Python](https://img.shields.io/badge/Python-3.13.3-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-nano-orange)
![Tkinter](https://img.shields.io/badge/Tkinter-8.6-purple)
![Threading](https://img.shields.io/badge/Threading-Yes-red)

> **Note:** All IP addresses, passwords, and camera information have been anonymized to protect sensitive data.

---

## Table of Contents
- [English](#english)
  - [Overview](#overview)
  - [1. Simple Difference-Based Detection](#1-simple-difference-based-detection)
  - [2. YOLO Single Camera People Counter](#2-yolo-single-camera-people-counter)
  - [3. YOLO Timer-Based People Counter](#3-yolo-timer-based-people-counter)
  - [4. Flask Video Stream](#4-flask-video-stream)
  - [5. Multi-Camera GUI People Counter](#5-multi-camera-gui-people-counter)
- [Português](#português)
  - [Visão Geral](#visão-geral)
  - [1. Detecção Baseada em Diferença Simples](#1-detecção-baseada-em-diferença-simples)
  - [2. Contador de Pessoas YOLO em Câmera Única](#2-contador-de-pessoas-yolo-em-câmera-única)
  - [3. Contador de Pessoas YOLO com Temporizador](#3-contador-de-pessoas-yolo-com-temporizador)
  - [4. Streaming de Vídeo com Flask](#4-streaming-de-vídeo-com-flask)
  - [5. Contador de Pessoas GUI Multi-Câmera](#5-contador-de-pessoas-gui-multi-câmera)

---

## English

### Overview
This repository contains a series of computer vision scripts designed to **count people in real-time** across one or multiple cameras. The project evolved from basic frame difference detection to YOLO-based tracking, timer-enabled snapshots, Flask video streaming, and finally a **multi-camera GUI people counter**.  

[Back to Top](#cv_lp_project)

---

### 1. Simple Difference-Based Detection

**Highlights:**
- Extremely lightweight; runs on low-power devices.
- Detects **moving objects** without complex models.
- Allows quick prototyping.

**Example Workflow:**
```python
first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
first_frame = cv2.GaussianBlur(first_frame, (21, 21), 0)

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (21, 21), 0)

delta = cv2.absdiff(first_frame, gray)
thresh = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for c in contours:
    if cv2.contourArea(c) > min_area:
        cx = int((x + x + w) / 2)
        if cx > line_x: count_exit += 1
```

**Lessons Learned:**
- Sensitive to lighting changes and shadows.
- Thresholds and minimum contour area require tuning.
- Simple and effective for testing but not robust for multi-camera setups.

[Full script](Scripts/simple_difference_detection.py) | [Back to Top](#cv_lp_project)

---

### 2. YOLO Single Camera People Counter

**Highlights:**
- Real-time **object detection** using YOLOv8 nano.
- Persistent **tracking IDs** prevent double-counting.
- Simple vertical line counting.
- Can save snapshots of detected people crossing the line.

**Example Workflow:**
```python
ret, frame = cap.read()
results = model.track(frame, persist=True, classes=[0])

for track_id, box in zip(results[0].boxes.id, results[0].boxes.xyxy):
    x1, y1, x2, y2 = box
    center_x = (x1 + x2) // 2

if prev_x < line_x and curr_x >= line_x:
    out_count += 1
```

**Lessons Learned:**
- YOLO improves detection accuracy over simple frame differencing.
- Centroid tracking is essential to maintain correct counts.
- Single-camera setup is easier for testing; multi-camera setups require further integration.

[Full script](Scripts/yolo_single_camera.py) | [Back to Top](#cv_lp_project)

---

### 3. YOLO Timer-Based People Counter

**Highlights:**
- Adds timers for each detected person using **Python threading**.
- Snapshots saved automatically when timer expires.
- Handles multiple people concurrently without freezing the video feed.

**Example Workflow:**
```python
threading.Thread(target=countdown, args=(15, track_id)).start()

def countdown(seconds, track_id):
    time.sleep(seconds)
    save_snapshot(track_id)
```

**Lessons Learned:**
- Threading ensures the main video feed is not blocked.
- Timer-based snapshots allow automated capture of events.
- Concurrent snapshot saving must be handled carefully.

[Full script](Scripts/yolo_timer_counter.py) | [Back to Top](#cv_lp_project)

---

### 4. Flask Video Stream

**Highlights:**
- Streams video from USB cameras over HTTP.
- Accessible from any device on the network.
- Works best for lightweight single-camera monitoring.

**Example Workflow:**
```python
camera = cv2.VideoCapture(0)
ret, frame = camera.read()

ret, buffer = cv2.imencode('.jpg', frame)
yield (b'--frame\r\n'
       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
```

**Lessons Learned:**
- Flask provides a simple interface for live streaming.
- Frame encoding must be efficient for smooth playback.

[Full script](Scripts/flask_video_stream.py) | [Back to Top](#cv_lp_project)

---

### 5. Multi-Camera GUI People Counter

**Highlights:**
- Dynamic camera selection via GUI.
- Threaded updates for smooth GUI operation.
- Real-time tracking and counting with YOLO.
- Highly scalable; cameras stored in a dictionary.
- Modular structure: GUI, detection, tracking, threading.

**Example Workflow:**
```python
selectcam("LavaBotas")
threading.Thread(target=start_feed).start()

if prev_x < line_x and curr_x >= line_x:
    out_count += 1

Cam_dict = {"adm": "Ti", "prod": "LavaBotas", "new_area": "NewCameraIP"}
video_label.config(image=ImageTk.PhotoImage(Image.fromarray(frame)))
```

**Lessons Learned:**
- Threading ensures smooth video updates and responsive GUI.
- Persistent IDs maintain accurate counting.
- Modular camera dictionary allows easy addition of new cameras.
- Multi-camera architecture is key to scaling from a single feed to multiple areas.

[Full script](Scripts/multi_camera_gui_counter.py) | [Back to Top](#cv_lp_project)

---

## Português

### Visão Geral
Este repositório contém uma série de scripts de visão computacional projetados para **contar pessoas em tempo real** em uma ou várias câmeras. O projeto evoluiu da detecção básica por diferença de quadros ao rastreamento com YOLO, snapshots com temporizador, streaming de vídeo com Flask e, finalmente, um **contador de pessoas GUI multi-câmera**.  

[Voltar ao Topo](#cv_lp_project)

---

### 1. Detecção Baseada em Diferença Simples

**Destaques:**
- Extremamente leve; roda em dispositivos de baixo consumo.
- Detecta **objetos em movimento** sem modelos complexos.
- Permite prototipagem rápida.

**Exemplo de Fluxo:**
```python
first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
first_frame = cv2.GaussianBlur(first_frame, (21, 21), 0)

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (21, 21), 0)

delta = cv2.absdiff(first_frame, gray)
thresh = cv2.threshold(delta, 50, 255, cv2.THRESH_BINARY)[1]

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for c in contours:
    if cv2.contourArea(c) > min_area:
        cx = int((x + x + w) / 2)
        if cx > line_x: count_exit += 1
```

**Lições Aprendidas:**
- Sensível a mudanças de iluminação e sombras.
- Limiares e área mínima de contorno exigem ajuste.
- Simples e eficaz, mas não robusto para multi-câmeras.

[Script completo](Scripts/simple_difference_detection.py) | [Voltar ao Topo](#cv_lp_project)

---

### 2. Contador de Pessoas YOLO em Câmera Única

**Destaques:**
- Detecção em tempo real com **YOLOv8 nano**.
- IDs persistentes evitam dupla contagem.
- Contagem simples com linha vertical.
- Possibilidade de snapshots automáticos.

**Exemplo de Fluxo:**
```python
ret, frame = cap.read()
results = model.track(frame, persist=True, classes=[0])

for track_id, box in zip(results[0].boxes.id, results[0].boxes.xyxy):
    x1, y1, x2, y2 = box
    center_x = (x1 + x2) // 2

if prev_x < line_x and curr_x >= line_x:
    out_count += 1
```

**Lições Aprendidas:**
- YOLO aumenta a precisão em relação à diferença de quadros.
- Rastreamento por centróides é essencial para contagens corretas.
- Configuração de uma câmera é mais simples; multi-câmera requer integração adicional.

[Script completo](Scripts/yolo_single_camera.py) | [Voltar ao Topo](#cv_lp_project)

---

### 3. Contador de Pessoas YOLO com Temporizador

**Destaques:**
- Adiciona temporizadores para cada pessoa usando **threading do Python**.
- Snapshots salvos automaticamente ao expirar o temporizador.
- Rastreia múltiplas pessoas simultaneamente sem travar o feed de vídeo.

**Exemplo de Fluxo:**
```python
threading.Thread(target=countdown, args=(15, track_id)).start()

def countdown(seconds, track_id):
    time.sleep(seconds)
    save_snapshot(track_id)
```

**Lições Aprendidas:**
- Threading evita travamento do feed principal.
- Snapshots automatizam a captura de eventos.
- Salvar simultaneamente exige cuidado.

[Script completo](Scripts/yolo_timer_counter.py) | [Voltar ao Topo](#cv_lp_project)

---

### 4. Streaming de Vídeo com Flask

**Destaques:**
- Transmite vídeo de câmeras USB via HTTP.
- Acessível pela rede via navegador.
- Ideal para monitoramento leve de uma única câmera.

**Exemplo de Fluxo:**
```python
camera = cv2.VideoCapture(0)
ret, frame = camera.read()

ret, buffer = cv2.imencode('.jpg', frame)
yield (b'--frame\r\n'
       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
```

**Lições Aprendidas:**
- Flask fornece streaming ao vivo de forma simples.
- Codificação eficiente mantém reprodução fluida.

[Script completo](Scripts/flask_video_stream.py) | [Voltar ao Topo](#cv_lp_project)

---

### 5. Contador de Pessoas GUI Multi-Câmera

**Destaques:**
- GUI permite seleção dinâmica de câmeras.
- Atualizações em threads para operação suave.
- Rastreamento e contagem em tempo real com YOLO.
- Altamente escalável; câmeras armazenadas em um dicionário.
- Estrutura modular: GUI, detecção, rastreamento, threading.

**Exemplo de Fluxo:**
```python
selectcam("LavaBotas")
threading.Thread(target=start_feed).start()

if prev_x < line_x and curr_x >= line_x:
    out_count += 1

Cam_dict = {"adm": "Ti", "prod": "LavaBotas", "new_area": "NewCameraIP"}
video_label.config(image=ImageTk.PhotoImage(Image.fromarray(frame)))
```

**Lições Aprendidas:**
- Threading garante atualizações suaves.
- IDs persistentes mantêm contagens precisas.
- Dicionário modular simplifica adicionar câmeras.
- Arquitetura multi-câmera escalável.

[Script completo](Scripts/multi_camera_gui_counter.py) | [Voltar ao Topo](#cv_lp_project)


