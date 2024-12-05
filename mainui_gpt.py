import sys
import os
import json
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QFileSystemModel,
    QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout,
    QFileDialog, QMessageBox, QInputDialog, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QDir, Qt
import subprocess

CONFIG_FILE = "file_manager_config.json"

class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        # 当前程序的工作路径
        self.initial_directory = os.getcwd()
        self.current_directory = self.initial_directory

        self.setWindowTitle("文件管理器")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

        self.load_config()

    def init_ui(self):
        # 左侧目录树
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(self.initial_directory))
        self.tree_view.selectionModel().selectionChanged.connect(self.on_directory_selected)
        self.tree_view.doubleClicked.connect(self.on_directory_double_clicked)

        # 文件表格
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(2)
        self.file_table.setHorizontalHeaderLabels(["文件名", "文件路径"])
        self.file_table.horizontalHeader().setStretchLastSection(True)
        self.file_table.setColumnWidth(0, self.width() // 2)
        self.file_table.setColumnWidth(1, self.width() // 2)
        self.file_table.cellDoubleClicked.connect(self.on_table_item_double_clicked)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.create_dir_button = QPushButton("新建目录")
        self.create_dir_button.clicked.connect(self.create_directory)
        self.add_file_button = QPushButton("添加文件")
        self.add_file_button.clicked.connect(self.add_file_to_directory)
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("搜索文件")
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_files)
        self.go_up_button = QPushButton("返回上级目录")
        self.go_up_button.clicked.connect(self.go_up_directory)

        button_layout.addWidget(self.create_dir_button)
        button_layout.addWidget(self.add_file_button)
        button_layout.addWidget(self.search_bar)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.go_up_button)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tree_view, 3)
        main_layout.addWidget(self.file_table, 7)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_config(self):
        """加载配置"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_config(self):
        """保存配置"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def on_directory_selected(self, selected):
        """更新当前目录"""
        index = self.tree_view.selectionModel().currentIndex()
        if index.isValid():
            self.current_directory = self.file_system_model.filePath(index)
            self.current_directory = os.path.dirname(self.current_directory)  # 保留用户修改
            self.update_file_list()

    def create_directory(self):
        """创建新目录"""
        new_dir_name, ok = QInputDialog.getText(self, "新建目录", "请输入目录名称:")
        if ok and new_dir_name:
            new_dir_path = os.path.join(self.current_directory, new_dir_name)
            try:
                os.makedirs(new_dir_path, exist_ok=True)
                QMessageBox.information(self, "成功", f"目录 '{new_dir_name}' 创建成功")
                self.update_file_list()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"目录创建失败: {str(e)}")

    def add_file_to_directory(self):
        """添加文件到目录"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file in selected_files:
                dest_file = os.path.join(self.current_directory, os.path.basename(file))
                try:
                    shutil.copy(file, dest_file)
                    QMessageBox.information(self, "成功", f"文件 {os.path.basename(file)} 添加成功")
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"文件添加失败: {str(e)}")
            self.update_file_list()

    def search_files(self):
        """搜索文件"""
        keyword = self.search_bar.text()
        if not keyword:
            QMessageBox.warning(self, "警告", "请输入搜索关键词")
            return

        results = []
        for root, _, files in os.walk(self.current_directory):
            for file in files:
                if keyword.lower() in file.lower():
                    results.append((file, os.path.join(root, file)))
        self.display_search_results(results)

    def display_search_results(self, results):
        """显示搜索结果"""
        self.file_table.setRowCount(0)
        for file_name, file_path in results:
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            self.file_table.setItem(row, 0, QTableWidgetItem(file_name))
            self.file_table.setItem(row, 1, QTableWidgetItem(file_path))

    def update_file_list(self):
        """更新文件列表"""
        self.file_table.setRowCount(0)
        for file in os.listdir(self.current_directory):
            file_path = os.path.join(self.current_directory, file)
            row = self.file_table.rowCount()
            self.file_table.insertRow(row)
            self.file_table.setItem(row, 0, QTableWidgetItem(file))
            self.file_table.setItem(row, 1, QTableWidgetItem(file_path))

    def on_table_item_double_clicked(self, row, column):
        """双击文件表格项时打开文件"""
        file_path = self.file_table.item(row, 1).text()
        if os.path.isfile(file_path):
            self.open_file(file_path)

    def open_file(self, filepath):
        """打开文件"""
        try:
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.run(["open", filepath])
            else:
                subprocess.run(["xdg-open", filepath])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件: {str(e)}")

    def on_directory_double_clicked(self, index):
        """双击目录时进入该目录"""
        file_path = self.file_system_model.filePath(index)
        if os.path.isdir(file_path):
            self.current_directory = file_path
            self.tree_view.setRootIndex(self.file_system_model.index(self.current_directory))
            self.update_file_list()

    def go_up_directory(self):
        """返回上级目录"""
        parent_dir = os.path.dirname(self.current_directory)
        if parent_dir != self.current_directory:
            self.current_directory = parent_dir
            self.tree_view.setRootIndex(self.file_system_model.index(self.current_directory))
            self.update_file_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec_())
