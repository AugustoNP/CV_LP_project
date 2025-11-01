import cv2
from ultralytics import YOLO
import cvzone
import os
import datetime
from tkinter import *
import threading
from tkinter.ttk import *
from PIL import Image, ImageTk

# Create a global variable to store the selected camera name
global current_Camera_name
current_Camera_name = None

# Create a global variable for the video label and its container
video_label = None
video_frame = None

# creating tkinter window
root = Tk()
root.title('CV_project')
root.geometry("1280x720")
root.attributes('-fullscreen', True)
root.configure(bg="#254b7a")

Cam_dict = {"adm" : "Ti",
            "prod" : "LavaBotas",
            "cam" : 0}

def selectcam(camera_name):
    global current_Camera_name
    current_Camera_name = camera_name
    print(f"Camera selected: {current_Camera_name}")

def start_thread():
    global current_Camera_name
    if not current_Camera_name:
        print("SELECIONE UMA CAMERA ANTES")
        return

    # Cria Frame e label
    global video_label, video_frame
    if video_frame is None:
        video_frame = Frame(root, width=1020, height=600)
        video_frame.pack_propagate(False) # shrin
        video_frame.place(relx=0.5, rely=0.5, anchor=CENTER) # Centro
        video_label = Label(video_frame)
        video_label.pack(expand=True, fill='both') # Faz o label encher a frame

    thread = threading.Thread(target=start_feed)
    thread.daemon = True
    thread.start()


# Criar menubar

menubar = Menu(root)
cam = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Monitorar', menu=cam)
cam.add_command(label='Iniciar Feed', command=start_thread)
cam.add_command(label='Exit', command=root.destroy)
cam.add_separator()

# Menu área
area_menu = Menu(cam, tearoff=0)
cam.add_cascade(label='Área', menu=area_menu)

# submenu Adm
adm_menu = Menu(area_menu, tearoff=0)
area_menu.add_cascade(label='Administrativo', menu=adm_menu)

# Adicionar comandos ao ADM
for key, value in Cam_dict.items():
    if key == "adm":
        adm_menu.add_command(label=str(value), command=lambda val=value: selectcam(val))


# Submenu Produção
prod_menu = Menu(area_menu, tearoff=0)
area_menu.add_cascade(label='Produção', menu=prod_menu)

# Comando Produção
for key, value in Cam_dict.items():
    if key == "prod":
        prod_menu.add_command(label=str(value), command=lambda val=value: selectcam(val))

# submenu Cam
adm_menu = Menu(area_menu, tearoff=0)
area_menu.add_cascade(label='Webcam', menu=adm_menu)

# Adicionar comandos ao Cam
for key, value in Cam_dict.items():
    if key == "cam":
        adm_menu.add_command(label=str(value), command=lambda val=value: selectcam(val))


# Menu de ajuda
help_ = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Ajuda', menu=help_)
help_.add_separator()
help_.add_command(label='README', command=None)

# Menu display
root.config(menu=menubar)

def update_frame(cap, model, ip_Dict, current_cam_ip, video_label, line_x, track_history, in_count, out_count):
    # Função recursiva para dar update na Frame
    ret, frame = cap.read()

    if ret:
        # Redefinir Tamanho
        frame = cv2.resize(frame, (1020, 600))
        height, width, _ = frame.shape

        # Desenhar Linha de contagem
        cv2.line(frame, (line_x, 0), (line_x, 600), (0, 255, 255), 2)

        # Lógica "Original"
        results = model.track(frame, persist=True, classes=[0], verbose=False)

        if results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            class_ids = results[0].boxes.cls.int().cpu().tolist()

            for track_id, box, class_id in zip(ids, boxes, class_ids):
                x1, y1, x2, y2 = box

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cvzone.putTextRect(frame, f'ID: {track_id}', (x1-20, y1), scale=1.2, thickness=1, colorR=(0, 0, 255))

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

                if track_id not in track_history:
                    track_history[track_id] = []

                track_history[track_id].append(center_x)

                if len(track_history[track_id]) > 1:
                    prev_x = track_history[track_id][-2]
                    curr_x = track_history[track_id][-1]

                    if prev_x < line_x and curr_x >= line_x:
                        out_count += 1
                        cv2.line(frame, (line_x, 0), (line_x, 600), (0, 0, 255), 5)
                    elif prev_x > line_x and curr_x <= line_x:
                        in_count += 1
                        cv2.line(frame, (line_x, 0), (line_x, 600), (0, 0, 255), 5)
                        # picture_save(frame, current_cam_ip, ip_Dict)

                track_history[track_id] = track_history[track_id][-5:]

        cvzone.putTextRect(frame, f'ENTROU: {in_count}', (50, 50), scale=2, thickness=2, colorR=(0, 255, 0))
        cvzone.putTextRect(frame, f'SAIU: {out_count}', (50, 100), scale=2, thickness=2, colorR=(0, 0, 255))
        
        # Converter a imagem pra pillow
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        
        # Pillow pra photoimiage
        image_tk = ImageTk.PhotoImage(image=image)
        
        # Mudar o label com a nova imagem
        video_label.config(image=image_tk)
        video_label.image = image_tk  # Keep a reference to prevent garbage collection
        
    # 10ms pro próximo update
    root.after(10, update_frame, cap, model, ip_Dict, current_cam_ip, video_label, line_x, track_history, in_count, out_count)


def start_feed():
    # Carregar modelo YOLO8nano
    model = YOLO('yolov8n.pt')
    names = model.names

    # Posição da linha vertical
    line_x = 510

    # Dicionário que armazena a posição dos objetos reconhecidos
    track_history = {}

    # Contador de entrada/saída
    in_count = 0
    out_count = 0

    # Abrir o vídeo
    ip_Dict = { "Ti" : 'YOURCAMERAIP',
                "LavaBotas" : 'YOURCAMERAIP',
                "Cam0" : 0
                }

    current_cam_ip = (ip_Dict[current_Camera_name])
    cap = cv2.VideoCapture(current_cam_ip)

    # Começar o loop contínuo de update de frames
    update_frame(cap, model, ip_Dict, current_cam_ip, video_label, line_x, track_history, in_count, out_count)


root.mainloop()