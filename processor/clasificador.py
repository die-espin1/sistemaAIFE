def clasificar_anexo(dte):

    tipo = dte.get("identificacion", {}).get("tipoDte")

    if tipo == "01":
        return 2

    if tipo == "03":

        if dte.get("respuestaMH") or dte.get("acuseMH"):
            return 3

        return 1

    return None