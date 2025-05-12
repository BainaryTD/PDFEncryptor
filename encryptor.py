import sys
import os
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QProgressBar, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class PDFEncryptor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("เข้ารหัส PDF ด้วย Excel")
        self.setGeometry(100, 100, 600, 250)

        self.excel_path = ""
        self.pdf_folder = ""
        self.output_folder = ""

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        font_label = QFont("Tahoma", 10)

        def create_row(button_text, label_ref, click_event):
            h_layout = QHBoxLayout()
            btn = QPushButton(button_text)
            btn.setFixedWidth(150)
            btn.clicked.connect(click_event)

            label = QLabel("ยังไม่เลือก")
            label.setFont(font_label)
            label.setStyleSheet("color: #333;")
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

            h_layout.addWidget(btn)
            h_layout.addWidget(label)

            label_ref.append(label)
            return h_layout

        # เก็บ QLabel ไว้อ้างอิงภายนอก
        self.labels = []

        # สร้างแต่ละแถว
        main_layout.addLayout(create_row("เลือก Excel", self.labels, self.select_excel))
        main_layout.addLayout(create_row("เลือกโฟลเดอร์ PDF", self.labels, self.select_pdf_folder))
        main_layout.addLayout(create_row("เลือกโฟลเดอร์ Output", self.labels, self.select_output_folder))

        # ปุ่มเริ่มประมวลผล
        self.start_btn = QPushButton("เริ่มเข้ารหัส PDF")
        self.start_btn.clicked.connect(self.process_files)
        self.start_btn.setFixedWidth(150)
        main_layout.addWidget(self.start_btn)

        # Status
        self.status_label = QLabel("")
        self.status_label.setFont(font_label)
        self.status_label.setStyleSheet("color: green;")
        main_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #dcdcdc;")  # สีพื้นหลัง

    def select_excel(self):
        file, _ = QFileDialog.getOpenFileName(self, "เลือก Excel", "", "Excel Files (*.xlsx *.xls)")
        if file:
            self.excel_path = file
            self.labels[0].setText(os.path.basename(file))

    def select_pdf_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ PDF")
        if folder:
            self.pdf_folder = folder
            self.labels[1].setText(folder)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์ Output")
        if folder:
            self.output_folder = folder
            self.labels[2].setText(folder)

    def process_files(self):
        if not self.excel_path or not self.pdf_folder or not self.output_folder:
            self.status_label.setText("กรุณาเลือกทุกอย่างให้ครบก่อนเริ่ม")
            self.status_label.setStyleSheet("color: red;")
            return

        try:
            df = pd.read_excel(self.excel_path)
            if 'filename' not in df.columns or 'password' not in df.columns:
                self.status_label.setText("Excel ต้องมีคอลัมน์ filename และ password")
                self.status_label.setStyleSheet("color: red;")
                return

            results = []
            total = len(df)
            self.progress_bar.setMaximum(total)

            for i, row in df.iterrows():
                filename = str(row['filename'])
                
                if not filename.lower().endswith(".pdf"):
                    filename += ".pdf"
                    
                password = str(row['password'])
                input_path = os.path.join(self.pdf_folder, filename)
                output_path = os.path.join(self.output_folder, f"{filename}")

                if not os.path.exists(input_path):
                    results.append({'filename': filename, 'status': 'ไม่พบไฟล์ PDF'})
                    continue

                try:
                    reader = PdfReader(input_path)
                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    writer.encrypt(password)

                    with open(output_path, "wb") as f:
                        writer.write(f)

                    results.append({'filename': filename, 'password':password, 'status': 'สำเร็จ'})
                except Exception as e:
                    results.append({'filename': filename, 'password':password, 'status': f'ล้มเหลว: {str(e)}'})

                self.progress_bar.setValue(i + 1)

            # สร้าง Excel ผลลัพธ์
            result_df = pd.DataFrame(results)
            result_path = os.path.join(self.output_folder, "ผลการเข้ารหัส.xlsx")
            result_df.to_excel(result_path, index=False)

            self.status_label.setText("ดำเนินการเสร็จสิ้น ✔️")
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"เกิดข้อผิดพลาด: {str(e)}")
            self.status_label.setStyleSheet("color: red;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFEncryptor()
    window.show()
    sys.exit(app.exec_())
