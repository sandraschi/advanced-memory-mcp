# Data Products, Archives & Mission Planning

**Confidence**: 🟢 HIGH  
**Last updated**: 2025-11-09  
**Primary references**: [Webb-ESA-2025], [Euclid-ESA-2025]

## Core archives
- **MAST (STScI)** – JWST, HST, TESS, Kepler, GALEX datasets with APIs for bulk download and cloud-native analysis.  
- **ESA Science Archives** – Euclid Science Archive (ESA), Solar Orbiter archive, CHEOPS data centre.  
- **ESO Science Portal** – VLT, ALMA, survey data (e.g., VISTA, MUSE).  
- **NASA/IPAC** – IRSA (Spitzer, WISE), NED, Exoplanet Archive.  
- **LIGO Open Science Center** – GW strain data, parameter estimation samples, tutorials.

## Mission planning essentials
| Step | Details |
| --- | --- |
| Proposal cycle awareness | JWST Cycle 4 (deadline April 2025), ESO Period 116, NASA ROSES cadence. |
| Tools | APT for JWST, ESA pNTAC for Euclid GO programmes, ESO p2 for VLT. |
| Observation constraints | Sun avoidance angles, guide-star availability, roll constraints, scheduling flexibility. |
| Calibration | Reference calibration plans (dark frames, flats, spectrophotometric standards). |

## Data handling tips
- Prefer programmatic access (astroquery, pyVO) for reproducibility.  
- Track calibration versioning (JWST CRDS context, Euclid pipeline release).  
- Use cloud/VM options (MAST Notebook, ESA Datalabs) for large datasets.  
- Document DOIs when publishing derived products; many archives auto-mint DOIs for datasets.

## Assistant reminders
1. When advising on proposals, mention **time allocation committees**, required templates, and review criteria.  
2. For data questions, supply **specific archive URLs** and note proprietary periods.  
3. Encourage use of **citizen-science** portals (Galaxy Zoo, Euclid Galaxy Zoo) for classification-heavy projects.  
4. Emphasise **data provenance**: cite observation IDs, pipeline versions, and processing scripts.  
5. Reference `known-gaps.md` if proposed analysis touches uncalibrated or controversial regimes.

## Quick reference
- Euclid early release data (ERD): public March 2025 with value-added catalogues.  
- JWST proprietary period standard: 12 months (shorter for some GO programs, zero for ERS).  
- LIGO open alerts issued in O4 with community follow-up guidelines hosted on SCiMMA/Treasure Map.

