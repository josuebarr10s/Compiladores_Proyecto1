import sys
import os
from pygments.lexer import RegexLexer, words
from pygments import token as PT

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QSplitter, QTabWidget, QFrame,
    QPlainTextEdit, QTextEdit, QScrollArea, QToolButton,
)
from PyQt6.QtGui import (
    QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QTextCursor,
    QPainter, QTextFormat, QFontMetricsF, QLinearGradient, QBrush, QPixmap, QIcon, QPen,
)
from PyQt6.QtCore import Qt, QRect, QSize, QPointF, QTimer

C = {
    "bg_deep":    "#0d1520",
    "bg_mid":     "#111d2e",
    "bg_light":   "#172438",
    "bg_row_alt": "#0f1a28",
    "teal":       "#99cbff",
    "teal_dim":   "#0ce3e8",
    "teal_glow":  "#0ce3e8",
    "purple":     "#c9a0ff",
    "pink":       "#ff8fab",
    "amber":      "#ffd166",
    "green":      "#38bdf8",
    "blue":       "#99cbff",
    "cyan":       "#67e8f9",
    "red":        "#ff6b6b",
    "comment":    "#4d6e8a",
    "text":       "#ddeeff",
    "text_dim":   "#5a7a9a",
    "border":     "#1e3350",
    "line_cur":   "#162030",
}

DARK_THEME = C.copy()

LIGHT_THEME = {
    "bg_deep":    "#f5f8fc",
    "bg_mid":     "#e8eef7",
    "bg_light":   "#ffffff",
    "bg_row_alt": "#eef4fb",
    "teal":       "#2563eb",
    "teal_dim":   "#3b82f6",
    "teal_glow":  "#60a5fa",
    "purple":     "#7c3aed",
    "pink":       "#db2777",
    "amber":      "#b45309",
    "green":      "#0284c7",
    "blue":       "#1d4ed8",
    "cyan":       "#0891b2",
    "red":        "#dc2626",
    "comment":    "#64748b",
    "text":       "#102033",
    "text_dim":   "#64748b",
    "border":     "#cbd5e1",
    "line_cur":   "#eaf2ff",
}

PALABRAS_RESERVADAS = (
    "Cliente", "Pedido", "Producto", "Repartidor", "Proveedor",
    "Empleado", "Empresa", "Sucursal",
    "Crear", "Asignar", "Cancelar", "Confirmar", "Devolver",
    "Entregar", "Actualizar", "Registrar", "Eliminar", "Buscar",
    "Pendiente", "Aprobado", "Rechazado", "Procesando", "Listo",
    "EnRuta", "Entregado", "Recibido", "Cancelado", "Agotado",
    "Disponible", "Inactivo",
    "Stock", "Cantidad", "Minimo", "Maximo", "Reservado", "Reponer",
    "Precio", "Descuento", "Impuesto", "Total", "Pagar", "Cobrar",
    "Factura", "Subtotal", "Saldo", "Credito",
    "Direccion", "Telefono", "Zona", "Fecha", "Referencia", "Nota",
    "Categoria", "Descripcion",
    "Entero", "Real", "Cadena", "Booleano",
    "Si", "Sino", "Mientras", "Para", "Inicio", "Fin", "Retornar",
    "Verdadero", "Falso",
)

class LenguajePedidosLexer(RegexLexer):
    name = "LenguajePedidos"
    aliases = ["pedidos"]
    filenames = ["*.txt"]
    tokens = {
        "root": [
            (r"//.*$",                        PT.Comment.Single),
            (r'"[^"]*"',                      PT.String.Double),
            (r"\b\d+\.\d+\b",                PT.Number.Float),
            (r"\b\d+\b",                      PT.Number.Integer),
            (words(PALABRAS_RESERVADAS,
                   suffix=r"\b"),             PT.Keyword),
            (r"\b[a-zA-Z][a-zA-Z0-9]*\b",   PT.Name),
            (r"[:;()$%]",                     PT.Punctuation),
            (r"[ \t]+",                       PT.Text.Whitespace),
            (r"\n",                           PT.Text),
            (r".",                            PT.Error),
        ]
    }

HIGHLIGHT_MAP = {
    PT.Comment.Single:  (C["comment"],  False, False),
    PT.String.Double:   (C["pink"],     False, False),
    PT.Number.Float:    (C["green"],    False, False),
    PT.Number.Integer:  (C["green"],    False, False),
    PT.Keyword:         (C["purple"],   True,  False),
    PT.Name:            (C["blue"],     False, False),
    PT.Operator:        (C["amber"],    False, False),
    PT.Punctuation:     (C["cyan"],     False, False),
    PT.Error:           (C["red"],      False, True),
    PT.Text:            (C["text"],     False, False),
    PT.Text.Whitespace: (C["text"],     False, False),
}

class PygmentsHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self._lexer = LenguajePedidosLexer()
        self._fmts = {}
        for ttype, (color, bold, italic) in HIGHLIGHT_MAP.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(QFont.Weight.Bold)
            if italic:
                fmt.setFontItalic(True)
            self._fmts[ttype] = fmt
        self._default_fmt = QTextCharFormat()
        self._default_fmt.setForeground(QColor(C["text"]))

    def _get_fmt(self, ttype):
        while ttype:
            if ttype in self._fmts:
                return self._fmts[ttype]
            ttype = ttype.parent
        return self._default_fmt

    def highlightBlock(self, text):
        index = 0
        for ttype, value in self._lexer.get_tokens(text):
            length = len(value)
            if index + length > len(text):
                length = len(text) - index
            if length > 0:
                self.setFormat(index, length, self._get_fmt(ttype))
            index += len(value)
            if index >= len(text):
                break

PALABRAS_CLAVE_BASICA = {
    "Empresa", "Sucursal", "Cliente", "Proveedor", "Empleado",
    "Producto", "Telefono", "Direccion", "Referencia", "Cantidad",
    "Precio", "Subtotal", "Descuento", "Impuesto", "Total", "Stock",
    "Minimo", "Maximo", "Categoria", "Nota", "Fecha", "Descripcion",
}

VERBOS_ESTADO = {
    "Confirmar", "Procesando", "EnRuta", "Entregado", "Cobrar",
    "Factura", "Listo", "Recibido", "Disponible", "Cancelado",
    "Pendiente", "Aprobado", "Rechazado", "Agotado", "Inactivo",
}


class NodoArbol:
    def __init__(self, tipo, valor=None):
        self.tipo   = tipo
        self.valor  = valor
        self.hijos  = []

    def agregar(self, hijo):
        self.hijos.append(hijo)
        return self

    def hoja(tipo, valor):
        return NodoArbol(tipo, valor)

    def render(self, prefijo="", es_ultimo=True):
        conector = "└── " if es_ultimo else "├── "
        etiqueta = f"{self.tipo}"
        if self.valor:
            etiqueta += f"  [{self.valor}]"
        lineas = [prefijo + conector + etiqueta]
        extension = "    " if es_ultimo else "│   "
        for i, hijo in enumerate(self.hijos):
            es_ult = (i == len(self.hijos) - 1)
            lineas += hijo.render(prefijo + extension, es_ult)
        return lineas


class ErrorSintactico(Exception):
    def __init__(self, mensaje, fila, col):
        super().__init__(mensaje)
        self.fila = fila
        self.col  = col


class ErrorSemantico(Exception):
    def __init__(self, codigo, titulo, mensaje, fila, col):
        super().__init__(mensaje)
        self.codigo = codigo
        self.titulo = titulo
        self.mensaje = mensaje
        self.fila = fila
        self.col = col

    def como_tupla(self):
        return (self.codigo, self.titulo, self.mensaje, self.fila, self.col)


class Simbolo:
    def __init__(self, identificador, clase, tipo, valor, estado, linea):
        self.identificador = identificador
        self.clase = clase
        self.tipo = tipo
        self.valor = valor
        self.estado = estado
        self.linea = linea

    def como_fila(self):
        return {
            "identificador": self.identificador,
            "clase": self.clase,
            "tipo": self.tipo,
            "valor": self.valor,
            "estado": self.estado,
            "linea": self.linea,
        }


