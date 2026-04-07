import time
import statistics
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scripts.table_magement_scripts.add_indexes import apply_indexes
from app.db import run_select, run_execute

root_path = str(Path(__file__).parent.parent.parent)

RUNS = 2000
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_FILE = OUTPUT_DIR / "performance_report.txt"
CHART_FILE = OUTPUT_DIR / "performance_chart.png"

DROP_LIST = [
    ("idx_vin_masini", "Masini"),
    ("idx_numar_status", "Masini"),
    ("idx_username", "Cont_Client"),
    ("idx_data_factura", "Factura"),
    ("idx_masini_model", "Masini"),
    ("idx_model_marca", "Model"),
    ("idx_raport_comanda", "Raport_Comanda"),
    ("idx_plata_factura", "Plata"),
    ("idx_client_nume_complet", "Date_Client")
]

TEST_QUERIES = [
    {
        "name": "Căutare VIN",
        "sql": "SELECT * FROM Masini WHERE vin = %s;",
        "params": ("7NTMC6NV0WZ4Y2450",),
    },
    {
        "name": "Login Username",
        "sql": "SELECT * FROM Cont_Client WHERE username = %s;",
        "params": ("lucian.ioniță9983",),
    },
    {
        "name": "Căutare Nume Client",
        "sql": "SELECT * FROM Date_Client WHERE nume = %s AND prenume = %s;",
        "params": ("Mocanu", "Florin"),
    },
    {
        "name": "Status Masina",
        "sql": "SELECT * FROM Masini WHERE status = %s;",
        "params":("In Service",)
    },
    {
        "name": "Cautare Factura dupa Data",
        "sql": "SELECT * FROM Factura WHERE data_emitere = %s",
        "params":("2024-10-03 00:00:00",)
    },
]

def drop_all():
    print("Curățăm indexii existenți...")
    for idx, table in DROP_LIST:
        try:
            run_execute(f"DROP INDEX {idx} ON {table};")
        except:
            pass

def benchmark_query(sql, params, runs):
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        run_select(sql, params)
        times.append((time.perf_counter() - start) * 1000)
    return times

def summarize(times):
    avg = statistics.mean(times)
    mn = min(times)
    mx = max(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    return {"avg": avg, "min": mn, "max": mx, "std": std}

def run_suite(label: str):
    results = {}
    for q in TEST_QUERIES:
        times = benchmark_query(q["sql"], q["params"], RUNS)
        results[q["name"]] = summarize(times)
        print(f"[{label}] {q['name']} -> avg {results[q['name']]['avg']:.2f} ms")
    return results

def pct_change(before, after):
    if before <= 0: return 0.0
    return ((before - after) / before) * 100.0

def generate_chart(before_results, after_results):
    labels = list(before_results.keys())
    before_means = [before_results[name]["avg"] for name in labels]
    after_means = [after_results[name]["avg"] for name in labels]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width / 2, before_means, width, label='Înainte de Index', color='#e74c3c')
    rects2 = ax.bar(x + width / 2, after_means, width, label='După Index', color='#2ecc71')

    ax.set_ylabel('Timp mediu (ms)')
    ax.set_title('Impactul Indexării asupra Performanței Query-urilor')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    ax.bar_label(rects1, padding=3, fmt='%.2f')
    ax.bar_label(rects2, padding=3, fmt='%.2f')

    fig.tight_layout()
    plt.savefig(CHART_FILE)
    print(f"Grafic salvat în: {CHART_FILE}")

def main():
    lines = []
    lines.append("=== ANALIZA PERFORMANTA SQL (BEFORE vs AFTER) ===\n")
    lines.append(f"Rulari per query: {RUNS}\n")

    drop_all()

    print("Rulăm testele FĂRĂ indexi...")
    before = run_suite("BEFORE")

    print("\nAplicăm indexurile din scriptul de management...")
    apply_indexes()

    print("\nRulăm testele CU indexi...")
    after = run_suite("AFTER")

    for name, m in before.items():
        lines.append(f"Query: {name} (BEFORE) -> AVG: {m['avg']:.2f} ms")

    lines.append("-" * 30)

    for name, m in after.items():
        improvement = pct_change(before[name]["avg"], m["avg"])
        lines.append(f"Query: {name} (AFTER) -> AVG: {m['avg']:.2f} ms | Improvement: {improvement:.1f}%")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nRaport text salvat în: {REPORT_FILE}")

    generate_chart(before, after)

if __name__ == "__main__":
    main()