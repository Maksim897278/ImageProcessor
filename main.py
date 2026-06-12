import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget, QFileDialog,
                             QMessageBox, QInputDialog, QAction, QMenuBar, QMenu)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt

class ImageProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.displayed_image = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Processor - Variant 25")
        self.setGeometry(100, 100, 1000, 700)

        # Центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Область для отображения изображения
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setMinimumSize(800, 600)
        main_layout.addWidget(self.image_label)

        # Панель кнопок
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # Кнопки загрузки
        load_file_btn = QPushButton("Load Image (File)")
        load_file_btn.clicked.connect(self.load_image_file)
        button_layout.addWidget(load_file_btn)

        load_cam_btn = QPushButton("Capture from Webcam")
        load_cam_btn.clicked.connect(self.capture_from_webcam)
        button_layout.addWidget(load_cam_btn)

        # Создание меню
        menubar = self.menuBar()
        
        # Меню "Каналы"
        channel_menu = menubar.addMenu("Color Channels")
        for color, text in [('R', "Red Channel"), ('G', "Green Channel"), ('B', "Blue Channel")]:
            action = QAction(text, self)
            action.triggered.connect(lambda checked, c=color: self.show_channel(c))
            channel_menu.addAction(action)

        # Меню "Изменения" (Базовый и индивидуальный функционал)
        edit_menu = menubar.addMenu("Edit")
        
        # Общие функции (Color Channels уже есть, добавим сброс)
        reset_action = QAction("Reset to Original", self)
        reset_action.triggered.connect(self.reset_image)
        edit_menu.addAction(reset_action)
        edit_menu.addSeparator()

        # Индивидуальные функции варианта 25
        resize_action = QAction("1. Resize Image", self)
        resize_action.triggered.connect(self.resize_image)
        edit_menu.addAction(resize_action)

        brighten_action = QAction("7. Increase Brightness", self)
        brighten_action.triggered.connect(self.increase_brightness)
        edit_menu.addAction(brighten_action)

        draw_line_action = QAction("14. Draw Green Line", self)
        draw_line_action.triggered.connect(self.draw_green_line)
        edit_menu.addAction(draw_line_action)

    # --- Вспомогательные функции ---
    def cv2_to_qpixmap(self, cv_img):
        """Конвертирует OpenCV изображение в QPixmap для отображения."""
        if cv_img is None:
            return QPixmap()
        if len(cv_img.shape) == 2:  # Grayscale
            h, w = cv_img.shape
            bytes_per_line = w
            q_img = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        else:  # BGR
            h, w, ch = cv_img.shape
            bytes_per_line = ch * w
            cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            q_img = QImage(cv_img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(q_img)

    def update_display(self, cv_img=None):
        """Обновляет отображаемое изображение."""
        if cv_img is not None:
            self.displayed_image = cv_img
        if self.displayed_image is not None:
            pixmap = self.cv2_to_qpixmap(self.displayed_image)
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("No image loaded")

    def reset_image(self):
        """Сбрасывает изображение к оригиналу."""
        if self.current_image is not None:
            self.displayed_image = self.current_image.copy()
            self.update_display()
            QMessageBox.information(self, "Reset", "Image reset to original.")
        else:
            QMessageBox.warning(self, "No Image", "Please load an image first.")

    # --- Загрузка изображений ---
    def load_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                img = cv2.imread(file_path)
                if img is None:
                    raise ValueError("Could not read the image file.")
                self.current_image = img
                self.displayed_image = img.copy()
                self.update_display()
                QMessageBox.information(self, "Success", f"Image loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {e}")

    def capture_from_webcam(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise ConnectionError("Cannot connect to webcam. Check if it's connected and accessible.")
            
            ret, frame = cap.read()
            cap.release()
            if ret:
                self.current_image = frame
                self.displayed_image = frame.copy()
                self.update_display()
                QMessageBox.information(self, "Success", "Photo captured from webcam.")
            else:
                QMessageBox.critical(self, "Error", "Failed to capture photo from webcam.")
        except Exception as e:
            QMessageBox.critical(self, "Webcam Error", f"Cannot access webcam: {e}. Make sure it's enabled and no other app is using it.")

    # --- Базовый функционал: Каналы ---
    def show_channel(self, color):
        if self.displayed_image is None:
            QMessageBox.warning(self, "No Image", "Please load an image first.")
            return
        
        b, g, r = cv2.split(self.displayed_image)
        zeros = np.zeros_like(b)
        if color == 'R':
            channel_img = cv2.merge([zeros, zeros, r])
        elif color == 'G':
            channel_img = cv2.merge([zeros, g, zeros])
        elif color == 'B':
            channel_img = cv2.merge([b, zeros, zeros])
        
        self.displayed_image = channel_img
        self.update_display()

    # --- Индивидуальные функции (Вариант 25) ---
    def resize_image(self):
        if self.current_image is None:
            QMessageBox.warning(self, "No Image", "Please load an image first.")
            return

        new_width, ok1 = QInputDialog.getInt(self, "Resize", "Enter new width:", value=self.current_image.shape[1], min=1, max=4096)
        if not ok1: return
        new_height, ok2 = QInputDialog.getInt(self, "Resize", "Enter new height:", value=self.current_image.shape[0], min=1, max=4096)
        if not ok2: return

        try:
            resized = cv2.resize(self.current_image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            self.displayed_image = resized
            self.current_image = resized  # Делаем измененный размер новым оригиналом
            self.update_display()
            QMessageBox.information(self, "Resized", f"Image resized to {new_width}x{new_height}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not resize image: {e}")

    def increase_brightness(self):
        if self.displayed_image is None:
            QMessageBox.warning(self, "No Image", "Please load an image first.")
            return

        value, ok = QInputDialog.getInt(self, "Brightness", "Enter brightness increase value (0-100):", value=30, min=0, max=100)
        if ok:
            try:
                hsv = cv2.cvtColor(self.displayed_image, cv2.COLOR_BGR2HSV)
                h, s, v = cv2.split(hsv)
                v = cv2.add(v, value)
                v = np.clip(v, 0, 255)
                final_hsv = cv2.merge((h, s, v))
                brighter_img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
                self.displayed_image = brighter_img
                self.update_display()
                QMessageBox.information(self, "Brightness", f"Brightness increased by {value}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not adjust brightness: {e}")

    def draw_green_line(self):
        if self.displayed_image is None:
            QMessageBox.warning(self, "No Image", "Please load an image first.")
            return

        x1, ok1 = QInputDialog.getInt(self, "Line", "Start X coordinate:", value=50, min=0, max=self.displayed_image.shape[1])
        if not ok1: return
        y1, ok2 = QInputDialog.getInt(self, "Line", "Start Y coordinate:", value=50, min=0, max=self.displayed_image.shape[0])
        if not ok2: return
        x2, ok3 = QInputDialog.getInt(self, "Line", "End X coordinate:", value=200, min=0, max=self.displayed_image.shape[1])
        if not ok3: return
        y2, ok4 = QInputDialog.getInt(self, "Line", "End Y coordinate:", value=200, min=0, max=self.displayed_image.shape[0])
        if not ok4: return
        thickness, ok5 = QInputDialog.getInt(self, "Line", "Thickness:", value=2, min=1, max=20)
        if not ok5: return

        try:
            img_with_line = self.displayed_image.copy()
            cv2.line(img_with_line, (x1, y1), (x2, y2), (0, 255, 0), thickness)
            self.displayed_image = img_with_line
            self.update_display()
            QMessageBox.information(self, "Line Drawn", f"Green line drawn from ({x1},{y1}) to ({x2},{y2}) with thickness {thickness}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not draw line: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageProcessor()
    ex.show()
    sys.exit(app.exec_())