from datetime import datetime

def formatear_fecha(fecha):
    if not fecha:
        return ""
    return datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")


def obtener_fecha_obj(fecha):
    if not fecha:
        return datetime.min
    return datetime.strptime(fecha, "%Y-%m-%d")


def vacio_si_cero(valor):
    if not valor:
        return ""
    return valor


def tipo_operacion(valor):
    mapa = {
        1: "01 Gravada",
        2: "02 Exenta",
        3: "03 No Sujeta"
    }
    return mapa.get(valor, "")


def formatear_nit(nit):
    if not nit:
        return ""
    if len(nit) == 14:
        return f"{nit[0:4]}-{nit[4:10]}-{nit[10:13]}-{nit[13]}"
    return nit