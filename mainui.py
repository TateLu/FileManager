import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeView, QFileSystemModel,
    QVBoxLayout, QWidget, QPushButton, QLineEdit, QHBoxLayout,
    QFileDialog, QMessageBox, QInputDialog, QTableWidget, QTableWidgetItem, QMenu, QAction
)
from PyQt5.QtCore import QDir, Qt
import subprocess


class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        # 当前程序的工作路径
        self.initial_directory = os.getcwd()
        self.current_directory = self.initial_directory

        self.setWindowTitle("文件管理器")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

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
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

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
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("搜索文件")
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_files)
        self.go_up_button = QPushButton("返回上级目录")
        self.go_up_button.clicked.connect(self.go_up_directory)

        button_layout.addWidget(self.create_dir_button)
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
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):  # 只添加文件
                        results.append((file, file_path))
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
        """更新文件列表，过滤掉目录，只展示文件"""
        self.file_table.setRowCount(0)
        for file in os.listdir(self.current_directory):
            file_path = os.path.join(self.current_directory, file)
            if os.path.isfile(file_path):  # 只展示文件
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

    # 右键菜单相关功能

    def show_context_menu(self, position):
        """右键菜单"""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        file_path = self.file_system_model.filePath(index)
        context_menu = QMenu(self)

        if os.path.isdir(file_path):
            # 添加文件
            add_file_action = QAction("添加文件", self)
            add_file_action.triggered.connect(lambda: self.add_file_to_directory(file_path))
            context_menu.addAction(add_file_action)

            # 新建子目录
            create_subdir_action = QAction("新建子目录", self)
            create_subdir_action.triggered.connect(lambda: self.create_sub_directory(file_path))
            context_menu.addAction(create_subdir_action)

            # 修改目录名称
            rename_dir_action = QAction("修改目录名称", self)
            rename_dir_action.triggered.connect(lambda: self.rename_directory(file_path))
            context_menu.addAction(rename_dir_action)

            # 删除目录
            delete_dir_action = QAction("删除目录", self)
            delete_dir_action.triggered.connect(lambda: self.delete_directory(file_path))
            context_menu.addAction(delete_dir_action)

        context_menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def add_file_to_directory(self, dir_path):
        """添加文件到选中的目录"""
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件")
        if file_path:
            try:
                target_file_path = os.path.join(dir_path, os.path.basename(file_path))
                shutil.copy(file_path, target_file_path)
                QMessageBox.information(self, "成功", f"文件已添加到目录 '{os.path.basename(dir_path)}'")
                self.update_file_list()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"添加文件失败: {str(e)}")

    def create_sub_directory(self, dir_path):
        """在选中目录下创建子目录"""
        new_dir_name, ok = QInputDialog.getText(self, "新建子目录", "请输入子目录名称:")
        if ok and new_dir_name:
            new_dir_path = os.path.join(dir_path, new_dir_name)
            try:
                os.makedirs(new_dir_path, exist_ok=True)
                QMessageBox.information(self, "成功", f"子目录 '{new_dir_name}' 创建成功")
                self.update_file_list()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"创建子目录失败: {str(e)}")

    def rename_directory(self, dir_path):
        """修改目录名称"""
        new_name, ok = QInputDialog.getText(self, "修改目录名称", "请输入新目录名称:")
        if ok and new_name:
            try:
                new_dir_path = os.path.join(os.path.dirname(dir_path), new_name)
                os.rename(dir_path, new_dir_path)
                QMessageBox.information(self, "成功", f"目录名称已修改为 '{new_name}'")
                self.update_file_list()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"重命名失败: {str(e)}")

    def delete_directory(self, dir_path):
        """删除选中目录及其所有内容"""
        reply = QMessageBox.question(
            self,
            "删除确认",
            f"您确定要删除目录 '{os.path.basename(dir_path)}' 及其所有内容吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                shutil.rmtree(dir_path)
                QMessageBox.information(self, "成功", f"目录 '{os.path.basename(dir_path)}' 已删除")
                self.update_file_list()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除失败: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_manager = FileManager()
    file_manager.show()
    sys.exit(app.exec_())
