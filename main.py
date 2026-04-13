import sys

from PyQt6.QtWidgets import QApplication

from analizador_sintactico import AnalizadorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AnalizadorApp()
    window.show()
    sys.exit(app.exec())