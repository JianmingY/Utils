import sys
import os
from PyQt5.QtWidgets import QShortcut, QMessageBox, QGraphicsSimpleTextItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView, QFrame, QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QSlider, QWidget, QColorDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QPainterPath, QFont, QKeySequence, QCursor
from PyQt5.QtCore import Qt,QRectF
import random


class Annotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_index = 0
        self.image_folder = ""
        self.label_folder = ""
        self.image_files = []
        self.label_files = []
        self.label_classes = []
        self.label_colors = {}
        self.bounding_boxes = []
        self.total_images = 0

        self.copy_and_paste_shortcut = QShortcut(QKeySequence("V"), self)
        self.copy_and_paste_shortcut.activated.connect(self.copyAndPasteBoundingBoxes)


        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.scene = QGraphicsScene(self)
        self.image_view = QGraphicsView(self.scene)
        self.image_view.setAlignment(Qt.AlignCenter)
        self.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view.setRenderHint(QPainter.Antialiasing, True)
        self.image_view.setRenderHint(QPainter.SmoothPixmapTransform, True)

        cursor_size = 1000  # Change the size of the cursor here
        crosshair_pixmap = QPixmap(cursor_size, cursor_size)
        crosshair_pixmap.fill(Qt.transparent)
        painter = QPainter(crosshair_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(
            QPen(QColor(0, 0, 0, 200), 4, Qt.SolidLine))  # Adjust the color and thickness of the crosshair lines
        painter.drawLine(0, cursor_size // 2, cursor_size, cursor_size // 2)
        painter.drawLine(cursor_size // 2, 0, cursor_size // 2, cursor_size)
        painter.end()

        crosshair_cursor = QCursor(crosshair_pixmap, cursor_size // 2, cursor_size // 2)
        self.image_view.setCursor(crosshair_cursor)

        self.initUI()
    def initUI(self):
        # Widgets
        self.image_label = QLabel(self)
        self.classes_panel = QWidget(self)
        self.load_classes_button = QPushButton("Load Label Classes", self)
        self.open_file_button = QPushButton("Open File", self)
        self.available_colors = ['cyan', 'red', 'green', 'pink', 'yellow', 'blue', 'gray', 'purple', 'brown', 'black', 'white']
        self.slider = QSlider(Qt.Horizontal, self)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.classes_panel)
        layout.addWidget(self.image_view)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.load_classes_button)
        main_layout.addWidget(self.open_file_button)
        main_layout.addWidget(self.slider)
        main_layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Signals and Slots
        self.load_classes_button.clicked.connect(self.loadLabelClasses)
        self.open_file_button.clicked.connect(self.loadImagesAndLabels)
        self.slider.valueChanged.connect(self.showImage)


    def copyAndPasteBoundingBoxes(self):

        if self.current_index > 0:
            previous_label_path = os.path.join(self.label_folder, self.label_files[self.current_index - 1])
            current_label_path = os.path.join(self.label_folder, self.label_files[self.current_index])


            # Copy and paste bounding boxes from the previous image to the current image's label file
            if os.path.exists(previous_label_path):
                with open(previous_label_path, "r") as prev_file:
                    previous_bounding_boxes = prev_file.readlines()

                with open(current_label_path, "w") as current_file:

                    # Copy previous bounding boxes to the current image's label file
                    current_file.writelines(previous_bounding_boxes)

                # Reload the current image and its bounding boxes
                self.update()  # Trigger the paintEvent to redraw bounding boxes

    def loadLabelClasses(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Label Classes File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, "r") as file:
                self.label_classes = [line.strip() for line in file.readlines()]

            # Set color for each class
            color_dict = {}
            for i, label in enumerate(self.label_classes):
                if i < len(self.available_colors):
                    color = self.available_colors[i]
                else:
                    color = self.getRandomColor()
                color_dict[label] = color

            self.label_colors = color_dict

            # Sort classes based on the preset order
            sorted_classes = sorted(color_dict.keys(), key=lambda x: self.available_colors.index(color_dict[x]))

            # Add class labels to the classes panel with colors
            layout = QVBoxLayout()
            for label in sorted_classes:
                color = color_dict[label]
                label_widget = QLabel(label)
                label_widget.setStyleSheet(f"background-color: {color}; color: white;")
                label_widget.setFrameShape(QFrame.StyledPanel)
                layout.addWidget(label_widget)

            self.classes_panel.setLayout(layout)

    def getRandomColor(self):
        # Generate a random color not in the available colors list
        while True:
            color = QColorDialog.getColor().name()
            if color not in self.available_colors:
                self.available_colors.append(color)
                return color
    def loadImagesAndLabels(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Open Image Folder", options=options)
        if folder_path:
            self.image_folder = folder_path
            self.image_files = [file for file in os.listdir(self.image_folder) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]

            # Load label files
            self.label_folder = self.image_folder  # Assuming labels are in the same folder
            self.label_files = [os.path.splitext(file)[0] + ".txt" for file in self.image_files]

            if self.label_files:
                # Load the first image and its corresponding label
                self.showImage(self.current_index)
            else:
                self.showNoImageLoadedMessage()

    def showImage(self, index):
        if 0 <= index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[index])
            label_path = os.path.join(self.label_folder, self.label_files[index])

            # Load image
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print("Image loading failed!")
            else:
                self.scene.clear()
                self.scene.addPixmap(pixmap)
                self.image_view.setScene(self.scene)

            self.image_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.image_view.setScene(self.scene)

            # Load and parse label file
            self.bounding_boxes = []  # Reset bounding boxes for the current image
            if os.path.exists(label_path):
                with open(label_path, "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        class_id, center_x, center_y, width, height = map(float, line.strip().split())
                        class_label = self.label_classes[int(class_id)]
                        box = {
                            "label": class_label,
                            "center_x": center_x,
                            "center_y": center_y,
                            "width": width,
                            "height": height
                        }
                        self.bounding_boxes.append(box)

            self.slider.setMaximum(len(self.image_files) - 1)
            self.slider.setValue(index)
            self.total_images = len(self.image_files)
            message = f"Image {index + 1} / {self.total_images}"
            self.status_label.setText(message)
            self.current_index = index

            self.update()  # Trigger the paintEvent to draw bounding boxes


    def paintEvent(self, event):
        super().paintEvent(event)


        for box in self.bounding_boxes:
            color = QColor(self.getColorForLabel(box["label"]))

            image_width = self.image_view.sceneRect().width()
            image_height = self.image_view.sceneRect().height()
            box_width = box["width"] * image_width
            box_height = box["height"] * image_height
            top_left_x = (box["center_x"] * image_width - box_width / 2)
            top_left_y = (box["center_y"] * image_height - box_height / 2)

            # Draw bounding box
            rect_item = QGraphicsRectItem(top_left_x, top_left_y, box_width, box_height)
            rect_item.setPen(QPen(color, 2))
            self.scene.addItem(rect_item)

            # Draw class label on the bounding box
            font_size = 12
            label_text = box['label']
            text_item = QGraphicsSimpleTextItem(label_text)
            text_item.setPos(top_left_x, top_left_y - font_size)
            text_item.setBrush(color)
            text_item.setFont(QFont("Arial", font_size))
            self.scene.addItem(text_item)

        self.image_view.setScene(self.scene)
    def getColorForLabel(self, label):
        # Check if the label has a specific color assigned in the dictionary
        if label in self.label_colors:
            return self.label_colors[label]
        else:
            # If the label does not have a specific color, generate a random color
            random_color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            return random_color.name()
    def showNoImageLoadedMessage(self):
        # Display a message when no image is loaded
        message_box = QMessageBox(self)
        message_box.setWindowTitle("No Image Loaded")
        message_box.setText("No images are loaded. Please select a folder containing images and labels.")
        message_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    annotator = Annotator()
    annotator.show()
    sys.exit(app.exec_())
