# Chinese Open Source Drones for MCP Server Integration

**Research Date**: 2025-12-02
**Purpose**: Identify open-source Chinese drone projects and ready-to-buy kits suitable for building a Drone MCP server with remote control and video streaming capabilities.

---

## Executive Summary

DJI remains closed-source, but several Chinese companies and open-source projects provide viable alternatives for building a drone MCP server. Key findings:

- **Best Open Source Projects**: Tdrone, OmniNxt, Fast-Drone-250
- **Best Ready-to-Buy Kits**: S2-F290, CQ230, ZD550/ZD680
- **Best Flight Controllers**: CUAV Pixhawk, APO22 Mini Plus, PX4/ArduPilot compatible
- **Video Streaming Solutions**: OpenIPC/APFPV, WFB-ng, RTSP/WebRTC via companion computer

---

## Part 1: GitHub & Open Source Projects

### Fully Open Source Drone Projects

#### 1. **Tdrone** by ShenZhenAccelerationTechCo
- **GitHub**: https://github.com/ShenZhenAccelerationTechCo/Tdrone
- **Type**: Coaxial twin-propeller UAV
- **Hardware**: 3D-printable frame, CC3D flight controller, motion camera, 2-axis gimbal
- **Software**: Open source firmware + ground station software
- **Video Streaming**: Basic camera included, needs custom streaming implementation
- **Remote Control**: Standard RC + ground station control
- **Flight Time**: ~10 minutes
- **Pros**: Fully open hardware/software, unique coaxial design
- **Cons**: Video streaming not built-in, limited flight time, requires customization
- **MCP Integration**: Medium - good foundation but needs video streaming module

#### 2. **OmniNxt** (HKUST Aerial Robotics)
- **Paper**: https://arxiv.org/abs/2403.20085
- **Type**: Fully open-source aerial robot platform
- **Hardware**: Custom flight controller (NxtPX4), multi-fisheye camera setup
- **Software**: Complete perception, mapping, localization stack
- **Video Streaming**: Multi-camera visual streams, dense mapping
- **Remote Control**: Research-grade, supports autonomous missions
- **Pros**: Excellent perception capabilities, production-ready software
- **Cons**: High complexity, research-oriented, requires significant compute
- **MCP Integration**: High - strong video/control foundation

#### 3. **UniQuad** (HKUST)
- **Paper**: https://arxiv.org/abs/2407.00578
- **Type**: Open-source quadrotor platform
- **Hardware**: Modular design, flexible payloads
- **Software**: Full open-source stack
- **Video Streaming**: Supports custom payloads including cameras
- **Remote Control**: Research-focused, supports telemetry
- **Pros**: Highly modular, versatile for research
- **Cons**: More research tool than production platform
- **MCP Integration**: High - good for custom integrations

#### 4. **Fast-Drone-250** (ZJU-FAST-Lab)
- **GitHub**: https://github.com/ZJU-FAST-Lab/Fast-Drone-250
- **Type**: 250mm autonomous quadrotor
- **Hardware**: PX4 flight controller, RealSense cameras, ROS-compatible
- **Software**: ROS, VINS (visual-inertial), autonomous navigation
- **Video Streaming**: ROS image topics, can bridge to RTSP/WebRTC
- **Remote Control**: MAVLink support, ROS-based control
- **Pros**: Mature academic project, good documentation
- **Cons**: Requires ROS knowledge, video streaming needs bridging
- **MCP Integration**: High - MAVLink + ROS integration points

#### 5. **esp-drone** (Espressif)
- **GitHub**: https://github.com/espressif/esp-drone
- **Type**: ESP32/ESP32-S based mini quadcopter
- **Hardware**: ESP32 SoC, lightweight design
- **Software**: Open firmware, WiFi control
- **Video Streaming**: No built-in, but ESP32 can support cameras
- **Remote Control**: WiFi via mobile app/gamepad
- **Pros**: Cheap, modular, good for prototyping
- **Cons**: Limited payload, no video streaming built-in
- **MCP Integration**: Medium - good control foundation, needs video add-on

