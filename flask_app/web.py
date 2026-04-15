import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from app.db import run_select, run_execute

app = Flask(__name__)
app.secret_key = "dev-secret"


CRUD_CONFIG = {
    "Marci": {
        "pk": "id_marca",
        "title": "Mărci Auto",
        "create_fields": ["nume_marca"],
        "update_fields": ["nume_marca"],
        "list_fields": ["id_marca", "nume_marca"],
        "children": [{"table": "Model", "fk": "fk_marca"}],
    },
    "Model": {
        "pk": "id_model",
        "title": "Modele Auto",
        "create_fields": ["fk_marca", "nume_model"],
        "update_fields": ["nume_model"],
        "list_fields": ["id_model", "fk_marca", "nume_model"],
        "fk_dropdowns": {"fk_marca": ("Marci", "id_marca", "nume_marca")},
        "children": [{"table": "Masini", "fk": "fk_model"}],
    },
    "Masini": {
        "pk": "id_masina",
        "title": "Flotă Mașini",
        "create_fields": ["fk_model", "numar_inmatriculare", "vin", "status", "pret_inchiriere", "categorie_permis"],
        "update_fields": ["status", "pret_inchiriere"],
        "list_fields": ["id_masina", "numar_inmatriculare","vin", "status", "pret_inchiriere", "categorie_permis"],
        "choices": {"status": ["Disponibil", "Inchiriat", "In Service", "Rezervat"]},
        "fk_dropdowns": {"fk_model": ("Model", "id_model", "nume_model")},
        "children": [{"table": "Raport_Comanda", "fk": "fk_masina"}],
    },
    "Cont_Client": {
        "pk": "id_user",
        "title": "Conturi Utilizatori",
        "create_fields": ["username", "password"],
        "update_fields": ["username", "password"],
        "list_fields": ["id_user", "username"],
        "children": [
            {"table": "Date_Client", "fk": "fk_user"},
            {"table": "Comanda", "fk": "fk_user"}
        ],
    },
    "Date_Client": {
        "pk": "id_client",
        "title": "Date Identitate Clienți",
        "create_fields": ["fk_user", "nume", "prenume", "numar_telefon", "adresa", "email", "permis_conducere", "cui"],
        "update_fields": ["nume", "prenume", "numar_telefon", "adresa", "email", "cui", "permis_conducere"],
        "list_fields": ["id_client", "nume", "prenume","numar_telefon", "adresa", "email", "permis_conducere"],
        "fk_dropdowns": {"fk_user": ("Cont_Client", "id_user", "username")},
        "children": [{"table": "Factura", "fk": "fk_client"}],
    },
    "Comanda": {
        "pk": "id_comanda",
        "title": "Comenzi / Rezervări",
        "create_fields": ["fk_user", "status_plata"],
        "update_fields": ["status_plata"],
        "list_fields": ["id_comanda", "fk_user", "status_plata", "data_comanda"],
        "choices": {"status_plata": ["Platita", "In curs", "Neplatita"]},
        "fk_dropdowns": {"fk_user": ("Cont_Client", "id_user", "username")},
        "children": [
            {"table": "Raport_Comanda", "fk": "fk_comanda"},
            {"table": "Factura", "fk": "fk_comanda"}
        ],
    },
    "Raport_Comanda": {
        "pk": "id_raport",
        "title": "Alocări Mașini pe Comenzi",
        "create_fields": ["fk_comanda", "fk_masina", "data_predare", "data_returnare"],
        "update_fields": ["data_predare", "data_returnare"],
        "list_fields": ["id_raport", "fk_comanda", "fk_masina", "data_predare"],
        "fk_dropdowns": {
            "fk_comanda": ("Comanda", "id_comanda", "id_comanda"),
            "fk_masina": ("Masini", "id_masina", "numar_inmatriculare")
        },
        "children": [
            {"table": "Raport_Predare", "fk": "fk_raport_comanda"},
            {"table": "Raport_Primire", "fk": "fk_raport_comanda"}
        ],
    },
    "Factura": {
        "pk": "id_factura",
        "title": "Facturare",
        "create_fields": ["fk_comanda", "fk_client", "serie", "numar", "valoare_neta", "valoare_tva", "valoare_totala", "status_factura"],
        "update_fields": ["status_factura"],
        "list_fields": ["id_factura", "serie", "numar", "valoare_totala", "status_factura"],
        "choices": {"status_factura": ["Emisa", "Platit", "Neplatit", "Anulat"]},
        "fk_dropdowns": {
            "fk_comanda": ("Comanda", "id_comanda", "id_comanda"),
            "fk_client": ("Date_Client", "id_client", "nume")
        },
        "children": [{"table": "Plata", "fk": "fk_factura"}],
    },
    "Plata": {
        "pk": "id_plata",
        "title": "Plăți Efectuate",
        "create_fields": ["fk_factura", "data_plata", "suma_plata", "metoda_plata", "id_tranzactie_bancara"],
        "update_fields": ["id_tranzactie_bancara"],
        "list_fields": ["id_plata", "fk_factura", "suma_plata", "data_plata", "metoda_plata", "id_tranzactie_bancara"],
        "fk_dropdowns": {"fk_factura": ("Factura", "id_factura", "numar")},
    },
    "Raport_Predare": {
        "pk": "id_raport_predare",
        "title": "Raport Predare (KM/Daune)",
        "create_fields": ["fk_raport_comanda", "numar_kilometrii", "daune"],
        "update_fields": ["daune"],
        "list_fields": ["id_raport_predare", "fk_raport_comanda", "numar_kilometrii", "daune"],
        "fk_dropdowns": {"fk_raport_comanda": ("Raport_Comanda", "id_raport", "id_raport")},
    },
    "Raport_Primire": {
        "pk": "id_raport_primire",
        "title": "Raport Primire (KM/Daune)",
        "create_fields": ["fk_raport_comanda", "numar_kilometrii", "daune"],
        "update_fields": ["daune"],
        "list_fields": ["id_raport_primire", "fk_raport_comanda", "numar_kilometrii", "daune"],
        "fk_dropdowns": {"fk_raport_comanda": ("Raport_Comanda", "id_raport", "id_raport")},
    },
    "Logs": {
        "pk": "id_log",
        "title": "Jurnal Activitate (Logs)",
        "create_fields": ["tabel_vizat", "camp_vizat", "modificare"],
        "update_fields": [],
        "list_fields": ["id_log", "tabel_vizat", "modificare", "data_log"],
        "default_sort": "id_log DESC",
    }
}

