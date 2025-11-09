# Space Weather Operations & Risk Mitigation

**Confidence**: 🟢 HIGH  
**Last updated**: 2025-11-09  
**Primary references**: [SO-ESA-2025]

## Operational posture
- **Observation assets**: Solar Orbiter, Parker Solar Probe, DSCOVR, and ground-based magnetometers provide continuous coverage. Emphasise multi-point triangulation—off-Sun-Earth line imaging reduces occultation gaps.  
- **Forecast horizons**:  
  - **Minutes to hours**: L1 monitors (DSCOVR, ACE) deliver near-real-time solar wind & IMF data.  
  - **Hours to days**: CME kinematics from heliospheric imagers (Solar Orbiter SoloHI) feed drag-based models.  
  - **Days to weeks**: Helioseismic farside imaging (SDO/HMI) and magnetofrictional models hint at emerging active regions.

## Recommended workflow
1. **Event detection** – identify flare/CME signatures (GOES soft X-ray flux, coronagraph halo, radio bursts).  
2. **Propagation modelling** – run ensemble drag-based or ENLIL simulations; provide centroid ETA with ±σ.  
3. **Impact assessment** – translate predicted solar wind parameters into geomagnetic indices, radiation dose rates, HF communication blackouts.  
4. **Mitigation guidance** – articulate clear protective actions (satellite safe-mode, GNSS error budgeting, power grid load balancing).

## Response templates
| User intent | Provide |
| --- | --- |
| Aviation operator | Polar route risk window, SWS advisories, HF communication outage probability, recommended altitude adjustments. |
| Satellite operator | Expected ΔB for LEO, charging risk for GEO, instructions to consult NOAA SWPC alerts. |
| Power grid planner | Time-stamped Kp/Dst projections, transformer risk thresholds, suggestion to coordinate with national grid geomagnetic disturbance plans. |

## Metrics & thresholds
- **Radiation**: For crewed flights, cite dose rates (µSv/h) and compare to regulatory limits.  
- **Geomagnetic**: Mention Kp ≥ 7 or Dst < –150 nT as triggers for high-alert operations.  
- **Communication**: Highlight HF blackout categories (minor to extreme) based on NOAA scales.

## Notes for assistants
- Always mention data sources and update cadence (NOAA SWPC, ESA SSA Space Weather Service Network).  
- Clarify uncertainty; emphasise ensemble spreads rather than deterministic forecasts.  
- Point to historical analogues (Carrington, Halloween 2003, May 2024 storms) when users request worst-case scenarios.  

