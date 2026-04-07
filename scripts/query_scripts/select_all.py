import json
from pathlib import Path
from app.db import run_select

sql = """
SELECT
    m.id_masina,
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
    print(i)
    data.append({
        "nume_marca": i[1],
        "nume_model": i[2],
        "numar_inmatriculare": i[3],
        "categorie_permis": i[4]
    })

out_path = Path("../outputs") / "Marci_si_Modele.json"
out_path.parent.mkdir(exist_ok=True, parents=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"JSON salvat cu succes în: {out_path}")