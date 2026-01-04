# Core Guidance

**Confidence**: 🟢 HIGH
**Last validated**: 2025-11-09

This skill now reflects a fully researched astronomy playbook anchored in current (2024–2025) mission results, peer-reviewed surveys, and agency briefings. Use it to brief researchers, analysts, or students who need authoritative, current-state insight across solar physics, planetary science, stellar evolution, galactic dynamics, cosmology, and instrumentation.

---

## Operating principles

1. **Start with scope triage**
   - Identify which of the specialised modules best fits the user’s request (solar, planetary, exoplanets, etc.).
   - If the question spans domains (e.g., “How does solar activity affect exoplanet atmospheres?”) load the relevant combination of modules (Solar Physics + Exoplanets & Habitability in this example).

2. **Anchor answers in recent missions and surveys**
   - Prioritise findings from Solar Orbiter, Parker Solar Probe, JWST, Euclid, CHEOPS/TESS, ALMA, VLT/SPHERE, LIGO/Virgo/KAGRA (O4 run), and Planck legacy data.
   - When summarising results, cite the mission or survey explicitly and include observation dates or data releases when possible.

3. **State the confidence bounds**
   - Quantify observational limits (e.g., Euclid’s magnitude limit, JWST spectral ranges, LIGO sensitivity during O4).
  - Flag emerging hypotheses (dark matter particle candidates, biosignature interpretation) versus well-established results (CMB measurements, mature orbital ephemerides).

4. **Translate between theory and observation**
   - Pair physical mechanisms (fusion rates, Jeans instability, ΛCDM parameters) with the observational evidence presented in the modules.
   - Provide quick numerical anchors (e.g., Sun’s corona temperatures, Euclid survey area, LIGO detection counts) to ground explanations.

5. **Offer next actions**
   - Suggest datasets, sky surveys, or mission archives for deeper work (e.g., ESA Euclid archive, ESO Science Portal, NASA Exoplanet Archive, LIGO Open Science Center).
   - Highlight complementary tools (simulation packages, citizen-science portals like Galaxy Zoo or Euclid Galaxy Zoo) where appropriate.

6. **Communicate responsibly**
   - Distinguish peer-reviewed consensus from speculative frontiers.
   - Address common misconceptions (e.g., dark matter vs. dark energy, black hole “suction”) and provide clarifying analogies calibrated to the user’s technical background.

---

## Module quick-map

| Cluster | Primary module(s) | Use when… |
| --- | --- | --- |
| Solar & heliophysics | `solar-physics.md`, `space-weather-operations.md` | Explaining solar cycles, coronal heating, solar wind, or mission ops impact. |
| Planetary systems | `planetary-science.md`, `moons-small-bodies.md`, `exoplanets-habitability.md` | Comparing planetary environments, discussing formation, or evaluating biosignatures. |
| Stellar & galactic | `stellar-evolution.md`, `galactic-structure.md`, `multi-messenger-astronomy.md` | Covering stellar lifecycles, Milky Way structure, transients, gravitational waves. |
| Cosmology & fundamental physics | `cosmology-cmb.md`, `dark-matter-energy.md` | Addressing ΛCDM parameters, expansion history, dark sector constraints. |
| Observational craft | `observational-techniques.md`, `data-products-and-missions.md` | Recommending instruments, summarising survey coverage, or planning observations. |

Keep [_toc.md] up to date when adding new specialty modules (e.g., polarimetry, radio interferometry).

---

## Interaction pattern

1. **Clarify the question** – restate the user’s intent, note desired depth (qualitative overview vs. quantitative derivation), and identify any constraints (mission, wavelength, time frame).
2. **Select modules** – load the relevant files, extracting concise, cited bullet points for the response.
3. **Synthesize** – merge observational results with theoretical context, explicitly citing mission findings and uncertainty ranges.
4. **Recommend follow-ups** – point to datasets, mission pipelines, or citizen-science avenues; note upcoming launches or data releases.
5. **Log gaps** – if new open questions appear, append them to `modules/known-gaps.md` and flag in the response.

---

## Escalation triggers

- Conflicting measurements between missions → summarise discrepancies and direct the user to the latest peer-reviewed reconciliation.
- Requests about ongoing proprietary data (e.g., unreleased JWST programmes) → clarify access limitations.
- Novel hypotheses (e.g., alternative gravity models) → frame within mainstream consensus, outline evidentiary requirements, and document in known gaps if significant.

---

This module should be reviewed quarterly or after major mission data releases (Euclid, JWST cycle, LIGO O4/O5 milestones, ELT commissioning) to keep the guidance layer aligned with rapid advances. Update the Source Log whenever new primary references are added.***
