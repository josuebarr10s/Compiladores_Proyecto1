import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QFrame,
    QGraphicsDropShadowEffect, QComboBox
)
from PyQt6.QtGui import (
    QFont, QColor, QTextCharFormat, QSyntaxHighlighter
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QParallelAnimationGroup


PALABRAS_RESERVADAS = {
    "Cliente", "Pedido", "Repartidor", "Precio", "Dirección", "Asignar",
    "Entregado", "Recibido", "Rechazado", "Aprobado", "Procesando",
    "Listo", "En", "Ruta", "Agotado", "Stock"
}

SIMBOLOS_PERMITIDOS = {":", ";", '"', "(", ")", "$", "%"}
PATRON_IDENTIFICADOR = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
PATRON_NUMERO = re.compile(r"^\d+(\.\d+)?$")


class ResaltadorLexico(QSyntaxHighlighter):
    def __init__(self, document, app_ref):
        super().__init__(document)
        self.app_ref = app_ref
        self.actualizar_formatos()

    def actualizar_formatos(self):
        tema = self.app_ref.tema_actual

        if tema == "oscuro":
            self.formato_reservada = self.crear_formato("#60a5fa", negrita=True)
            self.formato_identificador = self.crear_formato("#e5e7eb")
            self.formato_numero = self.crear_formato("#c084fc")
            self.formato_cadena = self.crear_formato("#34d399")
            self.formato_simbolo = self.crear_formato("#fbbf24", negrita=True)
            self.formato_error = self.crear_formato("#f87171")
            self.formato_error.setUnderlineColor(QColor("#ef4444"))
            self.formato_error.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        else:
            self.formato_reservada = self.crear_formato("#2563eb", negrita=True)
            self.formato_identificador = self.crear_formato("#111827")
            self.formato_numero = self.crear_formato("#7c3aed")
            self.formato_cadena = self.crear_formato("#059669")
            self.formato_simbolo = self.crear_formato("#ea580c", negrita=True)
            self.formato_error = self.crear_formato("#dc2626")
            self.formato_error.setUnderlineColor(QColor("#dc2626"))
            self.formato_error.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)

    def crear_formato(self, color_hex, negrita=False):
        formato = QTextCharFormat()
        formato.setForeground(QColor(color_hex))
        if negrita:
            formato.setFontWeight(QFont.Weight.Bold)
        return formato

    def highlightBlock(self, texto):
        i = 0
        n = len(texto)

        while i < n:
            ch = texto[i]

            if ch.isspace():
                i += 1
                continue

            if ch == '"':
                inicio = i
                i += 1
                cerrado = False
                while i < n:
                    if texto[i] == '"':
                        cerrado = True
                        i += 1
                        break
                    i += 1

                if cerrado:
                    self.setFormat(inicio, i - inicio, self.formato_cadena)
                else:
                    self.setFormat(inicio, n - inicio, self.formato_error)
                continue

            if ch in SIMBOLOS_PERMITIDOS - {'"'}:
                self.setFormat(i, 1, self.formato_simbolo)
                i += 1
                continue

            if ch.isdigit():
                inicio = i
                while i < n and (texto[i].isdigit() or texto[i] == "."):
                    i += 1

                lexema = texto[inicio:i]

                # Caso 01P -> error completo
                if i < n and texto[i].isalpha():
                    while i < n and texto[i].isalnum():
                        i += 1
                    self.setFormat(inicio, i - inicio, self.formato_error)
                    continue

                if PATRON_NUMERO.fullmatch(lexema):
                    self.setFormat(inicio, len(lexema), self.formato_numero)
                else:
                    self.setFormat(inicio, len(lexema), self.formato_error)
                continue

            if ch.isalpha():
                inicio = i
                while i < n and texto[i].isalnum():
                    i += 1
                lexema = texto[inicio:i]

                if lexema in PALABRAS_RESERVADAS:
                    self.setFormat(inicio, len(lexema), self.formato_reservada)
                elif PATRON_IDENTIFICADOR.fullmatch(lexema):
                    self.setFormat(inicio, len(lexema), self.formato_identificador)
                else:
                    self.setFormat(inicio, len(lexema), self.formato_error)
                continue

            self.setFormat(i, 1, self.formato_error)
            i += 1


class AnalizadorLexicoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador Léxico")
        self.resize(1380, 820)
        self.tema_actual = "claro"
        self.animaciones = []
        self.init_ui()

    def init_ui(self):
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setContentsMargins(18, 18, 18, 18)
        layout_raiz.setSpacing(14)

        encabezado = QFrame()
        encabezado.setObjectName("encabezado")
        header_layout = QHBoxLayout(encabezado)
        header_layout.setContentsMargins(20, 14, 20, 14)

        bloque_titulos = QVBoxLayout()
        titulo = QLabel("Analizador Léxico")
        titulo.setObjectName("titulo")
        subtitulo = QLabel("Lenguaje de gestión de pedidos")
        subtitulo.setObjectName("subtitulo")
        bloque_titulos.addWidget(titulo)
        bloque_titulos.addWidget(subtitulo)

        self.selector_tema = QComboBox()
        self.selector_tema.addItems(["Modo claro", "Modo oscuro"])
        self.selector_tema.currentIndexChanged.connect(self.cambiar_tema)
        self.selector_tema.setObjectName("selectorTema")

        header_layout.addLayout(bloque_titulos)
        header_layout.addStretch()
        header_layout.addWidget(self.selector_tema)

        layout_raiz.addWidget(encabezado)

        layout_principal = QHBoxLayout()
        layout_principal.setSpacing(16)

        # Panel izquierdo
        self.panel_izquierdo = QFrame()
        self.panel_izquierdo.setObjectName("card")
        self.agregar_sombra(self.panel_izquierdo)

        layout_izquierdo = QVBoxLayout(self.panel_izquierdo)
        layout_izquierdo.setContentsMargins(18, 18, 18, 18)
        layout_izquierdo.setSpacing(12)

        label_editor = QLabel("Ingresar el texto")
        label_editor.setObjectName("tituloPanel")

        self.editor_codigo = QTextEdit()
        self.editor_codigo.setObjectName("editor")
        self.editor_codigo.setFont(QFont("Consolas", 11))
        self.editor_codigo.setPlaceholderText(
            "Ingrese el texto a analizar"
        )

        self.resaltador = ResaltadorLexico(self.editor_codigo.document(), self)
        self.editor_codigo.textChanged.connect(self.actualizar_errores_en_vivo)

        botones = QHBoxLayout()
        botones.setSpacing(10)

        self.btn_cargar = QPushButton("Cargar .txt")
        self.btn_cargar.setObjectName("botonSecundario")
        self.btn_cargar.clicked.connect(self.cargar_archivo)

        self.btn_analizar = QPushButton("Analizar Código")
        self.btn_analizar.setObjectName("botonPrincipal")
        self.btn_analizar.clicked.connect(self.analizar_codigo)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setObjectName("botonPeligro")
        self.btn_limpiar.clicked.connect(self.limpiar_todo)

        botones.addWidget(self.btn_cargar)
        botones.addWidget(self.btn_analizar)
        botones.addWidget(self.btn_limpiar)

        layout_izquierdo.addWidget(label_editor)
        layout_izquierdo.addWidget(self.editor_codigo)
        layout_izquierdo.addLayout(botones)

        # Panel derecho
        panel_derecho_layout = QVBoxLayout()
        panel_derecho_layout.setSpacing(16)

        self.card_tokens = QFrame()
        self.card_tokens.setObjectName("card")
        self.agregar_sombra(self.card_tokens)

        layout_tokens = QVBoxLayout(self.card_tokens)
        layout_tokens.setContentsMargins(18, 18, 18, 18)
        layout_tokens.setSpacing(12)

        label_tokens = QLabel("Tabla de tokens")
        label_tokens.setObjectName("tituloPanel")

        self.tabla_tokens = QTableWidget()
        self.tabla_tokens.setColumnCount(2)
        self.tabla_tokens.setHorizontalHeaderLabels(["Lexema", "Token"])
        self.tabla_tokens.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_tokens.setObjectName("tabla")

        layout_tokens.addWidget(label_tokens)
        layout_tokens.addWidget(self.tabla_tokens)

        self.card_errores = QFrame()
        self.card_errores.setObjectName("cardErrores")
        self.agregar_sombra(self.card_errores)

        layout_errores = QVBoxLayout(self.card_errores)
        layout_errores.setContentsMargins(18, 18, 18, 18)
        layout_errores.setSpacing(12)

        label_errores = QLabel("Errores léxicos")
        label_errores.setObjectName("tituloPanel")

        self.tabla_errores = QTableWidget()
        self.tabla_errores.setColumnCount(4)
        self.tabla_errores.setHorizontalHeaderLabels(["Lexema", "Fila", "Columna", "Descripción"])
        self.tabla_errores.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_errores.setObjectName("tabla")

        layout_errores.addWidget(label_errores)
        layout_errores.addWidget(self.tabla_errores)

        panel_derecho_layout.addWidget(self.card_tokens, 1)
        panel_derecho_layout.addWidget(self.card_errores, 1)

        layout_principal.addWidget(self.panel_izquierdo, 3)
        layout_principal.addLayout(panel_derecho_layout, 2)

        layout_raiz.addLayout(layout_principal)

        self.aplicar_estilos()

    def agregar_sombra(self, widget):
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(28)
        sombra.setOffset(0, 8)
        sombra.setColor(QColor(15, 23, 42, 30))
        widget.setGraphicsEffect(sombra)

    def cambiar_tema(self):
        self.tema_actual = "oscuro" if self.selector_tema.currentIndex() == 1 else "claro"
        self.aplicar_estilos()
        self.resaltador.actualizar_formatos()
        self.resaltador.rehighlight()

    def aplicar_estilos(self):
        if self.tema_actual == "oscuro":
            self.setStyleSheet("""
                QWidget {
                    background-color: #0f172a;
                    color: #e5e7eb;
                    font-family: 'Segoe UI';
                }
                QFrame#encabezado, QFrame#card, QFrame#cardErrores {
                    background-color: #111827;
                    border: 1px solid #243041;
                    border-radius: 20px;
                }
                QLabel#titulo { font-size: 28px; font-weight: 700; color: #f8fafc; }
                QLabel#subtitulo { font-size: 13px; color: #94a3b8; }
                QLabel#tituloPanel { font-size: 18px; font-weight: 700; color: #e2e8f0; }
                QTextEdit#editor {
                    background-color: #0b1220;
                    border: 1px solid #243041;
                    border-radius: 16px;
                    padding: 14px;
                    color: #f8fafc;
                    selection-background-color: #1d4ed8;
                }
                QPushButton, QComboBox {
                    border: none;
                    border-radius: 12px;
                    padding: 11px 18px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton#botonPrincipal { background-color: #2563eb; color: white; }
                QPushButton#botonPrincipal:hover { background-color: #1d4ed8; }
                QPushButton#botonSecundario { background-color: #1e293b; color: #c7d2fe; }
                QPushButton#botonSecundario:hover { background-color: #243041; }
                QPushButton#botonPeligro { background-color: #3b1219; color: #fca5a5; }
                QPushButton#botonPeligro:hover { background-color: #4a1620; }
                QComboBox#selectorTema {
                    background-color: #1e293b;
                    color: #f8fafc;
                    padding: 10px 14px;
                }
                QTableWidget#tabla {
                    background-color: #0b1220;
                    border: 1px solid #243041;
                    border-radius: 14px;
                    gridline-color: #1f2937;
                    color: #f8fafc;
                }
                QHeaderView::section {
                    background-color: #111827;
                    color: #cbd5e1;
                    font-weight: bold;
                    padding: 8px;
                    border: none;
                    border-bottom: 1px solid #243041;
                }
                QFrame#cardErrores {
                    border: 1px solid #7f1d1d;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f6f8fc;
                    color: #1f2937;
                    font-family: 'Segoe UI';
                }
                QFrame#encabezado {
                    background-color: #ffffff;
                    border: 1px solid #e5e7eb;
                    border-radius: 20px;
                }
                QFrame#card {
                    background-color: #ffffff;
                    border: 1px solid #e8edf5;
                    border-radius: 20px;
                }
                QFrame#cardErrores {
                    background-color: #fff7f7;
                    border: 1px solid #fecaca;
                    border-radius: 20px;
                }
                QLabel#titulo { font-size: 28px; font-weight: 700; color: #111827; }
                QLabel#subtitulo { font-size: 13px; color: #64748b; }
                QLabel#tituloPanel { font-size: 18px; font-weight: 700; color: #334155; }
                QTextEdit#editor {
                    background-color: #fbfcfe;
                    border: 1px solid #e2e8f0;
                    border-radius: 16px;
                    padding: 14px;
                    color: #111827;
                    selection-background-color: #dbeafe;
                }
                QPushButton, QComboBox {
                    border: none;
                    border-radius: 12px;
                    padding: 11px 18px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton#botonPrincipal { background-color: #2563eb; color: white; }
                QPushButton#botonPrincipal:hover { background-color: #1d4ed8; }
                QPushButton#botonSecundario { background-color: #eef2ff; color: #3730a3; }
                QPushButton#botonSecundario:hover { background-color: #e0e7ff; }
                QPushButton#botonPeligro { background-color: #fef2f2; color: #b91c1c; }
                QPushButton#botonPeligro:hover { background-color: #fee2e2; }
                QComboBox#selectorTema {
                    background-color: #eef2ff;
                    color: #111827;
                    padding: 10px 14px;
                }
                QTableWidget#tabla {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 14px;
                    gridline-color: #edf2f7;
                    color: #111827;
                }
                QHeaderView::section {
                    background-color: #f8fafc;
                    color: #475569;
                    font-weight: bold;
                    padding: 8px;
                    border: none;
                    border-bottom: 1px solid #e2e8f0;
                }
            """)

    def cargar_archivo(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de texto", "", "Archivos de texto (*.txt)"
        )
        if ruta_archivo:
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                    self.editor_codigo.setPlainText(archivo.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")

    def limpiar_todo(self):
        self.editor_codigo.clear()
        self.tabla_tokens.setRowCount(0)
        self.tabla_errores.setRowCount(0)

    def actualizar_errores_en_vivo(self):
        codigo = self.editor_codigo.toPlainText()
        _, errores = self.analizador_lexico(codigo)
        self.mostrar_errores(errores)
        # tokens NO se actualizan aquí

    def analizar_codigo(self):
        codigo = self.editor_codigo.toPlainText().strip()
        if not codigo:
            QMessageBox.warning(self, "Advertencia", "Ingrese texto o cargue un archivo .txt")
            return

        tokens, errores = self.analizador_lexico(codigo)
        self.mostrar_tokens(tokens)
        self.mostrar_errores(errores)
        self.animar_paneles()

    def animar_paneles(self):
        self.animaciones.clear()
        for card, desplazamiento in [(self.card_tokens, 35), (self.card_errores, 55)]:
            geo_final = card.geometry()
            geo_inicio = QRect(
                geo_final.x() + desplazamiento,
                geo_final.y(),
                geo_final.width(),
                geo_final.height()
            )
            anim = QPropertyAnimation(card, b"geometry")
            anim.setDuration(380)
            anim.setStartValue(geo_inicio)
            anim.setEndValue(geo_final)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animaciones.append(anim)

        self.grupo_animacion = QParallelAnimationGroup()
        for anim in self.animaciones:
            self.grupo_animacion.addAnimation(anim)
        self.grupo_animacion.start()

    def analizador_lexico(self, codigo):
        tokens = []
        errores = []

        for num_fila, linea in enumerate(codigo.split("\n"), start=1):
            i = 0
            while i < len(linea):
                if linea[i].isspace():
                    i += 1
                    continue

                inicio = i
                columna = i + 1
                ch = linea[i]

                # Cadena
                if ch == '"':
                    i += 1
                    while i < len(linea) and linea[i] != '"':
                        i += 1

                    if i < len(linea) and linea[i] == '"':
                        i += 1
                        lexema = linea[inicio:i]
                        tokens.append((lexema, "CADENA_TEXTO"))
                    else:
                        errores.append((linea[inicio:], num_fila, columna, "Cadena no cerrada con comillas dobles"))
                    continue

                # Símbolos permitidos
                if ch in SIMBOLOS_PERMITIDOS - {'"'}:
                    tokens.append((ch, "SIMBOLO"))
                    i += 1
                    continue

                # Secuencia que inicia con número
                if ch.isdigit():
                    while i < len(linea) and (linea[i].isalnum() or linea[i] == "."):
                        i += 1
                    lexema = linea[inicio:i]

                    if PATRON_NUMERO.fullmatch(lexema):
                        tokens.append((lexema, "NUMERO"))
                    else:
                        errores.append((lexema, num_fila, columna, "Un identificador no puede iniciar con un número"))
                    continue

                # Secuencia que inicia con letra
                if ch.isalpha():
                    while i < len(linea) and linea[i].isalnum():
                        i += 1
                    lexema = linea[inicio:i]

                    if lexema in PALABRAS_RESERVADAS:
                        tokens.append((lexema, "PALABRA_RESERVADA"))
                    elif PATRON_IDENTIFICADOR.fullmatch(lexema):
                        tokens.append((lexema, "IDENTIFICADOR"))
                    else:
                        errores.append((lexema, num_fila, columna, "Identificador inválido"))
                    continue

                # Cualquier otro símbolo es error
                errores.append((ch, num_fila, columna, "Símbolo especial no definido en el lenguaje"))
                i += 1

        # Validaciones contextuales estrictas del lenguaje del documento
        errores.extend(self.validar_estructura(codigo))
        return tokens, errores

    def validar_estructura(self, codigo):
        errores = []
        lineas = [l.strip() for l in codigo.split("\n") if l.strip()]

        patrones = [
            r'^Cliente\s*:\s*[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Pedido\s*:\s*[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Dirección\s*:\s*"[^"]*"\s*;$',
            r'^Precio\s*:\s*\d+(\.\d+)?\s*;$',
            r'^Stock\s+\d+(\.\d+)?\s*;$',
            r'^Asignar\s+Repartidor\s+[A-Za-z][A-Za-z0-9]*\s*:\s*[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Listo\s+[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Entregado\s+[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Recibido\s+[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Rechazado\s+[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Aprobado\s+[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Procesando\s+[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^En\s+Ruta\s+[A-Za-z][A-Za-z0-9]*\s*;$',
            r'^Agotado\s+[A-Za-z][A-Za-z0-9]*\s*;$',
        ]

        for fila, linea in enumerate(lineas, start=1):
            valida = any(re.fullmatch(p, linea) for p in patrones)
            if not valida:
                # Casos que tu documento ejemplifica
                if linea.startswith("Dirección:") and '"' not in linea:
                    errores.append(("Dirección", fila, 1, 'Se esperaba una cadena entre comillas dobles'))
                elif re.search(r'\bCobrar\b', linea):
                    errores.append(("Cobrar", fila, 1, 'Palabra no reconocida en el alfabeto del lenguaje'))
                elif not linea.endswith(";"):
                    errores.append((linea, fila, 1, 'Fin de instrucción obligatorio: falta ";"'))
                else:
                    errores.append((linea, fila, 1, 'La instrucción no cumple la estructura definida del lenguaje'))
        return errores

    def mostrar_tokens(self, tokens):
        self.tabla_tokens.setRowCount(0)
        for lexema, token in tokens:
            fila = self.tabla_tokens.rowCount()
            self.tabla_tokens.insertRow(fila)
            self.tabla_tokens.setItem(fila, 0, QTableWidgetItem(lexema))
            self.tabla_tokens.setItem(fila, 1, QTableWidgetItem(token))

    def mostrar_errores(self, errores):
        self.tabla_errores.setRowCount(0)
        for lexema, fila_num, col, descripcion in errores:
            fila = self.tabla_errores.rowCount()
            self.tabla_errores.insertRow(fila)
            self.tabla_errores.setItem(fila, 0, QTableWidgetItem(str(lexema)))
            self.tabla_errores.setItem(fila, 1, QTableWidgetItem(str(fila_num)))
            self.tabla_errores.setItem(fila, 2, QTableWidgetItem(str(col)))
            self.tabla_errores.setItem(fila, 3, QTableWidgetItem(descripcion))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = AnalizadorLexicoApp()
    ventana.show()
    sys.exit(app.exec())