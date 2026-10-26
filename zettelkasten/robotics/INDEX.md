# Gemini Robotics & Active Inference Distillations (Oct 2026)

Synthesized from the 17-part iPad Gemini robotics research session and implemented across
[`isaac-mcp`](file:///D:/Dev/repos/isaac-mcp), [`robotics-mcp`](file:///D:/Dev/repos/robotics-mcp),
[`rust-saschirob-mcp`](file:///D:/Dev/repos/rust-saschirob-mcp), [`norirobotics-mcp`](file:///D:/Dev/repos/norirobotics-mcp),
and [`vla-mcp`](file:///D:/Dev/repos/vla-mcp).

## Index of Distilled Notes & Executable Counterparts

| # | Note | Google Doc ID | Executable Implementation |
|---|---|---|---|
| 1 | [Robotics Pipeline: FreeCAD to Isaac Lab & ROS 2 Control (RTX 4090 WSL2)](./00_Master_Robotics_Pipeline_FreeCAD_to_Isaac_Lab_and_ROS2.md) | `1caKSBFupxyxZgTdPOEwk8punBoPWwKVR-AKfXJgjOaY` | [`pipeline/03_isaac_lab_runner.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/03_isaac_lab_runner.py) |
| 2 | [Active Inference, Cognitive Science, and Robot Fleet Architecture](./00_Master_Active_Inference_Cognitive_Science_and_Fleet_Architecture.md) | `1Vro-qQpT6KU80GuEtRJm1pA4G-GiIwXuFnYO2OqUNu4` | [`pipeline/10_mujoco_active_inference_closed_loop.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/10_mujoco_active_inference_closed_loop.py) |
| 3 | [01 - FreeCAD, Blender, Omniverse, Newton Stack Overview](./01_FreeCAD_Blender_Omniverse_Newton_Stack_Overview.md) | `1IEYeQI0hIIpC_vejDR8JnG55mGeySKmAiI_W8q6Ay-k` | [`pipeline/01_cad_to_usd_blender.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/01_cad_to_usd_blender.py) |
| 4 | [02 - RTX 4090 Feasibility and Architecture](./02_RTX_4090_Feasibility_and_Architecture.md) | `1kYVd0MCfQmKXE-eDEzf_haSQGISYgwbqR7KhFNTSuto` | [`pipeline/03_isaac_lab_runner.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/03_isaac_lab_runner.py) |
| 5 | [03 - Isaac Lab Minimal Training Script and Launcher](./03_Isaac_Lab_Minimal_Training_Script_and_Launcher.md) | `1Mi4W6oxRytp2-XQNZhE9sfjw2c7Z4Eb4L9ire-94odQ` | [`pipeline/03_isaac_lab_runner.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/03_isaac_lab_runner.py) |
| 6 | [04 - Sandraschi GitHub Fleet Execution Environment](./04_Sandraschi_GitHub_Fleet_Execution_Environment.md) | `1g3Me0qDuCRS-TcWVwJVLBNchdMfKnAMUfHJ0uBpnh6A` | [`pipeline/10_mujoco_active_inference_closed_loop.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/10_mujoco_active_inference_closed_loop.py) |
| 7 | [05 - Blender Automation Script (CAD to USD)](./05_Blender_Automation_Script_CAD_to_USD.md) | `1MIRh7Qbizsno_CiFu0vm0hTC9QQYK9ipZEl5qu71VHw` | [`pipeline/01_cad_to_usd_blender.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/01_cad_to_usd_blender.py) |
| 8 | [06 - OpenUSD pxr API Snippets for Robotics](./06_OpenUSD_pxr_API_Snippets_for_Robotics.md) | `1-p_RvZcIa7uIv2lay7X38iJztkWAj_RyhQrLd7hO2GU` | [`pipeline/02_usd_mutator_pxr.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/02_usd_mutator_pxr.py) |
| 9 | [07 - pxr USD Python Script for Articulation and Physics Mutation](./07_pxr_USD_Python_Script_for_Articulation_and_Physics_Mutation.md) | `14_kyWhWHQVDNfWpojvLBwYEFAHhnzjZt9td9r_B3fl8` | [`pipeline/02_usd_mutator_pxr.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/02_usd_mutator_pxr.py) |
| 10 | [08 - Spawning and Loading Upgraded OpenUSD in Isaac Lab](./08_Spawning_and_Loading_Upgraded_OpenUSD_in_Isaac_Lab.md) | `1Hl3J7-a30BuYhHQ_mBK5BZVgg44XCM3x11iIh1chXIw` | [`pipeline/03_isaac_lab_runner.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/03_isaac_lab_runner.py) |
| 11 | [09 - Observation and Reward Terms Definition in Isaac Lab](./09_Observation_and_Reward_Terms_Definition_in_Isaac_Lab.md) | `1zMBLC2Xj5F0yAxHltixEvTIVOa-VCha_BYD19qSEDwo` | [`pipeline/03_isaac_lab_runner.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/03_isaac_lab_runner.py) |
| 12 | [10 - Configuring RSL-RL PPO Runner](./10_Configuring_RSL_RL_PPO_Runner.md) | `1PYuvqiczPQsb2ytHVxaJNsvjrMd2vCD39xcCQqp7SHg` | [`pipeline/03_isaac_lab_runner.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/03_isaac_lab_runner.py) |
| 13 | [11 - Loading Trained RSL-RL Policy Checkpoints](./11_Loading_Trained_RSL_RL_Policy_Checkpoints.md) | `1tdHEGVUk94oep5zoijOe1DdWWqmRoh9LEj1RhCO0FeM` | [`pipeline/04_rsl_rl_policy_export.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/04_rsl_rl_policy_export.py) |
| 14 | [12 - Minimal ROS 2 Python Node (Policy Inference)](./12_Minimal_ROS2_Python_Node_Policy_Inference.md) | `1N5zxr9rhS9_FMfZno7g7d2tEpPL6xOo8LtavelnKGqM` | [`pipeline/05_ros2_policy_bridge.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/05_ros2_policy_bridge.py) |
| 15 | [13 - Hardware Watchdog and Emergency Stop (E-Stop)](./13_Hardware_Watchdog_and_Emergency_Stop.md) | `1psCqY-GxYZ7sMacVGLaAqTlkheLATSFMGyeotPvMFqk` | [`pipeline/06_hardware_watchdog.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/06_hardware_watchdog.py) |
| 16 | [14 - Configuring ros2_control URDF and Hardware Interfaces](./14_Configuring_ros2_control_URDF_and_Hardware_Interfaces.md) | `1-XHho8-ZuKpAbOK7imalOfc2Ia1tI6Dv275jkLu0GyI` | [`pipeline/config/ros2_control.urdf.xacro`](file:///D:/Dev/repos/isaac-mcp/pipeline/config/ros2_control.urdf.xacro) |
| 17 | [15 - Windows Host vs WSL2 Linux Execution Guide](./15_Windows_Host_vs_WSL2_Linux_Execution_Guide.md) | `1ZGsCrZ-164iz9tIqBX39XNZBz090hrvjUDiKzkyEYPc` | [`pipeline/10_mujoco_active_inference_closed_loop.py`](file:///D:/Dev/repos/isaac-mcp/pipeline/10_mujoco_active_inference_closed_loop.py) |
