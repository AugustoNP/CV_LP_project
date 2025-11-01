import datetime
import cv2
import numpy as np
import os
absolute_dirpath = os.path.abspath(os.path.dirname(__file__))
output_dirpath = absolute_dirpath.replace("Scripts","Output")

#variaveis globais
width = 0
height = 0
ContadorEntradas = 0
ContadorSaidas = 0
AreaContornoLimiteMin = 4000  #este valor eh empirico. Ajuste-o conforme sua necessidade 
ThresholdBinarizacao = 50  #este valor eh empirico, Ajuste-o conforme sua necessidade
OffsetLinhasRef = 150  #este valor eh empirico. Ajuste- conforme sua necessidade.

#camera = cv2.VideoCapture(0)

# Adicionar stream local
camIp = 'YOURCAMERAIP'
camIpAxis = 'YOURCAMERAIP'
camera = cv2.VideoCapture(camIp)

width = 320
height = 240
camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)



PrimeiroFrame = None

#faz algumas leituras de frames antes de consierar a analise
#motivo: algumas camera podem demorar mais para se "acosumar a luminosidade" quando ligam, capturando frames consecutivos com muita variacao de luminosidade. Para nao levar este efeito ao processamento de imagem, capturas sucessivas sao feitas fora do processamento da imagem, dando tempo para a camera "se acostumar" a luminosidade do ambiente

for i in range(0,20):
    (grabbed, Frame) = camera.read()
