import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import imutils
import copy
from SoftstripImage import SoftstripImage
from SoftstripDecoder import SoftstripDecoder

INCREASE = 1
DECREASE = -1
UP = -1
DOWN = 1
IMG_RESIZE = 50
PEN_SIZE = 10
MINIATURE_WIDTH = 400
DEGREE = 90


class SoftstripGui(QWidget):

    def __init__(self):
        super(SoftstripGui, self).__init__()
        self.chosen_points = []
        self.softstrip_img = None
        self.painter = None
        self.softstrips = []
        self.create_components()
        self.init_ui()

    def create_components(self):
        self.select_img_btn = QPushButton('Select Image')
        self.select_img_btn.setIcon(QIcon('icons/img.png'))

        self.rotate_left_btn = QPushButton('Rotate Left')
        self.rotate_left_btn.clicked.connect(self.rotate_left)
        self.rotate_left_btn.setIcon(QIcon('icons/left_rotate.png'))

        self.rotate_right_btn = QPushButton('Rotate Right')
        self.rotate_right_btn.clicked.connect(self.rotate_right)
        self.rotate_right_btn.setIcon(QIcon('icons/right_rotate.png'))

        self.select_softstrip_btn = QPushButton('Select Softstrip')
        self.select_softstrip_btn.clicked.connect(self.select_softstrip)
        self.select_softstrip_btn.setIcon(QIcon('icons/cut.png'))

        self.cancel_selection_btn = QPushButton('Cancel Selection')
        self.cancel_selection_btn.setEnabled(False)
        self.cancel_selection_btn.clicked.connect(self.cancel_softstrip_selection)
        self.cancel_selection_btn.setIcon(QIcon('icons/cancel.png'))

        self.confirm_selection_btn = QPushButton('Confirm Selection')
        self.confirm_selection_btn.setEnabled(False)
        self.confirm_selection_btn.clicked.connect(self.confirm_softstrip_selection)
        self.confirm_selection_btn.setIcon(QIcon('icons/done.png'))

        self.extract_btn = QPushButton('Extract Data')
        self.extract_btn.clicked.connect(self.extract_data)

        self.increase_size_btn = QPushButton('Increase Size')
        self.increase_size_btn.clicked.connect(self.increase_size)
        self.increase_size_btn.setIcon(QIcon('icons/zoom_in.png'))

        self.decrease_size_btn = QPushButton('Decrease Size')
        self.decrease_size_btn.clicked.connect(self.decrease_size)
        self.decrease_size_btn.setIcon(QIcon('icons/zoom_out.png'))

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()

        self.image_lbl = QLabel(self)
        self.image_lbl.mousePressEvent = self.mouse_click

        self.selected_img_lbl = QLabel(self)
        self.selected_img_lbl.setText('<h2>Selected Image</h2>')

        self.selected_softstrips_lbl = QLabel(self)
        self.selected_softstrips_lbl.setText('<h2>Selected Softstrips</h2>')

        self.move_item_up_btn = QPushButton('Move Up')
        self.move_item_up_btn.setEnabled(False)
        self.move_item_up_btn.clicked.connect(self.move_item_up)
        self.move_item_up_btn.setIcon(QIcon('icons/up.png'))

        self.move_item_down_btn = QPushButton('Move Down')
        self.move_item_down_btn.setEnabled(False)
        self.move_item_down_btn.clicked.connect(self.move_item_down)
        self.move_item_down_btn.setIcon(QIcon('icons/down.png'))

        self.remove_item_btn = QPushButton('Remove')
        self.remove_item_btn.setEnabled(False)
        self.remove_item_btn.clicked.connect(self.remove_item)
        self.remove_item_btn.setIcon(QIcon('icons/trash.png'))

        self.image_list = QListWidget(self)
        self.image_list.setStyleSheet("background-color: transparent")
        self.image_list.clicked.connect(self.enable_list_btns)

        self.select_img_btn.clicked.connect(self.openFileNameDialog)

    def openFileNameDialog(self):    
        path, _ = QFileDialog.getOpenFileName(self,'Open File')
        if path:
            self.chosen_points = [] 
            self.softstrip_img = SoftstripImage(path)
            self.image_lbl.setPixmap(self.softstrip_img.pixmap)
            self.image_lbl.adjustSize()

    def init_ui(self):
        v_layout = QVBoxLayout()
        h_btn_layout = QHBoxLayout()

        h_btn_layout.addWidget(self.select_img_btn)
        h_btn_layout.addWidget(self.rotate_left_btn)
        h_btn_layout.addWidget(self.rotate_right_btn)
        h_btn_layout.addWidget(self.select_softstrip_btn)
        h_btn_layout.addWidget(self.cancel_selection_btn)
        h_btn_layout.addWidget(self.confirm_selection_btn)
        h_btn_layout.addWidget(self.extract_btn)
        h_btn_layout.addWidget(self.increase_size_btn)
        h_btn_layout.addWidget(self.decrease_size_btn)

        v_layout.addLayout(h_btn_layout)
        h_lbl_layout = QHBoxLayout()
        h_lbl_layout.addWidget(self.selected_img_lbl)
        h_lbl_layout.addWidget(self.selected_softstrips_lbl)
        v_layout.addLayout(h_lbl_layout)

        h_layout_scroll = QHBoxLayout()
        v_layout.addLayout(h_layout_scroll)

        self.scroll_area_img, self.scroll_layout_img = self.create_scroll_area()
        self.scroll_layout_img.addWidget(self.image_lbl)
        h_layout_scroll.addWidget(self.scroll_area_img)

        self.scroll_area_softstrips, self.scroll_layout_softstrips = self.create_scroll_area()
        self.scroll_layout_softstrips.addWidget(self.image_list)
        h_layout_scroll.addWidget(self.scroll_area_softstrips)

        h_softstrip_btn_layout = QHBoxLayout()
        h_softstrip_btn_layout.addStretch(1)
        h_softstrip_btn_layout.addWidget(self.move_item_up_btn)
        h_softstrip_btn_layout.addWidget(self.move_item_down_btn)
        h_softstrip_btn_layout.addWidget(self.remove_item_btn)

        v_layout.addLayout(h_softstrip_btn_layout)

        self.setLayout(v_layout)
        self.setWindowTitle('Cauzin Softstrip Reader')
        self.showMaximized()

    def create_scroll_area(self):
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        return scroll_area, scroll_layout

    def update_canvas(self):
        self.image_lbl.setPixmap(self.softstrip_img.pixmap)
        self.image_lbl.adjustSize()

    def paintEvent(self, paint_event):
        if self.softstrip_img and self.softstrip_img.pixmap:
            self.painter = self.create_painter()
            for pos in self.chosen_points:
                self.painter.drawPoint(pos)
            self.update_canvas()
            self.painter.end()
    
    def create_painter(self):
        painter = QPainter(self.softstrip_img.pixmap)
        painter.drawImage(0, 0, self.softstrip_img.qimg)
        pen = QPen(Qt.red)
        pen.setWidth(PEN_SIZE)
        painter.setPen(pen)
        return painter

    def select_softstrip(self, event):
        self.show_info_dialog()
        self.select_softstrip_btn.setEnabled(False)
        self.cancel_selection_btn.setEnabled(True)
    
    def show_info_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText('Click on each corner to select a softstrip.\nA right mouse click removes the last point.')
        msg.setWindowTitle('Softstrip Selection')
        msg.setStandardButtons(QMessageBox.Ok)            
        msg.exec_()

    def cancel_softstrip_selection(self, event):
        self.select_softstrip_btn.setEnabled(True)
        self.cancel_selection_btn.setEnabled(False)
        self.chosen_points = []  

    def confirm_softstrip_selection(self, event):
        points = []
        for point in self.chosen_points:
            points.append([point.x(), point.y()])
        self.chosen_points = []
        old_img = copy.deepcopy(self.softstrip_img.cv2_img)
        self.softstrip_img.perspective_transformation(points)
        self.softstrips.append(self.softstrip_img)
        self.softstrip_img = SoftstripImage(None, old_img)
        self.update_canvas()
        self.update_selected_softstrips()
        self.cancel_selection_btn.setEnabled(False)
        self.confirm_selection_btn.setEnabled(False)
        self.select_softstrip_btn.setEnabled(True)

    def update_selected_softstrips(self):
        last_softstrip = self.softstrips[-1]
        miniature_lbl = self.create_selected_softstrip_lbl(last_softstrip)
        item = QListWidgetItem()
        item.setSizeHint(miniature_lbl.pixmap().size())
        self.image_list.addItem(item)
        self.image_list.setItemWidget(item, miniature_lbl)

    def mouse_click(self, event):
        if event.button() == Qt.LeftButton:
            self.draw_point(event)
        elif event.button() == Qt.RightButton:
            self.remove_point()
    
    def remove_point(self):
        self.chosen_points.pop()
        self.painter.drawImage(0, 0, self.softstrip_img.qimg)
        self.update()
    
    def draw_point(self, event):
        if len(self.chosen_points) < 4 and not self.select_softstrip_btn.isEnabled():
            img_size = self.softstrip_img.qimg.size()
            lbl_size = self.image_lbl.size()
            y_offset = (lbl_size.height() - img_size.height()) / 2
            pos = event.pos()
            pos.setY(pos.y() - y_offset)
            self.chosen_points.append(pos)
            self.update()
        if len(self.chosen_points) == 4:
            self.confirm_selection_btn.setEnabled(True)

    def rotate_left(self, event):
        self.chosen_points = [] 
        self.softstrip_img.rotate(DEGREE * -1)
        self.update_canvas()

    def rotate_right(self, event):
        self.chosen_points = [] 
        self.softstrip_img.rotate(DEGREE)
        self.update_canvas()
    
    def increase_size(self, event):
        self.softstrip_img.resize(IMG_RESIZE * INCREASE)
        self.update_canvas()
    
    def decrease_size(self, event):
        self.softstrip_img.resize(IMG_RESIZE * DECREASE)
        self.update_canvas()
    
    def change_img_size(self, direction):
        self.chosen_points = [] 
        rows, cols, channels = self.softstrip_img.cv2_img.shape
        self.softstrip_img.resize(IMG_RESIZE * direction + cols)
        self.update_canvas()

    def enable_list_btns(self):
        self.move_item_down_btn.setEnabled(True)
        self.move_item_up_btn.setEnabled(True)
        self.remove_item_btn.setEnabled(True)
    
    def move_item_up(self, event):
        self.move_item(UP)

    def move_item_down(self, event):
        self.move_item(DOWN)
    
    def move_item(self, direction):
        current_row = self.image_list.currentRow()
        if direction == DOWN and current_row < len(self.softstrips) - 1 \
            or direction == UP and current_row > 0:
            current_softstrip = self.softstrips[current_row]
            swap_softstrip = self.softstrips[current_row + direction]

            miniature_current_lbl = self.create_selected_softstrip_lbl(current_softstrip)
            miniature_swap_lbl = self.create_selected_softstrip_lbl(swap_softstrip)
            
            swap_item = self.image_list.item(current_row + direction)
            swap_item.setSizeHint(miniature_current_lbl.pixmap().size())
            current_item = self.image_list.item(current_row)
            current_item.setSizeHint(miniature_swap_lbl.pixmap().size())

            self.image_list.setItemWidget(swap_item, miniature_current_lbl)
            self.image_list.setItemWidget(current_item, miniature_swap_lbl)

            self.softstrips[current_row] = swap_softstrip
            self.softstrips[current_row + direction] = current_softstrip
            self.image_list.update()

    def create_selected_softstrip_lbl(self, softstrip):
        miniature = imutils.resize(softstrip.cv2_img, width=MINIATURE_WIDTH)
        img = SoftstripImage.convert_opencv_to_qimg(miniature)
        pixmap = QPixmap.fromImage(img)
        miniature_lbl = QLabel()
        miniature_lbl.setPixmap(pixmap)
        miniature_lbl.adjustSize()
        return miniature_lbl

    def remove_item(self):
        current_row = self.image_list.currentRow()
        self.image_list.takeItem(current_row)
        del self.softstrips[current_row]

    def show_message_box(self, text, title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def extract_data(self, event):
        self.softstrip_img.autocrop()
        binary_imgs = [self.softstrip_img.binary_img]
        paths = [self.softstrip_img.path]
        gray_imgs = [self.softstrip_img.gray_img]
        decoder = SoftstripDecoder(imgs=binary_imgs, paths=paths, gray_imgs=gray_imgs)
        #self.softstrip_img.convert_to_grayscale()
        self.update_canvas()
        self.show_message_box(str(decoder.strip_meta_info), 'Decoding')
        

app = QApplication(sys.argv)
writer = SoftstripGui()
sys.exit(app.exec_())