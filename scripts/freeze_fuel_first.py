#!/usr/bin/env python3
"""Freeze the seven named FSOT fuels from the Lean hub PRED-034 panel.

Does not retune D1D38A. Does not copy unpublished hemp-grid variants.
Kill: changing centrals; stuffing gasoline as a designed fuel.

The values are copied from the Lean panel. The output records where they came
from: Lean commit, Lean compute pin in effect there, the panel commits, and the
Ledger B terms (S, f) read from Lean's own code, so the numbers are never
attributed to Materials' local pin.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# FSOT-2.1-Lean checkout: $FSOT_2_1_LEAN_ROOT, else a sibling clone next to this repo
HUB = Path(os.environ.get("FSOT_2_1_LEAN_ROOT", "").strip() or (ROOT.parent / "FSOT-2.1-Lean"))
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
PANEL_REL = "data/fuel_lab_live_panel_benchmark.json"
FORMULA = "computed = measured * (1 + |S|*f)"


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(HUB), *args], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def _keep_values(doc: dict) -> dict:
    out = {}
    for r in doc.get("material_records") or []:
        n, p = str(r.get("name") or ""), str(r.get("property") or "")
        if n in KEEP and p in AXES:
            out[(n, p)] = (r.get("computed"), r.get("measured"))
    return out


def _panel_values_commit(current: dict) -> str:
    """Oldest commit in the newest unbroken run whose panel gives these KEEP values."""
    found = ""
    for c in _git("log", "--format=%H", "--", PANEL_REL).splitlines():
        try:
            blob = subprocess.run(
                ["git", "-C", str(HUB), "show", f"{c}:{PANEL_REL}"],
                capture_output=True, text=True, check=True,
            ).stdout
            if _keep_values(json.loads(blob)) != current:
                break
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            break
        found = c
    return found


def _lean_pin() -> dict:
    pin = {}
    pin_path = HUB / "vendor" / "fsot_compute_AUTHORITY_PIN.json"
    if pin_path.is_file():
        pin = json.loads(pin_path.read_text(encoding="utf-8"))
    compute = HUB / "vendor" / "fsot_compute.py"
    actual = hashlib.sha256(compute.read_bytes()).hexdigest().upper() if compute.is_file() else ""
    want = str(pin.get("authority_sha256") or "").upper()
    return {
        "pin_prefix": pin.get("pin_prefix") or want[:6],
        "authority_sha256": want,
        "compute_file_sha256": actual,
        "compute_matches_pin": bool(want) and actual == want,
        "pin_file": "vendor/fsot_compute_AUTHORITY_PIN.json",
        "lineage_doc": "docs/PIN_LINEAGE.md",
        "decimal_knob_pin": pin.get("decimal_knob_pin"),
    }


def _ledger_b_terms(records: list[dict]) -> dict:
    """S per domain and f, from Lean's own code (fsot_api_predict_lib)."""
    sys.path[:0] = [str(HUB / "scripts"), str(HUB / "vendor")]
    import fsot_api_predict_lib as lib  # type: ignore

    domains = sorted({str(r.get("fsot_domain") or "") for r in records})
    terms = {}
    for d in domains:
        terms[d] = {
            "S": float(lib.domain_scalar(d)),
            "f": float(lib.domain_modulation_factor(d)),
        }
    mod = lib.load_authority()[0]
    alpha = float(mod.ALPHA)
    # Every record must reproduce from these terms (to the panel's 6-dp rounding).
    worst = 0.0
    for r in records:
        t = terms[str(r.get("fsot_domain") or "")]
        m = float(r["measured"])
        c = m * (1.0 + abs(t["S"]) * t["f"])
        worst = max(worst, abs(c - float(r["computed"])) / max(abs(m), 1e-300))
    return {
        "formula": FORMULA,
        "f_source": "Lean scripts/fsot_api_predict_lib.py domain_modulation_factor -> fsot_compute.ALPHA",
        "S_source": "Lean scripts/fsot_api_predict_lib.py domain_scalar -> fsot_canonical_adapter",
        "ALPHA": alpha,
        "by_domain": terms,
        "max_rel_reproduction_residual": worst,
    }


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
    kept: list[dict] = []
    for r in doc.get("material_records") or []:
        n = str(r.get("name") or "")
        p = str(r.get("property") or "")
        if n in KEEP and p in AXES:
            kept.append(r)
            by[n][p] = {
                "computed": r.get("computed"),
                "measured": r.get("measured"),
                "error_pct": r.get("error_pct"),
            }
    fuels = [{"name": n, "properties": by[n]} for n in sorted(KEEP)]
    lean_pin = _lean_pin()
    terms = _ledger_b_terms(kept)
    thermo = terms["by_domain"].get("Thermodynamics", {})
    out = {
        "pin": "D1D38A",
        "pin_scope": "Materials local authority pin (vendor/fsot_compute_AUTHORITY_PIN.json); "
        "NOT the compute that produced these values",
        "authority_sha256": sha,
        "pin_note": "Materials' own authority pin stays D1D38A pending Damian's pin finalization. "
        "The values below were computed by FSOT-2.1-Lean under the Lean compute pin recorded in "
        "provenance.lean_compute_pin (see Lean docs/PIN_LINEAGE.md).",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_from": "FSOT-2.1-Lean data/fuel_lab_live_panel_benchmark.json",
        "provenance": {
            "lean_repo": "https://github.com/dappalumbo91/FSOT-2.1-Lean",
            "lean_commit": _git("rev-parse", "HEAD"),
            "lean_compute_pin": lean_pin,
            "panel_file": PANEL_REL,
            "panel_last_commit": _git("log", "-1", "--format=%H", "--", PANEL_REL),
            "panel_values_last_changed_commit": _panel_values_commit(_keep_values(doc)),
            "panel_generated_at": doc.get("generated_at"),
            "formula": FORMULA,
            "S_thermo": thermo.get("S"),
            "f": thermo.get("f"),
            "f_is_ALPHA": thermo.get("f") == terms["ALPHA"],
            "ledger_b": terms,
        },
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
