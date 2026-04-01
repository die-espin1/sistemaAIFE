import json

def normalizar_dte(data):

    if "identificacion" in data:
        return data

    if "json" in data:
        return data["json"]

    if "documento" in data:
        return data["documento"]

    return None


def cargar_json_seguro(ruta):

    with open(ruta, "r", encoding="utf-8-sig") as f:
        contenido = f.read().strip()

    try:
        data = json.loads(contenido)
        return normalizar_dte(data)

    except json.JSONDecodeError:

        partes = contenido.split("}{")

        if len(partes) > 1:

            partes[0] = partes[0] + "}"
            partes[-1] = "{" + partes[-1]

            for p in partes:
                try:
                    data = json.loads(p)
                    dte = normalizar_dte(data)
                    if dte:
                        return dte
                except:
                    pass

    return None