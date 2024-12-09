import subprocess
from concurrent.futures.thread import ThreadPoolExecutor

from PyQt6.QtCore import QSize, QThread, QObject, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QWindow, QTextLine, QIcon, QDesktopServices, QPixmap, QTransform
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QApplication

from scraper import getItems

Query_res = []


class WorkerSignals(QObject):
    result = pyqtSignal(list)
    error = pyqtSignal(str)


class ScraperUI(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.left = 50
        self.top = 50
        self.width = 720
        self.height = 512
        self.initUI()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedSize(512, 512)
        self.pixmap = QPixmap("loading.png")  # Replace with your icon path



        self.label.setPixmap(self.pixmap)
        self.label.hide()  # Initially hidden

        # Set up the timer for rotation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_icon)

        # Layout
        self.angle = 0

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
        self.label.setFixedSize(512, 512)

        self.icon = QPixmap("loading.png")
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_icon)

        self.executor = ThreadPoolExecutor()
        self.signals = WorkerSignals()
        self.signals.result.connect(self.display_results)

        # adding them to horizontal layout
        self.horizontal1 = QHBoxLayout()
        self.horizontal1.addWidget(self.query)
        self.horizontal1.addWidget(self.button)

        # possible Results screen
        self.Results = QScrollArea()
        self.Results.setWidgetResizable(True)

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout()

        self.results_layout.addWidget(self.label)

        self.results_container.setLayout(self.results_layout)

        for i in Query_res:
            self.results_layout.addWidget(self.itemWidget(i))

        self.Results.setWidget(self.results_container)
        self.Results.resize(self.width, self.height)

        self.vertical1 = QVBoxLayout()
        self.vertical1.addWidget(self.Results)
        self.vertical1.addLayout(self.horizontal1)

        self.setLayout(self.vertical1)
        self.setGeometry(256, 192, 1366, 760)
        self.query.setFocus()

    def itemWidget(self, item_details):
        self.title = QLabel(str(item_details[2]).upper())
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
        self.magnet_button.setIcon(QIcon("magnet.png"))
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
        self.item.setStyleSheet("""
                QWidget#custom { 
                    background-color: white;
                    border: 1px solid lightblue;
                    border-radius: 16px;
                    background-color: transparent;
                }
            """)
        return self.item

    def search(self):
        self.text = self.query.text()
        if len(self.query.text()) > 2:
            # Clear existing results
            while self.results_layout.count():
                item = self.results_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            Query_res.clear()
            self.executor.submit(self.run_get_items, self.text, 1)
            if not self.timer.isActive():  # Check if the timer is already running
                self.label.setPixmap(self.icon)  # Reset the pixmap before starting
                self.label.show()
                self.timer.start(60)  # Start the timer only if it's not running

            self.text = self.query.text()

    def run_get_items(self, query, page):
        try:
            results = getItems(query, page=page)
            self.signals.result.emit(results)
        except Exception as e:
            print(e)

    def display_results(self, results):
        if self.timer.isActive():
            self.timer.stop()
            self.label.hide()

        for i in results:
            Query_res.append(i)

        # Add the new results to the layout
        if len(Query_res) < 50:
            for i in Query_res:
                self.results_layout.addWidget(self.itemWidget(i))
        elif len(Query_res) == 50:
            for i in Query_res:
                self.results_layout.addWidget(self.itemWidget(i))
            self.executor.submit(self.run_get_items, self.text, 2)
        else:
            for i in Query_res[50::]:
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
            print("Timer stopped, label is not visible")
            self.timer.stop()


app = QApplication([])
window = ScraperUI()
window.show()
app.exec()
