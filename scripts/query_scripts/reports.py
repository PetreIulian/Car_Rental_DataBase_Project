import json
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from app.db import run_select

OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

LOGO_PATH = Path("scripts/logo_fiir.jpg")


def normalize(v):
    if isinstance(v, Decimal):
        x = float(v)
        return int(x) if x.is_integer() else x
    return v


def fetch_data(order_type="DESC"):
    sql = f"""
    SELECT ma.nume_marca, mo.nume_model, SUM(f.valoare_totala) AS venit_total
    FROM Marci ma
    JOIN Model mo ON ma.id_marca = mo.fk_marca
    JOIN Masini m ON mo.id_model = m.fk_model
    JOIN Raport_Comanda rc ON m.id_masina = rc.fk_masina
    JOIN Comanda c ON rc.fk_comanda = c.id_comanda
    JOIN Factura f ON c.id_comanda = f.fk_comanda
    WHERE f.isDeleted = FALSE AND m.isDeleted = FALSE
    GROUP BY ma.nume_marca, mo.nume_model
    ORDER BY venit_total {order_type};
    """
    rows = run_select(sql)
    return [{"label": f"{r[0]} {r[1]}", "venit_total": normalize(r[2])} for r in rows]


def export_data(data, base_name):
    csv_path = OUT_DIR / f"{base_name}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "venit_total"])
        writer.writeheader()
        writer.writerows(data)

    json_path = OUT_DIR / f"{base_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return csv_path, json_path


def generate_bar_chart(data, base_name, title, color):
    chart_path = OUT_DIR / f"{base_name}_chart.png"
    plot_data = data[:10]
    labels = [d["label"] for d in plot_data]
    values = [d["venit_total"] for d in plot_data]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=color)
    plt.title(title, fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Venit (RON)")

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, f"{round(yval, 2)}",
                 va='bottom', ha='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(str(chart_path))
    plt.close()
    return chart_path


def generate_pdf(data, base_name, title, intro, chart_path):
    pdf_path = OUT_DIR / f"{base_name}.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(title, styles["Heading1"]))
    elements.append(Paragraph(intro, styles["Normal"]))
    elements.append(Spacer(1, 15))

    table_data = [["Model Auto", "Venit (RON)"]]
    for d in data[:20]:
        table_data.append([d["label"], f"{d['venit_total']:,.2f}"])

    table = Table(table_data, colWidths=[300, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
    ]))
    elements.append(table)

    if chart_path and chart_path.exists():
        elements.append(Spacer(1, 25))
        elements.append(Image(str(chart_path), width=6 * inch, height=3.5 * inch))

    doc.build(elements)


def raport_1():
    data = fetch_data(order_type="DESC")
    if data:
        export_data(data, "Top_Vanzari")
        c_path = generate_bar_chart(data, "Top_Vanzari", "Top 10 Modele dupa Venituri", "#2ecc71")
        generate_pdf(data, "Raport_Top_Vanzari", "Raport Performanta: Top Vanzari",
                     "Analiza modelelor cu cele mai mari incasari inregistrate.", c_path)
        print("Raport 1 generat: PDF, CSV, JSON, Grafic")


def raport_2():
    data = fetch_data(order_type="ASC")
    if data:
        export_data(data, "Bottom_Vanzari")
        c_path = generate_bar_chart(data, "Bottom_Vanzari", "Modele cu cele mai mici venituri", "#e67e22")
        generate_pdf(data, "Raport_Bottom_Vanzari", "Raport Performanta: Venituri Minime",
                     "Analiza modelelor care au generat cele mai putine venituri.", c_path)
        print("Raport 2 generat: PDF, CSV, JSON, Grafic")


if __name__ == "__main__":
    raport_1()
    raport_2()