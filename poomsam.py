import tkinter as tk
from tkinter import filedialog, ttk
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
import threading
import os
from tqdm import tqdm


class App:
    def __init__(self, root):
        self.root = root
        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()

        self.input_label = tk.Label(root, text="PDF 파일 경로:")
        self.input_label.pack()
        self.input_entry = tk.Entry(root, textvariable=self.pdf_path)
        self.input_entry.pack()
        self.input_button = tk.Button(root, text="입력", command=self.select_pdf_file)
        self.input_button.pack()

        self.output_label = tk.Label(root, text="출력 디렉토리 경로:")
        self.output_label.pack()
        self.output_entry = tk.Entry(root, textvariable=self.output_dir)
        self.output_entry.pack()
        self.output_button = tk.Button(root, text="출력", command=self.select_output_directory)
        self.output_button.pack()

        self.convert_button = tk.Button(root, text="변환", command=self.start_conversion_thread)
        self.convert_button.pack()

        self.progress = tk.IntVar()
        self.progressbar = ttk.Progressbar(root, length=200, mode='determinate', variable=self.progress)
        self.progressbar.pack()

        self.progress_label = tk.Label(root, text="0.00%")
        self.progress_label.pack()

    def select_pdf_file(self):
        self.pdf_path.set(filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")]))

    def select_output_directory(self):
        self.output_dir.set(filedialog.askdirectory())

    def start_conversion_thread(self):
        threading.Thread(target=self.extract_text_from_pdf).start()

    def extract_text_from_pdf(self):
        txt_path = os.path.join(self.output_dir.get(), "output.txt")
        html_path = os.path.join(self.output_dir.get(), "output.html")

        resource_manager = PDFResourceManager()
        device = PDFPageAggregator(resource_manager, laparams=LAParams())
        interpreter = PDFPageInterpreter(resource_manager, device)

        with open(self.pdf_path.get(), 'rb') as file:
            pages = list(PDFPage.get_pages(file))
            total_pages = len(pages)

        with open(txt_path, 'w', encoding='utf-8') as txt_file, \
                open(html_path, 'w', encoding='utf-8') as html_file:
            for i, page in tqdm(enumerate(pages), total=total_pages, desc="페이지 처리 중"):  # tqdm을 사용하여 진행 상황을 표시합니다.
                interpreter.process_page(page)
                layout = device.get_result()
                texts = []
                for element in layout:
                    if isinstance(element, LTTextBox):
                        for text_line in element:
                            if isinstance(text_line, LTTextLine):
                                texts.append((text_line.bbox[1], text_line.get_text()))  # y 좌표와 텍스트를 튜플로 저장합니다.
                texts.sort(reverse=True)  # y 좌표를 기준으로 텍스트를 정렬합니다.
                for _, text in texts:
                    txt_file.write(text)
                    html_file.write(text.replace('\n', '<br>\n'))
                txt_file.write('\f\n')  # 페이지 구분자 추가
                html_file.write('<div style="page-break-after: always;"></div>\n')  # HTML 페이지 구분자 추가
                self.progress.set((i + 1) / total_pages * 100)  # 프로그레스 바 업데이트
                self.progress_label.config(text=f"{self.progress.get():.2f}%")  # 프로그레스 텍스트 업데이트

        print("텍스트 추출이 완료되었습니다.")


root = tk.Tk()
app = App(root)
root.mainloop()

