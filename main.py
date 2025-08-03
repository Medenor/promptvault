import sys
from PyQt6.QtWidgets import QApplication
from prompt_manager_widget import PromptManager

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PromptManager()
    ex.show()
    sys.exit(app.exec())
