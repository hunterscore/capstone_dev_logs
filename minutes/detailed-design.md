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

┌─────────────────────────────────────────────────────────┐
│              1. Spatial Target Input                    │
│   • Desired End-Effector Location: Target (X, Y, Z)     │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│        2. Kinematic Solver (Raspberry Pi / Host)        │
│   • Closed-Form 3-PRRR Inverse Kinematics (IK)          │
│   • Algebraic Transformation: (X, Y, Z) ➔ (d1, d2, d3)  │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│       3. Motion Controller (32-Bit MCU Firmware)        │
│   • Displacement to Step Conversion: STEPS_PER_MM       │
│   • Pulse Generation & Trapezoidal Velocity Ramping     │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│          4. Actuation & Primary Drive Train             │
│   • 3x Stepper Motors + TMC2209 Silent Drivers          │
│   • Continuous GT2 Timing Belt Drive Loop               │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│     5. Single-Rail Mechanical Transmission (3-PRRR)     │
│   • 3x Collinear Carriages on Central Extrusion Track   │
│   • Passive Linkage Arms with Free Revolute Joints      │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│              6. End-Effector Spatial Output             │
│   • Realized 3D Coordinate (X, Y, Z)                    │
│   • Electromechanical Parallel-Jaw Sample Gripper       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│           1. Pre-Grip & Object Detection                │
│   • ToF IR Sensor (VL53L1X) checks vial presence        │
│   • Pi commands gripper lead-screw motor to start closing│
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│        2. Active Clamping & Lead-Screw Drive            │
│   • Micro stepper motor drives parallel jaws inward     │
│   • Strain gauge load cell flexes under contact force   │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│          3. Strain Gauge Signal Conditioning             │
│   • Wheatstone bridge outputs differential mV signal    │
│   • HX711 24-bit ADC amplifies & digitizes at 80 Hz    │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │  4. Force Comparison  │
                 │  Is F_meas >= F_target?│
                 └───────────┬───────────┘
                             │
               ┌─────────────┴─────────────┐
            NO │                           │ YES
               ▼                           ▼
┌────────────────────────────┐  ┌─────────────────────────┐
│ Continue Motor Inward Drive│  │ Halt Motor Immediately  │
└──────────────┬─────────────┘  │ Engage Holding Torque   │
               │                └────────────┬────────────┘
               └───────◄─────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────┐
│         5. In-Transit Sample Drop Protection            │
│   • Rail transit begins along Y-axis track               │
│   • Continuous background strain gauge force polling    │
│   • If F_meas drops < Threshold ➔ Trigger Drop Alert    │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│               6. Sample Release Phase                   │
│   • Target destination reached                          │
│   • Lead-screw motor reverses to retract jaws           │
└─────────────────────────────────────────────────────────┘

All of the control loops:

 ┌─────────────────────────────────────────────────────────────┐
 │                  1. Initial Grip Command                    │
 │  • Target force threshold set (e.g., F_target = 2.0 N)      │
 │  • Pi commands micro lead-screw stepper motor to close jaws │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                2. Continuous Signal Sampling                │
 │  • Lead-screw closes parallel jaws on sample                │
 │  • HX711 24-bit ADC samples load cell force at 80 Hz        │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
                   ┌───────────────────────────┐
                   │   3. Threshold Check      │
                   │   Is F_meas >= F_target?  │
                   └────────────┬──────────────┘
                                │
                 ┌──────────────┴──────────────┐
              NO │                             │ YES
                 ▼                             ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│  Continue Motor Inward Drive │ │  Halt Motor Drive Instantly │
└───────────────┬──────────────┘ │  Engage Holding Current     │
                │                └──────────────┬──────────────┘
                └───────◄───────────────────────┘
                                                │
                                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │             4. In-Transit Sample Drop Monitor               │
 │  • Rail moves sample along Y-axis track                     │
 │  • Background check: If F_meas drops < 0.2 N ➔ Alert & Halt │
 └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
 │                 1. Real-Time Distance Read                  │
 │  • VL53L1X ToF IR sensor measures vertical height above     │
 │    benchtop: Z_measured                                     │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                  2. Error Calculation                       │
 │  • Delta_Z = Z_target - Z_measured                          │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
                   ┌───────────────────────────┐
                   │   3. Tolerance Check      │
                   │   Is |Delta_Z| > 0.2 mm?  │
                   └────────────┬──────────────┘
                                │
                 ┌──────────────┴──────────────┐
              NO │                             │ YES
                 ▼                             ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│ Maintain Current Trajectory  │ │ Recalculate 3-PRRR IK       │
│ No adjustment needed         │ │ Adjust d1, d2, d3 Carriages │
└──────────────────────────────┘ └─────────────────────────────┘

 ┌─────────────────────────────────────────────────────────────┐
 │               1. Spatial Coordinate Target                  │
 │  • Input desired target coordinate: (X, Y, Z) in mm         │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │            2. Closed-Form Kinematic Solver                  │
 │  • Raspberry Pi computes carriage positions (d1, d2, d3)    │
 │    using linear 3-PRRR algebraic equations [4]             │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │               3. Pulse Generation & Motion                  │
 │  • Motion controller converts (d1, d2, d3) to step counts   │
 │  • TMC2209 drivers execute trapezoidal velocity profile     │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │            4. StallGuard Safety Back-EMF Loop               │
 │  • TMC2209 driver continuously monitors motor back-EMF      │
 │  • Spikes in back-EMF ➔ Physical obstacle or jam detected   │
 │  • Triggers emergency interrupt ➔ Disables motor torque    │
 └─────────────────────────────────────────────────────────────┘



## Decisions

Main controller: https://www.pishop.ca/product/raspberry-pi-4-model-b-4gb/
Low level communication: STM32 Nucleo connected with drivers

## Action items

- [ ] Kinematic Solver to target step counts — Khushmeet, 2026-11-7