#### 6. **hx-esp32-cam-fpv** (RomanLut)
- **GitHub**: https://github.com/RomanLut/hx-esp32-cam-fpv
- **Type**: Digital FPV system using ESP32
- **Hardware**: ESP32-S3 + cameras
- **Software**: MAVLink telemetry, RC control, OSD
- **Video Streaming**: Yes - video stream + telemetry over WiFi/UART
- **Remote Control**: MAVLink over WiFi
- **Latency**: ~90-110ms
- **Pros**: Complete video + control solution, low cost
- **Cons**: Limited range, ESP32-based limitations
- **MCP Integration**: High - ready for MCP server integration

#### 7. **Stamp Fly** (M5Stack + Shenzhen collaboration)
- **Hackster**: https://www.hackster.io/stampfly/stamp-fly-an-open-source-diy-drone-kit-from-japan-shenzhen-93d099
- **Type**: Educational DIY drone kit
- **Hardware**: Open PCB design, programmable controller
- **Software**: Open firmware, educational focus
- **Video Streaming**: Basic, can add custom modules
- **Remote Control**: Programmable, supports custom firmware
- **Pros**: Very hackable, affordable, good for learning
- **Cons**: Educational focus, not production-grade
- **MCP Integration**: Medium - good for prototyping

### Supporting Software Projects

#### 8. **Drone-shipping** (galprz/Technion)
- **GitHub**: https://github.com/galprz/Drone-shipping
- **Type**: Framework for autonomous missions with Pixhawk
- **Features**: Ground component + video streaming, APIs
- **MCP Integration**: High - designed for server integration

#### 9. **OpenVTx**
- **GitHub**: https://github.com/OpenVTx/OpenVTx
- **Type**: Open-source firmware for video transmitters
- **Features**: Controls VTx power, frequency, protocols (MSP, SmartAudio, Tramp)
- **MCP Integration**: Medium - useful for video hardware control

#### 10. **Flydan** (Fudan University)
- **Website**: https://weskeryuan.github.io/flydan/
- **Type**: Multi-agent drone swarm platform
- **Hardware**: Pixhawk + ArduPilot + Raspberry Pi companion computer
- **Features**: XBee communication, swarm coordination
- **MCP Integration**: High - designed for networked control

---

## Part 2: Ready-to-Buy Kits & Hardware

### Complete Drone Kits

#### 1. **S2-F290 Programmable Drone**
- **Supplier**: PropMotz
- **URL**: https://www.propmotz.com/product/s2-f290-programmable-drone-pixwawk-open-source-ros-slam-ai-secondary-development-industrial-level-for-drone-challenge/
- **Flight Controller**: Pixhawk
- **Companion Computer**: Included
- **Software**: ROS, SLAM, AI, open-source resources
- **Video**: Dual-lens camera option, 4G module available
- **Control**: WiFi or 4G remote control
- **Ground Station**: Chinese/English mobile app
- **Pros**: Production-ready, includes video streaming, 4G support
- **Cons**: Higher cost, may need integration work
- **MCP Integration**: Very High - closest to ready-to-use

#### 2. **CQ230 Assembly Drone Development Kit**
- **Supplier**: FPV Gear USA
- **URL**: https://www.fpvgearusa.com/product/cq230-assembly-drone-development-kit-raspberry-pi-4b-pixhawk-ardupilot-industrial-open-source-programmable-diy-drone-kit-with-anti-collision-rack/
- **Flight Controller**: Pixhawk
- **Companion Computer**: Raspberry Pi 4B
- **Software**: ArduPilot, MAVLink, open-source
- **Video**: Real-time video streaming supported
- **Control**: Full telemetry + remote control
- **Pros**: Complete development kit, Raspberry Pi included
- **Cons**: Requires assembly, DIY focus
- **MCP Integration**: Very High - perfect for MCP server development

#### 3. **ZD550 / ZD680 / ZD850** (OpenELAB)
- **Supplier**: OpenELAB
- **URL**: https://openelab.io/products/zd550-open-sourced-fly-ready-drone
- **Flight Controller**: Pixhawk/APM compatible
- **Payload**: 3kg+ (depending on model)
- **Video**: 4K camera options available
- **Control**: MAVLink telemetry, standard RC
- **Pros**: Heavy payload capacity, open flight controllers
- **Cons**: Higher cost, video streaming may need verification
- **MCP Integration**: High - good for production deployments

