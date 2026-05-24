import sys
import sqlite3
import random

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QRadioButton, QMessageBox, QButtonGroup
)
from PyQt6.QtGui import QFont

class ExamApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MCQ Exam Mode")
        self.setFixedSize(700, 500)

        self.layout = QVBoxLayout()

        self.start_button = QPushButton("Start Exam (50 Questions)")
        self.start_button.clicked.connect(self.start_exam)
        self.layout.addWidget(self.start_button)

        self.question_label = QLabel("")
        ###
        self.font = QFont()
        self.font.setPointSize(15)
        ###
        self.question_label.setWordWrap(True)
        self.question_label.setFont(self.font)
        self.question_label.setStyleSheet("""
            padding: 10px;
        """)

        self.layout.addWidget(self.question_label)

        self.options_group = QButtonGroup()

        self.option_a = QRadioButton()
        self.option_b = QRadioButton()
        self.option_c = QRadioButton()
        self.option_d = QRadioButton()

        self.option_a.setFont(self.font)
        self.option_b.setFont(self.font)
        self.option_c.setFont(self.font)
        self.option_d.setFont(self.font)

        self.option_a.setStyleSheet("padding: 6px;")
        self.option_b.setStyleSheet("padding: 6px;")
        self.option_c.setStyleSheet("padding: 6px;")
        self.option_d.setStyleSheet("padding: 6px;")

        self.option_a.setMinimumHeight(50)
        self.option_b.setMinimumHeight(50)
        self.option_c.setMinimumHeight(50)
        self.option_d.setMinimumHeight(50)

        self.options_group.addButton(self.option_a)
        self.options_group.addButton(self.option_b)
        self.options_group.addButton(self.option_c)
        self.options_group.addButton(self.option_d)


        self.layout.addWidget(self.option_a)
        self.layout.addWidget(self.option_b)
        self.layout.addWidget(self.option_c)
        self.layout.addWidget(self.option_d)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_question)
        self.layout.addWidget(self.next_button)

        self.setLayout(self.layout)

        # Exam data
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.user_answers = []

    def load_questions(self):
        conn = sqlite3.connect("mcq.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 50")
        self.questions = cursor.fetchall()

        conn.close()

    def start_exam(self):
        self.load_questions()
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.show_question()

    def show_question(self):
        if self.current_index >= len(self.questions):
            self.show_result()
            return

        q = self.questions[self.current_index]

        self.question_label.setText(f"Q{self.current_index+1}: {q[1]}")
        self.option_a.setText(q[2])
        self.option_b.setText(q[3])
        self.option_c.setText(q[4])
        self.option_d.setText(q[5])

        self.option_a.setChecked(False)
        self.option_b.setChecked(False)
        self.option_c.setChecked(False)
        self.option_d.setChecked(False)

    def next_question(self):
        selected = None

        if self.option_a.isChecked():
            selected = "A"
        elif self.option_b.isChecked():
            selected = "B"
        elif self.option_c.isChecked():
            selected = "C"
        elif self.option_d.isChecked():
            selected = "D"

        correct = self.questions[self.current_index][6]

        # Save user answer (IMPORTANT NEW LINE)
        self.user_answers.append(selected)

        if selected == correct:
            self.score += 1

        self.current_index += 1
        self.show_question()



    # def show_result(self):
    #     QMessageBox.information(
    #         self,
    #         "Exam Finished",
    #         f"Your Score: {self.score} / {len(self.questions)}"
    #     )

    def show_result(self):
        review_text = ""

        for i, q in enumerate(self.questions):
            question = q[1]
            option_a = q[2]
            option_b = q[3]
            option_c = q[4]
            option_d = q[5]
            correct = q[6]

            user = self.user_answers[i] if i < len(self.user_answers) else "Not Answered"

            # Decide status
            if user == correct:
                status = "✔ CORRECT"
            else:
                status = "✘ WRONG"


            review_text += f"\nQ{i+1}: {question}\n"
            review_text += f"A. {option_a}\n"
            review_text += f"B. {option_b}\n"
            review_text += f"C. {option_c}\n"
            review_text += f"D. {option_d}\n"
            review_text += f"Your Answer: {user}\n"
            review_text += f"Correct Answer: {correct}\n"
            review_text += f"Result: {status}\n"
            review_text += "-----------------------------\n"


        QMessageBox.information(
            self,
            "Exam Finished",
            f"Your Score: {self.score} / {len(self.questions)}\n\n"
            "Review will open next window."
        )

        # Create review window
        from PyQt6.QtWidgets import QTextEdit, QDialog, QVBoxLayout

        review_window = QDialog(self)
        review_window.setWindowTitle("Answer Review")
        review_window.resize(700, 600)

        layout = QVBoxLayout()

        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setText(review_text)

        layout.addWidget(text_area)

        review_window.setLayout(layout)
        review_window.exec()


app = QApplication(sys.argv)
window = ExamApp()
window.show()
sys.exit(app.exec())
