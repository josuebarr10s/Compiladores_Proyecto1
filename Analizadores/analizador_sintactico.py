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
