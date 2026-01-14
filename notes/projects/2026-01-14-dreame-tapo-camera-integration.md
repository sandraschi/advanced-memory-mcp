---
title: "Dreame D20 Pro Plus + Tapo Camera Mobile Patrol Robot"
entity_type: "project"
tags: ["robotics", "security", "smart-home", "dreame", "tapo", "patrol", "mobile-camera"]
created: "2026-01-14"
status: "planning"
priority: "high"
---

# Dreame D20 Pro Plus + Tapo Camera Mobile Patrol Robot

## Overview

Transform the Dreame D20 Pro Plus robot vacuum into a mobile security patrol robot by mounting a lightweight Tapo camera on top. This creates a dual-purpose device that can clean floors while providing autonomous security monitoring.

## Hardware Components

### Primary Robot: Dreame D20 Pro Plus
- **Model:** `dreame.vacuum.p2114o` (Self-Cleaning Robot Vacuum-Mop)
- **Weight:** ~3.6kg
- **Battery:** 5200mAh Li-ion
- **Navigation:** LiDAR-based with real-time mapping
- **Capabilities:** Full rotation/velocity control, room cleaning, autonomous navigation
- **API:** Complete FOSS integration via `dreame-vacuum` library

### Camera: Tapo C200 Pan/Tilt
- **Weight:** ~120g (negligible impact on Dreame)
- **Dimensions:** 86 × 85 × 91mm
- **Features:** 360° pan, 114° tilt, night vision, motion detection
- **Power:** 5V USB (needs external power solution)
- **Stream:** RTSP access for live viewing

### 3D Printed Mount: "Spider Mount"
- **Design:** Attaches to Dreame LiDAR housing
- **Materials:** PLA/ABS for strength and flexibility
- **Features:**
  - Adjustable height/angle
  - Cable management channels
  - Vibration dampening
  - Quick-release mechanism

## Implementation Plan

### Phase 1: Mechanical Design (Week 1)
- Design 3D printed spider mount using Vienna makerspace
- Test fit on Dreame LiDAR housing
- Ensure LiDAR field of view remains unobstructed
- Verify camera positioning doesn't interfere with navigation

### Phase 2: Power Solution (Week 1-2)
- **Option A:** 18650 battery pack (2-3 cells in series)
  - Runtime: 4-6 hours continuous
  - Recharge via USB when Dreame docks
- **Test:** Power consumption with camera streaming

### Phase 3: Software Integration (Week 2-3)

#### Robotics MCP Integration
```python
# Dreame + Camera control
robot_behavior("dreame_01", "navigation", "start_patrol")
robot_behavior("dreame_01", "camera", "start_stream")
robot_behavior("dreame_01", "camera", "detect_motion")
```

#### Tapo Camera MCP Integration
- RTSP stream access from mobile camera
- Motion detection events during patrol
- Camera pan/tilt control synchronized with robot movement

### Phase 4: Testing & Calibration (Week 3-4)
- Navigation accuracy with camera mounted
- Door clearance testing (Dreame height: ~120mm with mount)
- Battery life impact assessment
- Camera-LiDAR interference testing

## Use Cases

### 1. Autonomous Security Patrol
- **Scenario:** Home unoccupied, Dreame patrols predefined routes
- **Camera:** Streams live video, detects motion, alerts via app
- **Integration:** Patrols every 2 hours, focuses on entry points

### 2. Pet Monitoring
- **Scenario:** Monitor pets during cleaning operations
- **Camera:** Tracks pet movement and behavior
- **Integration:** AI detects unusual pet activity or distress

### 3. Cleaning Progress Verification
- **Scenario:** Visual confirmation of cleaning completion
- **Camera:** Records before/after footage of cleaning areas
- **Integration:** Timestamped video clips stored locally

### 4. Smart Home Integration
- **Scenario:** Vacuum detects issues during patrol
- **Camera:** Identifies potential problems (leaks, open doors)
- **Integration:** Sends alerts to home automation system

## Technical Specifications

### Weight Impact Analysis
- Dreame Base: 3.6kg
- Tapo C200: 0.12kg
- 3D Mount: 0.08kg
- Total Addition: 0.20kg (5.5% increase)
- **Assessment:** Negligible impact on performance

### Power Consumption
- Dreame Cleaning: ~25W average
- Tapo Camera (streaming): ~3W
- Total: ~28W (12% increase)
- **Impact:** ~10-15% reduction in battery life

### Navigation Considerations
- **Height:** Total height ~120mm (check door frames)
- **Balance:** Camera positioned behind LiDAR for stability
- **IR Interference:** Ensure camera IR doesn't affect LiDAR
- **Cable Management:** Secure cables to prevent snagging

## Integration Architecture

```
┌─────────────────┐    ┌──────────────────┐
│  Robotics MCP   │    │ Tapo Camera MCP  │
│                 │    │                  │
│ • Dreame Control│    │ • Camera Streams │
│ • Navigation    │    │ • Motion Detect  │
│ • LiDAR Maps    │◄──►│ • RTSP Access    │
│ • Patrol Routes │    │ • Pan/Tilt Ctrl  │
└─────────────────┘    └──────────────────┘
         │                       │
         └──────────┬────────────┘
                    │
          ┌─────────────────────┐
          │ Dreame + Tapo Camera│
          │ Mobile Patrol Robot │
          └─────────────────────┘
```

## Risk Assessment

### Low Risk
- **Weight Impact:** Camera is very lightweight
- **Power Draw:** Minimal additional consumption
- **Navigation:** LiDAR remains functional

### Medium Risk
- **Height Clearance:** May need door frame modifications
- **Cable Management:** Cables could snag during movement
- **Vibration:** Camera shake during high-speed movement

### Mitigation Strategies
- **Testing:** Comprehensive testing before deployment
- **Failsafe:** Easy camera removal if issues arise
- **Backup:** Camera can operate independently if needed

## Success Metrics

### Functional Goals
- [ ] Camera streams stable during movement
- [ ] Motion detection works during patrol
- [ ] Battery life acceptable (>2 hours)
- [ ] Navigation accuracy maintained
- [ ] No LiDAR interference

### Performance Goals
- [ ] Smooth camera footage during movement
- [ ] Reliable motion detection alerts
- [ ] Integration with home automation
- [ ] Pet monitoring capability

## Timeline & Milestones

- **Week 1:** 3D printed mount design and testing
- **Week 2:** Power solution implementation
- **Week 3:** Software integration and testing
- **Week 4:** Field testing and optimization
- **Week 5:** Production deployment

## Budget & Resources

### Hardware Costs
- **Tapo C200:** €30 (already owned)
- **18650 Battery Pack:** €15
- **3D Printing:** €5-10 (filament)
- **Cables/Connectors:** €5
- **Total:** €20-25

### Required Resources
- ✅ Dreame D20 Pro Plus (arriving tomorrow)
- ✅ Tapo C200 Camera (owned)
- ✅ 3D Printer access (Vienna makerspace)
- ✅ Robotics MCP integration (completed)
- ✅ Tapo Camera MCP integration (completed)

## Conclusion

This project transforms a standard robot vacuum into a mobile security platform with minimal cost and complexity. The lightweight Tapo camera adds significant functionality without compromising the Dreame's primary cleaning capabilities.

The integration leverages existing MCP infrastructure for seamless control and monitoring, creating a unique dual-purpose robot that enhances both cleaning and security automation.

**Status:** Ready for implementation upon Dreame delivery.
