import json
from pathlib import Path
from app.db import run_select

status_cautat = "In Service"

sql = """
SELECT 
    b.id_masina,
    p.nume_marca,
    m.nume_model,
    b.numar_inmatriculare,
    b.vin,
    b.status
FROM Masini b
INNER JOIN Model m ON b.fk_model = m.id_model
INNER JOIN Marci p ON m.fk_marca = p.id_marca
WHERE b.status = %s AND b.isDeleted = FALSE AND p.isDeleted = FALSE AND m.isDeleted = FALSE
ORDER BY b.id_masina;
"""

rows = run_select(sql, (status_cautat,))

data = []
for i in rows:
    data.append({
        "id_masina": i[0],
        "marca": i[1],
        "model": i[2],
        "nr_inmatriculare": i[3],
        "vin": i[4],
        "status": i[5]
    })

out_path = Path("../outputs") / "Masini_In_Service.json"
out_path.parent.mkdir(exist_ok=True, parents=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

numar_comenzi = 3

sql = """
SELECT 
    dc.nume, 
    dc.prenume, 
    dc.email, 
    dc.numar_telefon,
    COUNT(c.id_comanda) AS Numar_Comenzi
FROM Date_Client dc
JOIN Cont_Client cc ON dc.fk_user = cc.id_user
JOIN Comanda c ON cc.id_user = c.fk_user
WHERE c.isDeleted = 0
GROUP BY dc.nume, dc.prenume
HAVING COUNT(c.id_comanda) >= %s
ORDER BY Numar_Comenzi DESC;
"""

rows = run_select(sql, (numar_comenzi,))

data = []
for i in rows:
    data.append({
        "Nume Client": i[0],
        "Prenume Client": i[1],
        "Email": i[2],
        "Numar Telefon": i[3],
        "Numar_Comenzi": i[4],
    })

out_path = Path("../outputs") / "Top 5 Clienti.json"
out_path.parent.mkdir(exist_ok=True, parents=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding="utf-8"
)
