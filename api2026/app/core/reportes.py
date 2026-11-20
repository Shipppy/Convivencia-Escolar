"""Definicion y generacion de reportes (JSON, PDF con reportlab y Excel con openpyxl).
Las columnas son solo nombres y descripciones: ningun ID sale de aqui."""
import io
from datetime import date, datetime

from fastapi import HTTPException

from app.repositories.base import ejecutar

TIPOS = {
    "incidentes": {
        "titulo": "Reporte de incidentes de convivencia",
        "columnas": [
            ("fecha", "Fecha"), ("tipo", "Tipo"), ("nivel", "Nivel"), ("estado", "Estado"),
            ("gravedad", "Gravedad"), ("reportante", "Reportó"), ("reportado", "Reportado"),
            ("docente", "Docente"), ("lugar", "Lugar"), ("responsable", "Responsable"),
            ("descripcion", "Descripción"),
        ],
        "sql": """
            SELECT i.fecha, ti.nombre AS tipo, np.nombre AS nivel, i.estado, i.gravedad,
                   er.nombre || ' ' || er.apellido AS reportante,
                   ed.nombre || ' ' || ed.apellido AS reportado,
                   COALESCE(d.nombre || ' ' || d.apellido, 'Sin docente') AS docente,
                   i.lugar, COALESCE(co.nombre, 'Sin asignar') AS responsable, i.descripcion
            FROM incidentes i
            INNER JOIN estudiantes er ON er.id_estudiante = i.id_reportante
            INNER JOIN estudiantes ed ON ed.id_estudiante = i.id_reportado
            INNER JOIN tipos_incidente ti ON ti.id_tipo = i.id_tipo
            INNER JOIN nivel_protocolo np ON np.id_nivel = i.id_nivel
            LEFT JOIN docentes d ON d.id_docente = i.id_docente
            LEFT JOIN comites_orientacion co ON co.id_miembro = i.responsable
            WHERE {donde} ORDER BY i.fecha DESC, i.id_incidente DESC""",
        "col_fecha": "i.fecha", "col_estado": "i.estado",
    },
    "compromisos": {
        "titulo": "Reporte de compromisos y cumplimiento",
        "columnas": [
            ("fecha", "Fecha"), ("estudiante", "Estudiante"), ("tipo", "Tipo de incidente"),
            ("nivel", "Nivel"), ("compromiso", "Compromiso"), ("fecha_limite", "Fecha límite"),
            ("estado", "Estado"), ("responsable", "Asignado por"), ("cumplimiento", "Cumplimiento (1-5)"),
        ],
        "sql": """
            SELECT c.fecha, e.nombre || ' ' || e.apellido AS estudiante, ti.nombre AS tipo,
                   np.nombre AS nivel, c.descripcion AS compromiso, c.fecha_limite, c.estado,
                   COALESCE(co.nombre, 'Sin asignar') AS responsable, s.cumplimiento
            FROM compromisos c
            INNER JOIN estudiantes e ON e.id_estudiante = c.id_estudiante
            INNER JOIN incidentes i ON i.id_incidente = c.id_incidente
            INNER JOIN tipos_incidente ti ON ti.id_tipo = i.id_tipo
            INNER JOIN nivel_protocolo np ON np.id_nivel = i.id_nivel
            LEFT JOIN comites_orientacion co ON co.id_miembro = c.asignado_por
            LEFT JOIN (SELECT id_compromiso, ROUND(AVG(nivel_cumplimiento), 1) AS cumplimiento
                       FROM seguimientos_compromisos WHERE estado <> 'inactivo'
                       GROUP BY id_compromiso) s ON s.id_compromiso = c.id_compromiso
            WHERE {donde} ORDER BY c.fecha DESC, c.id_compromiso DESC""",
        "col_fecha": "c.fecha", "col_estado": "c.estado",
    },
}


def tipos_disponibles():
    return [{"clave": k, "nombre": v["titulo"]} for k, v in TIPOS.items()]


def _texto(v):
    if v is None:
        return ""
    if isinstance(v, (date, datetime)):
        return v.strftime("%d/%m/%Y")
    return str(v)