firstframe = True
while True:

    if firstframe == True:
        filename = f"{output_dirpath}/outputFIRST.jpeg"
        success = cv2.imwrite(filename, Frame)
        if not success:
            print(f"imwrite returned False for filename: {filename}")

    #le primeiro frame e determina resolucao da imagem
    (grabbed, Frame) = camera.read()
    height,width = Frame.shape[:2]

    #se nao foi possivel obter frame, nada mais deve ser feito
    if not grabbed:
        break

    #converte frame para escala de cinza e aplica efeito blur (para realcar os contornos)
    FrameGray = cv2.cvtColor(Frame, cv2.COLOR_BGR2GRAY)
    FrameGray = cv2.GaussianBlur(FrameGray, (21, 21), 0)

    #como a comparacao eh feita entre duas imagens subsequentes, se o primeiro frame eh nulo (ou seja, primeira "passada" no loop), este eh inicializado
    if PrimeiroFrame is None:
        PrimeiroFrame = FrameGray
        continue

    #ontem diferenca absoluta entre frame inicial e frame atual (subtracao de background)
    #alem disso, faz a binarizacao do frame com background subtraido 
    FrameDelta = cv2.absdiff(PrimeiroFrame, FrameGray)
    FrameThresh = cv2.threshold(FrameDelta, ThresholdBinarizacao, 255, cv2.THRESH_BINARY)[1]
    
    #faz a dilatacao do frame binarizado, com finalidade de elimunar "buracos" / zonas brancas dentro de contornos detectados. 
    #Dessa forma, objetos detectados serao considerados uma "massa" de cor preta 
    #Alem disso, encontra os contornos apos dilatacao.
    FrameThresh = cv2.dilate(FrameThresh, None, iterations=2)
    contours, _ = cv2.findContours(FrameThresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    CoordenadaYLinhaEntrada = int((height / 2.4)-OffsetLinhasRef)
    CoordenadaXLinhaEntrada = int((width / 2.4)-OffsetLinhasRef)

    CoordenadaYLinhaSaida = int((height / 2.4)+OffsetLinhasRef)
    CoordenadaXLinhaSaida = int((width / 2.4)+OffsetLinhasRef)

    # Adicionando linha vertical
    #cv2.line(Frame, (CoordenadaXLinhaEntrada,0), (CoordenadaXLinhaEntrada,height), (255, 0, 0), 2)
    cv2.line(Frame, (CoordenadaXLinhaSaida,0), (CoordenadaXLinhaSaida,height), (0, 0, 255), 2)


    it = 1
    QtdeContornos = 0
    rect_list = []
    for c in contours: # Check if any contours were found
        #c = max(contours, key=cv2.contourArea)

        #cv2.drawContours(Frame, c, -1, (255,0,0), 3)

        #print(c)
        
        if cv2.contourArea(c) < AreaContornoLimiteMin:
            continue


        #obtem coordenadas do contorno (na verdade, de um retangulo que consegue abrangir todo ocontorno) e
        #realca o contorno com um retangulo.
        (x, y, w, h) = cv2.boundingRect(c) #x e y: coordenadas do vertice superior esquerdo
                                            #w e h: respectivamente largura e altura do retangulo

        cv2.rectangle(Frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(Frame, (f"IT : {str(it)}"), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        rect_list.append([x, y, w, h,])

    
        hull = cv2.convexHull(c)

        # Desenhe o Hull
        cv2.drawContours(Frame, [hull], 0 , (0,225,130), 3) 

        #determina o ponto central do contorno e desenha um circulo para indicar
        
        CoordenadaXCentroContorno = int((x+x+w)/2)
        CoordenadaYCentroContorno = int((y+y+h)/2)
        PontoCentralContorno = (CoordenadaXCentroContorno,CoordenadaYCentroContorno)
        cv2.circle(Frame, PontoCentralContorno, 1, (0, 255, 0), 5)
        
        
        #if firstframe == False:
        if CoordenadaXCentroContorno >= CoordenadaXLinhaSaida:
            contains = True
            cv2.putText(Frame, f"Bloco {it} Contem: ".format(str(contains)), (10, (90+(20*it))),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 0, 1), 2)
            try:
                if contains == True and previous_contains == False:

                    date = datetime.datetime.now()
                    date = date.strftime('%Y-%m-%d_%H-%M-%S')

                    try:
                        os.makedirs(output_dirpath, exist_ok=False)
                        print(f"Foi criada a pasta: {output_dirpath}")
                    except FileExistsError:
                        #print(f"A pasta: {output_dirpath} já existe!")
                        pass

                    filename = f"{output_dirpath}/output_{str(date)}.jpeg"

                    print(filename)

                    #BLOCO QUE SALVA A FRAME
                    
                    success = cv2.imwrite(filename, Frame)
                    if not success:
                        print(f"imwrite returned False for filename: {filename}")
                        

                    print("ENTROU")
                    ContadorSaidas += 1
            except NameError:
                print("VAR NAO DEF")
                
                
        
        elif CoordenadaXCentroContorno <= CoordenadaXLinhaSaida:
            contains = False
            cv2.putText(Frame, "Contem: {}".format(str(contains)), (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (1, 0, 250), 2)
        
        it += 1


    print(rect_list)
    grouped_rects, weights = cv2.groupRectangles(rect_list, groupThreshold=1, eps=1.0)
    for (x, y, w, h,) in grouped_rects:
        
        cv2.rectangle(Frame, (x, y), (x + w, y + h), (255, 255, 0), 2)
                #determina o ponto central do contorno e desenha um circulo para indicar
       

    #Escreve na imagem o numero de pessoas que entraram ou sairam da area vigiada
    cv2.putText(Frame, "Entradas: {}".format(str(ContadorEntradas)), (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 0, 1), 2)
    cv2.putText(Frame, "Saidas: {}".format(str(ContadorSaidas)), (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    
    Frame_re = cv2.resize(Frame, (640, 480))
    FrameThresh_re = cv2.resize(FrameThresh, (320, 240))
    FrameThresh_re = cv2.cvtColor(FrameThresh_re, cv2.COLOR_GRAY2BGR)
    FrameDelta_re = cv2.resize(FrameDelta, (320, 240))
    FrameDelta_re = cv2.cvtColor(FrameDelta_re, cv2.COLOR_GRAY2BGR)

    delT_Display = np.concatenate((FrameThresh_re, FrameDelta_re), axis = 0)
    finalDisplay = np.concatenate((Frame_re,delT_Display), axis = 1)
    #finalDisplay = cv2.hconcat([Frame_re,FrameThresh_re]) 
    
    #cv2.imshow("Original", Frame)
    cv2.imshow("Original/Thresh/Delta", finalDisplay)
    cv2.waitKey(1);

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    
    try:
        if CoordenadaXCentroContorno >= CoordenadaXLinhaSaida:
            previous_contains = True

        elif CoordenadaXCentroContorno <= CoordenadaXLinhaSaida:
            previous_contains = False
        
    
        
    except NameError:
        pass
    

    firstframe == False

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
