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
    QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPen, QColor, QFont, QCursor, QKeySequence, QPainter, QBrush
from PyQt5.QtCore import Qt, QRectF, QPointF
import random


class Annotator(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize variables

        self.available_colors = ['cyan', 'red', 'green', 'pink', 'yellow', 'blue', 'pink', 'purple', 'brown', 'black',
                                 'white']
        self.drawing_start = False
        self.dragging_start = False
        self.adjusting_start = False
        self.translate_start = False
        self.start_pos = None
        self.end_pos = None
        self.left = False
        self.right = False
        self.up = False
        self.down = False

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
        self.selected_class = 0
        self.label_colors = {}
        self.bounding_boxes = []
        self.orginal_bounding_box = []
        self.deleted_box = []
        self.box_width = 0
        self.box_height = 0
        self.image_width = 100
        self.image_height = 100
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
        cursor_size = 16
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

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_D:
            # Save the bounding box coordinates to the current label file
            label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
            with open(label_path, "w") as label_file:
                for box in self.bounding_boxes:
                    class_id = self.label_classes.index(box["label"])
                    center_x = box["center_x"]
                    center_y = box["center_y"]
                    width = box["width"]
                    height = box["height"]
                    label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

            # Move to the next image
            next_index = (self.current_index + 1) % len(self.image_files)
            self.showImage(next_index)
        elif key == Qt.Key_F:
            # Save the bounding box coordinates to the current label file
            label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
            with open(label_path, "w") as label_file:
                for box in self.bounding_boxes:
                    class_id = self.label_classes.index(box["label"])
                    center_x = box["center_x"]
                    center_y = box["center_y"]
                    width = box["width"]
                    height = box["height"]
                    label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

            # Move to the next image
            next_ten_index = (self.current_index + 10) % len(self.image_files)
            self.showImage(next_ten_index)
        elif key == Qt.Key_S:
            # Move to the previous image
            if self.current_index >= 1:
                previous_index = (self.current_index - 1) % len(self.image_files)
            else:
                previous_index = 0
            self.showImage(previous_index)
        elif key == Qt.Key_Backspace:
            global_cursor_pos = QCursor.pos()
            local_cursor_pos = self.image_view.mapFromGlobal(global_cursor_pos)
            image_pos = self.image_view.mapToScene(local_cursor_pos)
            # Iterate through bounding boxes to find the one clicked on
            sel_box = None
            sel_box_index = None
            for index, box in enumerate(self.bounding_boxes):
                box_rect = self.calculateAbsoluteBoundingBox(box)
                if box_rect.contains(image_pos):
                    self.box_width = box["width"] * self.image_view.sceneRect().width() / 2
                    self.box_height = box["height"] * self.image_view.sceneRect().height() / 2
                    # Right-clicked on this bounding box, perform edit operations here
                    print(f"Deleting bounding box {index} in progress")
                    sel_box = box
                    sel_box_index = index
                    break

            if sel_box is not None and sel_box_index is not None:

                del self.bounding_boxes[sel_box_index]
                label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
                with open(label_path, "w") as label_file:
                    for box in self.bounding_boxes:
                        class_id = self.label_classes.index(box["label"])
                        center_x = box["center_x"]
                        center_y = box["center_y"]
                        width = box["width"]
                        height = box["height"]
                        label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
                self.showImage(self.current_index)

        elif key == Qt.Key_C:
            self.deleted_box = self.bounding_boxes
            self.bounding_boxes = []
            label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
            with open(label_path, "w") as label_file:
                for box in self.bounding_boxes:
                    class_id = self.label_classes.index(box["label"])
                    center_x = box["center_x"]
                    center_y = box["center_y"]
                    width = box["width"]
                    height = box["height"]
                    label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
            self.showImage(self.current_index)

        elif key == Qt.Key_A and self.adjusting_start == False:
            self.adjusting_start = True
            global_cursor_pos = QCursor.pos()
            local_cursor_pos = self.image_view.mapFromGlobal(global_cursor_pos)
            image_pos = self.image_view.mapToScene(local_cursor_pos)
            # Iterate through bounding boxes to find the one clicked on
            sel_box = None
            sel_box_index = None
            for index, box in enumerate(self.bounding_boxes):
                box_rect = self.calculateAbsoluteBoundingBox(box)
                if box_rect.contains(image_pos):
                    self.box_width = box["width"] * self.image_view.sceneRect().width() / 2
                    self.box_height = box["height"] * self.image_view.sceneRect().height() / 2
                    # Right-clicked on this bounding box, perform edit operations here
                    print(f"Adhusting {index} in progress")
                    sel_box = box
                    sel_box_index = index
                    break
            self.squares = []


            if sel_box is not None and sel_box_index is not None:
                self.orginal_bounding_box = self.calculateAbsoluteBoundingBox(sel_box)
                self.selected_class = sel_box["label"]
                self.deleted_box = self.bounding_boxes[sel_box_index]
                del self.bounding_boxes[sel_box_index]
                label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
                with open(label_path, "w") as label_file:
                    for box in self.bounding_boxes:
                        class_id = self.label_classes.index(box["label"])
                        center_x = box["center_x"]
                        center_y = box["center_y"]
                        width = box["width"]
                        height = box["height"]
                        label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                square_size = 15  # Size of the small squares
                for i in range(8):
                    if i == 0:
                        square = QGraphicsRectItem(self.top_left_x, self.top_left_y, square_size,
                                                   square_size)
                        self.squares.append(square)
                    elif i == 1:
                        square = QGraphicsRectItem(self.top_left_x + self.box_width / 2 - square_size / 2, self.top_left_y,
                                                   square_size, square_size)
                        self.squares.append(square)
                    elif i == 2:
                        square = QGraphicsRectItem(self.top_left_x + self.box_width - square_size, self.top_left_y, square_size,
                                                   square_size)
                        self.squares.append(square)
                    elif i == 3:
                        square = QGraphicsRectItem(self.top_left_x, self.top_left_y + self.box_height / 2 - square_size / 2,
                                                   square_size, square_size)
                        self.squares.append(square)
                    elif i == 4:
                        square = QGraphicsRectItem(self.top_left_x + self.box_width - square_size, self.top_left_y + self.box_height / 2 - square_size / 2,
                                                   square_size, square_size)
                        self.squares.append(square)
                    elif i == 5:
                        square = QGraphicsRectItem(self.top_left_x, self.top_left_y + self.box_height - square_size, square_size,
                                                   square_size)
                        self.squares.append(square)
                    elif i == 6:
                        square = QGraphicsRectItem(self.top_left_x + self.box_width / 2 - square_size / 2, self.top_left_y + self.box_height - square_size,
                                                   square_size, square_size)
                        self.squares.append(square)
                    else:
                        square = QGraphicsRectItem(self.top_left_x + self.box_width - square_size, self.top_left_y + self.box_height - square_size, square_size,
                                                   square_size)
                        self.squares.append(square)
                    color = QColor(self.label_colors[self.selected_class])
                    square.setPen(QPen(color, 2))
                    square.setBrush(QBrush(color))
                    self.scene.addItem(square)
                self.selected_class = self.label_classes.index(self.selected_class)
            else:
                self.adjusting_start = False


                # base on this add 8 small squares on the bounding box, at each corner and at the middle of each side
                # upon click, detect if cursor clicked on these squares, if on side square, change cursor to left right/ up down arrows allow translational adjust of that side when dragging mouse
                # if click on squares at corners, fix starting point at the opposite corner, change curesor to diagnal arrows, make the end point the clicked squares' corner from the original box



        elif Qt.Key_0 < key <= Qt.Key_9:
            self.selected_class = int(key - Qt.Key_0) - 1
        elif key == Qt.Key_0:
            self.selected_class = 9
        elif key == Qt.Key_F1:
            self.selected_class = 10
        elif key == Qt.Key_F2:
            self.selected_class = 11
        elif key == Qt.Key_F3:
            self.selected_class = 12
        elif key == Qt.Key_F4:
            self.selected_class = 13
        elif key == Qt.Key_F5:
            self.selected_class = 14

    def mousePressEventHandler(self, event):
        if (self.translate_start or self.adjusting_start) and event.button() == Qt.RightButton:
            self.translate_start = False

            self.temp_rect_item = QGraphicsRectItem()
            self.temp_rect_item.setPen(QPen(QColor("yellow"), 2, Qt.SolidLine))
            self.scene.addItem(self.temp_rect_item)

            print("restore")
            self.adjusting_start = False
            self.selected_class = 0
            self.scene.clear()
            self.bounding_boxes.append(self.deleted_box)

            label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
            with open(label_path, "w") as label_file:
                for box in self.bounding_boxes:
                    class_id = self.label_classes.index(box["label"])
                    center_x = box["center_x"]
                    center_y = box["center_y"]
                    width = box["width"]
                    height = box["height"]
                    label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
            self.showImage(self.current_index)
        elif event.button() == Qt.LeftButton and self.image_view.cursor().shape() == 24 and self.adjusting_start:
            clicked_point = self.image_view.mapToScene(event.pos())
            self.temp_rect_item = QGraphicsRectItem()
            self.temp_rect_item.setPen(QPen(QColor("yellow"), 2, Qt.SolidLine))
            self.scene.addItem(self.temp_rect_item)



            # box_rect = self.calculateAbsoluteBoundingBox(box)
            if self.squares[0].contains(clicked_point):
                print("top left slected")
                self.start_pos = QPointF(self.bottom_right_x, self.bottom_right_y)
                self.end_pos = QPointF(self.top_left_x, self.top_left_y)

            elif self.squares[2].contains(clicked_point):
                print("top right slected")
                self.start_pos = QPointF(self.top_left_x, self.bottom_right_y)
                self.end_pos = QPointF(self.bottom_right_x, self.top_left_y)
                # self.start_pos = self.bottom_right
            elif self.squares[5].contains(clicked_point):
                print("bot left slected")
                self.start_pos = QPointF(self.bottom_right_x, self.top_left_y)
                self.end_pos = QPointF(self.top_left_x, self.bottom_right_y)
                # self.start_pos = self.bottom_left
            elif self.squares[7].contains(clicked_point):
                print("bot right slected")
                self.start_pos = QPointF(self.top_left_x, self.top_left_y)
                self.end_pos = QPointF(self.bottom_right_x, self.bottom_right_y)
                # self.start_pos = self.top_right
            elif self.squares[1].contains(clicked_point):
                print("up slected")
                self.translate_start = True
                self.up = True
                self.start_pos = QPointF(self.bottom_right_x, self.bottom_right_y)
                self.end_pos = QPointF(self.top_left_x, self.top_left_y)

            elif self.squares[3].contains(clicked_point):
                print("left slected")
                self.translate_start = True
                self.left = True
                self.start_pos = QPointF(self.bottom_right_x, self.bottom_right_y)
                self.end_pos = QPointF(self.top_left_x, self.top_left_y)

            elif self.squares[4].contains(clicked_point):
                self.translate_start = True
                self.right = True
                print("right slected")
                self.start_pos = QPointF(self.top_left_x, self.top_left_y)
                self.end_pos = QPointF(self.bottom_right_x, self.bottom_right_y)
            elif self.squares[6].contains(clicked_point):
                self.translate_start = True
                self.down = True
                print("down slected")
                self.start_pos = QPointF(self.top_left_x, self.top_left_y)
                self.end_pos = QPointF(self.bottom_right_x, self.bottom_right_y)
            else:
                print("restore")
                self.adjusting_start = False
                self.selected_class = 0
                self.scene.clear()
                self.bounding_boxes.append(self.deleted_box)

                label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
                with open(label_path, "w") as label_file:
                    for box in self.bounding_boxes:
                        class_id = self.label_classes.index(box["label"])
                        center_x = box["center_x"]
                        center_y = box["center_y"]
                        width = box["width"]
                        height = box["height"]
                        label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")
                self.showImage(self.current_index)


        elif event.button() == Qt.LeftButton and self.image_view.cursor().shape() == 24 and not self.adjusting_start:
            # Start drawing the bounding box
            self.temp_rect_item = QGraphicsRectItem()
            self.temp_rect_item.setPen(QPen(QColor("cyan"), 2, Qt.SolidLine))
            self.scene.addItem(self.temp_rect_item)
            self.drawing_start = True
            self.start_pos = self.end_pos = self.image_view.mapToScene(event.pos())
        elif event.button() == Qt.RightButton and self.image_view.cursor().shape() == 24 and not self.adjusting_start and not self.translate_start:
            # Check if the right mouse button is clicked
            clicked_point = self.image_view.mapToScene(event.pos())
            print(clicked_point)
            # Iterate through bounding boxes to find the one clicked on
            sel_box = None
            sel_box_index = None
            for index, box in enumerate(self.bounding_boxes):
                box_rect = self.calculateAbsoluteBoundingBox(box)
                if box_rect.contains(clicked_point):
                    self.box_width = box["width"] * self.image_view.sceneRect().width() / 2
                    self.box_height = box["height"] * self.image_view.sceneRect().height() / 2
                    # Right-clicked on this bounding box, perform edit operations here
                    print(f"Selected bounding box {index}")
                    sel_box = box
                    sel_box_index = index
                    break

            if sel_box is not None and sel_box_index is not None :
                self.temp_rect_item = QGraphicsRectItem()
                self.temp_rect_item.setPen(QPen(QColor("red"), 2, Qt.SolidLine))
                self.scene.addItem(self.temp_rect_item)
                self.dragging_start = True
                self.orginal_bounding_box = self.calculateAbsoluteBoundingBox(sel_box)
                self.selected_class = sel_box["label"]
                self.deleted_box =self.bounding_boxes[sel_box_index]
                del self.bounding_boxes[sel_box_index]
                self.start_pos = self.image_view.mapToScene(event.pos())
                label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
                with open(label_path, "w") as label_file:
                    for box in self.bounding_boxes:
                        class_id = self.label_classes.index(box["label"])
                        center_x = box["center_x"]
                        center_y = box["center_y"]
                        width = box["width"]
                        height = box["height"]
                        label_file.write(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

    def calculateAbsoluteBoundingBox(self, box):
        image_width = self.image_view.sceneRect().width()
        image_height = self.image_view.sceneRect().height()

        # Calculate absolute coordinates
        self.top_left_x = box["center_x"] * image_width - box["width"] * image_width / 2
        self.top_left_y = box["center_y"] * image_height - box["height"] * image_height / 2
        self.bottom_right_x = self.top_left_x + box["width"] * image_width
        self.bottom_right_y = self.top_left_y + box["height"] * image_height
        self.box_width = self.bottom_right_x - self.top_left_x
        self.box_height = self.bottom_right_y - self.top_left_y

        # Create a QRectF representing the absolute bounding box
        return QRectF(self.top_left_x, self.top_left_y, self.bottom_right_x - self.top_left_x, self.bottom_right_y - self.top_left_y)

    def mouseMoveEventHandler(self, event):
        if self.adjusting_start and not self.translate_start and not self.dragging_start:
            new_end_pos = self.image_view.mapToScene(event.pos())

            # Ensure the new_end_pos stays within the image boundaries
            new_end_pos.setX(max(self.image_rect.left() + 1, min(self.image_rect.right() - 1, new_end_pos.x())))
            new_end_pos.setY(max(self.image_rect.top() + 1, min(self.image_rect.bottom() - 1, new_end_pos.y())))

            self.end_pos = new_end_pos
            self.updateTemporaryBoundingBox()

        elif self.translate_start:
            end_pos = self.image_view.mapToScene(event.pos())
            end_pos.setX(max(self.image_rect.left() + 1,
                             min(self.image_rect.right() - 1,
                                 end_pos.x())))
            end_pos.setY(max(self.image_rect.top() + 1,
                             min(self.image_rect.bottom() - 1,
                                 end_pos.y())))
            self.end_pos = end_pos
            self.updateTemporaryBoundingBox()

        elif self.drawing_start and self.image_view.cursor().shape() == 24:
            # Update the end position as the mouse moves
            new_end_pos = self.image_view.mapToScene(event.pos())

            # Ensure the new_end_pos stays within the image boundaries
            new_end_pos.setX(max(self.image_rect.left() + 1 , min(self.image_rect.right() - 1, new_end_pos.x())))
            new_end_pos.setY(max(self.image_rect.top() + 1, min(self.image_rect.bottom() - 1, new_end_pos.y())))

            self.end_pos = new_end_pos
            self.updateTemporaryBoundingBox()

        elif self.dragging_start and self.image_view.cursor().shape() == 24:
            end_pos = self.image_view.mapToScene(event.pos())

            # Ensure the new_end_pos stays within the image boundaries
            end_pos.setX(max(self.image_rect.left() + 1 + (self.start_pos.x() - self.top_left_x), min(self.image_rect.right() - 1 - abs(self.start_pos.x() - self.bottom_right_x), end_pos.x())))
            end_pos.setY(max(self.image_rect.top() + 1 + (self.start_pos.y() - self.top_left_y) , min(self.image_rect.bottom() - 1 - abs(self.start_pos.y() - self.bottom_right_y), end_pos.y())))
            self.end_pos = end_pos
            self.updateTemporaryBoundingBox()

    def mouseReleaseEventHandler(self, event):


        if self.drawing_start and event.button() == Qt.LeftButton:
            # End drawing the bounding box
            self.drawing_start = False

            if self.start_pos != self.end_pos:

                # Calculate bounding box coordinates (in relative values)
                top_left_x = min(self.start_pos.x(), self.end_pos.x())
                top_left_y = min(self.start_pos.y(), self.end_pos.y())
                box_width = abs(self.end_pos.x() - self.start_pos.x())
                box_height = abs(self.end_pos.y() - self.start_pos.y())

                # Ensure the bounding box coordinates stay within the image boundaries
                image_rect = self.image_view.sceneRect()
                top_left_x = max(image_rect.left(), min(image_rect.right(), top_left_x))
                top_left_y = max(image_rect.top(), min(image_rect.bottom(), top_left_y))
                box_width = min(image_rect.right() - top_left_x, box_width)
                box_height = min(image_rect.bottom() - top_left_y, box_height)
                # print(top_left_x,top_left_y,box_width,box_height)


                class_name = self.label_classes[self.selected_class]
                center_x = (top_left_x + box_width / 2) / self.image_view.sceneRect().width()
                center_y = (top_left_y + box_height / 2) / self.image_view.sceneRect().height()
                width = box_width / self.image_view.sceneRect().width()
                height = box_height / self.image_view.sceneRect().height()
                print(f"{self.selected_class} {class_name} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                # Save the bounding box coordinates to the current label file
                label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
                with open(label_path, "a") as label_file:
                    label_file.write(f"{self.selected_class} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                self.showImage(self.current_index)


        elif  self.adjusting_start and event.button() == Qt.LeftButton and not self.translate_start:
            self.adjusting_start = False

            if self.start_pos != self.end_pos:
                # Calculate bounding box coordinates (in relative values)
                top_left_x = min(self.start_pos.x(), self.end_pos.x())
                top_left_y = min(self.start_pos.y(), self.end_pos.y())
                box_width = abs(self.end_pos.x() - self.start_pos.x())
                box_height = abs(self.end_pos.y() - self.start_pos.y())

                # Ensure the bounding box coordinates stay within the image boundaries
                image_rect = self.image_view.sceneRect()
                top_left_x = max(image_rect.left(), min(image_rect.right(), top_left_x))
                top_left_y = max(image_rect.top(), min(image_rect.bottom(), top_left_y))
                box_width = min(image_rect.right() - top_left_x, box_width)
                box_height = min(image_rect.bottom() - top_left_y, box_height)
                # print(top_left_x,top_left_y,box_width,box_height)

                class_name = self.label_classes[self.selected_class]
                center_x = (top_left_x + box_width / 2) / self.image_view.sceneRect().width()
                center_y = (top_left_y + box_height / 2) / self.image_view.sceneRect().height()
                width = box_width / self.image_view.sceneRect().width()
                height = box_height / self.image_view.sceneRect().height()
                print(f"{self.selected_class} {class_name} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                # Save the bounding box coordinates to the current label file
                label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
                with open(label_path, "a") as label_file:
                    label_file.write(f"{self.selected_class} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                self.showImage(self.current_index)

        elif self.translate_start and event.button() == Qt.LeftButton:
            self.translate_start = False
            self.adjusting_start = False

            if self.start_pos != self.end_pos:

                if self.left == True:
                    top_left_x = min(self.end_pos.x(), self.start_pos.x())
                    box_width = abs(self.start_pos.x() - self.end_pos.x())
                    top_left_y = self.top_left_y
                    box_height = self.bottom_right_y - self.top_left_y
                elif self.right == True:
                    top_left_x = min(self.end_pos.x(), self.start_pos.x())
                    box_width = abs(self.start_pos.x() - self.end_pos.x())
                    top_left_y = self.top_left_y
                    box_height = self.bottom_right_y - self.top_left_y
                elif self.down == True:
                    top_left_x = self.top_left_x
                    box_width = self.bottom_right_x - self.top_left_x
                    top_left_y = min(self.end_pos.y(), self.start_pos.y())
                    box_height = abs(self.start_pos.y() - self.end_pos.y())
                elif self.up == True:
                    top_left_x = self.top_left_x
                    box_width = self.bottom_right_x - self.top_left_x
                    top_left_y = min(self.end_pos.y(), self.start_pos.y())
                    box_height = abs(self.start_pos.y() - self.end_pos.y())

                self.left = False
                self.right = False
                self.up = False
                self.down = False


                class_name = self.label_classes[self.selected_class]
                center_x = (top_left_x + box_width / 2) / self.image_view.sceneRect().width()
                center_y = (top_left_y + box_height / 2) / self.image_view.sceneRect().height()
                width = box_width / self.image_view.sceneRect().width()
                height = box_height / self.image_view.sceneRect().height()
                print(f"{self.selected_class} {class_name} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                # Save the bounding box coordinates to the current label file
                label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
                with open(label_path, "a") as label_file:
                    label_file.write(f"{self.selected_class} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                # Reload the current image and its bounding boxes
                self.showImage(self.current_index)


        elif self.dragging_start and event.button() == Qt.RightButton:
            # End dragging the bounding box
            self.dragging_start = False

            if self.start_pos != self.end_pos:

                top_left_x = self.top_left_x + (self.end_pos.x() - self.start_pos.x())
                box_width = self.bottom_right_x - self.top_left_x
                top_left_y = self.top_left_y + (self.end_pos.y() - self.start_pos.y())
                box_height = self.bottom_right_y - self.top_left_y

                class_name = self.label_classes[self.label_classes.index(self.selected_class)]
                self.selected_class = self.label_classes.index(self.selected_class)
                center_x = (top_left_x + box_width / 2) / self.image_view.sceneRect().width()
                center_y = (top_left_y + box_height / 2) / self.image_view.sceneRect().height()
                width = box_width / self.image_view.sceneRect().width()
                height = box_height / self.image_view.sceneRect().height()
                print(f"{self.selected_class} {class_name} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                # Save the bounding box coordinates to the current label file
                label_path = os.path.join(self.label_folder, self.label_files[self.current_index])
                with open(label_path, "a") as label_file:
                    label_file.write(f"{self.selected_class} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n")

                # Reload the current image and its bounding boxes
                self.showImage(self.current_index)



    def updateTemporaryBoundingBox(self):
        if self.drawing_start and not self.adjusting_start and self.start_pos and self.end_pos and self.image_view.cursor().shape() == 24:

            top_left_x = min(self.start_pos.x(), self.end_pos.x())
            box_width = abs(self.end_pos.x() - self.start_pos.x())
            top_left_y = min(self.start_pos.y(), self.end_pos.y())
            box_height = abs(self.end_pos.y() - self.start_pos.y())

            self.temp_rect_item.setRect(top_left_x, top_left_y, box_width, box_height)

            # Update the temporary rectangle item's position and size
        elif self.adjusting_start and not self.translate_start and not self.dragging_start:
            top_left_x = min(self.start_pos.x(), self.end_pos.x())
            box_width = abs(self.end_pos.x() - self.start_pos.x())
            top_left_y = min(self.start_pos.y(), self.end_pos.y())
            box_height = abs(self.end_pos.y() - self.start_pos.y())

            # self.temp_rect_item = QGraphicsRectItem()
            # self.temp_rect_item.setPen(QPen(QColor("yellow"), 2, Qt.SolidLine))
            # self.scene.addItem(self.temp_rect_item)

            self.temp_rect_item.setRect(top_left_x, top_left_y, box_width, box_height)

        elif self.translate_start and self.start_pos and self.end_pos and self.image_view.cursor().shape() == 24:

            if self.left == True:
                top_left_x = min(self.end_pos.x(), self.start_pos.x())
                box_width = abs(self.start_pos.x() - self.end_pos.x())
                top_left_y = self.top_left_y
                box_height = self.bottom_right_y - self.top_left_y
            elif self.right == True:
                top_left_x = min(self.end_pos.x(), self.start_pos.x())
                box_width = abs(self.start_pos.x() - self.end_pos.x())
                top_left_y = self.top_left_y
                box_height = self.bottom_right_y - self.top_left_y
            elif self.down == True:
                top_left_x = self.top_left_x
                box_width = self.bottom_right_x - self.top_left_x
                top_left_y = min(self.end_pos.y(), self.start_pos.y())
                box_height = abs(self.start_pos.y() - self.end_pos.y())
            elif self.up == True:
                top_left_x = self.top_left_x
                box_width = self.bottom_right_x - self.top_left_x
                top_left_y = min(self.end_pos.y(), self.start_pos.y())
                box_height = abs(self.start_pos.y() - self.end_pos.y())

            # Update the temporary rectangle item's position and size
            self.temp_rect_item.setRect(top_left_x, top_left_y, box_width, box_height)

        elif self.dragging_start and self.start_pos and self.end_pos and self.image_view.cursor().shape() == 24:
            top_left_x = self.top_left_x + (self.end_pos.x() - self.start_pos.x())
            box_width = self.bottom_right_x - self.top_left_x
            top_left_y = self.top_left_y + (self.end_pos.y() - self.start_pos.y())
            box_height = self.bottom_right_y - self.top_left_y

            # Update the temporary rectangle item's position and size
            self.temp_rect_item.setRect(top_left_x, top_left_y, box_width, box_height)
    def copyAndPasteBoundingBoxes(self):
        if self.current_index > 0:
            previous_label_path = os.path.join(self.label_folder, self.label_files[self.current_index - 1])
            TEN_BEFORE_label_path = os.path.join(self.label_folder, self.label_files[self.current_index - 10])
            current_label_path = os.path.join(self.label_folder, self.label_files[self.current_index])

            # Copy and paste bounding boxes from the previous image to the current image's label file
            if os.path.exists(previous_label_path):
                with open(previous_label_path, "r") as prev_file:
                    previous_bounding_boxes = prev_file.readlines()
                    print(previous_bounding_boxes)
                    print(previous_bounding_boxes == [])

                if previous_bounding_boxes != []:

                    with open(current_label_path, "w") as current_file:
                        # Copy previous bounding boxes to the current image's label file
                        current_file.writelines(previous_bounding_boxes)
                elif os.path.exists(TEN_BEFORE_label_path):
                    with open(TEN_BEFORE_label_path, "r") as TEN_prev_file:
                        bounding_boxes = TEN_prev_file.readlines()
                        print(bounding_boxes)

                    if bounding_boxes != []:
                        with open(current_label_path, "w") as current_file:
                            # Copy previous bounding boxes to the current image's label file
                            current_file.writelines(bounding_boxes)

            elif os.path.exists(TEN_BEFORE_label_path):
                with open(TEN_BEFORE_label_path, "r") as TEN_prev_file:
                    bounding_boxes = TEN_prev_file.readlines()
                    print(bounding_boxes)

                if bounding_boxes != []:

                    with open(current_label_path, "w") as current_file:
                        # Copy previous bounding boxes to the current image's label file
                        current_file.writelines(bounding_boxes)

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



            self.image_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.image_width = self.image_view.sceneRect().width()
            self.image_height = self.image_view.sceneRect().height()
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
        # super().paintEvent(event)

        for box in self.bounding_boxes:
            color = QColor(self.getColorForLabel(box["label"]))


            box_width = box["width"] * self.image_width
            box_height = box["height"] * self.image_height
            top_left_x = (box["center_x"] * self.image_width - box_width / 2)
            top_left_y = (box["center_y"] * self.image_height - box_height / 2)


            # Draw bounding box
            rect_item = QGraphicsRectItem(top_left_x, top_left_y, box_width, box_height)
            rect_item.setPen(QPen(color, 2))
            self.scene.addItem(rect_item)


            # Draw class label on the bounding box
            font_size = 14
            label_text = box['label']
            text_item = QGraphicsSimpleTextItem(label_text)
            text_item.setPos(top_left_x + 2, top_left_y + 2)
            text_item.setBrush(color)
            text_item.setFont(QFont("Arial", font_size))
            self.scene.addItem(text_item)



        self.image_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
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