class AnalizadorSemantico:
    CAMPOS_NUMERICOS = {
        "Cantidad", "Precio", "Subtotal", "Descuento", "Impuesto", "Total",
        "Stock", "Minimo", "Maximo", "Reservado", "Saldo", "Credito",
    }

    CAMPOS_TEXTO = {
        "Empresa", "Sucursal", "Cliente", "Proveedor", "Empleado",
        "Repartidor", "Producto", "Telefono", "Direccion", "Referencia",
        "Categoria", "Nota", "Fecha", "Descripcion",
    }

    ENTIDADES_REGISTRABLES = {"Empleado", "Repartidor", "Cliente", "Proveedor"}

    ESTADO_NORMALIZADO = {
        "Confirmar": "Confirmado",
        "Procesando": "Procesando",
        "EnRuta": "EnRuta",
        "Entregado": "Entregado",
        "Cobrar": "Cobrado",
        "Factura": "Facturado",
        "Listo": "Listo",
        "Recibido": "Recibido",
        "Cancelado": "Cancelado",
        "Pendiente": "Pendiente",
        "Aprobado": "Aprobado",
        "Rechazado": "Rechazado",
    }

    TRANSICIONES_PEDIDO = {
        "Creado": {"Confirmado", "Procesando", "Cancelado", "Pendiente", "Aprobado", "Rechazado"},
        "Pendiente": {"Confirmado", "Aprobado", "Rechazado", "Cancelado"},
        "Aprobado": {"Confirmado", "Procesando", "Cancelado"},
        "Confirmado": {"Procesando", "Listo", "EnRuta", "Cobrado", "Facturado", "Cancelado"},
        "Procesando": {"Listo", "EnRuta", "Entregado", "Cobrado", "Facturado", "Cancelado"},
        "Listo": {"EnRuta", "Entregado", "Cobrado", "Facturado", "Recibido", "Cancelado"},
        "EnRuta": {"Entregado", "Recibido", "Cancelado"},
        "Entregado": {"Recibido", "Cobrado", "Facturado"},
        "Cobrado": {"Facturado", "Listo", "EnRuta", "Entregado", "Recibido"},
        "Facturado": {"Listo", "EnRuta", "Entregado", "Recibido"},
        "Recibido": set(),
        "Cancelado": set(),
        "Rechazado": set(),
    }

    ESTADOS_NO_PEDIDO = {"Disponible", "Inactivo", "Agotado"}

    def __init__(self, tokens):
        self._tokens = [t for t in tokens if t[1] != "ERROR_LEXICO"]
        self._pos = 0
        self.tabla_simbolos = {}
        self.errores = []

    def analizar(self):
        try:
            while not self._es_fin():
                self._sentencia()
        except ErrorSemantico as e:
            self.errores.append(e.como_tupla())
        return list(self.tabla_simbolos.values()), self.errores

    def _actual(self):
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return ("EOF", "EOF", 0, 0)

    def _lexema(self): return self._actual()[0]
    def _tipo(self): return self._actual()[1]
    def _fila(self): return self._actual()[2]
    def _col(self): return self._actual()[3]
    def _es_fin(self): return self._pos >= len(self._tokens)

    def _avanzar(self):
        tok = self._actual()
        self._pos += 1
        return tok

    def _saltar_hasta_fin_sentencia(self):
        while not self._es_fin() and self._lexema() != ";":
            self._avanzar()
        if not self._es_fin():
            self._avanzar()

    def _sentencia(self):
        lex = self._lexema()
        if lex == "Crear":
            return self._crear_pedido()
        if lex == "Asignar":
            return self._asignar()
        if lex == "Si":
            return self._condicion()
        if lex in VERBOS_ESTADO:
            return self._cambio_estado()
        if lex in PALABRAS_CLAVE_BASICA:
            return self._declaracion_o_dato()
        self._saltar_hasta_fin_sentencia()

    def _declaracion_o_dato(self):
        campo = self._avanzar()
        if self._lexema() != ":":
            self._saltar_hasta_fin_sentencia()
            return
        self._avanzar()
        valor = self._actual()

        if campo[0] in self.CAMPOS_NUMERICOS:
            if valor[1] not in ("NUMERO", "NUMERO_REAL"):
                self._error("SEM-03", "Tipo de dato incorrecto",
                            f"El campo {campo[0]} necesita un valor numerico.",
                            valor)
            tipo = valor[1]
            self._registrar_o_actualizar(campo[0], "Dato", tipo, valor[0], "Valido", campo[2])

        elif campo[0] in self.CAMPOS_TEXTO:
            if valor[1] not in ("IDENTIFICADOR", "CADENA_TEXTO"):
                self._error("SEM-03", "Tipo de dato incorrecto",
                            f"El campo {campo[0]} necesita texto o identificador.",
                            valor)
            if campo[0] in self.ENTIDADES_REGISTRABLES and valor[1] == "IDENTIFICADOR":
                self._registrar_o_actualizar(valor[0], campo[0], "IDENTIFICADOR", valor[0], "Registrado", campo[2])

        self._saltar_hasta_fin_sentencia()

    def _crear_pedido(self):
        crear = self._avanzar()
        if self._lexema() != "Pedido":
            self._saltar_hasta_fin_sentencia()
            return
        self._avanzar()
        if self._lexema() == ":":
            self._avanzar()
        pedido = self._actual()
        if pedido[0] in self.tabla_simbolos and self.tabla_simbolos[pedido[0]].clase == "Pedido":
            self._error("SEM-02", "Pedido repetido",
                        f"El pedido {pedido[0]} ya fue creado en la linea {self.tabla_simbolos[pedido[0]].linea}.",
                        pedido)
        self._registrar_o_actualizar(pedido[0], "Pedido", "IDENTIFICADOR", pedido[0], "Creado", crear[2])
        self._saltar_hasta_fin_sentencia()

    def _asignar(self):
        self._avanzar()
        entidad = self._actual()
        self._avanzar()
        pedido = self._actual()
        if not self._existe_clase(pedido[0], "Pedido"):
            self._error("SEM-01", "Pedido no creado",
                        f"No se puede asignar {entidad[0]} al pedido {pedido[0]} porque no ha sido creado.",
                        pedido)
        self._avanzar()
        if self._lexema() == ":":
            self._avanzar()
        asignado = self._actual()
        if not self._existe_clase(asignado[0], entidad[0]):
            self._error("SEM-04", f"{entidad[0]} no registrado",
                        f"{entidad[0]} no registrado: {asignado[0]}",
                        asignado)
        self._saltar_hasta_fin_sentencia()

    def _cambio_estado(self):
        verbo = self._avanzar()
        ident = self._actual()

        if verbo[0] in self.ESTADOS_NO_PEDIDO:
            if ident[0] not in self.tabla_simbolos:
                self._error("SEM-05", "Identificador invalido",
                            f"El identificador {ident[0]} no existe para cambiarlo a {verbo[0]}.",
                            ident)
            self.tabla_simbolos[ident[0]].estado = verbo[0]
            self._saltar_hasta_fin_sentencia()
            return

        if not self._existe_clase(ident[0], "Pedido"):
            self._error("SEM-01", "Pedido no creado",
                        f"No se puede aplicar {verbo[0]} al pedido {ident[0]} porque no ha sido creado.",
                        ident)

        pedido = self.tabla_simbolos[ident[0]]
        nuevo_estado = self.ESTADO_NORMALIZADO.get(verbo[0], verbo[0])
        permitidos = self.TRANSICIONES_PEDIDO.get(pedido.estado, set())
        if nuevo_estado not in permitidos:
            self._error("SEM-06", "Secuencia de estado incorrecta",
                        f"El pedido {ident[0]} no puede pasar de {pedido.estado} a {nuevo_estado}.",
                        verbo)
        pedido.estado = nuevo_estado
        self._saltar_hasta_fin_sentencia()

    def _condicion(self):
        self._avanzar()
        ident = self._actual()
        if ident[0] not in self.tabla_simbolos:
            self._error("SEM-05", "Identificador invalido",
                        f"El identificador {ident[0]} no existe para usarse en una condicion.",
                        ident)
        self._saltar_hasta_fin_sentencia()

    def _registrar_o_actualizar(self, identificador, clase, tipo, valor, estado, linea):
        if identificador in self.tabla_simbolos and self.tabla_simbolos[identificador].clase == clase:
            simbolo = self.tabla_simbolos[identificador]
            simbolo.tipo = tipo
            simbolo.valor = valor
            simbolo.estado = estado
        else:
            self.tabla_simbolos[identificador] = Simbolo(identificador, clase, tipo, valor, estado, linea)

    def _existe_clase(self, identificador, clase):
        return identificador in self.tabla_simbolos and self.tabla_simbolos[identificador].clase == clase

    def _error(self, codigo, titulo, mensaje, tok):
        raise ErrorSemantico(codigo, titulo, mensaje, tok[2], tok[3])


def analizar_backend(codigo):
    app_proxy = AnalizadorApp.__new__(AnalizadorApp)
    tokens, lex_errors = AnalizadorApp._run_lexer(app_proxy, codigo)
    arbol = None
    syn_errors = []
    tabla_simbolos = []
    sem_errors = []

    if not lex_errors:
        parser = AnalizadorSintactico(tokens)
        arbol, syn_errors = parser.parsear()
        if not syn_errors:
            sem = AnalizadorSemantico(tokens)
            tabla_simbolos, sem_errors = sem.analizar()

    return {
        "tokens": tokens,
        "errores_lexicos": lex_errors,
        "arbol": arbol,
        "errores_sintacticos": syn_errors,
        "tabla_simbolos": [s.como_fila() for s in tabla_simbolos],
        "errores_semanticos": sem_errors,
    }


