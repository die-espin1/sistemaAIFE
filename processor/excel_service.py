import shutil
from pathlib import Path
import openpyxl

from processor.json_loader import cargar_json_seguro
from processor.clasificador import clasificar_anexo
from processor.handlers import *


def generar_anexos(carpeta_json, plantilla_path, salida_path):

    CARPETA_JSON = Path(carpeta_json)

    # copiar plantilla
    shutil.copy(plantilla_path, salida_path)

    wb = openpyxl.load_workbook(salida_path, keep_vba=True)

    ws_contrib = wb["ANEXO CONTRIBUYENTES"]
    ws_consumidor = wb["ANEXO CONSUMIDOR FINAL"]
    ws_compras = wb["ANEXO DE COMPRAS"]

    # ---------------- PROCESADORES ----------------

    def procesar_contribuyente(data, fila):

        resumen = data.get("resumen", {})
        identificacion = data.get("identificacion", {})
        receptor = data.get("receptor", {})

        iva = ""
        tributos = resumen.get("tributos")

        if tributos:
            for t in tributos:
                if t.get("codigo") == "20":
                    iva = round(t.get("valor", 0), 2)

        valores = [
            formatear_fecha(identificacion.get("fecEmi")),
            "4. DOCUMENTO TRIBUTARIO ELECTRÓNICO (DTE)",
            "03. COMPROBANTE DE CRÉDITO FISCAL",
            identificacion.get("numeroControl"),
            data.get("selloRecibido"),
            identificacion.get("codigoGeneracion"),
            identificacion.get("codigoGeneracion"),
            receptor.get("nit"),
            receptor.get("nombre"),
            vacio_si_cero(resumen.get("totalExenta")),
            vacio_si_cero(resumen.get("totalNoSuj")),
            round(resumen.get("totalGravada", 0), 2),
            iva,
            "",
            "",
            round(resumen.get("montoTotalOperacion", 0), 2),
            "",
            tipo_operacion(identificacion.get("tipoOperacion")),
            "03 Actividades Comerciales",
            1
        ]

        for col, valor in enumerate(valores, start=1):
            ws_contrib.cell(row=fila, column=col).value = valor


    def procesar_consumidor(data, fila):

        resumen = data.get("resumen", {})
        identificacion = data.get("identificacion", {})

        total = round(resumen.get("montoTotalOperacion", 0), 2)

        valores = [
            formatear_fecha(identificacion.get("fecEmi")),
            "4. DOCUMENTO TRIBUTARIO ELECTRÓNICO (DTE)",
            "01. FACTURA",
            identificacion.get("numeroControl"),
            data.get("acuseMH", {}).get("numValidacion"),
            identificacion.get("codigoGeneracion"),
            identificacion.get("codigoGeneracion"),
            "",
            "",
            "",
            0.00,
            0.00,
            0.00,
            total,
            "",
            "",
            "",
            "",
            "",
            total,
            tipo_operacion(identificacion.get("tipoOperacion")),
            "02 Actividades de Servicios",
            2
        ]

        for col, valor in enumerate(valores, start=1):
            ws_consumidor.cell(row=fila, column=col).value = valor


    def procesar_compra(data, fila):

        resumen = data.get("resumen", {})
        identificacion = data.get("identificacion", {})
        emisor = data.get("emisor", {})

        iva = 0
        tributos = resumen.get("tributos")

        if tributos:
            for t in tributos:
                if t.get("codigo") == "20":
                    iva = round(t.get("valor", 0), 2)

        valores = [
            formatear_fecha(identificacion.get("fecEmi")),
            "4. DOCUMENTO TRIBUTARIO ELECTRONICO (DTE)",
            "03. COMPROBANTE DE CRÉDITO FISCAL",
            identificacion.get("numeroControl"),
            formatear_nit(emisor.get("nit")),
            emisor.get("nombre"),
            "",
            "",
            "",
            round(resumen.get("totalGravada", 0), 2),
            "",
            "",
            "",
            iva,
            round(resumen.get("montoTotalOperacion", 0), 2),
            "",
            "1 Gravada",
            "2 Gasto",
            "4 Servicios, Profesiones, Artes y Oficios",
            "2 Gasto de Administración sin Donación",
            3
        ]

        for col, valor in enumerate(valores, start=1):
            ws_compras.cell(row=fila, column=col).value = valor


    # ---------------- CARGA ----------------

    documentos = []

    for archivo in CARPETA_JSON.glob("*.json"):

        dte = cargar_json_seguro(archivo)

        if not dte:
            continue

        fecha = dte.get("identificacion", {}).get("fecEmi")
        numero = dte.get("identificacion", {}).get("numeroControl", "")

        documentos.append((dte, obtener_fecha_obj(fecha), numero))

    documentos.sort(key=lambda x: (x[1], x[2]))

    # ---------------- PROCESO ----------------

    fila_contrib = 3
    fila_consumidor = 3
    fila_compras = 3

    for data, _, _ in documentos:

        anexo = clasificar_anexo(data)

        if anexo == 1:
            procesar_contribuyente(data, fila_contrib)
            fila_contrib += 1

        elif anexo == 2:
            procesar_consumidor(data, fila_consumidor)
            fila_consumidor += 1

        elif anexo == 3:
            procesar_compra(data, fila_compras)
            fila_compras += 1

    wb.save(salida_path)

    return salida_path