import cv2
import mediapipe as mp
import pyautogui
import time

def zoom_frame(frame, factor_zoom):
    # Obtener las dimensiones originales del frame
    alto_original, ancho_original = frame.shape[:2]
    
    # Calcular las nuevas dimensiones
    nuevo_ancho = int(ancho_original * factor_zoom)
    nuevo_alto = int(alto_original * factor_zoom)
    
    # Redimensionar el frame usando la interpolación
    frame_zoom = cv2.resize(frame, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LINEAR)
    
    # Recortar el centro del frame con zoom para que tenga el mismo tamaño que el frame original
    start_x = (nuevo_ancho - ancho_original) // 2
    start_y = (nuevo_alto - alto_original) // 2
    frame_zoom = frame_zoom[start_y:start_y + alto_original, start_x:start_x + ancho_original]

    return frame_zoom

# Inicializar la cámara (0 es el índice de la cámara predeterminada)
cap = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,  # Detectar solo una cara
    refine_landmarks=True,  # Mayor precisión en los puntos de referencia del ojo
    min_detection_confidence=0.5,  # Ajustar la confianza de detección
    min_tracking_confidence=0.5,
)
screen_w, screen_h = pyautogui.size()

modo_calibracion = True

pos_central_x = 0
pos_central_y = 0

limite_x1 = 0
limite_x2 = 0
limite_y1 = 0
limite_y2 = 0

screen_w, screen_h = 1920, 1080  # Dimensiones de la pantalla
posiciones_x = []  # Lista para almacenar las últimas posiciones X del cursor
posiciones_y = []  # Lista para almacenar las últimas posiciones Y del cursor
tamaño_ventana = 6  # Tamaño de la ventana para la media móvil

# Variables para calcular FPS
prev_frame_time = 0
new_frame_time = 0

# Variables para la detección del parpadeo
PARPADEO_UMBRAL = 0.03  # Ajusta este valor según sea necesario
PARPADEO_FRAMES_MIN = 6  # Número mínimo de cuadros consecutivos con el ojo cerrado
contador_parpadeo = 0

while True:
    # Capturar frame por frame
    ret, frame = cap.read()
    
    if not ret:
        print('Hubo un error con la camara')
        break

    # Obtener el frame con zoom
    frame = zoom_frame(frame, factor_zoom = 2.0)
    
    # Invertir el frame
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks

    frame_h, frame_w, _ = frame.shape

    # lineas para marcar la posicion central
    cv2.line(frame, (pos_central_x, 0), (pos_central_x, frame_h), (0, 0, 255), 1)
    cv2.line(frame, (0, pos_central_y), (frame_w, pos_central_y), (0, 0, 255), 1)

    # Recuadro del limite
    cv2.rectangle(frame, (limite_x1, limite_y1), (limite_x2, limite_y2), (0, 255, 0), 2)

    if landmark_points:
        landmarks = landmark_points[0].landmark
        centro_pupila = landmarks[473]
        x, y = int(centro_pupila.x * frame_w), int(centro_pupila.y * frame_h)

        # Visualizar landmarks 33 y 159
        cv2.circle(frame, (int(landmarks[385].x * frame_w), int(landmarks[385].y * frame_h)), 3, (255, 0, 0), -1)  # Rojo
        cv2.circle(frame, (int(landmarks[380].x * frame_w), int(landmarks[380].y * frame_h)), 3, (0, 0, 255), -1)  # Azul

        
        # Detección del parpadeo
        distancia_parpados = abs(landmarks[385].y - landmarks[380].y)
        if distancia_parpados < PARPADEO_UMBRAL:
            contador_parpadeo += 1
        else:
            if contador_parpadeo >= PARPADEO_FRAMES_MIN:
                if contador_parpadeo >= PARPADEO_FRAMES_MIN * 2: # Doble parpadeo
                    pyautogui.click(button='right')  
                else:
                    pyautogui.click()  # Simular clic izquierdo del mouse
            contador_parpadeo = 0

        # Suavizado del movimiento
        if 'last_x' in locals():
            x = int(last_x * 0.7 + x * 0.3)
            y = int(last_y * 0.7 + y * 0.3)
        last_x, last_y = x, y 

        # Usar el landmark del centro de la pupila 
        centro_pupila = landmarks[473]

        # Dibujar centro de pupila en frame
        x = int(centro_pupila.x * frame_w)
        y = int(centro_pupila.y * frame_h)
        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        # marcar posicion central 
        if pos_central_x == 0 and pos_central_y == 0:
            pos_central_x = x
            pos_central_y = y

            limite_x1 = pos_central_x
            limite_x2 = pos_central_x
            limite_y1 = pos_central_y
            limite_y2 = pos_central_y

            modo_calibracion = True

        # Expandir los limites al activar la calibracion
        if modo_calibracion:
            if x < limite_x1:
                limite_x1 = x
            if x > limite_x2:
                limite_x2 = x
            if y < limite_y1:
                limite_y1 = y
            if y > limite_y2:
                limite_y2 = y

        # Mapear la posición del ojo dentro del recuadro a la pantalla
        if limite_x1 < x < limite_x2 and limite_y1 < y < limite_y2 and not modo_calibracion:
            relative_x = (x - limite_x1) / (limite_x2 - limite_x1)
            relative_y = (y - limite_y1) / (limite_y2 - limite_y1)

            screen_x = int(screen_w * relative_x)
            screen_y = int(screen_h * relative_y)

            # Agregar las posiciones actuales a las listas
            posiciones_x.append(screen_x)
            posiciones_y.append(screen_y)

            # Mantener solo las últimas 'tamaño_ventana' posiciones
            posiciones_x = posiciones_x[-tamaño_ventana:]
            posiciones_y = posiciones_y[-tamaño_ventana:]

            # Calcular la media de las posiciones
            screen_x_suave = int(sum(posiciones_x) / len(posiciones_x))
            screen_y_suave = int(sum(posiciones_y) / len(posiciones_y))

            # Mover el cursor a la posición suavizada
            pyautogui.moveTo(screen_x_suave, screen_y_suave)

        # # Mover cursor en pantalla
        # screen_x = screen_w * centro_pupila.x
        # screen_y = screen_h * centro_pupila.y
        # pyautogui.moveTo(screen_x, screen_y)
        
        # Calcular FPS
        new_frame_time = time.time()
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        fps = str(fps)

        # Mostrar FPS en el cuadro
        cv2.putText(frame, f"FPS: {fps}", (5, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    frame = cv2.putText(frame, 'Q salir', (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
    frame = cv2.putText(frame, 'R reinicar centro y limites', (5, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
    frame = cv2.putText(frame, 'C calibrar limites', (5, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)


    if modo_calibracion:
        mensaje_calibracion = 'Calibracion activada'
    else:
        mensaje_calibracion = ''
    frame = cv2.putText(frame, mensaje_calibracion, (5, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

    # Mostrar el frame original y el frame con zoom
    cv2.imshow('Frame con Zoom', frame)
    
    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord('c'):
        modo_calibracion = not modo_calibracion

    if tecla == ord('r'): # Reiniciar centro
        pos_central_x = 0
        pos_central_y = 0

    if tecla == ord('q'): # Salir del bucle si se presiona la tecla 'q'
        break

# Liberar la cámara y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()