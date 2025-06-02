import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QAction, QFileDialog, QInputDialog, QScrollArea, QDockWidget, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard

class ManajemenBuku(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(100, 100, 900, 800)

        self.conn = sqlite3.connect("books.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, author TEXT, year TEXT)
        """)

        # Menu bar
        self.menu_bar = self.menuBar()
        self.menu_python = self.menu_bar.addMenu("Python")
        self.menu_file = self.menu_bar.addMenu("File")
        self.menu_edit = self.menu_bar.addMenu("Edit")

        self.file_save_action = QAction("Simpan", self)
        self.file_export_action = QAction("Ekspor ke CSV", self)
        self.file_exit_action = QAction("Keluar", self)
        self.menu_file.addAction(self.file_save_action)
        self.menu_file.addAction(self.file_export_action)
        self.menu_file.addAction(self.file_exit_action)
        self.file_export_action.triggered.connect(self.export_csv)
        self.file_exit_action.triggered.connect(self.close)

        self.edit_search_action = QAction("Cari Judul", self)
        self.edit_delete_action = QAction("Hapus Data", self)
        self.menu_edit.addAction(self.edit_search_action)
        self.menu_edit.addAction(self.edit_delete_action)
        self.edit_delete_action.triggered.connect(self.delete_data)

        # Layout atas
        top_layout = QVBoxLayout()
        tab_button_layout = QHBoxLayout()
        tab_button_layout.setAlignment(Qt.AlignCenter)

        self.btn_data = QPushButton("Data Buku")
        self.btn_export = QPushButton("Ekspor")
        self.btn_data.clicked.connect(lambda: self.switch_content("data"))
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_data.setStyleSheet("background-color: green; color: white;")
        self.btn_export.setStyleSheet("")
        tab_button_layout.addWidget(self.btn_data)
        tab_button_layout.addWidget(self.btn_export)
        top_layout.addLayout(tab_button_layout)

        self.content_widget = QWidget()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content_widget)
        top_layout.addWidget(self.scroll)

        central_widget = QWidget()
        central_widget.setLayout(top_layout)
        self.setCentralWidget(central_widget)

        self.init_data_content()
        self.init_export_content()
        self.switch_content("data")

        self.help_dock = QDockWidget("Bantuan", self)
        self.help_text = QTextEdit()
        self.help_text.setReadOnly(True)
        self.help_text.setText(
            "🛈 Tips:\n"
            "- Gunakan tombol 'Simpan' untuk menyimpan buku.\n"
            "- Klik dua kali sel untuk mengedit data.\n"
            "- Gunakan menu File > Ekspor untuk menyimpan data ke CSV.\n"
            "- Gunakan dock ini sebagai panel bantuan."
        )
        self.help_dock.setWidget(self.help_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.help_dock)

        self.statusBar().showMessage("Nama: Cindy Aulia Rahmani - NIM: F1D022116")

    def switch_content(self, name):
        if name == "data":
            self.btn_data.setStyleSheet("background-color: green; color: white;")
            self.btn_export.setStyleSheet("")
            self.content_widget.setLayout(self.data_layout)
        elif name == "export":
            self.btn_export.setStyleSheet("background-color: green; color: white;")
            self.btn_data.setStyleSheet("")
            self.content_widget.setLayout(self.export_layout)

    def init_data_content(self):
        self.data_layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        form_left = QVBoxLayout()
        form_right = QVBoxLayout()

        form_left.addWidget(QLabel("Judul:"))
        form_left.addWidget(QLabel("Pengarang:"))
        form_left.addWidget(QLabel("Tahun:"))

        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.year_input = QLineEdit()

        title_input_layout = QHBoxLayout()
        title_input_layout.addWidget(self.title_input)
        paste_btn = QPushButton("Paste from Clipboard")
        paste_btn.clicked.connect(self.paste_from_clipboard)
        title_input_layout.addWidget(paste_btn)

        form_right.addLayout(title_input_layout)
        form_right.addWidget(self.author_input)
        form_right.addWidget(self.year_input)

        form_layout.addLayout(form_left)
        form_layout.addLayout(form_right)
        self.data_layout.addLayout(form_layout)

        self.save_btn = QPushButton("Simpan")
        self.save_btn.clicked.connect(self.save_data)
        self.save_btn.setFixedWidth(100)
        self.data_layout.addWidget(self.save_btn, alignment=Qt.AlignHCenter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul...")
        self.search_input.textChanged.connect(self.search_data)
        self.data_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.data_layout.addWidget(self.table)

        self.delete_btn = QPushButton("Hapus Data")
        self.delete_btn.clicked.connect(self.delete_data)
        self.delete_btn.setStyleSheet("background-color: orange; color: black;")
        self.delete_btn.setFixedWidth(120)
        self.data_layout.addWidget(self.delete_btn, alignment=Qt.AlignLeft)

        self.load_data()
        self.table.cellDoubleClicked.connect(self.edit_cell)

    def init_export_content(self):
        self.export_layout = QVBoxLayout()
        label = QLabel("Klik menu File > Ekspor ke CSV untuk menyimpan data.")
        self.export_layout.addWidget(label)

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.title_input.setText(clipboard.text())

    def save_data(self):
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()
        if title and author and year:
            self.cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
                                (title, author, year))
            self.conn.commit()
            self.load_data()
            self.title_input.clear()
            self.author_input.clear()
            self.year_input.clear()
        else:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi!")

    def load_data(self):
        self.cursor.execute("SELECT * FROM books")
        records = self.cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(records):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def search_data(self):
        query = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and query in item.text().lower():
                    match = True
            self.table.setRowHidden(row, not match)

    def delete_data(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data yang dipilih!")
            return
        reply = QMessageBox.question(self, "Konfirmasi", "Hapus buku ID {}?".format(
            self.table.item(selected_row, 0).text()), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            book_id = self.table.item(selected_row, 0).text()
            self.cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
            self.conn.commit()
            self.load_data()

    def edit_cell(self, row, column):
        if column == 0:
            return
        current_value = self.table.item(row, column).text()
        field_map = {1: "title", 2: "author", 3: "year"}
        field_name = field_map.get(column)
        new_value, ok = QInputDialog.getText(self, f"Edit {field_name.capitalize()}",
                                             f"{field_name.capitalize()}:", text=current_value)
        if ok and new_value:
            book_id = self.table.item(row, 0).text()
            self.cursor.execute(f"UPDATE books SET {field_name}=? WHERE id=?", (new_value, book_id))
            self.conn.commit()
            self.load_data()

    def export_csv(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan CSV",
            "file_export.csv",
            "CSV Files (*.csv)",
            options=options
        )
        if filename:
            self.cursor.execute("SELECT * FROM books")
            records = self.cursor.fetchall()
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                writer.writerows(records)
            QMessageBox.information(self, "Sukses", "Data berhasil diekspor!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManajemenBuku()
    window.show()
    sys.exit(app.exec_())