class AnalizadorSintactico:
    def __init__(self, tokens):
        self._tokens  = [t for t in tokens if t[1] not in ("ERROR_LEXICO",)]
        self._pos     = 0
        self._errores = []

    def _actual(self):
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return ("EOF", "EOF", 0, 0)

    def _lexema(self):   return self._actual()[0]
    def _tipo(self):     return self._actual()[1]
    def _fila(self):     return self._actual()[2]
    def _col(self):      return self._actual()[3]

    def _avanzar(self):
        tok = self._actual()
        self._pos += 1
        return tok

    def _consumir(self, esperado_lexema=None, esperado_tipo=None):
        tok = self._actual()
        if esperado_lexema and tok[0] != esperado_lexema:
            raise ErrorSintactico(
                f"Se esperaba '{esperado_lexema}' pero se encontró '{tok[0]}'",
                tok[2], tok[3]
            )
        if esperado_tipo and tok[1] != esperado_tipo:
            raise ErrorSintactico(
                f"Se esperaba {esperado_tipo} pero se encontró '{tok[0]}' ({tok[1]})",
                tok[2], tok[3]
            )
        return self._avanzar()

    def _es_fin(self):
        return self._pos >= len(self._tokens)

    def parsear(self):
        raiz = NodoArbol("PROGRAMA")
        lista = self._lista_sentencias()
        raiz.agregar(lista)
        return raiz, self._errores

    def _lista_sentencias(self, terminadores=None):
        terminadores = terminadores or {"EOF"}
        nodo = NodoArbol("LISTA_SENTENCIAS")
        while not self._es_fin() and self._lexema() not in terminadores:
            try:
                sent = self._sentencia()
                if sent:
                    nodo.agregar(sent)
            except ErrorSintactico as e:
                self._errores.append((str(e), e.fila, e.col))
                while not self._es_fin() and self._lexema() != ";":
                    self._avanzar()
                if not self._es_fin() and self._lexema() == ";":
                    self._avanzar()
        return nodo

    def _sentencia(self):
        lex = self._lexema()

        if lex in PALABRAS_CLAVE_BASICA:
            return self._declaracion_basica()

        if lex == "Crear":
            return self._accion_compuesta_crear()

        if lex == "Asignar":
            return self._accion_compuesta_asignar()

        if lex == "Reponer":
            return self._accion_compuesta_reponer()

        if lex == "Si":
            return self._estructura_condicional()

        if lex in VERBOS_ESTADO:
            return self._accion_estado()

        raise ErrorSintactico(
            f"Instrucción no reconocida: '{lex}'",
            self._fila(), self._col()
        )

    def _declaracion_basica(self):
        nodo = NodoArbol("DECLARACION_BASICA")
        tok = self._avanzar()
        nodo.agregar(NodoArbol("PALABRA_CLAVE", tok[0]))
        self._consumir(":")
        nodo.agregar(NodoArbol("SIMBOLO", ":"))
        val = self._valor()
        nodo.agregar(val)
        self._consumir(";")
        nodo.agregar(NodoArbol("SIMBOLO", ";"))
        return nodo

    def _valor(self):
        tok = self._actual()
        if tok[1] in ("IDENTIFICADOR", "CADENA_TEXTO", "NUMERO", "NUMERO_REAL"):
            self._avanzar()
            return NodoArbol(tok[1], tok[0])
        raise ErrorSintactico(
            f"Se esperaba un valor (IDENTIFICADOR, CADENA, NUMERO) pero se encontró '{tok[0]}'",
            tok[2], tok[3]
        )

    def _accion_compuesta_crear(self):
        nodo = NodoArbol("ACCION_COMPUESTA")
        self._consumir("Crear")
        nodo.agregar(NodoArbol("PALABRA_RESERVADA", "Crear"))
        entidad = self._actual()
        if entidad[0] != "Pedido":
            raise ErrorSintactico(
                f"Se esperaba 'Pedido' después de 'Crear' pero se encontró '{entidad[0]}'",
                entidad[2], entidad[3]
            )
        self._avanzar()
        nodo.agregar(NodoArbol("PALABRA_RESERVADA", "Pedido"))
        self._consumir(":")
        nodo.agregar(NodoArbol("SIMBOLO", ":"))
        tok = self._consumir(esperado_tipo="IDENTIFICADOR")
        nodo.agregar(NodoArbol("IDENTIFICADOR", tok[0]))
        self._consumir(";")
        nodo.agregar(NodoArbol("SIMBOLO", ";"))
        return nodo

    def _accion_compuesta_asignar(self):
        nodo = NodoArbol("ACCION_COMPUESTA")
        self._consumir("Asignar")
        nodo.agregar(NodoArbol("PALABRA_RESERVADA", "Asignar"))
        entidad = self._actual()
        if entidad[0] not in ("Repartidor", "Empleado"):
            raise ErrorSintactico(
                f"Se esperaba 'Repartidor' o 'Empleado' después de 'Asignar' pero se encontró '{entidad[0]}'",
                entidad[2], entidad[3]
            )
        self._avanzar()
        nodo.agregar(NodoArbol("PALABRA_RESERVADA", entidad[0]))
        tok_obj = self._consumir(esperado_tipo="IDENTIFICADOR")
        nodo.agregar(NodoArbol("IDENTIFICADOR", tok_obj[0]))
        self._consumir(":")
        nodo.agregar(NodoArbol("SIMBOLO", ":"))
        tok_asig = self._consumir(esperado_tipo="IDENTIFICADOR")
        nodo.agregar(NodoArbol("IDENTIFICADOR", tok_asig[0]))
        self._consumir(";")
        nodo.agregar(NodoArbol("SIMBOLO", ";"))
        return nodo

    def _accion_compuesta_reponer(self):
        nodo = NodoArbol("ACCION_COMPUESTA")
        self._consumir("Reponer")
        nodo.agregar(NodoArbol("PALABRA_RESERVADA", "Reponer"))
        prod = self._actual()
        if prod[0] != "Producto":
            raise ErrorSintactico(
                f"Se esperaba 'Producto' después de 'Reponer' pero se encontró '{prod[0]}'",
                prod[2], prod[3]
            )
        self._avanzar()
        nodo.agregar(NodoArbol("PALABRA_RESERVADA", "Producto"))
        self._consumir(":")
        nodo.agregar(NodoArbol("SIMBOLO", ":"))
        tok = self._consumir(esperado_tipo="CADENA_TEXTO")
        nodo.agregar(NodoArbol("CADENA_TEXTO", tok[0]))
        self._consumir(";")
        nodo.agregar(NodoArbol("SIMBOLO", ";"))
        return nodo

    def _accion_estado(self):
        nodo = NodoArbol("ACCION_ESTADO")
        verbo = self._avanzar()
        nodo.agregar(NodoArbol("PALABRA_RESERVADA", verbo[0]))
        tok = self._consumir(esperado_tipo="IDENTIFICADOR")
        nodo.agregar(NodoArbol("IDENTIFICADOR", tok[0]))
        self._consumir(";")
        nodo.agregar(NodoArbol("SIMBOLO", ";"))
        return nodo

    def _estructura_condicional(self):
        nodo = NodoArbol("ESTRUCTURA_CONDICIONAL")
        self._consumir("Si")
        nodo.agregar(NodoArbol("PALABRA_RESERVADA", "Si"))
        cond = self._condicion()
        nodo.agregar(cond)
        self._consumir(";")
        nodo.agregar(NodoArbol("SIMBOLO", ";"))
        cuerpo = self._lista_sentencias(terminadores={"Sino", "Fin", "EOF"})
        nodo.agregar(cuerpo)
        if self._lexema() == "Sino":
            self._avanzar()
            nodo.agregar(NodoArbol("PALABRA_RESERVADA", "Sino"))
            alt = self._lista_sentencias(terminadores={"Fin", "EOF"})
            nodo.agregar(alt)
        if self._lexema() == "Fin":
            self._avanzar()
            nodo.agregar(NodoArbol("PALABRA_RESERVADA", "Fin"))
        else:
            raise ErrorSintactico(
                "Se esperaba 'Fin' para cerrar la estructura 'Si'",
                self._fila(), self._col()
            )
        return nodo

    def _condicion(self):
        nodo = NodoArbol("CONDICION")
        tok_id = self._consumir(esperado_tipo="IDENTIFICADOR")
        nodo.agregar(NodoArbol("IDENTIFICADOR", tok_id[0]))
        self._consumir(":")
        nodo.agregar(NodoArbol("SIMBOLO", ":"))
        tok_n = self._actual()
        if tok_n[1] not in ("NUMERO", "NUMERO_REAL"):
            raise ErrorSintactico(
                f"Se esperaba NUMERO en la condición pero se encontró '{tok_n[0]}'",
                tok_n[2], tok_n[3]
            )
        self._avanzar()
        nodo.agregar(NodoArbol("NUMERO", tok_n[0]))
        return nodo
class ArbolCanvas(QWidget):
    NW   = 148
    NH   = 40
    HGAP = 12
    VGAP = 68
    PADX = 50
    PADY = 50

    ESTILOS = {
        "PROGRAMA":               ("#071628", "#99cbff", "#99cbff", False),
        "LISTA_SENTENCIAS":       ("#071820", "#67e8f9", "#67e8f9", False),
        "DECLARACION_BASICA":     ("#140a30", "#c9a0ff", "#c9a0ff", False),
        "ACCION_COMPUESTA":       ("#0e1f06", "#86efac", "#86efac", False),
        "ACCION_ESTADO":          ("#1e1400", "#ffd166", "#ffd166", False),
        "ESTRUCTURA_CONDICIONAL": ("#081a0c", "#4ade80", "#4ade80", False),
        "CONDICION":              ("#1a1400", "#fbbf24", "#fbbf24", False),
        "PALABRA_CLAVE":          ("#1a0830", "#c9a0ff", "#c9a0ff", True),
        "PALABRA_RESERVADA":      ("#1a0830", "#c9a0ff", "#c9a0ff", True),
        "IDENTIFICADOR":          ("#071830", "#99cbff", "#99cbff", True),
        "CADENA_TEXTO":           ("#280a14", "#ff8fab", "#ff8fab", True),
        "NUMERO":                 ("#071c14", "#38bdf8", "#38bdf8", True),
        "NUMERO_REAL":            ("#071c14", "#38bdf8", "#38bdf8", True),
        "SIMBOLO":                ("#071418", "#67e8f9", "#4d7a88", True),
    }

    SHORT = {
        "LISTA_SENTENCIAS":       "LISTA SENT.",
        "DECLARACION_BASICA":     "DECL. BASICA",
        "ACCION_COMPUESTA":       "ACCION COMP.",
        "ACCION_ESTADO":          "ACC. ESTADO",
        "ESTRUCTURA_CONDICIONAL": "COND.",
    }

    LEAF_TYPES = {
        "PALABRA_CLAVE", "PALABRA_RESERVADA", "IDENTIFICADOR",
        "CADENA_TEXTO", "NUMERO", "NUMERO_REAL", "SIMBOLO",
    }

    def __init__(self):
        super().__init__()
        self._raiz = None
        self._ndata = []
        self._edges = []
        self._zoom = 1.0
        self._zoom_min = 0.2
        self._zoom_max = 3.0
        self.setMinimumSize(300, 200)
        self.setStyleSheet(f"background-color: {C['bg_deep']};")

    def set_tree(self, raiz):
        self._raiz = raiz
        self._layout(raiz)
        self.update()

    def clear_tree(self):
        self._raiz = None
        self._ndata = []
        self._edges = []
        self._zoom = 1.0
        self.setMinimumSize(300, 200)
        self.update()

    def set_zoom(self, zoom):
        zoom = max(self._zoom_min, min(self._zoom_max, zoom))
        if abs(zoom - self._zoom) < 0.001:
            return False
        self._zoom = zoom
        if self._raiz is not None:
            self._layout(self._raiz)
        else:
            self.update()
        return True

    def zoom_in(self):
        return self.set_zoom(self._zoom * 1.15)

    def zoom_out(self):
        return self.set_zoom(self._zoom / 1.15)

    def reset_zoom(self):
        return self.set_zoom(1.0)

    def zoom_percent(self):
        return int(round(self._zoom * 100))

    def _assign_leaf_x(self, node, ctr):
        if not node.hijos:
            node._lx = ctr[0]; ctr[0] += 1
        else:
            for h in node.hijos: self._assign_leaf_x(h, ctr)
            node._lx = (node.hijos[0]._lx + node.hijos[-1]._lx) / 2

    def _assign_depth(self, node, d=0):
        node._depth = d
        for h in node.hijos: self._assign_depth(h, d + 1)

    def _layout(self, raiz):
        ctr = [0]
        self._assign_leaf_x(raiz, ctr)
        self._assign_depth(raiz)
        node_w = self.NW * self._zoom
        node_h = self.NH * self._zoom
        padx = self.PADX * self._zoom
        pady = self.PADY * self._zoom
        sx = node_w + (self.HGAP * self._zoom)
        sy = node_h + (self.VGAP * self._zoom)
        self._ndata = []
        self._edges = []

        def collect(node):
            cx = int(padx + node._lx * sx + node_w / 2)
            cy = int(pady + node._depth * sy + node_h / 2)
            node._cx = cx
            node._cy = cy
            if node.tipo in self.LEAF_TYPES:
                text = node.valor or node.tipo
            else:
                text = self.SHORT.get(node.tipo, node.tipo)
            self._ndata.append((cx, cy, text, node.tipo))
            for h in node.hijos:
                collect(h)
                self._edges.append((cx, cy + int(node_h / 2),
                                     h._cx, h._cy - int(node_h / 2)))

        collect(raiz)
        if self._ndata:
            max_x = max(cx for cx, *_ in self._ndata) + int(node_w / 2) + int(padx)
            max_y = max(cy for _, cy, *_ in self._ndata) + int(node_h / 2) + int(pady)
            self.setMinimumSize(int(max_x), int(max_y))

    def paintEvent(self, event):
        if not self._ndata:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        node_w = int(self.NW * self._zoom)
        node_h = int(self.NH * self._zoom)

        p.setPen(QPen(QColor("#253d55"), 1.5, Qt.PenStyle.SolidLine))
        for x1, y1, x2, y2 in self._edges:
            p.drawLine(x1, y1, x2, y2)

        for cx, cy, text, tipo in self._ndata:
            bg, bd, tx, is_leaf = self.ESTILOS.get(
                tipo, ("#111d2e", "#99cbff", "#99cbff", False))
            x = cx - node_w // 2
            y = cy - node_h // 2
            p.setBrush(QBrush(QColor(bg)))
            p.setPen(QPen(QColor(bd), 1.5))
            p.drawEllipse(x, y, node_w, node_h)
            p.setPen(QColor(tx))
            f = QFont("Consolas", max(8, int(8 * self._zoom)))
            f.setBold(not is_leaf)
            p.setFont(f)
            p.drawText(x + 4, y, node_w - 8, node_h,
                       Qt.AlignmentFlag.AlignCenter, text)
        p.end()


