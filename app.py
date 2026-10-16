import time

from flask import jsonify, request

from modelo import Pedido, app, db


# Caché en memoria
cache_pedidos = {}

# El caché dura 30 segundos
TTL_CACHE = 30


def respuesta_con_cache(contenido, estado_cache):
    respuesta = jsonify({
        **contenido,
        "cache": estado_cache
    })

    respuesta.headers["X-Cache"] = estado_cache
    respuesta.headers["Cache-Control"] = f"public, max-age={TTL_CACHE}"

    return respuesta


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensaje": "API de pedidos de la pastelería funcionando",
        "endpoints": [
            "POST /pedidos",
            "GET /pedidos/fecha/<fecha>"
        ]
    }), 200


@app.route("/pedidos", methods=["POST"])
def crear_pedido():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "El cuerpo debe enviarse en formato JSON"
        }), 400

    campos_obligatorios = [
        "cliente",
        "tipoPastel",
        "porciones",
        "decoracion",
        "fechaEntrega",
        "horaEntrega",
        "tiempoPreparacion"
    ]

    campos_faltantes = [
        campo
        for campo in campos_obligatorios
        if campo not in datos
        or datos[campo] is None
        or datos[campo] == ""
    ]

    if campos_faltantes:
        return jsonify({
            "error": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400

    try:
        porciones = int(datos["porciones"])
        tiempo_preparacion = int(datos["tiempoPreparacion"])

    except (TypeError, ValueError):
        return jsonify({
            "error": "porciones y tiempoPreparacion deben ser números enteros"
        }), 400

    if porciones <= 0 or tiempo_preparacion <= 0:
        return jsonify({
            "error": "porciones y tiempoPreparacion deben ser mayores que cero"
        }), 400

    nuevo_pedido = Pedido(
        cliente=datos["cliente"],
        tipo_pastel=datos["tipoPastel"],
        porciones=porciones,
        decoracion=datos["decoracion"],
        fecha_entrega=datos["fechaEntrega"],
        hora_entrega=datos["horaEntrega"],
        tiempo_preparacion=tiempo_preparacion,
        estado=datos.get("estado", "pendiente")
    )

    try:
        db.session.add(nuevo_pedido)
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "error": "No fue posible guardar el pedido"
        }), 500

    # Invalidar el caché de la fecha modificada
    clave_cache = f"pedidos_fecha:{nuevo_pedido.fecha_entrega}"
    cache_pedidos.pop(clave_cache, None)

    return jsonify({
        "mensaje": "Pedido registrado correctamente",
        "pedido": nuevo_pedido.to_dict()
    }), 201


@app.route("/pedidos/fecha/<string:fecha>", methods=["GET"])
def consultar_pedidos_por_fecha(fecha):
    clave_cache = f"pedidos_fecha:{fecha}"
    ahora = time.time()

    entrada = cache_pedidos.get(clave_cache)

    # HIT: la información fue encontrada en el caché
    if entrada and entrada["expira"] > ahora:
        return respuesta_con_cache(
            entrada["contenido"],
            "HIT"
        ), 200

    # Eliminar el caché si ya venció
    if entrada:
        cache_pedidos.pop(clave_cache, None)

    # MISS: consultar la base de datos
    pedidos = (
        Pedido.query
        .filter_by(fecha_entrega=fecha)
        .order_by(Pedido.hora_entrega.asc())
        .all()
    )

    contenido = {
        "fecha": fecha,
        "cantidad": len(pedidos),
        "pedidos": [
            pedido.to_dict()
            for pedido in pedidos
        ]
    }

    # Guardar el resultado durante 30 segundos
    cache_pedidos[clave_cache] = {
        "contenido": contenido,
        "expira": ahora + TTL_CACHE
    }

    return respuesta_con_cache(
        contenido,
        "MISS"
    ), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)