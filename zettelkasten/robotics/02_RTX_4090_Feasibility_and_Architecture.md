# 02 - RTX 4090 Feasibility and Architecture

> **Google Doc ID**: `1kYVd0MCfQmKXE-eDEzf_haSQGISYgwbqR7KhFNTSuto`
> **Executable Pipeline Implementation**: [`isaac-mcp/pipeline/03_isaac_lab_runner.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/03_isaac_lab_runner.py)
> **Twin Robots**: `saschibot` ([`rust-saschirob-mcp`](file:///D:/Dev/repos/rust-saschirob-mcp)) & `Nori A3` ([`norirobotics-mcp`](file:///D:/Dev/repos/norirobotics-mcp))

## Executive Summary

VRAM budget and throughput analysis for a single 24 GB RTX 4090 running 4,096 parallel Isaac Lab / MuJoCo Warp environments alongside local VLA inference (`SmolVLA` 450M at 50 Hz, `X-VLA` 0.9B, `pi0.5-FAST`, `GR00T N1.5` LoRA).

## Fleet Integration

- **OpenUSD Stages**:
  - [`isaac-mcp/scenes/saschibot_sim.usda`](file:///D:/Dev/repos/isaac-mcp/scenes/saschibot_sim.usda) (30 links, 29 joints, 4-caster support polygon, full rest-pose FK)
  - [`isaac-mcp/scenes/nori_a3_sim.usda`](file:///D:/Dev/repos/isaac-mcp/scenes/nori_a3_sim.usda) (46 links, 45 joints, oriented STL collision proxies, full rest-pose FK)
- **MCP Tool Entrypoints**:
  - `isaac-mcp`: `convert_urdf_to_usd`, `run_active_inference`, `isaac_pipeline`
  - `vla-mcp`: `vla_weights` (`smolvla`, `pi0.5-fast`, `gr00t-n1.5`, `x-vla`, `wall-oss-0.5`), `vla_xvla` (`saschibot`, `nori_a3`, `isaac_twin`)
  - `rust-saschirob-mcp`: `feetech::sync_write_goals` (`0x83`) & `feetech::sync_read_present` (`0x82`)
