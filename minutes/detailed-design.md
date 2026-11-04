---
title: Kinematics and End Effector
date: 2026-11-02
type: minutes
attendees: [Name, Name, Name]
tags: [team]
---

# Kinematics and End Effector

**Time.** 00:00–00:00, location.

## Discussion

This section covers the signal and control flow for the single-rail 3-PRRR parallel manipulator and its sample gripper.

### 1. Overall System Pipeline

From a target coordinate to the realized end-effector position.

| Step | Stage | What happens |
|------|-------|--------------|
| 1 | **Spatial Target Input** | Desired end-effector location, target (X, Y, Z) |
| 2 | **Kinematic Solver** (Raspberry Pi / host) | Closed-form 3-PRRR inverse kinematics: (X, Y, Z) → (d1, d2, d3) |
| 3 | **Motion Controller** (32-bit MCU firmware) | Displacement to steps via `STEPS_PER_MM`; pulse generation and trapezoidal velocity ramping |
| 4 | **Actuation & Drive Train** | 3x stepper motors with TMC2209 silent drivers; continuous GT2 timing belt loop |
| 5 | **Single-Rail Transmission** (3-PRRR) | 3x collinear carriages on a central extrusion track; passive linkage arms with free revolute joints |
| 6 | **End-Effector Output** | Realized 3D coordinate (X, Y, Z); electromechanical parallel-jaw sample gripper |

### 2. Gripper Operation Sequence

Full lifecycle of a pick, transit and release.

1. **Pre-grip and object detection**
   - ToF IR sensor (VL53L1X) checks that the vial is present.
   - The Pi commands the lead-screw motor to start closing.
2. **Active clamping**
   - A micro stepper drives the parallel jaws inward.
   - The strain gauge load cell flexes under contact force.
3. **Strain gauge signal conditioning**
   - The Wheatstone bridge outputs a differential mV signal.
   - The HX711 24-bit ADC amplifies and digitizes it at 80 Hz.
4. **Force comparison: is F_meas ≥ F_target?**
   - **No:** continue driving the motor inward and return to step 3.
   - **Yes:** halt the motor immediately and engage holding torque.
5. **In-transit sample drop protection**
   - Rail transit begins along the Y-axis track.
   - The strain gauge is polled continuously in the background.
   - If F_meas drops below the threshold, trigger a drop alert.
6. **Sample release**
   - Target destination reached.
   - The lead-screw motor reverses to retract the jaws.

### 3. Gripper Force Control Loop

The closed loop that clamps the sample at a fixed force and monitors for drops.

1. **Initial grip command**
   - Set the target force threshold (e.g., F_target = 2.0 N).
   - The Pi commands the lead-screw stepper to close the jaws.
2. **Continuous signal sampling**
   - The lead screw closes the parallel jaws on the sample.
   - The HX711 samples the load cell at 80 Hz.
3. **Threshold check: is F_meas ≥ F_target?**
   - **No:** continue the motor inward drive and return to step 2.
   - **Yes:** halt the motor instantly and engage holding current.
4. **In-transit sample drop monitor**
   - The rail moves the sample along the Y-axis track.
   - Background check: if F_meas falls below 0.2 N, alert and halt.

### 4. Z-Height Closed-Loop Correction

Uses the ToF sensor to correct vertical error against the benchtop.

1. **Real-time distance read:** the VL53L1X measures height above the benchtop (Z_measured).
2. **Error calculation:** ΔZ = Z_target − Z_measured.
3. **Tolerance check: does the magnitude of ΔZ exceed 0.2 mm?**
   - **No:** maintain the current trajectory; no adjustment needed.
   - **Yes:** recalculate the 3-PRRR IK and adjust the d1, d2, d3 carriages.

### 5. Motion Planning and StallGuard Safety

From target coordinate to motion, with jam detection.

1. **Spatial coordinate target:** input the desired (X, Y, Z) in mm.
2. **Closed-form kinematic solver:** the Raspberry Pi computes carriage positions (d1, d2, d3) using linear 3-PRRR algebraic equations [4].
3. **Pulse generation and motion**
   - The motion controller converts (d1, d2, d3) to step counts.
   - The TMC2209 drivers execute a trapezoidal velocity profile.
4. **StallGuard safety back-EMF loop**
   - The TMC2209 continuously monitors motor back-EMF.
   - **No spike:** continue motion.
   - **Spike:** a physical obstacle or jam is detected, so trigger an emergency interrupt and disable motor torque.

## Decisions

- **Main controller:** [Raspberry Pi 4 Model B (4 GB)](https://www.pishop.ca/product/raspberry-pi-4-model-b-4gb/)
- **Low-level communication:** STM32 Nucleo connected to the stepper drivers

## Action items

- [ ] Kinematic Solver to target step counts — Khushmeet, 2026-11-07