import json
from pathlib import Path
from app.db import run_select

sql = """
SELECT 
    ma.nume_marca, 
    mo.nume_model,
    SUM(f.valoare_totala) AS venit_total
FROM Marci ma
JOIN Model mo ON ma.id_marca = mo.fk_marca
JOIN Masini m ON mo.id_model = m.fk_model
JOIN Raport_Comanda rc ON m.id_masina = rc.fk_masina
JOIN Comanda c ON rc.fk_comanda = c.id_comanda
JOIN Factura f ON c.id_comanda = f.fk_comanda
WHERE f.isDeleted = FALSE AND m.isDeleted = FALSE
GROUP BY mo.nume_model
ORDER BY venit_total DESC
LIMIT 10;
"""

rows = run_select(sql)

data = []
for row in rows:
    data.append({
        "marca": row[0],
        "model": row[1],
        "venit_total": str(float(row[2])) + " RON"
    })

out_path = Path("../outputs") / "Top_Venituri_Masini.json"
out_path.parent.mkdir(exist_ok=True, parents=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON salvat cu succes în: {out_path} ({len(data)} înregistrări)")