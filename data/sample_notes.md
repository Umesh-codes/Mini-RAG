# Technical Documentation: Project Aritha Local Knowledge Base

## Overview
Project Aritha is a next-generation offline autonomous field robotics platform engineered for remote environmental monitoring and soil sampling in disconnected environments.

## Core Hardware Specifications
- **Main Computing Unit:** Jetson Orin Nano with 8GB unified LPDDR5 memory and 40 TOPS AI compute.
- **Primary Sensors:**
  - 360-degree Solid-State LiDAR with an operational detection range of 0.2m to 25.0m.
  - Dual global-shutter stereo cameras operating at 60 FPS (1080p resolution).
  - High-precision 9-axis Inertial Measurement Unit (IMU) sampling at 200 Hz.
- **Power System:** 24V 5000mAh lithium-iron-phosphate (LiFePO4) battery pack delivering up to 6.5 hours of continuous field operation.

## Operational Constraints and Safety Protocols
- **Speed Limits:** Maximum forward velocity in autonomous navigation mode is strictly capped at 1.5 meters per second. In obstacle-dense environments, velocity automatically scales down to 0.4 meters per second.
- **Emergency Braking:** If an obstacle is detected within 0.5 meters of the vehicle chassis, the Emergency Stop (E-Stop) protocol triggers an immediate mechanical brake lock within 120 milliseconds.
- **Operating Temperature:** The operational thermal envelope is between -10 degrees Celsius and 45 degrees Celsius. If internal battery temperature exceeds 55 degrees Celsius, the system initiates a safe thermal shutdown.

## Communication and Telemetry
- **Primary Link:** Long-range sub-GHz LoRa telemetry transceivers with a maximum line-of-sight range of 8.5 kilometers.
- **Local Fallback:** Wi-Fi 6 (802.11ax) enabled only when stationary within the docking bay for high-speed diagnostic telemetry transfer.
- **Data Encryption:** All telemetry packets transmitted over LoRa are encrypted using AES-256-GCM with pre-shared rolling session keys.

## Maintenance and Calibration
- **LiDAR Calibration:** Sensor alignment must be recalibrated every 100 hours of active mission runtime using the calibration target array in Bay 4.
- **Firmware Updates:** Firmware patches are signed using an ed25519 private key and verified by the hardware secure enclave before applying to flash memory.