#### 4. **Taobotics Q300**
- **Supplier**: Taobotics
- **URL**: https://shop.taobotics.com/products/modular-air-ground-collaborative-formation-small-open-source-uav
- **Flight Controller**: Pixhawk
- **Companion Computer**: Jetson host
- **Software**: ROS, open flight control, tutorials
- **Video**: Supports air-ground collaborative formation
- **Control**: Secondary development supported
- **Pros**: Jetson compute, good for research
- **Cons**: Research-focused, may be overkill
- **MCP Integration**: High - Jetson enables advanced features

#### 5. **SkyByte Mini**
- **Type**: WiFi/Bluetooth drone
- **Firmware**: Open-source esp-drone firmware
- **Control**: WiFi control
- **Pros**: Cheap, open firmware
- **Cons**: Limited payload, no video streaming
- **MCP Integration**: Low - too limited for production

#### 6. **PyDrone Python Programming Drone Kit**
- **Supplier**: PropMotz
- **URL**: https://www.propmotz.com/product/pydrone-python-programming-drone-github-open-source-easy-development-esp-s3-diy-drone-kit/
- **Hardware**: ESP32-S3
- **Software**: Python programming, open-source on GitHub
- **Control**: WiFi/Bluetooth
- **Pros**: Educational, Python-friendly
- **Cons**: Limited capabilities
- **MCP Integration**: Low - educational only

### Flight Controllers & Components

#### 7. **CUAV Flight Controllers**
- **Supplier**: CUAV (Guangzhou/China)
- **URL**: https://store.cuav.net/
- **Models**: Pixhack, X7, various Pixhawk-compatible boards
- **Software**: PX4/ArduPilot compatible
- **Pros**: Widely used, reliable, open firmware support
- **MCP Integration**: High - standard MAVLink support

#### 8. **APO22 Mini Plus** (Spider UAV)
- **Supplier**: Spider UAV
- **URL**: https://spideruav.com/product/controller/apo22-mini-plusf-light-controller/
- **Type**: Open-source flight controller
- **Features**: Mesh networking, dual IMUs, rich I/O
- **Payload**: Up to 30kg UAVs
- **Pros**: Industrial-grade, open-source, mesh networking
- **MCP Integration**: High - advanced features

#### 9. **VIEWPRO V7 Pro**
- **Supplier**: VIEWPRO
- **URL**: https://www.viewprouav.com/news/viewpros-first-generation-open-source-autopilot-v7-pro-release/
- **Type**: Open-source autopilot (Dec 2024 release)
- **Hardware**: STM32H743, triple-redundant IMUs
- **Pros**: Industrial-grade, safety-focused
- **Cons**: Just autopilot, needs video/control modules
- **MCP Integration**: Medium - requires integration

### Video & FPV Components

#### 10. **CaddxFPV** (Shenzhen)
- **Type**: FPV cameras and digital video transmission
- **Products**: Vista, Walksnail Avatar systems
- **Pros**: High-quality video, low latency
- **Cons**: Mostly proprietary firmware
- **MCP Integration**: Medium - good hardware, may need reverse engineering

#### 11. **Makerfire** (Shenzhen)
- **URL**: https://www.makerfire.com/
- **Type**: Open hardware FPV/racing drone components
- **Focus**: Educational, STEAM, open-source hardware
- **Pros**: Good for sourcing components, open designs
- **Cons**: More component supplier than complete solution
- **MCP Integration**: Medium - good for DIY builds

---

## Part 3: Video Streaming Solutions

### Open Source Streaming Solutions

1. **OpenIPC/APFPV**
   - WiFi AP mode for drones
   - RTP/UDP streaming
   - Latency: ~40-70ms
   - Browser/web interfaces

2. **WFB-ng** (WiFi Broadcast)
   - WiFi-based video + telemetry + control
   - Works with PX4 companion computers
   - Low latency, bidirectional

3. **Standard Protocols**
   - RTSP (Real-Time Streaming Protocol)
   - WebRTC (browser-based)
   - gStreamer (Linux-based)
   - Via companion computer (Raspberry Pi, Jetson)

### Streaming Server Software

1. **OvenMediaEngine (OME)**
   - Open-source streaming server
   - Supports RTMP, RTSP, SRT input
   - WebRTC, LL-HLS output
   - Low latency