def ensure_table_allowed(table):
    if table not in CRUD_CONFIG:
        abort(404)
    return CRUD_CONFIG[table]


def has_any_user():
    try:
        rows = run_select("SELECT id_user FROM Cont_Client WHERE isDeleted = 0 LIMIT 1;")
        return bool(rows)
    except Exception:
        return False

def record_exists(table, field, value):
    ensure_table_allowed(table)
    q = f"SELECT 1 FROM {table} WHERE {field}=%s AND isDeleted = 0 LIMIT 1;"
    return bool(run_select(q, (value,)))


def fetch_list(table):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]

    q = f"SELECT {', '.join(cols)} FROM {table} WHERE isDeleted = 0 ORDER BY {cfg.get('default_sort', pk + ' ASC')};"
    rows = run_select(q)
    return cols, rows


def fetch_by_id(table, rec_id):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} WHERE {pk}=%s AND isDeleted = 0 LIMIT 1;"
    rows = run_select(q, (rec_id,))
    return cols, (rows[0] if rows else None)


def build_fk_options(cfg):
    options = {}
    for field, spec in cfg.get("fk_dropdowns", {}).items():
        parent_table, parent_pk, label_col = spec
        rows = run_select(
            f"SELECT {parent_pk}, {label_col} FROM {parent_table} WHERE isDeleted = 0 ORDER BY {parent_pk} ASC;"
        )
        options[field] = [(str(r[0]), str(r[1])) for r in rows]
    return options


def insert_record(table, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["create_fields"]

    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Camp obligatoriu lipsa: {f}")
        values.append(v)

    for f, v in zip(fields, values):
        if f.endswith("_id") and "fk_dropdowns" in cfg and f in cfg["fk_dropdowns"]:
            parent_table, parent_pk, _label = cfg["fk_dropdowns"][f]
            if not record_exists(parent_table, parent_pk, v):
                raise ValueError(f"Valoare invalida pentru {f} (nu exista in {parent_table}).")

    cols = ", ".join(fields)
    placeholders = ", ".join(["%s"] * len(fields))
    q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders});"
    run_execute(q, tuple(values))


