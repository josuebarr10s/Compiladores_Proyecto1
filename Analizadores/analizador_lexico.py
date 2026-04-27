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

def analizar_lexico(codigo):
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