class ArbolScrollArea(QScrollArea):
    def __init__(self, canvas, zoom_changed_callback=None):
        super().__init__()
        self._canvas = canvas
        self._zoom_changed_callback = zoom_changed_callback
        self.setWidget(canvas)
        self.setWidgetResizable(False)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            changed = self._canvas.zoom_in() if event.angleDelta().y() > 0 else self._canvas.zoom_out()
            if changed and self._zoom_changed_callback:
                self._zoom_changed_callback()
            event.accept()
            return
        super().wheelEvent(event)


class _LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self._editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self._lineNumberArea = _LineNumberArea(self)
        self.blockCountChanged.connect(self._updateLineNumberAreaWidth)
        self.updateRequest.connect(self._updateLineNumberArea)
        self.cursorPositionChanged.connect(self._highlightCurrentLine)
        self._font_family = "Cascadia Code"
        self._font_size = 11
        self._font_min = 8
        self._font_max = 28
        font = QFont(self._font_family, self._font_size)
        if not font.exactMatch():
            self._font_family = "Consolas"
        self._diagnostics = []
        self._apply_editor_font()
        self._updateLineNumberAreaWidth(0)
        self._highlightCurrentLine()

    def _apply_editor_font(self):
        font = QFont(self._font_family, self._font_size)
        self.setFont(font)
        self.document().setDefaultFont(font)
        self.setTabStopDistance(QFontMetricsF(font).horizontalAdvance(" ") * 4)
        self._updateLineNumberAreaWidth(0)
        self.updateGeometry()
        self.document().markContentsDirty(0, self.document().characterCount())
        self.viewport().update()
        self._lineNumberArea.update()

    def set_zoom(self, size):
        size = max(self._font_min, min(self._font_max, size))
        if size == self._font_size:
            return False
        self._font_size = size
        self._apply_editor_font()
        return True

    def zoom_in_editor(self):
        return self.set_zoom(self._font_size + 1)

    def zoom_out_editor(self):
        return self.set_zoom(self._font_size - 1)

    def reset_zoom_editor(self):
        return self.set_zoom(11)

    def zoom_percent(self):
        return int(round((self._font_size / 11) * 100))

    def lineNumberAreaWidth(self):
        digits = max(1, len(str(self.blockCount())))
        return 24 + self.fontMetrics().horizontalAdvance("9") * digits

    def _updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def _updateLineNumberArea(self, rect, dy):
        if dy:
            self._lineNumberArea.scroll(0, dy)
        else:
            self._lineNumberArea.update(
                0, rect.y(), self._lineNumberArea.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            changed = self.zoom_in_editor() if event.angleDelta().y() > 0 else self.zoom_out_editor()
            parent = self.window()
            if changed and hasattr(parent, "_update_editor_zoom_label"):
                parent._update_editor_zoom_label()
            event.accept()
            return
        super().wheelEvent(event)

    def set_diagnostics(self, diagnostics):
        self._diagnostics = diagnostics
        self._highlightCurrentLine()

    def clear_diagnostics(self):
        self.set_diagnostics([])

    def _highlightCurrentLine(self):
        selections = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor(C["line_cur"]))
            sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            selections.append(sel)

        for diag in self._diagnostics:
            block = self.document().findBlockByNumber(max(0, diag["fila"] - 1))
            if not block.isValid():
                continue
            cursor = QTextCursor(block)
            start = block.position() + max(0, diag["col"] - 1)
            end = min(start + max(1, diag.get("longitud", 1)), block.position() + block.length() - 1)
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

            sel = QTextEdit.ExtraSelection()
            sel.cursor = cursor
            sel.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
            sel.format.setUnderlineColor(QColor(diag.get("color", C["red"])))
            sel.format.setToolTip(diag.get("mensaje", ""))
            selections.append(sel)

        self.setExtraSelections(selections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self._lineNumberArea)
        painter.fillRect(event.rect(), QColor(C["bg_deep"]))
        painter.setPen(QColor("#0ce3e8"))
        painter.drawLine(
            self._lineNumberArea.width() - 1, event.rect().top(),
            self._lineNumberArea.width() - 1, event.rect().bottom()
        )
        block    = self.firstVisibleBlock()
        blockNum = block.blockNumber()
        offset   = self.contentOffset()
        top      = int(self.blockBoundingGeometry(block).translated(offset).top())
        bottom   = top + int(self.blockBoundingRect(block).height())
        lineH    = self.fontMetrics().height()
        current  = self.textCursor().blockNumber()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                is_cur = blockNum == current
                painter.setPen(QColor(C["teal"]) if is_cur else QColor(C["text_dim"]))
                f = QFont(self.font())
                f.setBold(is_cur)
                painter.setFont(f)
                painter.drawText(
                    0, top, self._lineNumberArea.width() - 10, lineH,
                    Qt.AlignmentFlag.AlignRight, str(blockNum + 1),
                )
            block    = block.next()
            top      = bottom
            bottom   = top + int(self.blockBoundingRect(block).height())
            blockNum += 1


class AnalizadorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Compilador Pedidos")
        _icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-pedidos.png")
        if os.path.exists(_icon_path):
            self.setWindowIcon(QIcon(_icon_path))
        self.resize(1400, 900)
        self._filename = "sin_titulo.txt"
        self._results_font_size = 10.2
        self._results_font_min = 9
        self._results_font_max = 20
        self._dark_mode = True
        self._last_error_signatures = []
        self._active_error_signature = None
        self._build_ui()
        self._apply_styles()
        self._live_timer = QTimer(self)
        self._live_timer.setSingleShot(True)
        self._live_timer.setInterval(550)
        self._live_timer.timeout.connect(self._run_live_analysis)
        self._editor.textChanged.connect(self._schedule_live_analysis)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._make_title_bar())
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        h.addWidget(self._make_activity_bar())
        self._splitter = QSplitter(Qt.Orientation.Vertical)
        self._splitter.setHandleWidth(4)
        self._splitter.addWidget(self._make_editor_section())
        self._splitter.addWidget(self._make_results_panel())
        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 2)
        h.addWidget(self._splitter, stretch=1)
        root.addLayout(h, stretch=1)
        self._status = self.statusBar()
        self._status_label = QLabel("  Ln 1, Col 1   ·   Tokens: 0   ·   Errores: 0  ")
        self._status.addPermanentWidget(self._status_label)
        self._status.showMessage("  ⬡  Listo para analizar")
        self._editor.cursorPositionChanged.connect(self._update_status)

    def _make_title_bar(self):
        bar = QFrame()
        bar.setObjectName("titleBar")
        bar.setFixedHeight(48)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 0, 18, 0)
        lay.setSpacing(0)
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Iconos", "logo-pedidos.png")
        logo_label = QLabel()
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaledToHeight(34, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("⬡")
            logo_label.setObjectName("titleIcon")
        lay.addWidget(logo_label)
        lay.addSpacing(12)
        title = QLabel("COMPILADOR PEDIDOS")
        title.setObjectName("titleText")
        sub = QLabel("análisis en tiempo real · léxico · sintáctico · semántico")
        sub.setObjectName("titleSub")
        lay.addWidget(title)
        lay.addSpacing(14)
        lay.addWidget(sub)
        lay.addStretch()
        return bar

    def _make_activity_bar(self):
        bar = QFrame()
        bar.setObjectName("activityBar")
        bar.setFixedWidth(58)
        lay = QVBoxLayout(bar)
        lay.setContentsMargins(10, 16, 10, 16)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)
        for icon, tip, fn, obj in [
            ("carpeta", "Abrir archivo .txt", self._open_file, "btnOpen"),
            ("▶",  "Analizar código",    self._analyze,   "btnRun"),
            ("theme", "Activar modo claro", self._toggle_dark_mode, "btnTheme"),
            ("✕",  "Limpiar todo",       self._clear,     "btnClear"),
        ]:
            btn = QPushButton()
            _base = os.path.dirname(os.path.abspath(__file__))
            if icon == "theme":
                btn.setIcon(QIcon(os.path.join(_base, "Iconos", "Sol.png" if self._dark_mode else "luna.png")))
                btn.setIconSize(QSize(24, 24))
            elif icon == "carpeta":
                btn.setIcon(QIcon(os.path.join(_base, "Iconos", "carpeta.png")))
                btn.setIconSize(QSize(24, 24))
            else:
                btn.setText(icon)
            btn.setToolTip(tip)
            btn.setObjectName(obj)
            btn.setFixedSize(38, 38)
            btn.clicked.connect(fn)
            if obj == "btnTheme":
                self._theme_btn = btn
            lay.addWidget(btn)
        lay.addStretch()
        lbl = QLabel("LX")
        lbl.setObjectName("langBadge")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl)
        return bar

    def _make_editor_section(self):
        container = QWidget()
        container.setObjectName("editorContainer")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        tab_bar = QFrame()
        tab_bar.setObjectName("editorTabBar")
        tab_bar.setFixedHeight(40)
        tbl = QHBoxLayout(tab_bar)
        tbl.setContentsMargins(0, 0, 12, 0)
        tbl.setSpacing(8)
        self._tab_icon = QLabel()
        _base = os.path.dirname(os.path.abspath(__file__))
        self._tab_icon.setPixmap(QPixmap(os.path.join(_base, "Iconos", "txt.png")).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self._tab_icon.setContentsMargins(8, 0, 0, 0)
        tbl.addWidget(self._tab_icon)

        self._tab_label = QLabel(f" {self._filename}  ")
        self._tab_label.setObjectName("editorActiveTab")
        tbl.addWidget(self._tab_label)
        tbl.addStretch()
        self._editor_zoom_out_btn = QToolButton()
        self._editor_zoom_out_btn.setObjectName("editorZoomBtn")
        self._editor_zoom_out_btn.setText("-")
        self._editor_zoom_out_btn.setToolTip("Alejar texto")
        self._editor_zoom_out_btn.clicked.connect(self._zoom_editor_out)
        self._editor_zoom_label = QLabel("100%")
        self._editor_zoom_label.setObjectName("editorZoomLabel")
        self._editor_zoom_reset_btn = QToolButton()
        self._editor_zoom_reset_btn.setObjectName("editorZoomBtn")
        self._editor_zoom_reset_btn.setText("100%")
        self._editor_zoom_reset_btn.setToolTip("Restablecer tamaño del texto")
        self._editor_zoom_reset_btn.clicked.connect(self._reset_editor_zoom)
        self._editor_zoom_in_btn = QToolButton()
        self._editor_zoom_in_btn.setObjectName("editorZoomBtn")
        self._editor_zoom_in_btn.setText("+")
        self._editor_zoom_in_btn.setToolTip("Acercar texto")
        self._editor_zoom_in_btn.clicked.connect(self._zoom_editor_in)
        tbl.addWidget(self._editor_zoom_out_btn)
        tbl.addWidget(self._editor_zoom_label)
        tbl.addWidget(self._editor_zoom_reset_btn)
        tbl.addWidget(self._editor_zoom_in_btn)
        lay.addWidget(tab_bar)
        self._editor = CodeEditor()
        self._editor.setPlaceholderText(
            "// Escribe tu código aquí o carga un archivo .txt\n"
            "// Presiona ▶ en la barra lateral para analizar\n"
        )
        self._highlighter = PygmentsHighlighter(self._editor.document())
        self._update_editor_zoom_label()
        lay.addWidget(self._editor, stretch=1)
        return container

    def _make_results_panel(self):
        wrapper = QWidget()
        wrapper.setObjectName("resultsWrapper")
        lay = QVBoxLayout(wrapper)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        header = QFrame()
        header.setObjectName("panelHeader")
        header.setFixedHeight(40)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(10)
        hl.addWidget(QLabel("SALIDA DEL ANÁLISIS").also(lambda l: l.setObjectName("panelTitle")))
        hl.addStretch()
        for label, obj, color in [
            ("● Reservada", "legendKw",   C["purple"]),
            ("● Identif.",  "legendId",   C["blue"]),
            ("● Número",    "legendNum",  C["green"]),
            ("● Cadena",    "legendStr",  C["pink"]),
            ("● Operador",  "legendOp",   C["amber"]),
            ("● Delimit.",  "legendPunc", C["cyan"]),
        ]:
            l = QLabel(label)
            l.setObjectName(obj)
            l.setStyleSheet(f"color: {color}; font-size: 11px; font-family: Consolas;")
            hl.addWidget(l)
        hl.addSpacing(16)
        self._badge_tokens = QLabel("Tokens: 0")
        self._badge_tokens.setObjectName("badgeTokens")
        self._badge_errors = QLabel("Errores: 0")
        self._badge_errors.setObjectName("badgeErrors")
        hl.addWidget(self._badge_tokens)
        hl.addWidget(self._badge_errors)
        self._results_zoom_out_btn = QToolButton()
        self._results_zoom_out_btn.setObjectName("resultsZoomBtn")
        self._results_zoom_out_btn.setText("-")
        self._results_zoom_out_btn.setToolTip("Alejar tablas")
        self._results_zoom_out_btn.clicked.connect(self._zoom_results_out)
        self._results_zoom_label = QLabel("100%")
        self._results_zoom_label.setObjectName("resultsZoomLabel")
        self._results_zoom_reset_btn = QToolButton()
        self._results_zoom_reset_btn.setObjectName("resultsZoomBtn")
        self._results_zoom_reset_btn.setText("100%")
        self._results_zoom_reset_btn.setToolTip("Restablecer tamaño de tablas")
        self._results_zoom_reset_btn.clicked.connect(self._reset_results_zoom)
        self._results_zoom_in_btn = QToolButton()
        self._results_zoom_in_btn.setObjectName("resultsZoomBtn")
        self._results_zoom_in_btn.setText("+")
        self._results_zoom_in_btn.setToolTip("Acercar tablas")
        self._results_zoom_in_btn.clicked.connect(self._zoom_results_in)
        hl.addSpacing(8)
        hl.addWidget(self._results_zoom_out_btn)
        hl.addWidget(self._results_zoom_label)
        hl.addWidget(self._results_zoom_reset_btn)
        hl.addWidget(self._results_zoom_in_btn)
        lay.addWidget(header)
        self._tabs = QTabWidget()
        self._tabs.setObjectName("resultsTabs")
        self._tabs.setIconSize(QSize(16, 16))
        self._token_table = self._make_table(["#", "Lexema", "Tipo de Token", "Fila", "Col"])
        self._error_table = self._make_table(["#", "Lexema", "Tipo de Error", "Fila", "Col", "Descripción"])
        _base = os.path.dirname(os.path.abspath(__file__))
        _icon_tokens = QIcon(os.path.join(_base, "Iconos", "cadena-de-bloques.png"))
        _icon_errors = QIcon(os.path.join(_base, "Iconos", "cancelar.png"))
        self._tabs.addTab(self._token_table, _icon_tokens, "  Análisis Léxico  ")
        self._tabs.addTab(self._error_table, _icon_errors, "  Error Léxico  ")

        tree_tab = QWidget()
        tree_lay = QVBoxLayout(tree_tab)
        tree_lay.setContentsMargins(0, 0, 0, 0)
        tree_lay.setSpacing(0)
        tree_toolbar = QFrame()
        tree_toolbar.setObjectName("treeToolbar")
        tree_toolbar.setFixedHeight(40)
        tree_toolbar_lay = QHBoxLayout(tree_toolbar)
        tree_toolbar_lay.setContentsMargins(12, 0, 12, 0)
        tree_toolbar_lay.setSpacing(8)
        tree_toolbar_lay.addWidget(QLabel("Vista del árbol").also(lambda l: l.setObjectName("treeToolbarTitle")))
        tree_toolbar_lay.addStretch()
        self._tree_export_btn = QToolButton()
        self._tree_export_btn.setObjectName("treeActionBtn")
        self._tree_export_btn.setText("Guardar")
        self._tree_export_btn.setToolTip("Guardar árbol en HTML")
        self._tree_export_btn.clicked.connect(self._save_tree_html)
        self._tree_zoom_out_btn = QToolButton()
        self._tree_zoom_out_btn.setObjectName("treeZoomBtn")
        self._tree_zoom_out_btn.setText("-")
        self._tree_zoom_out_btn.setToolTip("Alejar")
        self._tree_zoom_out_btn.clicked.connect(self._zoom_tree_out)
        self._tree_zoom_label = QLabel("100%")
        self._tree_zoom_label.setObjectName("treeZoomLabel")
        self._tree_zoom_reset_btn = QToolButton()
        self._tree_zoom_reset_btn.setObjectName("treeZoomBtn")
        self._tree_zoom_reset_btn.setText("100%")
        self._tree_zoom_reset_btn.setToolTip("Restablecer zoom")
        self._tree_zoom_reset_btn.clicked.connect(self._reset_tree_zoom)
        self._tree_zoom_in_btn = QToolButton()
        self._tree_zoom_in_btn.setObjectName("treeZoomBtn")
        self._tree_zoom_in_btn.setText("+")
        self._tree_zoom_in_btn.setToolTip("Acercar")
        self._tree_zoom_in_btn.clicked.connect(self._zoom_tree_in)
        tree_toolbar_lay.addWidget(self._tree_export_btn)
        tree_toolbar_lay.addWidget(self._tree_zoom_out_btn)
        tree_toolbar_lay.addWidget(self._tree_zoom_label)
        tree_toolbar_lay.addWidget(self._tree_zoom_reset_btn)
        tree_toolbar_lay.addWidget(self._tree_zoom_in_btn)
        self._tree_canvas = ArbolCanvas()
        self._tree_scroll = ArbolScrollArea(self._tree_canvas, self._update_tree_zoom_label)
        self._tree_scroll.setObjectName("treeScroll")
        tree_lay.addWidget(tree_toolbar)
        tree_lay.addWidget(self._tree_scroll, stretch=1)
        _icon_arbol = QIcon(os.path.join(_base, "Iconos", "arbol.png"))
        self._tabs.addTab(tree_tab, _icon_arbol, "  Árbol Sintáctico  ")

        self._synerr_table = self._make_table(["#", "Descripción del Error", "Fila", "Col"])
        self._tabs.addTab(self._synerr_table, _icon_errors, "  Errores Sintácticos  ")

        self._symbol_table = self._make_table([
            "#", "Identificador", "Clase", "Tipo", "Valor", "Estado", "Línea"
        ])
        _icon_tabla = QIcon(os.path.join(_base, "Iconos", "tabla.png"))
        self._tabs.addTab(self._symbol_table, _icon_tabla, "  Tabla de Símbolos  ")

        self._semerr_table = self._make_table([
            "#", "Código", "Error", "Descripción", "Fila", "Col"
        ])
        self._tabs.addTab(self._semerr_table, _icon_errors, "  Errores Semánticos  ")

        self._apply_results_table_font()
        self._update_results_zoom_label()
        lay.addWidget(self._tabs, stretch=1)
        return wrapper

    def _make_table(self, headers):
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        t.setObjectName("resultTable")
        t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.verticalHeader().setVisible(False)
        t.setShowGrid(True)
        t.setAlternatingRowColors(True)
        return t

    def _toggle_dark_mode(self):
        self._dark_mode = not self._dark_mode
        C.clear()
        C.update(DARK_THEME if self._dark_mode else LIGHT_THEME)

        _base = os.path.dirname(os.path.abspath(__file__))
        self._theme_btn.setIcon(QIcon(os.path.join(_base, "Iconos", "Sol.png" if self._dark_mode else "luna.png")))
        self._theme_btn.setToolTip("Activar modo claro" if self._dark_mode else "Activar modo oscuro")

        self._apply_styles()
        self._apply_results_table_font()
        self._highlighter = PygmentsHighlighter(self._editor.document())
        self._highlighter.rehighlight()
        self._editor._highlightCurrentLine()
        self._tree_canvas.setStyleSheet(f"background-color: {C['bg_deep']};")
        self._tree_canvas.update()
        self._tree_scroll.viewport().update()

        if self._editor.toPlainText().strip():
            current_tab = self._tabs.currentIndex()
            self._perform_analysis(auto=True)
            if not (self._active_error_signature and self._tabs.currentIndex() != current_tab):
                self._tabs.setCurrentIndex(current_tab)

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo", "", "Archivos de texto (*.txt)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._editor.setPlainText(f.read())
            self._filename = path.replace("\\", "/").split("/")[-1]
            self._tab_label.setText(f" {self._filename}  ")
            self._status.showMessage(f"  ⬡  Archivo cargado: {self._filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error al cargar", str(e))

    def _schedule_live_analysis(self):
        self._live_timer.start()

    def _run_live_analysis(self):
        self._perform_analysis(auto=True)

    def _analyze(self):
        self._perform_analysis(auto=False)

    def _perform_analysis(self, auto=False):
        code = self._editor.toPlainText()
        if not code.strip():
            self._clear_analysis_outputs()
            if not auto:
                QMessageBox.warning(self, "Editor vacío",
                                    "Ingresa código o carga un archivo .txt primero.")
            return

        tokens, lex_errors = self._run_lexer(code)
        self._fill_token_table(tokens)
        self._fill_error_table(lex_errors)

        syn_errors = []
        sem_errors = []
        tabla_simbolos = []

        if not lex_errors:
            parser = AnalizadorSintactico(tokens)
            arbol, syn_errors = parser.parsear()
            self._fill_tree(arbol)
            self._fill_synerr_table(syn_errors)

            if not syn_errors:
                semantico = AnalizadorSemantico(tokens)
                tabla_simbolos, sem_errors = semantico.analizar()
                self._fill_symbol_table(tabla_simbolos)
                self._fill_semerr_table(sem_errors)
                if not auto:
                    self._tabs.setCurrentIndex(5 if sem_errors else 4)
            else:
                self._symbol_table.setRowCount(0)
                self._semerr_table.setRowCount(0)
                if not auto:
                    self._tabs.setCurrentIndex(3)

            syn_msg = f", {len(syn_errors)} errores sintácticos" if syn_errors else ", sintaxis correcta ✔"
            sem_msg = f", {len(sem_errors)} errores semánticos" if sem_errors else (", semántica correcta ✔" if not syn_errors else "")
        else:
            self._tree_canvas.clear_tree()
            self._update_tree_zoom_label()
            self._synerr_table.setRowCount(0)
            self._symbol_table.setRowCount(0)
            self._semerr_table.setRowCount(0)
            if not auto:
                self._tabs.setCurrentIndex(1)
            syn_msg = ""
            sem_msg = ""

        self._update_error_tab_navigation(lex_errors, syn_errors, sem_errors)

        diagnostics = self._build_editor_diagnostics(code, lex_errors, syn_errors, sem_errors)
        self._editor.set_diagnostics(diagnostics)

        total_errors = len(lex_errors) + len(syn_errors) + len(sem_errors)
        self._badge_tokens.setText(f"Tokens: {len(tokens)}")
        self._badge_errors.setText(f"Errores: {total_errors}")
        self._update_status(len(tokens), total_errors)
        icon = "⚠" if total_errors else "✔"
        mode = "IDE" if auto else "Análisis"
        self._status.showMessage(
            f"  {icon}  {mode}: {len(tokens)} tokens, {len(lex_errors)} errores léxicos{syn_msg}{sem_msg}"
        )

    def _clear_analysis_outputs(self):
        self._token_table.setRowCount(0)
        self._error_table.setRowCount(0)
        self._tree_canvas.clear_tree()
        self._update_tree_zoom_label()
        self._synerr_table.setRowCount(0)
        self._symbol_table.setRowCount(0)
        self._semerr_table.setRowCount(0)
        self._editor.clear_diagnostics()
        self._last_error_signatures = []
        self._active_error_signature = None
        self._badge_tokens.setText("Tokens: 0")
        self._badge_errors.setText("Errores: 0")
        self._update_status(0, 0)

    def _update_error_tab_navigation(self, lex_errors, syn_errors, sem_errors):
        error_targets = self._collect_error_targets(lex_errors, syn_errors, sem_errors)
        current_signatures = [target["signature"] for target in error_targets]

        if not error_targets:
            self._last_error_signatures = []
            self._active_error_signature = None
            return

        previous_signatures = set(self._last_error_signatures)
        target = next(
            (error for error in error_targets if error["signature"] not in previous_signatures),
            None
        )

        if target is None and self._active_error_signature not in current_signatures:
            target = error_targets[0]

        if target is not None:
            self._focus_error_target(target)
            self._active_error_signature = target["signature"]

        self._last_error_signatures = current_signatures

    def _collect_error_targets(self, lex_errors, syn_errors, sem_errors):
        targets = []

        for row, (lexema, tipo, fila, col, desc) in enumerate(lex_errors):
            targets.append({
                "signature": ("lexico", tipo, fila, col),
                "tab_index": 1,
                "table": self._error_table,
                "row": row,
            })

        for row, (desc, fila, col) in enumerate(syn_errors):
            targets.append({
                "signature": ("sintactico", fila, col),
                "tab_index": 3,
                "table": self._synerr_table,
                "row": row,
            })

        for row, (codigo, titulo, mensaje, fila, col) in enumerate(sem_errors):
            targets.append({
                "signature": ("semantico", codigo, fila, col),
                "tab_index": 5,
                "table": self._semerr_table,
                "row": row,
            })

        return targets

    def _focus_error_target(self, target):
        table = target["table"]
        row = target["row"]
        self._tabs.setCurrentIndex(target["tab_index"])
        if 0 <= row < table.rowCount():
            table.clearSelection()
            table.selectRow(row)
            item = table.item(row, 0)
            if item is not None:
                table.scrollToItem(item, QTableWidget.ScrollHint.PositionAtCenter)

    def _build_editor_diagnostics(self, code, lex_errors, syn_errors, sem_errors):
        lineas = code.split("\n")
        diagnostics = []

        for lexema, tipo, fila, col, desc in lex_errors:
            diagnostics.append({
                "fila": fila,
                "col": col,
                "longitud": max(1, len(lexema)),
                "color": C["red"],
                "mensaje": f"Léxico: {desc}",
            })

        for desc, fila, col in syn_errors:
            diagnostics.append({
                "fila": fila,
                "col": col,
                "longitud": self._diagnostic_word_length(lineas, fila, col),
                "color": C["amber"],
                "mensaje": f"Sintáctico: {desc}",
            })

        for codigo, titulo, mensaje, fila, col in sem_errors:
            diagnostics.append({
                "fila": fila,
                "col": col,
                "longitud": self._diagnostic_word_length(lineas, fila, col),
                "color": C["purple"],
                "mensaje": f"Semántico {codigo}: {titulo} — {mensaje}",
            })

        return diagnostics

    def _diagnostic_word_length(self, lineas, fila, col):
        if fila < 1 or fila > len(lineas):
            return 1
        linea = lineas[fila - 1]
        i = max(0, min(len(linea), col - 1))
        if i >= len(linea):
            return 1
        if not linea[i].isalnum() and linea[i] != "_":
            return 1
        j = i
        while j < len(linea) and (linea[j].isalnum() or linea[j] == "_"):
            j += 1
        return max(1, j - i)

    def _clear(self):
        self._live_timer.stop()
        self._editor.clear()
        self._clear_analysis_outputs()
        self._filename = "sin_titulo.txt"
        self._tab_label.setText(f" {self._filename}  ")
        self._status.showMessage("  ⬡  Listo para analizar")

    def _update_status(self, token_count=None, error_count=None):
        cursor = self._editor.textCursor()
        ln  = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        tc  = self._token_table.rowCount() if token_count is None else token_count
        ec  = self._error_table.rowCount() if error_count is None else error_count
        self._status_label.setText(
            f"  Ln {ln}, Col {col}   ·   Tokens: {tc}   ·   Errores: {ec}  "
        )

    def _run_lexer(self, codigo):
        palabras_reservadas = set(PALABRAS_RESERVADAS)
        simbolos            = set(':;()$%')
        tokens, errores = [], []
        for num_fila, linea in enumerate(codigo.split('\n'), start=1):
            i = 0
            while i < len(linea):
                ch = linea[i]
                if ch.isspace():
                    i += 1; continue
                col = i + 1
                if linea[i:i+2] == '//':
                    break
                if ch == '"':
                    inicio, s = i, '"'
                    i += 1
                    while i < len(linea) and linea[i] != '"':
                        s += linea[i]; i += 1
                    if i < len(linea):
                        s += '"'; i += 1
                        tokens.append((s, "CADENA_TEXTO", num_fila, inicio + 1))
                    else:
                        errores.append((s, "ERROR_LEXICO", num_fila,
                                        inicio + 1, 'Cadena sin comilla de cierre (")'))
                    continue
                if ch.isdigit():
                    inicio, num, punto = i, '', False
                    while i < len(linea) and (linea[i].isdigit() or
                                              (linea[i] == '.' and not punto)):
                        if linea[i] == '.': punto = True
                        num += linea[i]; i += 1
                    if i < len(linea) and linea[i].isalpha():
                        mal = num
                        while i < len(linea) and linea[i].isalnum():
                            mal += linea[i]; i += 1
                        errores.append((mal, "ERROR_LEXICO", num_fila, inicio + 1,
                                        "Un identificador no puede iniciar con un número"))
                    else:
                        tipo = "NUMERO_REAL" if punto else "NUMERO"
                        tokens.append((num, tipo, num_fila, inicio + 1))
                    continue
                if ch in simbolos:
                    tokens.append((ch, "SIMBOLO", num_fila, col))
                    i += 1; continue
                if ch.isalpha():
                    inicio, ident = i, ''
                    while i < len(linea) and linea[i].isalnum():
                        ident += linea[i]; i += 1
                    tipo = ("PALABRA_RESERVADA"
                            if ident in palabras_reservadas else "IDENTIFICADOR")
                    tokens.append((ident, tipo, num_fila, inicio + 1))
                    continue
                errores.append((ch, "ERROR_LEXICO", num_fila, col,
                                 "Símbolo no definido en el lenguaje"))
                i += 1
        return tokens, errores

    _TOKEN_STYLE = {
        "PALABRA_RESERVADA": (C["purple"] + "25", C["purple"]),
        "IDENTIFICADOR":     (C["blue"]   + "18", C["blue"]),
        "SIMBOLO":           (C["cyan"]   + "20", C["cyan"]),
        "CADENA_TEXTO":      (C["pink"]   + "20", C["pink"]),
        "NUMERO":            (C["green"]  + "20", C["green"]),
        "NUMERO_REAL":       (C["green"]  + "20", C["green"]),
    }

    def _fill_token_table(self, tokens):
        self._token_table.setRowCount(0)
        for idx, (lexema, tipo, fila, col) in enumerate(tokens, start=1):
            r = self._token_table.rowCount()
            self._token_table.insertRow(r)
            _, fg = self._TOKEN_STYLE.get(tipo, (C["bg_light"], C["text"]))
            for c, val in enumerate([idx, lexema, tipo, fila, col]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(fg))
                self._token_table.setItem(r, c, item)

    def _fill_error_table(self, errores):
        self._error_table.setRowCount(0)
        for idx, (lexema, tipo, fila, col, desc) in enumerate(errores, start=1):
            r = self._error_table.rowCount()
            self._error_table.insertRow(r)
            for c, val in enumerate([idx, lexema, "Error Léxico", fila, col, desc]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(C["red"]))
                self._error_table.setItem(r, c, item)

    def _fill_tree(self, raiz):
        self._tree_canvas.set_tree(raiz)
        self._update_tree_zoom_label()

    def _fill_synerr_table(self, syn_errors):
        self._synerr_table.setRowCount(0)
        for idx, (desc, fila, col) in enumerate(syn_errors, start=1):
            r = self._synerr_table.rowCount()
            self._synerr_table.insertRow(r)
            for c, val in enumerate([idx, desc, fila, col]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(C["amber"]))
                self._synerr_table.setItem(r, c, item)

    def _fill_symbol_table(self, simbolos):
        self._symbol_table.setRowCount(0)
        for idx, simbolo in enumerate(simbolos, start=1):
            r = self._symbol_table.rowCount()
            self._symbol_table.insertRow(r)
            valores = [
                idx,
                simbolo.identificador,
                simbolo.clase,
                simbolo.tipo,
                simbolo.valor,
                simbolo.estado,
                simbolo.linea,
            ]
            for c, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(C["green"] if simbolo.clase == "Pedido" else C["blue"]))
                self._symbol_table.setItem(r, c, item)

    def _fill_semerr_table(self, sem_errors):
        self._semerr_table.setRowCount(0)
        for idx, (codigo, titulo, mensaje, fila, col) in enumerate(sem_errors, start=1):
            r = self._semerr_table.rowCount()
            self._semerr_table.insertRow(r)
            for c, val in enumerate([idx, codigo, titulo, mensaje, fila, col]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(C["red"]))
                self._semerr_table.setItem(r, c, item)

    def _update_tree_zoom_label(self):
        zoom = self._tree_canvas.zoom_percent()
        self._tree_zoom_label.setText(f"{zoom}%")
        self._tree_zoom_reset_btn.setText(f"{zoom}%")

    def _save_tree_html(self):
        if self._tree_canvas._raiz is None:
            QMessageBox.warning(
                self,
                "Árbol no disponible",
                "Primero analiza una entrada para generar el árbol sintáctico."
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar árbol en HTML",
            "arbol_sintactico.html",
            "Documento HTML (*.html)"
        )
        if not path:
            return

        if not path.lower().endswith(".html"):
            path += ".html"

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._build_tree_html(self._tree_canvas._raiz))
            saved_name = path.replace("\\", "/").split("/")[-1]
            self._status.showMessage(f"  ✔  Árbol guardado en HTML: {saved_name}")
        except Exception:
            QMessageBox.critical(
                self,
                "Error al guardar",
                "No se pudo guardar el árbol sintáctico en HTML."
            )

    def _build_tree_html(self, raiz):
        def esc(texto):
            return (
                str(texto)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
            )

        def render_node(nodo):
            valor_html = ""
            if nodo.valor is not None:
                valor_html = f'<span class="node-value">{esc(nodo.valor)}</span>'

            hijos_html = ""
            if nodo.hijos:
                hijos = "".join(render_node(hijo) for hijo in nodo.hijos)
                hijos_html = f'<ul class="tree-children">{hijos}</ul>'

            return (
                '<li class="tree-item">'
                f'<div class="node-card node-{esc(nodo.tipo)}">'
                f'<div class="node-type">{esc(nodo.tipo)}</div>'
                f'{valor_html}'
                '</div>'
                f'{hijos_html}'
                '</li>'
            )

        tree_html = render_node(raiz)
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Árbol Sintáctico</title>
    <style>
        :root {{
            --bg: #0d1520;
            --panel: #111d2e;
            --panel-soft: #172438;
            --line: #35506d;
            --text: #ddeeff;
            --muted: #88a7c5;
            --accent: #99cbff;
            --value: #ff8fab;
            --shadow: rgba(0, 0, 0, 0.28);
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            min-height: 100vh;
            font-family: "Segoe UI", Tahoma, sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(153, 203, 255, 0.12), transparent 30%),
                linear-gradient(180deg, #0a1018 0%, var(--bg) 100%);
        }}

        .page {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 32px 24px 48px;
        }}

        .hero {{
            margin-bottom: 28px;
            padding: 24px 28px;
            border: 1px solid rgba(153, 203, 255, 0.18);
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(17, 29, 46, 0.96), rgba(23, 36, 56, 0.92));
            box-shadow: 0 20px 40px var(--shadow);
        }}

        .eyebrow {{
            margin: 0 0 8px;
            color: var(--accent);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
        }}

        h1 {{
            margin: 0 0 8px;
            font-size: clamp(28px, 4vw, 42px);
            line-height: 1.1;
        }}

        .subtitle {{
            margin: 0;
            color: var(--muted);
            font-size: 15px;
        }}

        .tree-shell {{
            overflow: auto;
            padding: 24px;
            border-radius: 20px;
            border: 1px solid rgba(153, 203, 255, 0.16);
            background: rgba(17, 29, 46, 0.88);
            box-shadow: 0 18px 36px var(--shadow);
        }}

        .tree,
        .tree ul {{
            margin: 0;
            padding-left: 28px;
            list-style: none;
            position: relative;
        }}

        .tree {{
            padding-left: 0;
        }}

        .tree ul::before {{
            content: "";
            position: absolute;
            top: 0;
            bottom: 14px;
            left: 12px;
            width: 2px;
            background: linear-gradient(180deg, rgba(103, 232, 249, 0.4), rgba(53, 80, 109, 0.1));
        }}

        .tree-item {{
            position: relative;
            margin: 14px 0;
            padding-left: 28px;
        }}

        .tree-item::before {{
            content: "";
            position: absolute;
            top: 28px;
            left: 12px;
            width: 16px;
            height: 2px;
            background: rgba(103, 232, 249, 0.4);
        }}

        .node-card {{
            display: inline-flex;
            flex-direction: column;
            gap: 6px;
            min-width: 220px;
            padding: 14px 16px;
            border-radius: 16px;
            border: 1px solid rgba(153, 203, 255, 0.2);
            background: linear-gradient(180deg, rgba(23, 36, 56, 0.98), rgba(13, 21, 32, 0.98));
            box-shadow: 0 10px 22px rgba(0, 0, 0, 0.2);
        }}

        .node-type {{
            color: var(--accent);
            font-family: Consolas, "Cascadia Code", monospace;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.04em;
        }}

        .node-value {{
            display: inline-block;
            color: var(--value);
            font-family: Consolas, "Cascadia Code", monospace;
            font-size: 14px;
            background: rgba(255, 143, 171, 0.12);
            border: 1px solid rgba(255, 143, 171, 0.2);
            border-radius: 10px;
            padding: 6px 10px;
            word-break: break-word;
        }}

        .node-PROGRAMA {{
            border-color: rgba(153, 203, 255, 0.4);
        }}

        .node-LISTA_SENTENCIAS {{
            border-color: rgba(103, 232, 249, 0.35);
        }}

        .node-DECLARACION_BASICA,
        .node-ACCION_COMPUESTA,
        .node-ACCION_ESTADO,
        .node-ESTRUCTURA_CONDICIONAL,
        .node-CONDICION {{
            background: linear-gradient(180deg, rgba(24, 30, 54, 0.98), rgba(13, 21, 32, 0.98));
        }}

        @media (max-width: 768px) {{
            .page {{
                padding: 20px 14px 32px;
            }}

            .hero,
            .tree-shell {{
                padding: 18px;
                border-radius: 16px;
            }}

            .node-card {{
                min-width: 0;
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <main class="page">
        <section class="hero">
            <p class="eyebrow">Compiladores</p>
            <h1>Árbol Sintáctico</h1>
            <p class="subtitle"></p>
        </section>
        <section class="tree-shell">
            <ul class="tree">
                {tree_html}
            </ul>
        </section>
    </main>
</body>
</html>
"""

    def _apply_results_table_font(self):
        table_font = QFont("Consolas")
        table_font.setPointSizeF(self._results_font_size)
        header_font = QFont("Consolas")
        header_font.setPointSizeF(max(10, self._results_font_size - 1))
        row_height = QFontMetricsF(table_font).height() + 10
        header_height = int(QFontMetricsF(header_font).height() + 14)
        for table in (
            self._token_table, self._error_table, self._synerr_table,
            self._symbol_table, self._semerr_table
        ):
            table.setFont(table_font)
            table.horizontalHeader().setFont(header_font)
            table.verticalHeader().setDefaultSectionSize(int(row_height))
            table.horizontalHeader().setMinimumHeight(header_height)
            table.horizontalHeader().setDefaultSectionSize(header_height)
            table.setStyleSheet(
                f"""
                QTableWidget {{
                    font-family: 'Consolas', monospace;
                    font-size: {self._results_font_size}pt;
                }}
                QHeaderView::section {{
                    font-family: 'Consolas', monospace;
                    font-size: {max(10, self._results_font_size - 1)}pt;
                }}
                """
            )
            table.viewport().update()

    def _update_results_zoom_label(self):
        zoom = int(round((self._results_font_size / 12) * 100))
        self._results_zoom_label.setText(f"{zoom}%")
        self._results_zoom_reset_btn.setText(f"{zoom}%")

    def _set_results_zoom(self, size):
        size = max(self._results_font_min, min(self._results_font_max, size))
        if size == self._results_font_size:
            return False
        self._results_font_size = size
        self._apply_results_table_font()
        self._update_results_zoom_label()
        return True

    def _zoom_results_in(self):
        self._set_results_zoom(self._results_font_size + 1)

    def _zoom_results_out(self):
        self._set_results_zoom(self._results_font_size - 1)

    def _reset_results_zoom(self):
        self._set_results_zoom(12)

    def _update_editor_zoom_label(self):
        zoom = self._editor.zoom_percent()
        self._editor_zoom_label.setText(f"{zoom}%")
        self._editor_zoom_reset_btn.setText(f"{zoom}%")

    def _zoom_editor_in(self):
        if self._editor.zoom_in_editor():
            self._update_editor_zoom_label()

    def _zoom_editor_out(self):
        if self._editor.zoom_out_editor():
            self._update_editor_zoom_label()

    def _reset_editor_zoom(self):
        if self._editor.reset_zoom_editor():
            self._update_editor_zoom_label()

    def _zoom_tree_in(self):
        if self._tree_canvas.zoom_in():
            self._update_tree_zoom_label()

    def _zoom_tree_out(self):
        if self._tree_canvas.zoom_out():
            self._update_tree_zoom_label()

    def _reset_tree_zoom(self):
        if self._tree_canvas.reset_zoom():
            self._update_tree_zoom_label()

    def _apply_styles(self):
        self.setStyleSheet(f"""
        QMainWindow, QWidget {{
            background-color: {C["bg_deep"]};
            color: {C["text"]};
            font-family: 'Segoe UI', Helvetica, sans-serif;
            font-size: 13px;
        }}
        QFrame#titleBar {{
            background-color: {C["bg_mid"]};
            border-bottom: 2px solid {C["teal"]};
        }}
        QLabel#titleIcon {{
            color: {C["teal"]};
            font-size: 20px;
        }}
        QLabel#titleText {{
            color: {C["teal"]};
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 4px;
            font-family: 'Consolas', monospace;
        }}
        QLabel#titleSub {{
            color: {C["text_dim"]};
            font-size: 11px;
            letter-spacing: 1px;
        }}
        QFrame#activityBar {{
            background-color: {C["bg_mid"]};
            border-right: 1px solid {C["border"]};
        }}
        QPushButton#btnOpen {{
            background: transparent;
            color: {C["teal"]};
            border: 1px solid rgba(12,227,232,0.33);
            border-radius: 10px;
            font-size: 16px;
        }}
        QPushButton#btnRun {{
            background: transparent;
            color: {C["green"]};
            border: 1px solid {C["green"]}55;
            border-radius: 10px;
            font-size: 16px;
        }}
        QPushButton#btnTheme {{
            background: transparent;
            color: {C["amber"]};
            border: 1px solid {C["amber"]}55;
            border-radius: 10px;
            font-size: 16px;
        }}
        QPushButton#btnClear {{
            background: transparent;
            color: {C["red"]};
            border: 1px solid {C["red"]}55;
            border-radius: 10px;
            font-size: 16px;
        }}
        QPushButton#btnOpen:hover  {{
            background: rgba(12,227,232,0.13);
            border-color: {C["teal"]};
        }}
        QPushButton#btnRun:hover   {{
            background: {C["green"]}22;
            border-color: {C["green"]};
        }}
        QPushButton#btnTheme:hover {{
            background: {C["amber"]}22;
            border-color: {C["amber"]};
        }}
        QPushButton#btnClear:hover {{
            background: {C["red"]}22;
            border-color: {C["red"]};
        }}
        QLabel#langBadge {{
            color: {C["teal"]};
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 2px;
            border: 1px solid rgba(12,227,232,0.40);
            border-radius: 5px;
            padding: 3px 5px;
            background: rgba(12,227,232,0.07);
        }}
        QWidget#editorContainer {{ background-color: {C["bg_deep"]}; }}
        QFrame#editorTabBar {{
            background-color: {C["bg_mid"]};
            border-bottom: 1px solid {C["border"]};
        }}
        QLabel#editorActiveTab {{
            background-color: {C["bg_deep"]};
            color: {C["text"]};
            border-top: 2px solid {C["teal"]};
            border-right: 1px solid {C["border"]};
            padding: 0 16px;
            font-size: 12px;
        }}
        QLabel#editorZoomLabel {{
            color: {C["teal"]};
            min-width: 48px;
            font-size: 11px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            font-family: 'Consolas', monospace;
        }}
        QToolButton#editorZoomBtn {{
            background-color: {C["bg_light"]};
            color: {C["text"]};
            border: 1px solid {C["border"]};
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: bold;
            min-width: 36px;
        }}
        QToolButton#editorZoomBtn:hover {{
            color: {C["teal"]};
            border-color: {C["teal"]};
            background-color: rgba(12,227,232,0.10);
        }}
        QPlainTextEdit {{
            background-color: {C["bg_deep"]};
            color: {C["text"]};
            border: none;
            selection-background-color: rgba(12,227,232,0.27);
            selection-color: #ffffff;
            line-height: 1.6;
        }}
        QSplitter::handle {{ background-color: rgba(12, 227, 232, 0.25); }}
        QSplitter::handle:hover {{ background-color: #0ce3e8; }}
        QWidget#resultsWrapper {{
            background-color: {C["bg_mid"]};
            border-top: 2px solid rgba(12,227,232,0.33);
        }}
        QFrame#panelHeader {{
            background-color: {C["bg_mid"]};
            border-bottom: 1px solid {C["border"]};
        }}
        QLabel#panelTitle {{
            color: {C["text_dim"]};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 3px;
            font-family: 'Consolas', monospace;
        }}
        QLabel#badgeTokens {{
            color: #99cbff;
            background-color: rgba(153, 203, 255, 0.12);
            border: 1px solid rgba(153, 203, 255, 0.4);
            border-radius: 10px;
            padding: 2px 12px;
            font-size: 11px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        }}
        QLabel#badgeErrors {{
            color: #ff6b6b;
            background-color: rgba(255, 107, 107, 0.12);
            border: 1px solid rgba(255, 107, 107, 0.4);
            border-radius: 10px;
            padding: 2px 12px;
            font-size: 11px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        }}
        QLabel#resultsZoomLabel {{
            color: {C["teal"]};
            min-width: 48px;
            font-size: 11px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            font-family: 'Consolas', monospace;
        }}
        QToolButton#resultsZoomBtn {{
            background-color: {C["bg_light"]};
            color: {C["text"]};
            border: 1px solid {C["border"]};
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: bold;
            min-width: 36px;
        }}
        QToolButton#resultsZoomBtn:hover {{
            color: {C["teal"]};
            border-color: {C["teal"]};
            background-color: rgba(12,227,232,0.10);
        }}
        QTabWidget#resultsTabs::pane {{
            border: none;
            background-color: {C["bg_deep"]};
        }}
        QTabBar::tab {{
            background-color: {C["bg_mid"]};
            color: {C["text_dim"]};
            padding: 8px 28px;
            border: none;
            border-right: 1px solid {C["border"]};
            font-size: 12px;
            font-family: 'Consolas', monospace;
            letter-spacing: 1px;
        }}
        QTabBar::tab:selected {{
            color: {C["teal"]};
            border-bottom: 2px solid {C["teal"]};
            background-color: {C["bg_deep"]};
        }}
        QTabBar::tab:hover:!selected {{
            color: {C["text"]};
            background-color: {C["bg_light"]};
        }}
        QTableWidget#resultTable {{
            background-color: {C["bg_deep"]};
            alternate-background-color: {C["bg_row_alt"]};
            border: none;
            gridline-color: {C["border"]};
            color: {C["text"]};
            font-family: 'Consolas', monospace;
            font-size: 12px;
        }}
        QHeaderView::section {{
            background-color: {C["bg_mid"]};
            color: {C["teal"]};
            font-weight: bold;
            border: none;
            border-bottom: 1px solid rgba(12,227,232,0.27);
            border-right: 1px solid {C["border"]};
            padding: 8px 0;
            font-family: 'Consolas', monospace;
            font-size: 11px;
            letter-spacing: 2px;
        }}
        QTableWidget#resultTable::item {{ padding: 5px 8px; }}
        QTableWidget#resultTable::item:selected {{
            background-color: rgba(12,227,232,0.16);
            color: #ffffff;
        }}
        QStatusBar {{
            background-color: {C["bg_mid"]};
            color: {C["text_dim"]};
            font-size: 11px;
            font-family: 'Consolas', monospace;
            border-top: 1px solid rgba(12,227,232,0.27);
        }}
        QStatusBar QLabel {{
            color: {C["teal"]};
            font-size: 11px;
            background-color: transparent;
            font-family: 'Consolas', monospace;
        }}
        QScrollBar:vertical {{ background: {C["bg_deep"]}; width: 8px; }}
        QScrollBar::handle:vertical {{
            background: {C["bg_light"]};
            border-radius: 4px; min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{ background: rgba(12,227,232,0.53); }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar:horizontal {{ background: {C["bg_deep"]}; height: 8px; }}
        QScrollBar::handle:horizontal {{
            background: {C["bg_light"]}; border-radius: 4px;
        }}
        QScrollBar::handle:horizontal:hover {{ background: rgba(12,227,232,0.53); }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        QToolTip {{
            background-color: {C["bg_mid"]};
            color: {C["text"]};
            border: 1px solid rgba(12,227,232,0.40);
            padding: 5px 12px;
            font-size: 12px;
        }}
        QScrollArea#treeScroll {{
            background-color: {C["bg_deep"]};
            border: none;
        }}
        QScrollArea#treeScroll > QWidget > QWidget {{
            background-color: {C["bg_deep"]};
        }}
        QFrame#treeToolbar {{
            background-color: {C["bg_mid"]};
            border-bottom: 1px solid {C["border"]};
        }}
        QLabel#treeToolbarTitle {{
            color: {C["text_dim"]};
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 2px;
            font-family: 'Consolas', monospace;
        }}
        QLabel#treeZoomLabel {{
            color: {C["teal"]};
            min-width: 48px;
            font-size: 11px;
            font-weight: bold;
            qproperty-alignment: AlignCenter;
            font-family: 'Consolas', monospace;
        }}
        QToolButton#treeZoomBtn {{
            background-color: {C["bg_light"]};
            color: {C["text"]};
            border: 1px solid {C["border"]};
            border-radius: 8px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: bold;
            min-width: 36px;
        }}
        QToolButton#treeZoomBtn:hover {{
            color: {C["teal"]};
            border-color: {C["teal"]};
            background-color: rgba(12,227,232,0.10);
        }}
        QToolButton#treeActionBtn {{
            background-color: {C["bg_light"]};
            color: {C["green"]};
            border: 1px solid {C["green"]}55;
            border-radius: 8px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: bold;
        }}
        QToolButton#treeActionBtn:hover {{
            color: {C["green"]};
            border-color: {C["green"]};
            background-color: {C["green"]}22;
        }}
        """)


def _also(self, fn):
    fn(self)
    return self
QLabel.also = _also


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AnalizadorApp()
    window.show()
    sys.exit(app.exec())
