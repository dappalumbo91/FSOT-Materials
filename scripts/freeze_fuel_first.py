#!/usr/bin/env python3
"""Freeze the seven named FSOT fuels from the Lean hub PRED-034 panel.

Does not retune D1D38A. Does not copy unpublished hemp-grid variants.
Kill: changing centrals; stuffing gasoline as a designed fuel.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUB = Path(r"C:\Users\damia\Desktop\FSOT-2.1-Lean")
PIN_JSON = ROOT / "vendor" / "fsot_compute_AUTHORITY_PIN.json"
OUT = ROOT / "predictions" / "fuel_first_freeze.json"

KEEP = {
    "fsot_hemp_waste_grounded",
    "fsot_hemp_waste_advanced",
    "fsot_algae_oil_biodiesel",
    "fsot_mushroom_spore_fuel",
    "fsot_green_hydrogen",
    "fsot_optimax",
    "fsot_bio_spark",
}
AXES = {
    "lhv_kj_per_kg",
    "stoich_afr",
    "thermal_efficiency",
    "octane_rating",
    "density_kg_m3",
    "flame_speed_m_s",
    "bsfc_g_kwh",
}
PIN = "D1D38A185487B452E470AC68ECE2EB45AEB1CA9CE25FC9BF9564C19633FFBE70"


def main() -> int:
    cert = json.loads(PIN_JSON.read_text(encoding="utf-8"))
    sha = str(cert.get("authority_sha256") or "")
    if sha.upper() != PIN:
        print(f"FAIL pin {sha}", flush=True)
        return 1
    hub_panel = HUB / "data" / "fuel_lab_live_panel_benchmark.json"
    if not hub_panel.is_file():
        print(f"FAIL missing hub panel {hub_panel}", flush=True)
        return 1
    doc = json.loads(hub_panel.read_text(encoding="utf-8"))
    by: dict[str, dict] = {n: {} for n in KEEP}
    for r in doc.get("material_records") or []:
        n = str(r.get("name") or "")
        p = str(r.get("property") or "")
        if n in KEEP and p in AXES:
            by[n][p] = {
                "computed": r.get("computed"),
                "measured": r.get("measured"),
                "error_pct": r.get("error_pct"),
            }
    fuels = [{"name": n, "properties": by[n]} for n in sorted(KEEP)]
    out = {
        "pin": "D1D38A",
        "authority_sha256": sha,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_from": "FSOT-2.1-Lean data/fuel_lab_live_panel_benchmark.json",
        "hub_pred": "PRED-034",
        "object": "named_fuel_property_vector",
        "kill": "vector miss without retuning seed",
        "fuels": fuels,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    n_props = sum(len(f["properties"]) for f in fuels)
    print(f"Wrote {OUT}  fuels={len(fuels)} properties={n_props} pin={sha[:6]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