def consultar(tipo, fecha_desde=None, fecha_hasta=None, id_tipo=None, id_nivel=None, estado=None):
    d = TIPOS.get(tipo)
    if not d:
        raise HTTPException(404, "Tipo de reporte no encontrado")
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        raise HTTPException(422, "La fecha 'desde' no puede ser posterior a la fecha 'hasta'")
    cond, params, textos = [f"{d['col_estado']} <> 'inactivo'"], [], []
    if fecha_desde:
        cond.append(f"{d['col_fecha']} >= %s"); params.append(fecha_desde); textos.append(f"desde {fecha_desde}")
    if fecha_hasta:
        cond.append(f"{d['col_fecha']} <= %s"); params.append(fecha_hasta); textos.append(f"hasta {fecha_hasta}")
    if id_tipo:
        cond.append("i.id_tipo = %s"); params.append(id_tipo); textos.append("tipo de incidente")
    if id_nivel:
        cond.append("i.id_nivel = %s"); params.append(id_nivel); textos.append("nivel")
    if estado:
        cond.append(f"{d['col_estado']} = %s"); params.append(estado); textos.append(f"estado {estado}")
    filas = ejecutar(d["sql"].format(donde=" AND ".join(cond)), tuple(params),
                     accion="generar el reporte", fetch="all")
    filas = [{k: _texto(v) for k, v in f.items()} for f in filas]
    return {
        "titulo": d["titulo"],
        "filtros": ", ".join(textos) if textos else "Sin filtros (todos los registros)",
        "total": len(filas),
        "columnas": [{"data": k, "title": t} for k, t in d["columnas"]],
        "filas": filas,
    }


def generar_pdf(reporte, autor):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas as lienzo
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    azul = colors.HexColor("#0d4a94")

    class Numerado(lienzo.Canvas):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._paginas = []

        def showPage(self):
            self._paginas.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            total = len(self._paginas)
            for estado in self._paginas:
                self.__dict__.update(estado)
                self.setFont("Helvetica", 8)
                self.setFillColor(colors.grey)
                self.drawCentredString(landscape(A4)[0] / 2, 0.8 * cm, f"Página {self._pageNumber} de {total}")
                super().showPage()
            super().save()

    def encabezado(c, doc):
        w, h = landscape(A4)
        c.setFillColor(azul)
        c.rect(0, h - 1.6 * cm, w, 1.6 * cm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1.5 * cm, h - 1.05 * cm, reporte["titulo"])

    est = getSampleStyleSheet()
    celda = ParagraphStyle("c", parent=est["Normal"], fontSize=7, leading=8.5)
    celda_h = ParagraphStyle("h", parent=celda, textColor=colors.white, fontName="Helvetica-Bold")
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1.2 * cm, rightMargin=1.2 * cm,
                            topMargin=2.2 * cm, bottomMargin=1.5 * cm, title=reporte["titulo"], author=autor)
    historia = [
        Paragraph(f"<b>Filtros aplicados:</b> {reporte['filtros']}", est["Normal"]),
        Paragraph(f"<b>Generado por:</b> {autor} · {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
                  f"<b>Total:</b> {reporte['total']} registro(s)", est["Normal"]),
        Spacer(1, 0.3 * cm),
    ]
    cols = reporte["columnas"]
    datos = [[Paragraph(c["title"], celda_h) for c in cols]]
    for f in reporte["filas"]:
        datos.append([Paragraph(f[c["data"]].replace("&", "&amp;").replace("<", "&lt;"), celda) for c in cols])
    ancho = (landscape(A4)[0] - 2.4 * cm) / len(cols)
    tabla = Table(datos, colWidths=[ancho] * len(cols), repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), azul),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3fa")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    historia.append(tabla)
    doc.build(historia, onFirstPage=encabezado, onLaterPages=encabezado, canvasmaker=Numerado)
    return buf.getvalue()


def generar_excel(reporte, autor):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"
    n = len(reporte["columnas"])
    ws["A1"] = reporte["titulo"]; ws["A1"].font = Font(bold=True, size=14, color="0D4A94")
    ws["A2"] = f"Filtros aplicados: {reporte['filtros']}"
    ws["A3"] = f"Generado por {autor} el {datetime.now().strftime('%d/%m/%Y %H:%M')} · Total: {reporte['total']}"
    for i, c in enumerate(reporte["columnas"], 1):
        celda = ws.cell(row=5, column=i, value=c["title"])
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="0D4A94")
    for r, f in enumerate(reporte["filas"], 6):
        for i, c in enumerate(reporte["columnas"], 1):
            celda = ws.cell(row=r, column=i, value=f[c["data"]])
            celda.alignment = Alignment(wrap_text=True, vertical="top")
            if r % 2 == 0:
                celda.fill = PatternFill("solid", fgColor="EEF3FA")
    for i in range(1, n + 1):
        ws.column_dimensions[ws.cell(row=5, column=i).column_letter].width = 18
    ws.freeze_panes = "A6"
    ws.page_setup.orientation = "landscape"
    ws.oddFooter.center.text = "Página &P de &N"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def generar(reporte, formato, autor):
    """Devuelve (bytes, nombre_archivo, mime)."""
    base = reporte["titulo"].lower().replace(" ", "_").replace("ó", "o").replace("í", "i")
    if formato == "pdf":
        return generar_pdf(reporte, autor), f"{base}.pdf", "application/pdf"
    if formato in ("excel", "xlsx"):
        return (generar_excel(reporte, autor), f"{base}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    raise HTTPException(422, "Formato no válido: usa pdf o excel")
