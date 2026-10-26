# 14 - Configuring ros2_control URDF and Hardware Interfaces

> **Google Doc ID**: `1-XHho8-ZuKpAbOK7imalOfc2Ia1tI6Dv275jkLu0GyI`
> **Executable Pipeline Implementation**: [`isaac-mcp/pipeline/config/ros2_control.urdf.xacro`](file:///D:/Dev/repos/isaac-mcp/pipeline/config/ros2_control.urdf.xacro)
> **Twin Robots**: `saschibot` ([`rust-saschirob-mcp`](file:///D:/Dev/repos/rust-saschirob-mcp)) & `Nori A3` ([`norirobotics-mcp`](file:///D:/Dev/repos/norirobotics-mcp))

## Executive Summary

Wheeled Telescoping Bimanual `ros2_control` tags and `200 Hz` `controller_manager` YAML (`diff_drive_controller`, `lift_controller` with `0.5x` stage2 mimic, `left_arm_controller`, `right_arm_controller`, grippers, and Feetech `SYNC_WRITE 0x83` / `SYNC_READ 0x82` serial bus parameters).

## Fleet Integration

- **OpenUSD Stages**:
  - [`isaac-mcp/scenes/saschibot_sim.usda`](file:///D:/Dev/repos/isaac-mcp/scenes/saschibot_sim.usda) (30 links, 29 joints, 4-caster support polygon, full rest-pose FK)
  - [`isaac-mcp/scenes/nori_a3_sim.usda`](file:///D:/Dev/repos/isaac-mcp/scenes/nori_a3_sim.usda) (46 links, 45 joints, oriented STL collision proxies, full rest-pose FK)
- **MCP Tool Entrypoints**:
  - `isaac-mcp`: `convert_urdf_to_usd`, `run_active_inference`, `isaac_pipeline`
  - `vla-mcp`: `vla_weights` (`smolvla`, `pi0.5-fast`, `gr00t-n1.5`, `x-vla`, `wall-oss-0.5`), `vla_xvla` (`saschibot`, `nori_a3`, `isaac_twin`)
  - `rust-saschirob-mcp`: `feetech::sync_write_goals` (`0x83`) & `feetech::sync_read_present` (`0x82`)
