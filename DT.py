import cv2
import numpy as np

# Iniciar la captura de video desde la cámara (0 para la cámara predeterminada)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    # Capturar frame por frame
    ret, frame = cap.read()
    if not ret:
        break  # Salir si no hay más fotogramas

    # Convertir el frame a escala de grises
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplicar un filtro Gaussiano para reducir el ruido
    gauss = cv2.GaussianBlur(gris, (5, 5), 0)

    # Aplicar el detector de bordes Canny
    canny = cv2.Canny(gauss, 50, 150)

    # Encontrar los contornos en la imagen procesada
    contornos, _ = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Dibujar los contornos detectados en la imagen original
    cv2.drawContours(frame, contornos, -1, (0, 0, 255), 2)

    # Mostrar la imagen con los contornos detectados
    cv2.imshow("Detección de Obstáculos", frame)

    # Salir del bucle al presionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
