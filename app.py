import sys
import sqlite3

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)

class MCQApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MCQ Question Entry")
        self.setGeometry(200, 200, 500, 600)

        layout = QVBoxLayout()

        # Question
        layout.addWidget(QLabel("Question"))
        self.question_input = QTextEdit()
        layout.addWidget(self.question_input)

        # Options
        layout.addWidget(QLabel("Option A"))
        self.option_a = QLineEdit()
        layout.addWidget(self.option_a)

        layout.addWidget(QLabel("Option B"))
        self.option_b = QLineEdit()
        layout.addWidget(self.option_b)

        layout.addWidget(QLabel("Option C"))
        self.option_c = QLineEdit()
        layout.addWidget(self.option_c)

        layout.addWidget(QLabel("Option D"))
        self.option_d = QLineEdit()
        layout.addWidget(self.option_d)

        # Correct answer
        layout.addWidget(QLabel("Correct Answer (A/B/C/D)"))
        self.correct_answer = QLineEdit()
        layout.addWidget(self.correct_answer)

        # Save button
        save_button = QPushButton("Save Question")
        save_button.clicked.connect(self.save_question)
        layout.addWidget(save_button)


        self.setLayout(layout)

    def save_question(self):
        question = self.question_input.toPlainText()
        option_a = self.option_a.text()
        option_b = self.option_b.text()
        option_c = self.option_c.text()
        option_d = self.option_d.text()
        correct_answer = self.correct_answer.text().upper()

        # Database connection
        conn = sqlite3.connect("mcq.db")
        cursor = conn.cursor()

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
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_answer
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Question saved successfully!")

        # Clear fields
        self.question_input.clear()
        self.option_a.clear()
        self.option_b.clear()
        self.option_c.clear()
        self.option_d.clear()
        self.correct_answer.clear()


app = QApplication(sys.argv)

window = MCQApp()
window.show()

sys.exit(app.exec())


