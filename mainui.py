import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTreeView, QListView,
                             QSplitter, QVBoxLayout, QWidget, QPushButton, QFileDialog, QFileSystemModel)
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()

    def initUI(self):
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Directory Tree
        self.treeView = QTreeView()
        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(QDir.rootPath())
        self.treeView.setModel(self.dirModel)
        self.treeView.setRootIndex(self.dirModel.index(QDir.homePath()))
        self.treeView.clicked.connect(self.on_tree_clicked)

        # Right side - File List
        self.listView = QListView()
        self.fileModel = QFileSystemModel()
        self.fileModel.setFilter(QDir.Files | QDir.NoDotAndDotDot)
        self.listView.setModel(self.fileModel)

        splitter.addWidget(self.treeView)
        splitter.addWidget(self.listView)

        self.setCentralWidget(splitter)
        self.setWindowTitle('File Manager')

        self.setup_directory_operations()

    def setup_directory_operations(self):
        # Add buttons and connect signals/slots here
        # For example, create a toolbar with buttons for adding, deleting, etc.
        pass

    def on_tree_clicked(self, index):
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        self.listView.setRootIndex(self.fileModel.setRootPath(path))

    def save_config(self):
        # Save the current state to a JSON file
        config = {
            'root_path': self.treeView.rootIndex().data(),
            'custom_directories': []  # This should be filled with actual data
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                # Restore the root path or custom directories from config
                root_path = config.get('root_path', QDir.homePath())
                self.treeView.setRootIndex(self.dirModel.index(root_path))
                # Implement logic to restore custom directories

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileManager()
    ex.show()
    sys.exit(app.exec_())