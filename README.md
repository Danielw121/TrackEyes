
# Sistema de Control Ocular con OpenCV y MediaPipe

Este proyecto implementa un sistema de control ocular que permite mover el cursor del ratón y hacer clic utilizando el movimiento de los ojos y los parpadeos. Utiliza OpenCV para la captura de video, MediaPipe para el reconocimiento de rostros y pyautogui para controlar el ratón.

## Requisitos

Antes de ejecutar este proyecto, asegúrate de tener instaladas las siguientes bibliotecas:

- OpenCV
- MediaPipe
- PyAutoGUI

Puedes instalarlas usando pip:

```bash
pip install opencv-python mediapipe pyautogui
```

## Descripción del Código

### Funcionalidades Principales

1. **Captura de Video:**
   Se captura la transmisión en tiempo real de la cámara web utilizando OpenCV (`cv2.VideoCapture(0)`).

2. **Detección Facial y Seguimiento Ocular:**
   El modelo de `MediaPipe Face Mesh` detecta los puntos de referencia faciales, en particular los ojos, para rastrear el movimiento de las pupilas.

3. **Control del Ratón:**
   Se mapea la posición de los ojos a la pantalla, lo que permite mover el cursor del ratón según el movimiento ocular detectado.

4. **Simulación de Clics:**
   - Un **parpadeo simple** genera un clic izquierdo del ratón.
   - Un **parpadeo doble** genera un clic derecho.

5. **Zoom en el Video:**
   El frame de video capturado se amplía por un factor de 2x y luego se recorta para ajustarse a las dimensiones originales de la ventana.

6. **Calibración Manual:**
   El área de detección del movimiento ocular puede ser calibrada manualmente. Al iniciar, el sistema determina automáticamente el centro de la pantalla, y el usuario puede ajustar los límites de la región de seguimiento.

### Controles del Teclado

- **Tecla `c`:** Alterna el modo de calibración para ajustar manualmente los límites de la detección ocular.
- **Tecla `r`:** Reinicia la posición central y los límites del área de seguimiento.
- **Tecla `q`:** Finaliza la ejecución del programa.

### Cálculo de FPS

El sistema también calcula y muestra los frames por segundo (FPS) en la ventana de video para medir el rendimiento.

### Estructura del Código

1. **zoom_frame(frame, factor_zoom):** Esta función aplica un zoom al frame y lo recorta para que mantenga su tamaño original.
   
2. **face_mesh de MediaPipe:** Se utiliza para detectar hasta 468 puntos de referencia en la cara, con mayor precisión en los ojos. El punto de referencia 473 corresponde al centro de la pupila, que se utiliza para el seguimiento ocular.

3. **Detección de parpadeo:** El sistema detecta parpadeos al medir la distancia entre dos puntos de referencia de los párpados (landmarks 380 y 385). Si la distancia es menor a un umbral definido, cuenta como un parpadeo.

4. **Movimiento suave del cursor:** Las posiciones oculares se suavizan mediante una media móvil de las últimas 6 posiciones para evitar movimientos bruscos del cursor.

## Ejecución del Código

Para ejecutar el código, simplemente usa Python desde tu terminal:

```bash
python control_ocular.py
```

Esto abrirá una ventana donde se mostrará el video capturado de la cámara con las marcas de seguimiento y la información de FPS.

## Mejoras Potenciales

- **Multifuncionalidad de los parpadeos:** Se pueden asignar diferentes acciones a los parpadeos o a combinaciones de gestos faciales.
- **Seguimiento de múltiples caras:** Actualmente, el código está diseñado para rastrear una sola cara, pero puede modificarse para admitir múltiples usuarios.
- **Optimización de FPS:** Mejorar el rendimiento para asegurar una experiencia de control fluida en máquinas con especificaciones más bajas.

## Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo libremente con fines educativos o personales, pero el autor no se responsabiliza por el mal uso de este código.
