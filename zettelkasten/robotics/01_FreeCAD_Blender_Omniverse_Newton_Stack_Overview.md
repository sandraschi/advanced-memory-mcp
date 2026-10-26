# 01 - FreeCAD, Blender, Omniverse, Newton Stack Overview

> **Google Doc ID**: `1IEYeQI0hIIpC_vejDR8JnG55mGeySKmAiI_W8q6Ay-k`
> **Executable Pipeline Implementation**: [`isaac-mcp/pipeline/01_cad_to_usd_blender.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/01_cad_to_usd_blender.py)
> **Twin Robots**: `saschibot` ([`rust-saschirob-mcp`](file:///D:/Dev/repos/rust-saschirob-mcp)) & `Nori A3` ([`norirobotics-mcp`](file:///D:/Dev/repos/norirobotics-mcp))

## Executive Summary

Unified asset pipeline: parametric mechanical design in FreeCAD 1.1 (`saschirob_skeleton.FCStd`), mesh conditioning & Y-up/Z-up normalization in Blender 4.4, OpenUSD scene assembly (`saschibot_sim.usda`, `nori_a3_sim.usda`), and GPU simulation in Isaac Sim 5.x and Newton Physics (`newton_warp`).

## Fleet Integration

- **OpenUSD Stages**:
  - [`isaac-mcp/scenes/saschibot_sim.usda`](file:///D:/Dev/repos/isaac-mcp/scenes/saschibot_sim.usda) (30 links, 29 joints, 4-caster support polygon, full rest-pose FK)
  - [`isaac-mcp/scenes/nori_a3_sim.usda`](file:///D:/Dev/repos/isaac-mcp/scenes/nori_a3_sim.usda) (46 links, 45 joints, oriented STL collision proxies, full rest-pose FK)
- **MCP Tool Entrypoints**:
  - `isaac-mcp`: `convert_urdf_to_usd`, `run_active_inference`, `isaac_pipeline`
  - `vla-mcp`: `vla_weights` (`smolvla`, `pi0.5-fast`, `gr00t-n1.5`, `x-vla`, `wall-oss-0.5`), `vla_xvla` (`saschibot`, `nori_a3`, `isaac_twin`)
  - `rust-saschirob-mcp`: `feetech::sync_write_goals` (`0x83`) & `feetech::sync_read_present` (`0x82`)
