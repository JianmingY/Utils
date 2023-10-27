import sys
import os
from PyQt5.QtWidgets import (
    QShortcut,
    QMessageBox,
    QGraphicsSimpleTextItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QFrame,
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QSlider,
    QWidget,
    QColorDialog,
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QFont, QCursor, QKeySequence, QPainter
from PyQt5.QtCore import Qt, QRectF, QPointF
import random


class Annotator(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize variables
        self.available_colors = ['cyan', 'red', 'green', 'pink', 'yellow', 'blue', 'gray', 'purple', 'brown', 'black',
                                 'white']
        self.drawing_start = False
        self.start_pos = None
        self.end_pos = None

        self.scene = QGraphicsScene(self)
        self.image_view = QGraphicsView(self.scene)
        self.image_view.setAlignment(Qt.AlignCenter)
        self.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view.setRenderHint(QPainter.Antialiasing, True)
        self.image_view.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.temp_rect_item = None
        self.image_rect = None



        self.current_index = 0
        self.image_folder = ""
        self.label_folder = ""
        self.image_files = []
        self.label_files = []
        self.label_classes = []
        self.label_colors = {}
        self.bounding_boxes = []
        self.total_images = 0

        # Create a shortcut for copy and paste action
        self.copy_and_paste_shortcut = QShortcut(QKeySequence("V"), self)
        self.copy_and_paste_shortcut.activated.connect(self.copyAndPasteBoundingBoxes)


        # Initialize UI elements
        self.initUI()

    def initUI(self):
        # Widgets
        self.image_label = QLabel(self)
        self.classes_panel = QWidget(self)
        self.load_classes_button = QPushButton("Load Label Classes", self)
        self.open_file_button = QPushButton("Open File", self)
        self.slider = QSlider(Qt.Horizontal, self)

        self.image_view.mousePressEvent = self.mousePressEventHandler
        self.image_view.mouseMoveEvent = self.mouseMoveEventHandler
        self.image_view.mouseReleaseEvent = self.mouseReleaseEventHandler

        # Status label setup
        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.classes_panel)
        layout.addWidget(self.image_view)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_classes_button)
        button_layout.addWidget(self.open_file_button)
        button_layout.addWidget(self.slider)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)  # Status label is added here

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Signals and Slots
        self.load_classes_button.clicked.connect(self.loadLabelClasses)
        self.open_file_button.clicked.connect(self.loadImagesAndLabels)
        self.slider.valueChanged.connect(self.showImage)

        # Set up the crosshair cursor
        cursor_size = 32
        crosshair_pixmap = QPixmap(cursor_size, cursor_size)
        crosshair_pixmap.fill(Qt.transparent)
        painter = QPainter(crosshair_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.cyan, 3, Qt.SolidLine))
        painter.drawLine(0, cursor_size // 2, cursor_size, cursor_size // 2)
        painter.drawLine(cursor_size // 2, 0, cursor_size // 2, cursor_size)
        painter.end()

        self.crosshair_cursor = QCursor(crosshair_pixmap, cursor_size // 2, cursor_size // 2)
        self.image_view.setCursor(self.crosshair_cursor)

    def mousePressEventHandler(self, event):
        if event.button() == Qt.LeftButton and self.image_view.cursor().shape() == 24:
            # Start drawing the bounding box
            self.temp_rect_item = QGraphicsRectItem()
            self.temp_rect_item.setPen(QPen(QColor("cyan"), 2, Qt.SolidLine))
            self.scene.addItem(self.temp_rect_item)
            self.drawing_start = True
            self.start_pos = self.end_pos = self.image_view.mapToScene(event.pos())


    def mouseMoveEventHandler(self, event):
        if self.drawing_start and self.image_view.cursor().shape() == 24:
            # Update the end position as the mouse moves
            new_end_pos = self.image_view.mapToScene(event.pos())

            # Ensure the new_end_pos stays within the image boundaries

            new_end_pos.setX(max(self.image_rect.left(), min(self.image_rect.right(), new_end_pos.x())))
            new_end_pos.setY(max(self.image_rect.top(), min(self.image_rect.bottom(), new_end_pos.y())))

            self.end_pos = new_end_pos
            self.updateTemporaryBoundingBox()

    def mouseReleaseEventHandler(self, event):
        pass
        # if self.drawing_start and event.button() == Qt.LeftButton:
        #     print(self.end_pos)
        #     self.temp_rect_item = None
        #     # End drawing the bounding box
        #     self.drawing_start = False
        #
        #     # Calculate bounding box coordinates (in relative values)
        #     top_left_x = min(self.start_pos.x(), self.end_pos.x())
        #     top_left_y = min(self.start_pos.y(), self.end_pos.y())
        #     box_width = abs(self.end_pos.x() - self.start_pos.x())
        #     box_height = abs(self.end_pos.y() - self.start_pos.y())
        #
        #
        #
        #     # Save the bounding box coordinates to the current label file
        #     label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
        #     with open(label_path, "a") as label_file:
        #         class_id = self.label_classes.index(self.selected_class)
        #         center_x = (top_left_x + box_width / 2) / self.image_view.sceneRect().width()
        #         center_y = (top_left_y + box_height / 2) / self.image_view.sceneRect().height()
        #         width = box_width / self.image_view.sceneRect().width()
        #         height = box_height / self.image_view.sceneRect().height()
        #         label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
        #
        #     # Reload the current image and its bounding boxes
        #     self.showImage(self.current_index)

    def updateTemporaryBoundingBox(self):
        if self.drawing_start and self.start_pos and self.end_pos and self.image_view.cursor().shape() == 24:
            # Calculate bounding box coordinates in pixel values
            # if self.end_pos.x() >= self.image_view.sceneRect().width() / 2:
            #     top_left_x = self.start_pos.x()
            #     box_width = abs(self.image_view.sceneRect().width() / 2 - self.start_pos.x())
            # elif self.end_pos.x() <= -self.image_view.sceneRect().width() / 2:
            #     top_left_x = -self.image_view.sceneRect().width() / 2
            #     box_width = abs(self.image_view.sceneRect().width() / 2 - self.start_pos.x())
            # else:
            top_left_x = min(self.start_pos.x(), self.end_pos.x())
            box_width = abs(self.end_pos.x() - self.start_pos.x())


            # if self.end_pos.y() >= self.image_view.sceneRect().height() / 2:
            #     top_left_y = (self.start_pos.y())
            #     box_height = abs(self.image_view.sceneRect().height() / 2 - self.start_pos.y())
            # elif self.end_pos.y() <= -self.image_view.sceneRect().height() / 2:
            #     top_left_y = -self.image_view.sceneRect().height() / 2
            #     box_height = abs(self.image_view.sceneRect().height() / 2 - self.start_pos.y())
            # else:
            top_left_y = min(self.start_pos.y(), self.end_pos.y())
            box_height = abs(self.end_pos.y() - self.start_pos.y())


            # Update the temporary rectangle item's position and size
            self.temp_rect_item.setRect(top_left_x, top_left_y, box_width, box_height)

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
                self.showImage(self.current_index)

    def loadLabelClasses(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Label Classes File", "",
                                                   "Text Files (*.txt);;All Files (*)", options=options)
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
            self.image_files = [file for file in os.listdir(self.image_folder) if
                                file.lower().endswith(('.jpg', '.jpeg', '.png'))]

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
            self.image_rect = self.image_view.sceneRect()

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
            self.image_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.image_view.setScene(self.scene)

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
