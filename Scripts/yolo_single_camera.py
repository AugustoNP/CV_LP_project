import cv2
from ultralytics import YOLO
import cvzone
import os
import datetime


absolute_dirpath = os.path.abspath(os.path.dirname(__file__))
output_dirpath = absolute_dirpath.replace("Scripts","Output")

# Carregar modelo YOLO8nano
model = YOLO('yolov8n.pt')
names = model.names

# Posição da linha vertical
line_x = 510

# Função pra salvar a foto
def picture_save():
    
    date = datetime.datetime.now()
    date = date.strftime('%Y-%m-%d_%H-%M-%S')

    try:
        os.makedirs(output_dirpath, exist_ok=False)
        print(f"Foi criada a pasta: {output_dirpath}")
    except FileExistsError:
        print(f"A pasta: {output_dirpath} já existe!")

    filename = f"{output_dirpath}\\output_{str(date)}.jpeg"

    print(filename)

    #BLOCO QUE SALVA A FRAME
    '''
    success = cv2.imwrite(filename, frame)
    if not success:
        print(f"imwrite returned False for filename: {filename}")
    '''
# Dicionário que armazena a posição dos objetos reconhecidos
track_history = {}

# Contador de entrada/saída
in_count = 0 
out_count = 0

# Abrir o vídeo
#cap = cv2.VideoCapture(0) 
camIpTi = 'YOURCAMERAIP'


cap = cv2.VideoCapture(camIpTi)

# VIDEOWRITER
'''
out = cv2.VideoWriter(
    'output.mp4',
    cv2.VideoWriter_fourcc(*'mp4v'),
    15.,
    (1020, 600))
'''
while True:


    
    ret, frame = cap.read()

    if not ret:
        break
    
    # Pegar dimensões e canais de cor da imagem
    height, width, channels = frame.shape
    #line_x = (width//2)
    
    # Determinar o tempo atual e adiocionar na tela
    time = datetime.datetime.now()
    cv2.putText(frame, f"{time}", (width-800,height-30),  cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)


    # Resize n
    frame = cv2.resize(frame, (1020, 600))
    
    # Desenhar a linha de contagem dos objs
    cv2.line(frame, (line_x, 0), (line_x, 600), (0, 255, 255), 2)
    
    # tracking de objetos

    results = model.track(frame, persist=True, classes=[0])

    # Checar se alguma pessoa foi detectada, [0] = pessoas
    if results[0].boxes.id is not None:
        ids = results[0].boxes.id.cpu().numpy().astype(int)
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
        
     
        class_ids = results[0].boxes.cls.int().cpu().tolist()
        
        face_list = []
        for track_id, box, class_id in zip(ids, boxes, class_ids):
            x1, y1, x2, y2 = box
            
            # Desenhar a caixa em torno do objeto 
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            '''            
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_location = face_recognition.face_locations(rgb)
            
            try:
                top, right, bottom, left = face_location
                print(f"A face is located at pixel location Top: {top}, Left: {left}, Bottom: {bottom}, Right: {right}")
            except ValueError:
                cvzone.putTextRect(frame, f'NO PEOPLE', (50, 150), scale=2, thickness=2, colorR=(255, 0, 255))
            '''    



            
            # Adicionar id em cima da caixa do objeto
            cvzone.putTextRect(frame, f'ID: {track_id}', (x1+-20, y1), scale=1.2, thickness=1, colorR=(0, 0, 255))
            
            # Calcular centroíde da caixa
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            
            # Desenhar centroíde
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

            # Contagem e tracking
            if track_id not in track_history:
                track_history[track_id] = []
            
            track_history[track_id].append(center_x)

            # SSe o objeto está em tracking por duas frames
            if len(track_history[track_id]) > 1:
                
                # Pega as posições da frame prévia e a da atual
                prev_x = track_history[track_id][-2]
                curr_x = track_history[track_id][-1]

                # Verifica se "saiu", comparando os valores x da frame antiga e da atual
                if prev_x < line_x and curr_x >= line_x:
                    out_count += 1
                    cv2.line(frame, (line_x, 0), (line_x, 600), (0, 0, 255), 5) # Mudar a cor da linha
                    picture_save()
                    
                # Verifica se "saiu", comparando os valores x da frame antiga e da atual
                elif prev_x > line_x and curr_x <= line_x:
                    in_count += 1
                    cv2.line(frame, (line_x, 0), (line_x, 600), (0, 0, 255), 5) # Mudar a cor da linha
                    picture_save()

            # Atualiza a nosso histórico, mantendo as 5 frames mais recentes
            track_history[track_id] = track_history[track_id][-5:]

    # Mostrar se entrou ou saiu
    cvzone.putTextRect(frame, f'ENTROU: {in_count}', (50, 50), scale=2, thickness=2, colorR=(0, 255, 0))
    cvzone.putTextRect(frame, f'SAIU: {out_count}', (50, 100), scale=2, thickness=2, colorR=(0, 0, 255))

    # Mostrar a frame na janela de contagem e adicionar ao video writer se necessário
    #out.write(frame)
    cv2.imshow("CONTAGEM", frame)
    
    # Aperte 'esc' pra sair do loop
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Limpeza
cap.release()
cv2.destroyAllWindows()
#out.release()