import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QProgressBar, QTextEdit, QFileDialog
from PyQt5.QtCore import Qt
import FileSorter

class FileSorterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('File Organizer')
        self.setGeometry(100, 100, 800, 600)  # Window size
        
        # Main Layout
        main_layout = QVBoxLayout()

        # Top Row Layout
        top_layout = QHBoxLayout()
        self.path_display = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.api_status = QLabel("API Status: Not Connected")
        self.fetch_button = QPushButton("Fetch Data")
        top_layout.addWidget(self.path_display)
        top_layout.addWidget(self.browse_button)
        top_layout.addWidget(self.api_status)
        top_layout.addWidget(self.fetch_button)
        self.browse_button.clicked.connect(self.browse_files)
        self.fetch_button.clicked.connect(self.fetch_data)

        # Middle Row Layout
        middle_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.progress_bar = QProgressBar()
        middle_layout.addWidget(self.start_button)
        middle_layout.addWidget(self.stop_button)
        middle_layout.addWidget(self.progress_bar)
        self.start_button.clicked.connect(self.start_sorting)

        # Bottom Row Layout
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        # Adding rows to the main layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(self.log_area)

        # Central Widget Setup
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def browse_files(self):
        # Opens a dialog to select a directory and updates the path_display LineEdit
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.path_display.setText(folder_path)
            self.update_log("Selected folder: " + folder_path)

    def fetch_data(self):
        # Placeholder for fetching data from an API
        self.update_log("Fetching data from the API...")
        # Simulate API fetching
        self.api_status.setText("API Status: Connected")

    def start_sorting(self):
        folder_path = self.path_display.text()
        if not folder_path:
            self.log_area.append("Please select a folder first.")
            return

        self.log_area.clear()
        try:
            organizer = FileSorter("config.json")  # Ensure 'config.json' is correctly pathed
            for progress, log in organizer.organize_files(folder_path):
                self.progress_bar.setValue(progress)
                self.log_area.append(log)
                QApplication.processEvents()  # This keeps the GUI responsive
        except Exception as e:
            self.log_area.append(f"An error occurred: {str(e)}")


    def update_log(self, message):
        # Updates the log area with the given message
        self.log_area.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    main_window = FileSorterGUI()
    main_window.show()
    sys.exit(app.exec_())
