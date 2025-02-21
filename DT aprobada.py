import cv2
import numpy as np
import time
import platform
import os

# Verificar si estamos en una Raspberry Pi
def is_raspberry_pi():
    try:
        with open('/proc/device-tree/model', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except FileNotFoundError:
        return False

# Configuración de GPIO solo si estamos en una Raspberry Pi
if is_raspberry_pi():
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    MOTOR_IZQUIERDO = 17
    MOTOR_DERECHO = 27

    GPIO.setup(MOTOR_IZQUIERDO, GPIO.OUT)
    GPIO.setup(MOTOR_DERECHO, GPIO.OUT)

    def activar_motor_izquierdo():
        GPIO.output(MOTOR_IZQUIERDO, GPIO.HIGH)
        GPIO.output(MOTOR_DERECHO, GPIO.LOW)
        print("[GPIO] Motor izquierdo activado")

    def activar_motor_derecho():
        GPIO.output(MOTOR_IZQUIERDO, GPIO.LOW)
        GPIO.output(MOTOR_DERECHO, GPIO.HIGH)
        print("[GPIO] Motor derecho activado")

    def activar_ambos_motores():
        GPIO.output(MOTOR_IZQUIERDO, GPIO.HIGH)
        GPIO.output(MOTOR_DERECHO, GPIO.HIGH)
        print("[GPIO] Ambos motores activados")

    def detener_motores():
        GPIO.output(MOTOR_IZQUIERDO, GPIO.LOW)
        GPIO.output(MOTOR_DERECHO, GPIO.LOW)
        print("[GPIO] Motores detenidos")
else:
    print("Ejecutando en modo simulado (sin GPIO)")

    def activar_motor_izquierdo():
        print("[SIMULADO] Motor izquierdo activado")

    def activar_motor_derecho():
        print("[SIMULADO] Motor derecho activado")

    def activar_ambos_motores():
        print("[SIMULADO] Ambos motores activados")

    def detener_motores():
        print("[SIMULADO] Motores detenidos")

def main():
    # Parámetros para ajustar el rango de visión (ROI)
    roi_width = 400
    roi_height = 300

    # Forzar el uso de V4L2 en lugar de GStreamer
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return

    cv2.namedWindow('Camara en Vivo')
    cv2.namedWindow('Bordes Izquierda')
    cv2.namedWindow('Bordes Centro')
    cv2.namedWindow('Bordes Derecha')

    last_message_time = time.time()
    message_delay = 1.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: No se pudo capturar la imagen.")
                break

            height, width, _ = frame.shape
            roi_width = min(roi_width, width)
            roi_height = min(roi_height, height)

            x_start = (width - roi_width) // 2
            y_start = (height - roi_height) // 2
            x_end = x_start + roi_width
            y_end = y_start + roi_height

            roi_frame = frame[y_start:y_end, x_start:x_end]

            third_width = roi_width // 3
            left_section = roi_frame[:, :third_width]
            middle_section = roi_frame[:, third_width:2 * third_width]
            right_section = roi_frame[:, 2 * third_width:]

            def process_section(section):
                gray = cv2.cvtColor(section, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                return edges, np.count_nonzero(edges)

            left_edges, left_count = process_section(left_section)
            center_edges, center_count = process_section(middle_section)
            right_edges, right_count = process_section(right_section)

            current_time = time.time()
            if current_time - last_message_time > message_delay:
                min_borders = min(left_count, center_count, right_count)

                if min_borders == center_count:
                    print("Seguir derecho")
                    activar_ambos_motores()
                elif min_borders == left_count:
                    print("Girar izquierda")
                    activar_motor_izquierdo()
                elif min_borders == right_count:
                    print("Girar derecha")
                    activar_motor_derecho()

                last_message_time = current_time

            cv2.imshow('Camara en Vivo', roi_frame)
            cv2.imshow('Bordes Izquierda', left_edges)
            cv2.imshow('Bordes Centro', center_edges)
            cv2.imshow('Bordes Derecha', right_edges)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        detener_motores()
        cap.release()
        cv2.destroyAllWindows()
        if is_raspberry_pi():
            GPIO.cleanup()

if __name__ == "__main__":
    main()


