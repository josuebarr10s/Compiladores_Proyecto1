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
    
    PALABRAS_CLAVE_BASICA = {
        "Empresa", "Sucursal", "Cliente", "Proveedor", "Empleado",
        "Producto", "Telefono", "Direccion", "Referencia", "Cantidad",
        "Precio", "Subtotal", "Descuento", "Impuesto", "Total", "Stock",
        "Minimo", "Maximo", "Categoria", "Nota", "Fecha", "Descripcion",
    }

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
        if lex in self.ESTADO_NORMALIZADO or lex in self.ESTADOS_NO_PEDIDO:
            return self._cambio_estado()
        if lex in self.PALABRAS_CLAVE_BASICA:
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
