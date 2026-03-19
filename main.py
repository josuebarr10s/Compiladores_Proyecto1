import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFrame, QFileDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class AnalizadorLexicoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador Léxico")
        self.setGeometry(100, 100, 1200, 750)
        self.init_ui()

    def init_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        titulo = QLabel("Analizador Léxico")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        titulo.setObjectName("titulo")

        subtitulo = QLabel("Ingrese código manualmente o cargue un archivo .txt")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setObjectName("subtitulo")

        self.editor_codigo = QTextEdit()
        self.editor_codigo.setPlaceholderText(
            "Ingrese el texto a analizar"
        )
        self.editor_codigo.setFont(QFont("Consolas", 11))
        self.editor_codigo.setObjectName("editor")

        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)

        self.btn_cargar = QPushButton("Cargar archivo .txt")
        self.btn_cargar.clicked.connect(self.cargar_archivo)
        self.btn_cargar.setObjectName("botonCargar")

        self.btn_analizar = QPushButton("Analizar código")
        self.btn_analizar.clicked.connect(self.analizar_codigo)
        self.btn_analizar.setObjectName("botonAnalizar")

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_todo)
        self.btn_limpiar.setObjectName("botonLimpiar")

        botones_layout.addWidget(self.btn_cargar)
        botones_layout.addWidget(self.btn_analizar)
        botones_layout.addWidget(self.btn_limpiar)

        separador1 = self.crear_separador()

        label_tokens = QLabel("Tabla de Tokens")
        label_tokens.setObjectName("seccion")

        self.tabla_tokens = QTableWidget()
        self.tabla_tokens.setColumnCount(5)
        self.tabla_tokens.setHorizontalHeaderLabels(
            ["No.", "Lexema", "Token", "Fila", "Columna"]
        )
        self.tabla_tokens.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_tokens.setObjectName("tabla")

        separador2 = self.crear_separador()

        label_errores = QLabel("Errores Léxicos")
        label_errores.setObjectName("seccion")

        self.tabla_errores = QTableWidget()
        self.tabla_errores.setColumnCount(6)
        self.tabla_errores.setHorizontalHeaderLabels(
            ["No.", "Lexema", "Tipo Error", "Fila", "Columna", "Descripción"]
        )
        self.tabla_errores.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_errores.setObjectName("tabla")

        layout_principal.addWidget(titulo)
        layout_principal.addWidget(subtitulo)
        layout_principal.addWidget(self.editor_codigo)
        layout_principal.addLayout(botones_layout)
        layout_principal.addWidget(separador1)
        layout_principal.addWidget(label_tokens)
        layout_principal.addWidget(self.tabla_tokens)
        layout_principal.addWidget(separador2)
        layout_principal.addWidget(label_errores)
        layout_principal.addWidget(self.tabla_errores)

        self.setLayout(layout_principal)
        self.aplicar_estilos()

    def crear_separador(self):
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setFrameShadow(QFrame.Shadow.Sunken)
        separador.setObjectName("separador")
        return separador

    def aplicar_estilos(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                font-family: 'Segoe UI';
            }

            QLabel#titulo {
                color: #38bdf8;
                padding: 10px;
            }

            QLabel#subtitulo {
                color: #cbd5e1;
                font-size: 14px;
                margin-bottom: 5px;
            }

            QLabel#seccion {
                font-size: 16px;
                font-weight: bold;
                color: #f8fafc;
                padding: 6px 0;
            }

            QTextEdit#editor {
                background-color: #1e293b;
                color: #f8fafc;
                border: 2px solid #334155;
                border-radius: 12px;
                padding: 12px;
                selection-background-color: #2563eb;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#botonCargar {
                background-color: #8b5cf6;
                color: white;
            }

            QPushButton#botonCargar:hover {
                background-color: #7c3aed;
            }

            QPushButton#botonAnalizar {
                background-color: #0ea5e9;
                color: white;
            }

            QPushButton#botonAnalizar:hover {
                background-color: #0284c7;
            }

            QPushButton#botonLimpiar {
                background-color: #ef4444;
                color: white;
            }

            QPushButton#botonLimpiar:hover {
                background-color: #dc2626;
            }

            QTableWidget#tabla {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
                gridline-color: #475569;
                color: #f8fafc;
            }

            QHeaderView::section {
                background-color: #334155;
                color: #f8fafc;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #475569;
            }

            QFrame#separador {
                color: #475569;
                background-color: #475569;
                max-height: 2px;
            }
        """)

    def cargar_archivo(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de texto",
            "",
            "Archivos de texto (*.txt)"
        )

        if ruta_archivo:
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                    contenido = archivo.read()
                    self.editor_codigo.setPlainText(contenido)
                QMessageBox.information(self, "Archivo cargado", "El archivo .txt se cargó correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")

    def limpiar_todo(self):
        self.editor_codigo.clear()
        self.tabla_tokens.setRowCount(0)
        self.tabla_errores.setRowCount(0)

    def analizar_codigo(self):
        codigo = self.editor_codigo.toPlainText()

        if not codigo.strip():
            QMessageBox.warning(self, "Advertencia", "Ingrese código o cargue un archivo para analizar.")
            return

        tokens, errores = self.analizador_lexico(codigo)
        self.mostrar_tokens(tokens)
        self.mostrar_errores(errores)

    def analizador_lexico(self, codigo):
        palabras_reservadas = {
            "programa", "entero", "real", "cadena", "si", "sino",
            "mientras", "para", "imprimir", "leer", "inicio", "fin"
        }

        operadores_dobles = {"==", "!=", ">=", "<=", "&&", "||"}
        operadores_simples = {"+", "-", "*", "/", "=", ">", "<", "!"}
        delimitadores = {";", ",", "(", ")", "{", "}", "[", "]", ":"}

        tokens = []
        errores = []

        filas = codigo.split("\n")

        for num_fila, linea in enumerate(filas, start=1):
            i = 0
            while i < len(linea):
                char = linea[i]

                if char.isspace():
                    i += 1
                    continue

                columna = i + 1

                if i + 1 < len(linea) and linea[i:i+2] == "//":
                    break

                if char == '"':
                    inicio = i
                    i += 1
                    cadena = '"'
                    cerrado = False

                    while i < len(linea):
                        cadena += linea[i]
                        if linea[i] == '"':
                            cerrado = True
                            i += 1
                            break
                        i += 1

                    if cerrado:
                        tokens.append((cadena, "Cadena", num_fila, inicio + 1))
                    else:
                        errores.append((
                            cadena,
                            "Cadena no cerrada",
                            num_fila,
                            inicio + 1,
                            "Falta comilla de cierre"
                        ))
                    continue

                if i + 1 < len(linea) and linea[i:i+2] in operadores_dobles:
                    lexema = linea[i:i+2]
                    tokens.append((lexema, "Operador", num_fila, columna))
                    i += 2
                    continue

                if char in operadores_simples:
                    tokens.append((char, "Operador", num_fila, columna))
                    i += 1
                    continue

                if char in delimitadores:
                    tokens.append((char, "Delimitador", num_fila, columna))
                    i += 1
                    continue

                if char.isdigit():
                    inicio = i
                    numero = ""
                    puntos = 0

                    while i < len(linea) and (linea[i].isdigit() or linea[i] == "."):
                        if linea[i] == ".":
                            puntos += 1
                        numero += linea[i]
                        i += 1

                    if puntos <= 1:
                        tipo_num = "Número real" if "." in numero else "Número entero"
                        tokens.append((numero, tipo_num, num_fila, inicio + 1))
                    else:
                        errores.append((
                            numero,
                            "Número inválido",
                            num_fila,
                            inicio + 1,
                            "El número contiene más de un punto decimal"
                        ))
                    continue

                if char.isalpha() or char == "_":
                    inicio = i
                    identificador = ""

                    while i < len(linea) and (linea[i].isalnum() or linea[i] == "_"):
                        identificador += linea[i]
                        i += 1

                    if identificador in palabras_reservadas:
                        tokens.append((identificador, "Palabra reservada", num_fila, inicio + 1))
                    else:
                        tokens.append((identificador, "Identificador", num_fila, inicio + 1))
                    continue

                errores.append((
                    char,
                    "Símbolo no reconocido",
                    num_fila,
                    columna,
                    "Carácter no pertenece al lenguaje"
                ))
                i += 1

        return tokens, errores

    def mostrar_tokens(self, tokens):
        self.tabla_tokens.setRowCount(0)

        for idx, token in enumerate(tokens, start=1):
            fila = self.tabla_tokens.rowCount()
            self.tabla_tokens.insertRow(fila)

            self.tabla_tokens.setItem(fila, 0, QTableWidgetItem(str(idx)))
            self.tabla_tokens.setItem(fila, 1, QTableWidgetItem(token[0]))
            self.tabla_tokens.setItem(fila, 2, QTableWidgetItem(token[1]))
            self.tabla_tokens.setItem(fila, 3, QTableWidgetItem(str(token[2])))
            self.tabla_tokens.setItem(fila, 4, QTableWidgetItem(str(token[3])))

    def mostrar_errores(self, errores):
        self.tabla_errores.setRowCount(0)

        for idx, error in enumerate(errores, start=1):
            fila = self.tabla_errores.rowCount()
            self.tabla_errores.insertRow(fila)

            self.tabla_errores.setItem(fila, 0, QTableWidgetItem(str(idx)))
            self.tabla_errores.setItem(fila, 1, QTableWidgetItem(error[0]))
            self.tabla_errores.setItem(fila, 2, QTableWidgetItem(error[1]))
            self.tabla_errores.setItem(fila, 3, QTableWidgetItem(str(error[2])))
            self.tabla_errores.setItem(fila, 4, QTableWidgetItem(str(error[3])))
            self.tabla_errores.setItem(fila, 5, QTableWidgetItem(error[4]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AnalizadorLexicoApp()
    ventana.show()
    sys.exit(app.exec())