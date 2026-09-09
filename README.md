# FSOT-Materials

**Forward design lab** for fuels and synthetic lattices under Fluid Space-Time Omni Theory (FSOT).  
Zero free parameters. Pin **D1D38A**. Not a residual-catalog headline.

| | |
|--|--|
| **Mathematical hub** | [FSOT-2.1-Lean](https://github.com/dappalumbo91/FSOT-2.1-Lean) |
| **Authority pin** | `D1D38A` (`vendor/fsot_compute.py` in the hub) |
| **Scalar law** | \(S = K(T_1+T_2+T_3)\) |
| **Hub residual lock** | PRED-034 fuel-lab panel (366 rec, 0.039%) — **this repo does not retune that lock** |
| **This repo’s object** | Named candidate **property vectors**, frozen before sim/lab |

Same pattern as [FSOT-Genetics](https://github.com/dappalumbo91/FSOT-Genetics): product freeze lives here; the Lean hub quotes it.

---

## What this is

Chemistry / Materials / Thermo folds already green in the hub are **table matching**. This sibling is **design**:

1. Propose a molecule or fuel path that does not have to pre-exist in CRC.
2. Freeze the predicted property vector (LHV, \(T_b\), density, stoich AFR, thermal efficiency, …).
3. Simulate or wet-lab it.
4. Kill = the freeze misses **without** retuning the seed.

Two campaigns, one pin:

| Campaign | First freeze | Not |
|----------|--------------|-----|
| **Fuels** | Seven FSOT-designed fuels vs thermochemistry + engine sim | Beating a dyno as a 0.5% central; stuffing gasoline CRC as a new fuel |
| **Materials** | Lattice / metamaterial class (next) | A fitted EOS; one ε per crystal |

---

## First fuel freeze (quoted from hub PRED-034)

Named fuels (not the hemp combinatorial grid, not gasoline baseline):

- `fsot_hemp_waste_grounded`
- `fsot_hemp_waste_advanced`
- `fsot_algae_oil_biodiesel`
- `fsot_mushroom_spore_fuel`
- `fsot_green_hydrogen`
- `fsot_optimax`
- `fsot_bio_spark`

Property axes: `lhv_kj_per_kg`, `stoich_afr`, `thermal_efficiency`, `octane_rating`, `density_kg_m3`, `flame_speed_m_s`, `bsfc_g_kwh`.

Machine: [`predictions/fuel_first_freeze.json`](predictions/fuel_first_freeze.json)  
Kill objects: [`docs/KILL_OBJECTS.md`](docs/KILL_OBJECTS.md)

Hub PRED-034 stays the **residual** quote. A new candidate that is not in that panel is a **design** freeze here.

---

## Pin

Do not copy a second `fsot_compute.py` and drift it. Point at the hub pin:

```
SHA-256 D1D38A185487B452E470AC68ECE2EB45AEB1CA9CE25FC9BF9564C19633FFBE70
```

Certificate: `vendor/fsot_compute_AUTHORITY_PIN.json`.

---

## Explicitly not

- Rewriting PRED-034 after a miss
- A 477-domain headline
- Cold fusion / transporter as this product
- Clock-time of the next fuel-price move