def update_record(table, rec_id, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["update_fields"]
    if not fields:
        raise ValueError("Acest tabel nu are UPDATE in template.")

    pairs = []
    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Camp obligatoriu lipsa: {f}")
        pairs.append(f"{f}=%s")
        values.append(v)

    values.append(rec_id)
    q = f"UPDATE {table} SET {', '.join(pairs)} WHERE {cfg['pk']}=%s;"
    run_execute(q, tuple(values))


def delete_record_safe(table, rec_id):
    cfg = ensure_table_allowed(table)
    q = f"UPDATE {table} SET isDeleted = TRUE WHERE {cfg['pk']} = %s;"
    run_execute(q, (rec_id,))

@app.before_request
def guard_if_no_users():
    allowed = {"/", "/setup", "/seed-admin", "/search"}
    if request.path.startswith("/static/"):
        return
    if not has_any_user() and request.path not in allowed:
        return redirect(url_for("setup_required"))


@app.route("/")
def index():
    counts = {}
    ready = has_any_user()
    for t in CRUD_CONFIG.keys():
        try:
            counts[t] = run_select(f"SELECT COUNT(*) FROM {t} WHERE isDeleted = 0;")[0][0] if ready else 0
        except Exception:
            counts[t] = 0
    return render_template("index.html", site_cfg=CRUD_CONFIG, counts=counts, ready=ready)


@app.route("/setup")
def setup_required():
    return render_template("setup_required.html", site_cfg=CRUD_CONFIG)


@app.route("/seed-admin")
def seed_admin():
    if has_any_user():
        flash("Exista deja utilizatori.", "info")
        return redirect(url_for("crud_list", table="Cont_Client"))
    run_execute("INSERT INTO Cont_Client (username, password) VALUES (%s, %s);", ("admin", "hash_admin"))
    flash("Admin demo creat.", "success")
    return redirect(url_for("crud_list", table="Cont_Client"))


@app.route("/crud/<table>")
def crud_list(table):
    cfg = ensure_table_allowed(table)
    cols, rows = fetch_list(table)
    return render_template(
        "crud_list.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        cols=cols,
        rows=rows,
    )


@app.route("/crud/<table>/create", methods=["GET", "POST"])
def crud_create(table):
    cfg = ensure_table_allowed(table)
    fk_options = build_fk_options(cfg)

    if request.method == "POST":
        try:
            insert_record(table, request.form)
            flash("Creat cu succes.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")

    return render_template(
        "crud_form.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        mode="create",
        fields=cfg["create_fields"],
        values={},
        fk_options=fk_options,
        choices=cfg.get("choices", {}),
    )


@app.route("/crud/<table>/edit/<int:rec_id>", methods=["GET", "POST"])
def crud_edit(table, rec_id):
    cfg = ensure_table_allowed(table)
    cols, row = fetch_by_id(table, rec_id)
    if not row:
        abort(404)

    values = dict(zip(cols, row))
    fk_options = build_fk_options(cfg)

    if request.method == "POST":
        try:
            update_record(table, rec_id, request.form)
            flash("Update reusit.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")

    return render_template(
        "crud_form.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        mode="edit",
        fields=cfg["update_fields"],
        values=values,
        fk_options=fk_options,
        choices=cfg.get("choices", {}),
        rec_id=rec_id,
    )


@app.route("/crud/<table>/delete/<int:rec_id>", methods=["POST"])
def crud_delete(table, rec_id):
    ensure_table_allowed(table)
    try:
        delete_record_safe(table, rec_id)
        flash("Sters cu succes!", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("crud_list", table=table))


@app.route("/search", methods=["GET", "POST"])
def search():
    result = None
    if request.method == "POST":
        table = (request.form.get("table") or "").strip()
        field = (request.form.get("field") or "").strip()
        value = (request.form.get("value") or "").strip()
        try:
            ensure_table_allowed(table)
            exists = record_exists(table, field, value)
            result = {"ok": True, "exists": exists, "table": table, "field": field, "value": value}
        except Exception as e:
            result = {"ok": False, "error": str(e)}

    return render_template("search.html", site_cfg=CRUD_CONFIG, result=result)


if __name__ == "__main__":
    app.run(debug=True)
