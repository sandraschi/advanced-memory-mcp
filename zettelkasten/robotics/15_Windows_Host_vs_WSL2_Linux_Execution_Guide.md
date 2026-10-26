# 15 - Windows Host vs WSL2 Linux Execution Guide

> **Google Doc ID**: `1ZGsCrZ-164iz9tIqBX39XNZBz090hrvjUDiKzkyEYPc`
> **Executable Pipeline Implementation**: [`isaac-mcp/pipeline/10_mujoco_active_inference_closed_loop.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/10_mujoco_active_inference_closed_loop.py)
> **Twin Robots**: `saschibot` ([`rust-saschirob-mcp`](file:///D:/Dev/repos/rust-saschirob-mcp)) & `Nori A3` ([`norirobotics-mcp`](file:///D:/Dev/repos/norirobotics-mcp))

## Executive Summary

Hybrid Windows 11 + WSL2 Ubuntu 22.04/24.04 workflow: native Windows execution for `rust-saschirob-mcp`, `norirobotics-mcp`, `isaac-mcp`, `vla-mcp`, and MuJoCo 3.x (`10_mujoco_active_inference_closed_loop.py`), paired with WSL2 `/dev/dxg` RTX 4090 passthrough for Isaac Lab and ROS 2 Humble/Jazzy.

## Fleet Integration

- **OpenUSD Stages**:
  - [`isaac-mcp/scenes/saschibot_sim.usda`](file:///D:/Dev/repos/isaac-mcp/scenes/saschibot_sim.usda) (30 links, 29 joints, 4-caster support polygon, full rest-pose FK)
  - [`isaac-mcp/scenes/nori_a3_sim.usda`](file:///D:/Dev/repos/isaac-mcp/scenes/nori_a3_sim.usda) (46 links, 45 joints, oriented STL collision proxies, full rest-pose FK)
- **MCP Tool Entrypoints**:
  - `isaac-mcp`: `convert_urdf_to_usd`, `run_active_inference`, `isaac_pipeline`
  - `vla-mcp`: `vla_weights` (`smolvla`, `pi0.5-fast`, `gr00t-n1.5`, `x-vla`, `wall-oss-0.5`), `vla_xvla` (`saschibot`, `nori_a3`, `isaac_twin`)
  - `rust-saschirob-mcp`: `feetech::sync_write_goals` (`0x83`) & `feetech::sync_read_present` (`0x82`)
