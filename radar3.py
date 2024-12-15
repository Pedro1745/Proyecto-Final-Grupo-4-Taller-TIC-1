import sys
import math
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QPen, QBrush, QPolygon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget


class RadarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)  # Tamaño inicial ampliado
        self.angle = 0
        self.data = []  # Datos del radar (distancia y ángulo)

    def update_radar(self, angle, distance):
        """
        Actualiza los datos del radar.
        :param angle: Ángulo del servo en grados (0° a 180°).
        :param distance: Distancia detectada por el sensor (en la misma escala que el radio del radar).
        """
        self.angle = angle
        self.data.append((angle, distance))
        if len(self.data) > 50:  # Limitar el número de puntos guardados
            self.data.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = self.width()
        height = self.height()

        # Tamaño dinámico del radar según la ventana
        center_x = width // 2
        center_y = height - 50  # Ajustar para centrar mejor
        radius = min(width, height) // 2 - 50

        # Dibujar fondo del radar
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.setPen(Qt.GlobalColor.black)
        painter.drawRect(0, 0, width, height)

        # Dibujar círculo de media circunferencia
        painter.setPen(QPen(Qt.GlobalColor.darkGreen, 3))
        painter.drawArc(
            center_x - radius, center_y - radius, 2 * radius, 2 * radius,
            0 * 16, 180 * 16  # Media circunferencia (0° a 180°)
        )

        # Dibujar líneas de guía estáticas
        painter.setPen(QPen(Qt.GlobalColor.darkGreen, 1))
        for i in range(0, 181, 30):  # Líneas cada 30°
            x = center_x + radius * math.cos(math.radians(i))
            y = center_y - radius * math.sin(math.radians(i))
            painter.drawLine(center_x, center_y, int(x), int(y))

        # Dibujar líneas de barrido
        start_angle = max(0, self.angle - 10)
        end_angle = min(180, self.angle + 10)

        painter.setPen(QPen(Qt.GlobalColor.red, 2))
        start_x = center_x + radius * math.cos(math.radians(start_angle))
        start_y = center_y - radius * math.sin(math.radians(start_angle))
        end_x = center_x + radius * math.cos(math.radians(end_angle))
        end_y = center_y - radius * math.sin(math.radians(end_angle))

        painter.drawLine(center_x, center_y, int(start_x), int(start_y))
        painter.drawLine(center_x, center_y, int(end_x), int(end_y))

        # Dibujar áreas detectadas entre las dos líneas guía
        painter.setBrush(QBrush(Qt.GlobalColor.darkRed, Qt.BrushStyle.Dense4Pattern))
        for angle, distance in self.data:
            if start_angle <= angle <= end_angle:
                x1 = center_x + distance * math.cos(math.radians(start_angle))
                y1 = center_y - distance * math.sin(math.radians(start_angle))
                x2 = center_x + distance * math.cos(math.radians(end_angle))
                y2 = center_y - distance * math.sin(math.radians(end_angle))
                polygon = QPolygon([
                    QPoint(center_x, center_y),
                    QPoint(int(x1), int(y1)),
                    QPoint(int(x2), int(y2))
                ])
                painter.drawPolygon(polygon)


class RadarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radar - Media Circunferencia Ampliada")
        self.setGeometry(100, 100, 800, 600)  # Tamaño inicial de la ventana
        self.radar_widget = RadarWidget()
        self.setCentralWidget(self.radar_widget)

        # Temporizador para actualizar el radar
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_radar)
        self.timer.start(100)  # Actualizar cada 100 ms

        # Variables iniciales
        self.current_angle = 0

    def update_radar(self):
        """
        Simulación de datos del radar. Sustituye estas líneas con tu implementación real.
        """
        # Aquí debes ingresar el valor real del ángulo y distancia.
        # Por ejemplo, actualiza `self.current_angle` con el ángulo real del servo,
        # y asigna `distance` al valor medido por el sensor de ultrasonido.

        distance = 200  # Distancia simulada (reemplaza con datos del sensor)
        self.radar_widget.update_radar(self.current_angle, distance)

        # Actualiza el ángulo del radar simulando movimiento del servo
        self.current_angle += 10
        if self.current_angle > 180:  # Resetea después de completar el barrido
            self.current_angle = 0


if __name__ == "__main__":
    app = QApplication(sys.argv)
    radar_app = RadarApp()
    radar_app.show()
    sys.exit(app.exec())
