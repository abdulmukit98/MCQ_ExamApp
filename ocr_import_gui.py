import sys
import sqlite3
import re

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QMessageBox
)

OPTION_PATTERN = r"^\(?([a-dA-D])[\)\.]\s*"

def clean_text(text):
    text = re.sub(r"COMPACT IT.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Page\s*\d+", "", text, flags=re.IGNORECASE)
    return text


def extract_mcqs(text):
    text = clean_text(text)

    lines = text.split("\n")

    mcq_list = []
    current_block = []

    def flush_block(block_lines):
        block = "\n".join(block_lines).strip()

        if len(block) < 20:
            return

        ans_match = re.search(r"Ans:\s*([a-dA-D])", block)

        if not ans_match:
            return

        answer = ans_match.group(1).upper()

        block = re.split(r"Ans:\s*[a-dA-D]", block, flags=re.IGNORECASE)[0]

        block_lines = [
            l.strip()
            for l in block.split("\n")
            if l.strip()
        ]

        # Remove only Note lines
        block_lines = [
            l for l in block_lines
            if not re.match(r"^Note:", l, re.IGNORECASE)
        ]

        if not block_lines:
            return

        option_index = None

        for i, line in enumerate(block_lines):
            if re.match(OPTION_PATTERN, line):
                option_index = i
                break

        if option_index is None:
            return

        question_lines = block_lines[:option_index]

        option_lines = block_lines[option_index:option_index + 4]

        if len(option_lines) < 4:
            return

        question = "\n".join(question_lines)

        # options = []
        #
        # for opt in option_lines:
        #     opt = re.sub(r"^[a-dA-D]\)\s*", "", opt)
        #     options.append(opt.strip())

        options_dict = {
            "A": "",
            "B": "",
            "C": "",
            "D": ""
        }

        for opt in option_lines:

            label_match = re.match(OPTION_PATTERN, opt)

            if not label_match:
                continue

            label = label_match.group(1).upper()

            opt_text = re.sub(OPTION_PATTERN, "", opt)

            options_dict[label] = opt_text.strip()

        # mcq_list.append({
        #     "question": question,
        #     "a": options[0],
        #     "b": options[1],
        #     "c": options[2],
        #     "d": options[3],
        #     "answer": answer
        # })

        mcq_list.append({
            "question": question,
            "a": options_dict["A"],
            "b": options_dict["B"],
            "c": options_dict["C"],
            "d": options_dict["D"],
            "answer": answer
        })

    for line in lines:
        line = line.rstrip()

        # Detect ONLY true question start
        if re.match(r"^\d+\.\s", line):
            flush_block(current_block)
            current_block = [line]
        else:
            current_block.append(line)

    flush_block(current_block)

    return mcq_list


class OCRImporter(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OCR MCQ Importer")
        self.resize(900, 700)

        layout = QVBoxLayout()

        # OCR Input
        layout.addWidget(QLabel("Paste OCR Text"))

        self.ocr_input = QTextEdit()
        layout.addWidget(self.ocr_input)

        # Parse Button
        self.parse_button = QPushButton("Parse MCQs")
        self.parse_button.clicked.connect(self.parse_mcqs)
        layout.addWidget(self.parse_button)

        # Preview Area
        layout.addWidget(QLabel("Preview"))

        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        layout.addWidget(self.preview_area)

        # Save Button
        self.save_button = QPushButton("Save To Database")
        self.save_button.clicked.connect(self.save_mcqs)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.parsed_mcqs = []

    def parse_mcqs(self):
        text = self.ocr_input.toPlainText()

        self.parsed_mcqs = extract_mcqs(text)

        preview = ""

        for i, q in enumerate(self.parsed_mcqs):
            preview += f"\n========== MCQ {i+1} ==========\n"
            preview += f"{q['question']}\n\n"

            preview += f"A) {q['a']}\n"
            preview += f"B) {q['b']}\n"
            preview += f"C) {q['c']}\n"
            preview += f"D) {q['d']}\n"

            preview += f"\nCorrect Answer: {q['answer']}\n"

        self.preview_area.setText(preview)

        QMessageBox.information(
            self,
            "Parse Complete",
            f"Extracted {len(self.parsed_mcqs)} MCQs"
        )

    def save_mcqs(self):
        if not self.parsed_mcqs:
            QMessageBox.warning(self, "Error", "No MCQs parsed.")
            return

        conn = sqlite3.connect("mcq.db")
        cursor = conn.cursor()

        for q in self.parsed_mcqs:
            cursor.execute("""
            INSERT INTO questions (
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                q["question"],
                q["a"],
                q["b"],
                q["c"],
                q["d"],
                q["answer"]
            ))

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Success",
            f"Saved {len(self.parsed_mcqs)} MCQs to database!"
        )


app = QApplication(sys.argv)

window = OCRImporter()
window.show()

sys.exit(app.exec())