2. **ATAK-UAS-RTSP**
   - mediamtx-based RTSP server/proxy
   - For UAS applications
   - Can integrate drone streams

---

## Part 4: Recommendations for Drone MCP Server

### Architecture Components

1. **Flight Controller**: PX4 or ArduPilot compatible (CUAV, Pixhawk)
2. **Companion Computer**: Raspberry Pi 4B or Jetson Nano/Orin
3. **Video Pipeline**: Camera → Companion Computer → RTSP/WebRTC → MCP Server
4. **Control Link**: MAVLink over WiFi/4G/5G or ExpressLRS for RC
5. **Ground Station**: Custom MCP server or QGroundControl + custom backend

### Best Options by Use Case

#### For Production/Commercial Use:
- **S2-F290** - Most complete, includes 4G, production-ready
- **ZD550/ZD680** - Heavy payload, proven platform

#### For Development/Research:
- **CQ230** - Complete dev kit with Raspberry Pi
- **Fast-Drone-250** - Academic-grade, ROS integration

#### For Prototyping/Learning:
- **Tdrone** - Fully open, good for learning
- **esp-drone** - Cheap, WiFi control
- **Stamp Fly** - Educational, hackable

#### For Advanced Research:
- **OmniNxt** - Best perception capabilities
- **UniQuad** - Most modular
- **Taobotics Q300** - Jetson compute power

### Integration Checklist

- [ ] Open flight controller firmware (PX4/ArduPilot)
- [ ] MAVLink telemetry support
- [ ] Companion computer for video encoding
- [ ] Camera with USB/CSI interface
- [ ] Video streaming protocol (RTSP/WebRTC)
- [ ] Network link (WiFi/4G/5G)
- [ ] Ground station software
- [ ] MCP server integration layer

---

## Part 5: Chinese Companies & Suppliers

### Shenzhen-Based Companies

1. **CUAV** (Guangzhou) - Open flight controllers
2. **Makerfire** (Shenzhen) - Open hardware components
3. **CaddxFPV** (Shenzhen) - FPV video systems
4. **ZeroOne AeroSpace** (Nanjing) - Open avionics
5. **Spider UAV** - Open flight controllers
6. **VIEWPRO** - Open autopilots

### Online Suppliers

- **Made-in-China.com** - Various Shenzhen suppliers
- **OpenELAB** - Open-source drone kits
- **PropMotz** - Programmable drones
- **FPV Gear USA** - Development kits
- **Taobotics** - Research platforms

---

## Part 6: Key GitHub Repositories Summary

| Repository | Stars | Language | Focus | MCP Ready? |
|------------|-------|----------|-------|------------|
| [ShenZhenAccelerationTechCo/Tdrone](https://github.com/ShenZhenAccelerationTechCo/Tdrone) | - | C/C++ | Coaxial drone | Medium |
| [ZJU-FAST-Lab/Fast-Drone-250](https://github.com/ZJU-FAST-Lab/Fast-Drone-250) | - | C++/ROS | Autonomous quad | High |
| [espressif/esp-drone](https://github.com/espressif/esp-drone) | - | C | ESP32 drone | Medium |
| [RomanLut/hx-esp32-cam-fpv](https://github.com/RomanLut/hx-esp32-cam-fpv) | - | C++ | ESP32 FPV | High |
| [galprz/Drone-shipping](https://github.com/galprz/Drone-shipping) | - | Python | Mission framework | High |
| [OpenVTx/OpenVTx](https://github.com/OpenVTx/OpenVTx) | - | C | VTx firmware | Medium |

---

## Part 7: Next Steps

1. **Evaluate Requirements**: Determine payload, range, video quality needs
2. **Choose Platform**: Select from recommended options above
3. **Prototype**: Start with CQ230 or Fast-Drone-250 for development
4. **Integrate MCP Server**: Build MAVLink bridge + video streaming layer
5. **Test & Deploy**: Validate remote control + video streaming

---

## References

- PX4 Documentation: https://px4.io
- ArduPilot Documentation: https://ardupilot.org
- MAVLink Protocol: https://mavlink.io
- ExpressLRS: https://www.expresslrs.org
- OpenIPC: https://openipc.org

---

**Last Updated**: 2025-12-02
**Research Method**: Web search + GitHub exploration
**Status**: Comprehensive overview complete, ready for platform selection
