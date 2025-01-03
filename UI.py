import multiprocessing
import time
import math
import subprocess
from concurrent.futures.thread import ThreadPoolExecutor

from PyQt6.QtCore import QSize, QObject, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QTransform
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QApplication
import os

from joint import joint
from limetorrent import getItemsLimeTorrents
from torrentgalaxy import getItemsTorrentGalaxy

Query_res = []


class WorkerSignals(QObject):
    result = pyqtSignal(list)
    error = pyqtSignal(str)


class ClickableLabel(QLabel):
    def __init__(self, text="", parent=None, link=""):
        super().__init__(text, parent)
        self.link = link

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.LeftButton:
            subprocess.call(["xdg-open", self.link])


class ScraperUI(QWidget):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        super().__init__()
        self.setGeometry(256, 192, 1366, 768)

        self.label = QLabel(self)
        self.initUI()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pixmap = QPixmap(f"{self.dir_path}/rss/loading.png")  # Replace with your icon path

        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)
        self.label.hide()  # Initially hidden

        # Set up the timer for rotation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_icon)
        # Layout
        self.angle = 0
        self.keys_pressed = {}

    def keyPressEvent(self, event):
        key = event.key()
        self.keys_pressed[key] = True  # Mark the key as pressed

        # Check if both keys are pressed (e.g., 'Q' and 'W')
        if (self.keys_pressed.get(Qt.Key.Key_Q) and self.keys_pressed.get(Qt.Key.Key_Control)) or self.keys_pressed.get(
                Qt.Key.Key_W) and self.keys_pressed.get(Qt.Key.Key_Control):
            self.close()

    def initUI(self):
        # search bar and button

        self.query = QLineEdit()
        self.query.setPlaceholderText("Query")
        self.query.setFixedHeight(60)
        self.query.setFont(QFont('Times', 25))
        self.query.returnPressed.connect(self.search)

        self.button = QPushButton("Search")
        self.button.pressed.connect(self.search)

        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon = QPixmap(f"{self.dir_path}/rss/loading.png")
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_icon)

        self.executor = ThreadPoolExecutor()
        self.signals = WorkerSignals()
        self.signals.result.connect(self.display_results)

        # adding them to horizontal layout
        self.search_container = QWidget(self)
        self.horizontal1 = QHBoxLayout(self.search_container)
        self.horizontal1.addWidget(self.query)
        self.horizontal1.addWidget(self.button)
        self.search_container.setObjectName("search")
        self.search_container.setStyleSheet("""
                    QWidget#search
                    {
                    border : 1px solid lightblue;
                    }
                    """)
        # possible Results screen
        self.Results = QScrollArea()
        self.Results.setWidgetResizable(True)

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()

        self.horizontal_loading = QHBoxLayout()
        self.horizontal_loading.addStretch(1)
        self.horizontal_loading.addWidget(self.label)
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.horizontal_loading.addStretch(1)
        self.results_layout.addLayout(self.horizontal_loading)

        self.results_container.setLayout(self.results_layout)

        self.Results.setWidget(self.results_container)

        self.vertical1 = QVBoxLayout()
        self.vertical1.addWidget(self.Results)
        self.vertical1.addWidget(self.search_container)

        self.setLayout(self.vertical1)
        self.query.setFocus()

    def itemWidget(self, item_details):
        self.title = ClickableLabel(item_details[2], link=item_details[3])
        self.seeds = QLabel("Seeds : " + item_details[7].__str__())
        self.leeches = QLabel("Leeches : " + item_details[8].__str__())
        self.size = QLabel("Size : " + item_details[6])
        self.uploader = QLabel("By : " + item_details[4])
        self.date = QLabel("On : " + item_details[5])

        self.type = QLabel(item_details[0])
        self.type.setFixedWidth(86)
        self.lang = QLabel(item_details[1])
        self.lang.setFixedWidth(86)

        self.magnet_button = QPushButton()
        self.magnet_button.setStyleSheet("""
            """)
        self.magnet_button.setIcon(QIcon(f"{self.dir_path}/rss/magnet.png"))
        self.magnet_button.setIconSize(QSize(48, 48))
        self.magnet_button.setFixedSize(64, 64)
        self.magnet_button.pressed.connect(lambda: self.open_magnet(str(item_details[-1])))

        self.item_row = QHBoxLayout()
        self.item_innner_column = QVBoxLayout()
        self.title.setWordWrap(True)

        self.item_row.addWidget(self.seeds)
        self.item_row.addWidget(self.leeches)
        self.item_row.addWidget(self.size)
        self.item_row.addWidget(self.uploader)
        self.item_row.addWidget(self.date)
        self.item_innner_column.addWidget(self.title)
        self.item_innner_column.addLayout(self.item_row)
        self.item = QWidget()

        self.category_col = QVBoxLayout()
        self.category_col.addWidget(self.type)
        self.category_col.addWidget(self.lang)

        self.main_row = QHBoxLayout()
        self.main_row.addLayout(self.category_col)
        self.main_row.addLayout(self.item_innner_column)
        self.main_row.addWidget(self.magnet_button)
        self.item.setObjectName("custom")
        self.item.setLayout(self.main_row)
        self.size.setStyleSheet("""
        QLabel{
        color:lightblue;
        }
        """)
        self.seeds.setStyleSheet("""
            QLabel{
                    color:green;
                        }
                        """)
        self.leeches.setStyleSheet("""
                QLabel{
                color: red;
                }
                """)
        self.item.setStyleSheet(
            """
            QWidget#custom
            {
                border:1px solid lightblue;
                }""")
        return self.item

    def search(self):
        if not self.button.isEnabled():
            return

        self.width = self.frameGeometry().width()
        self.height = self.frameGeometry().height()
        self.labelSize = (math.sqrt(self.height * self.width) // 2).__int__()
        self.label.setGeometry(int(self.width / 2 - self.labelSize / 2), int(self.height / 2 - self.labelSize / 2),
                               self.labelSize, self.labelSize)

        self.button.setEnabled(False)
        self.text = self.query.text()
        if len(self.query.text()) > 2:
            # Clear existing results
            while self.results_layout.count():
                item = self.results_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            Query_res.clear()
            self.executor.submit(self.run_get_items, self.text)
            if not self.timer.isActive():  # Check if the timer is already running
                self.label.setPixmap(self.icon)  # Reset the pixmap before starting
                self.label.show()
                self.timer.start(60)  # Start the timer only if it's not running

            self.text = self.query.text()

    def run_get_items(self, query):
        try:
            queue1 = multiprocessing.Queue()
            queue2 = multiprocessing.Queue()

            process1 = multiprocessing.Process(target=getItemsLimeTorrents, args=[query, queue1])
            process2 = multiprocessing.Process(target=getItemsTorrentGalaxy, args=[query, queue2])

            process1.start()
            process2.start()

            process1.join()
            process2.join()

            results1 = queue1.get()
            results2 = queue2.get()
            self.signals.result.emit(joint(results1, results2))
        except Exception as e:
            self.button.setEnabled(True)
            print(e)

    def display_results(self, results):
        if self.timer.isActive():
            self.timer.stop()
            self.label.hide()

        for i in results:
            Query_res.append(i)

        # Add the new results to the layout
        for i in Query_res:
            self.results_layout.addWidget(self.itemWidget(i))
        self.button.setEnabled(True)

    def open_magnet(self, link):
        print(f"this is the link : {link}")
        subprocess.call(["xdg-open", link])

    def rotate_icon(self):
        # Print statements to debug the method execution
        if self.label is not None and self.label.isVisible():
            transform = QTransform().rotate(self.angle)
            rotated_pixmap = self.icon.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(rotated_pixmap)
            self.angle += 6  # Adjust this for speed
            if self.angle >= 360:
                self.angle = 0
        else:
            self.timer.stop()


app = QApplication([])
window = ScraperUI()
window.setStyleSheet("""  
                    QWidget { 
                    background-color: grey;
                    border-radius: 16px;
                    background-color: gray;
                }
                """)
window.setWindowTitle("PYSOUP")
window.show()
app.exec()
