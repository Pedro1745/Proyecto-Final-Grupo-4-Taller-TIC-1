import RPi.GPIO as GPIO
import pygame
import time
import threading

# Configuración de la Raspberry Pi
GPIO.setmode(GPIO.BCM)  # Usamos el esquema de numeración BCM
GPIO.setwarnings(False)  # Desactivamos las advertencias

# Definir pines
servo_pin = 23  # Pin GPIO para el servomotor
trigger_pin = 12  # Pin GPIO para el Trigger del sensor ultrasónico
echo_pin = 6  # Pin GPIO para el Echo del sensor ultrasónico

# Configuración del servomotor
GPIO.setup(servo_pin, GPIO.OUT)
servo = GPIO.PWM(servo_pin, 50)  # 50Hz de frecuencia (estándar para servos)
servo.start(0)  # Inicializa el servomotor en la posición 0

# Configuración del sensor ultrasónico
GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)

# Definir el pin al que está conectado el láser
laser_pin = 25  # Pin GPIO para el láser

# Configuración del pin del láser
GPIO.setup(laser_pin, GPIO.OUT)

# Buzzer Activo:
GPIO.setup(5, GPIO.OUT)

# Definimos los pines de control del L298N para dos motores
IN1 = 26  # GPIO 17 para Motor 1
IN2 = 20  # GPIO 27 para Motor 1
IN3 = 17  # GPIO 22 para Motor 2
IN4 = 18  # GPIO 23 para Motor 2

# Configuramos los pines como salida
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Inicializar pygame para manejar eventos de teclado
pygame.init()

# Configurar la pantalla de pygame (puede ser una ventana sin contenido)
screen = pygame.display.set_mode((100, 100))
pygame.display.set_caption('Control de Automóvil Robótico')

# Función para mover el motor 1 hacia adelante
def adelante_motor1():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    print("Motor 1 adelante")

# Función para mover el motor 1 hacia atrás
def atras_motor1():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    print("Motor 1 atrás")

# Función para mover el motor 2 hacia adelante
def adelante_motor2():
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    print("Motor 2 adelante")

# Función para mover el motor 2 hacia atrás
def atras_motor2():
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    print("Motor 2 atrás")

# Función para detener ambos motores
def detener():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    print("Motores detenidos")
    
# Función para medir la distancia con el sensor ultrasónico
def medir_distancia():
    # Enviar un pulso de 10 microsegundos
    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)

    # Medir el tiempo que tarda el pulso en volver
    while GPIO.input(echo_pin) == GPIO.LOW:
        pulse_start = time.time()
    
    while GPIO.input(echo_pin) == GPIO.HIGH:
        pulse_end = time.time()

    # Calcular la distancia
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # 34300 / 2 = 17150 cm/s
    distance = round(distance, 2)  # Redondear a 2 decimales
    return distance

# Función para mover el servomotor

def servo_sweep():
    for angulo in range(0, 181, 10):  # Mover de 0 a 180 grados en pasos de 10
        mover_servo(angulo)
        distancia = medir_distancia()
        print(f"Ángulo: {angulo}° - Distancia: {distancia} cm")

        if distancia<=10:
            encender_laser()  # Encender el láser
            time.sleep(2)     # Mantenerlo encendido por 2 segundos
            apagar_laser()    # Apagar el láser
            time.sleep(2)     # Mantenerlo apagado por 2 segundos
            GPIO.output(5, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(5, GPIO.LOW)
            time.sleep(1)
    
# Función para encender el láser
def encender_laser():
    GPIO.output(laser_pin, GPIO.HIGH)
    print("Láser encendido.")

# Función para apagar el láser
def apagar_laser():
    GPIO.output(laser_pin, GPIO.LOW)
    print("Láser apagado.")

# Programa principal

# Bucle principal para escuchar las teclas del teclado
    try:
        hilo = threading.Thread(target=servo_sweep)
        hilo.start()
        while True:
            apagar_laser()
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    GPIO.cleanup()  # Limpiamos la configuración de los pines GPIO
                    exit()

                # Comprobamos si una tecla es presionada
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:    # Flecha hacia arriba
                        atras_motor1()
                        atras_motor2()
                    elif event.key == pygame.K_DOWN:  # Flecha hacia abajo
                        adelante_motor1()
                        adelante_motor2()
                    elif event.key == pygame.K_LEFT:  # Flecha hacia la izquierda
                        adelante_motor1()
                        atras_motor2()
                    elif event.key == pygame.K_RIGHT:  # Flecha hacia la derecha
                        atras_motor1()
                        adelante_motor2()
                    elif event.key == pygame.K_SPACE:  # Tecla de espacio para detener
                        detener()

                # Si se deja de presionar una tecla, los motores se detienen
                if event.type == pygame.KEYUP:
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        detener()
    except KeyboardInterrupt:
        print("Programa terminado por el usuario")
    finally:
        pygame.quit()  # Aseguramos que pygame se cierre correctamente
        GPIO.cleanup()  # Limpiamos la configuración de los pines GPIO
        hilo.join()
                
