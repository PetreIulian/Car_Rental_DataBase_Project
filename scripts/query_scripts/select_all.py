import json
from pathlib import Path
from app.db import run_select

sql = """
SELECT 
    o.nume_marca, 
    n.nume_model, 
    COUNT(m.id_masina) AS numar_masini_disponibile
FROM Masini m
INNER JOIN Model n ON m.fk_model = n.id_model
INNER JOIN Marci o ON n.fk_marca = o.id_marca
WHERE m.isDeleted = FALSE AND n.isDeleted = FALSE AND o.isDeleted = FALSE AND m.status = 'Disponibil'
GROUP BY o.nume_marca, n.nume_model
ORDER BY m.id_masina
"""

rows = run_select(sql)

data = []
for i in rows:
    data.append({
        "nume_marca": i[0],
        "nume_model": i[1],
        "numar_masini_disponibile": i[2],
    })

out_path = Path("../outputs") / "Masini_Disponibile.json"
out_path.parent.mkdir(exist_ok=True, parents=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON salvat cu succes în: {out_path}")

sql = """
SELECT
    o.nume_marca,
    n.nume_model,
    m.numar_inmatriculare,
    m.categorie_permis
FROM Masini m
INNER JOIN Model n ON m.fk_model = n.id_model
INNER JOIN Marci o ON n.fk_marca = o.id_marca
WHERE m.isDeleted = FALSE AND o.isDeleted = FALSE AND n.isDeleted = FALSE
ORDER BY m.id_masina
"""

rows = run_select(sql)

data = []
for i in rows:
    data.append({
        "nume_marca": i[0],
        "nume_model": i[1],
        "numar_inmatriculare": i[2],
        "categorie_permis": i[3],
    })

out_path = Path("../outputs") / "Marci_si_Modele.json"
out_path.parent.mkdir(exist_ok=True, parents=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON salvat cu succes în: {out_path}")