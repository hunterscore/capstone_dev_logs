---
title: Kinematics and End Effector
date: 2026-11-2
type: minutes
attendees: [Name, Name, Name]
tags: [team]
---

# Kinematics and End Effector

**Time.** 00:00–00:00, location.

## Discussion

What was discussed.
# 3-PRRR Sample Handler: System Flowcharts

This document describes the full signal and control flow for the single-rail 3-PRRR parallel manipulator and its sample gripper.

---

## 1. Overall System Pipeline

From a target coordinate to the realized end-effector position.

```mermaid
flowchart TD
    A["<b>1. Spatial Target Input</b><br/>Desired end-effector location<br/>Target (X, Y, Z)"]
    B["<b>2. Kinematic Solver</b> (Raspberry Pi / Host)<br/>Closed-form 3-PRRR inverse kinematics<br/>(X, Y, Z) → (d1, d2, d3)"]
    C["<b>3. Motion Controller</b> (32-bit MCU firmware)<br/>Displacement to steps: STEPS_PER_MM<br/>Pulse generation + trapezoidal velocity ramping"]
    D["<b>4. Actuation & Primary Drive Train</b><br/>3x stepper motors + TMC2209 silent drivers<br/>Continuous GT2 timing belt drive loop"]
    E["<b>5. Single-Rail Mechanical Transmission</b> (3-PRRR)<br/>3x collinear carriages on central extrusion track<br/>Passive linkage arms with free revolute joints"]
    F["<b>6. End-Effector Spatial Output</b><br/>Realized 3D coordinate (X, Y, Z)<br/>Electromechanical parallel-jaw sample gripper"]

    A --> B --> C --> D --> E --> F
```

---

## 2. Gripper Operation Sequence

Full lifecycle of a pick, transit and release.

```mermaid
flowchart TD
    A["<b>1. Pre-Grip & Object Detection</b><br/>ToF IR sensor (VL53L1X) checks vial presence<br/>Pi commands lead-screw motor to start closing"]
    B["<b>2. Active Clamping & Lead-Screw Drive</b><br/>Micro stepper drives parallel jaws inward<br/>Strain gauge load cell flexes under contact force"]
    C["<b>3. Strain Gauge Signal Conditioning</b><br/>Wheatstone bridge outputs differential mV signal<br/>HX711 24-bit ADC amplifies and digitizes at 80 Hz"]
    D{"<b>4. Force Comparison</b><br/>Is F_meas ≥ F_target?"}
    E["Continue motor inward drive"]
    F["Halt motor immediately<br/>Engage holding torque"]
    G["<b>5. In-Transit Sample Drop Protection</b><br/>Rail transit begins along Y-axis track<br/>Continuous background strain gauge polling<br/>If F_meas drops below threshold → Drop Alert"]
    H["<b>6. Sample Release Phase</b><br/>Target destination reached<br/>Lead-screw motor reverses to retract jaws"]

    A --> B --> C --> D
    D -- NO --> E --> C
    D -- YES --> F --> G --> H
```

---

## 3. Gripper Force Control Loop

The closed loop that clamps the sample at a fixed force and monitors for drops.

```mermaid
flowchart TD
    A["<b>1. Initial Grip Command</b><br/>Target force threshold set (e.g., F_target = 2.0 N)<br/>Pi commands lead-screw stepper to close jaws"]
    B["<b>2. Continuous Signal Sampling</b><br/>Lead-screw closes parallel jaws on sample<br/>HX711 24-bit ADC samples load cell at 80 Hz"]
    C{"<b>3. Threshold Check</b><br/>Is F_meas ≥ F_target?"}
    D["Continue motor inward drive"]
    E["Halt motor drive instantly<br/>Engage holding current"]
    F["<b>4. In-Transit Sample Drop Monitor</b><br/>Rail moves sample along Y-axis track<br/>Background check: if F_meas falls below 0.2 N<br/>→ Alert and halt"]

    A --> B --> C
    C -- NO --> D --> B
    C -- YES --> E --> F
```

---

## 4. Z-Height Closed-Loop Correction

Uses the ToF sensor to correct vertical error against the benchtop.

```mermaid
flowchart TD
    A["<b>1. Real-Time Distance Read</b><br/>VL53L1X ToF IR sensor measures vertical<br/>height above benchtop: Z_measured"]
    B["<b>2. Error Calculation</b><br/>ΔZ = Z_target − Z_measured"]
    C{"<b>3. Tolerance Check</b><br/>Does the magnitude of ΔZ<br/>exceed 0.2 mm?"}
    D["Maintain current trajectory<br/>No adjustment needed"]
    E["Recalculate 3-PRRR IK<br/>Adjust d1, d2, d3 carriages"]

    A --> B --> C
    C -- NO --> D
    C -- YES --> E
```

---

## 5. Motion Planning and StallGuard Safety

From target coordinate to motion, with jam detection.

```mermaid
flowchart TD
    A["<b>1. Spatial Coordinate Target</b><br/>Input desired target coordinate<br/>(X, Y, Z) in mm"]
    B["<b>2. Closed-Form Kinematic Solver</b><br/>Raspberry Pi computes carriage positions (d1, d2, d3)<br/>using linear 3-PRRR algebraic equations [4]"]
    C["<b>3. Pulse Generation & Motion</b><br/>Motion controller converts (d1, d2, d3) to step counts<br/>TMC2209 drivers execute trapezoidal velocity profile"]
    D["<b>4. StallGuard Safety Back-EMF Loop</b><br/>TMC2209 continuously monitors motor back-EMF"]
    E{"Back-EMF spike?"}
    F["Continue motion"]
    G["Physical obstacle or jam detected<br/>Emergency interrupt → disable motor torque"]

    A --> B --> C --> D --> E
    E -- NO --> F
    E -- YES --> G
```
## Decisions

Main controller: https://www.pishop.ca/product/raspberry-pi-4-model-b-4gb/
Low level communication: STM32 Nucleo connected with drivers

## Action items

- [ ] Kinematic Solver to target step counts — Khushmeet, 2026-11-7
