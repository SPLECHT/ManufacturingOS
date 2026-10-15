# ManufacturingOS

**Robot cell design, offline programming and digital twin, in one desktop application.**

Design a robotic cell, plan the motion, verify it against collisions, then export a program
that runs on the real controller (FANUC / KUKA / Yaskawa).

> Closed source. This page is the public overview and devlog of the project.

---

## What it does

```
 CAD / robot library ──► Cell layout ──► Weld seams ──► Motion plan ──► Verification ──► Controller program
   STEP · STL · URDF      robots, rails,    auto-detect     MoveIt 2       collisions,       FANUC .LS
                          gantries,         or pick on      (in-process)   reach, zones,     KUKA .src/.dat
                          positioners,      the model                      cell timing       Yaskawa .JBI
                          conveyors, fences                                                  + setup notes
```

### Cell design
- Industrial robot library (FANUC, KUKA, ABB, Yaskawa Motoman), tools attached at runtime with their TCP.
- **Tool import wizard**: STEP / STL → units, orientation, origin, nozzle / TCP suggestion.
- **Robot carriers**: linear track, column, gantry, column-and-boom. Several robots can share one carrier.
- **Mechanism import wizard**: turn a STEP assembly of a real gantry or positioner into a kinematic model (axes, limits, collision geometry).
- **Positioners**: turntable, tilt-rotate, or imported models. Workpieces mount on the table and move with it.
- Factory elements: parametric conveyors (straight, curved, inclined), diverters, stoppers, sensors, safety fences with doors and light curtains.

### Welding (offline programming)
- **STEP workpiece import**. Fillet seams are found automatically from the geometry: plate intersections, plus arcs and circles such as pipe-to-plate and rim welds. Seams can also be picked by hand with 2 or 3 clicks.
- **Torch-aware planning**: work and travel angles, collision of the torch body with the part, a continuous IK chain with no wrist flips along the seam, and safe approach and retract points.
- **Positioner selection** per seam: the table angle that gives the best weld position (flat or horizontal).
- **Coordinated motion**: the positioner rotates while the robot welds circular seams.
- **External axes**: per-seam carrier position for track, gantry and boom robots.
- **Reach margin check**: warns when a point would become unreachable if the part shifts ±25 mm on site.

### Verification
- Motion planning with MoveIt 2 (Pilz PTP / LIN / CIRC). MoveIt runs inside the application, with no `move_group` process.
- Multi-robot cells:
  - collision check of every robot against the cell along a time-synchronized trace;
  - automatic interference zones, and interlock lines generated into the programs.
- Signal-based simulation:
  - deterministic simulation clock;
  - 16+ DI / DO per robot;
  - user PLC in IEC 61131-3 Structured Text;
  - safety fences and doors stop the robots.
- **OPC UA** server and client: the virtual cell can be driven by, or drive, a real PLC.

### Export to the real controller
- **Post-processors**:
  - FANUC `.LS` with ArcTool `Weld Start` / `Weld End`, user frames and a GP2 positioner group;
  - KUKA `.src` / `.dat`;
  - Yaskawa `.JBI` with ARCON / ARCOF and coordinated `SMOVL` / `SMOVC`.
- **Setup notes for the field**: tool frame values, user frame values with their teach points, axis mapping and warnings, for each brand's menu.
- **User frame calibration**: define a 3-point frame on the part in the software and teach the same 3 points on site. The program follows the real part position without re-export. *Align from site* moves the digital part to its measured position.
- **Simulator cell model**: the fixtures and tool are exported as STL, placed for the robot simulator.

---

## Validation

| Test | Result |
|---|---|
| Program export → FANUC ROBOGUIDE (R-30iB Plus virtual controller, M-10iA, ArcTool) | Joint values and TCP match the ManufacturingOS simulation within **0.1 mm / 0.01°** |
| Weld program with user frame (UFRAME taught from 3 points) | Runs in ROBOGUIDE, torch on the seam |
| Part shifted on site, frame re-taught | Program follows. A reach-limit case (+20 mm → MOTN-018) led to the reach margin check |
| Automated test suite | 23 test programs: kinematics, planning, post-processor read-back (exported points re-checked with FK), calibration, factory flow, PLC, OPC UA |

**Not yet validated:**
- on a physical robot;
- KUKA / Yaskawa output in their own simulators;
- coordinated positioner motion in ROBOGUIDE.

---

## Architecture

- **C++17 · Qt 5 · VTK 9** desktop application (~49k lines).
- **ROS 2 Humble · MoveIt 2** used as libraries: an in-process `RobotModel`, Pilz industrial planner, KDL / TRAC-IK kinematics.
- **Pure modules with no UI dependency**, each covered by headless tests:

  | Module | Role |
  |---|---|
  | `weld/` | seam detection, torch model, planner |
  | `post/` | controller code generation |
  | `calib/` | user frames |
  | `factory/` | flow simulation |
  | `plc/` | Structured Text interpreter |
  | `planning/` | cell model, collision trace |
- **OpenCASCADE** for STEP, **open62541** for OPC UA, **Assimp** for meshes.
- Z-up (REP-103) everywhere. Tools, carriers and positioners are added to an in-memory URDF, and the vendor files are never modified.
- Project files are versioned, with migration, atomic save, autosave and crash recovery.

---

## Roadmap

- Physical robot pilot (FANUC arc welding cell)
- Touch sensing / seam tracking commands in the exported program
- Controller connection: upload, start and monitor the program over the network
- Live digital twin: joint and I/O streaming from the controller → SCADA view
- Point cloud input: scan → mesh → seams, on the same planning path

---

## Devlog

### 2026-10-15: Validated in FANUC ROBOGUIDE
The first end-to-end loop is closed: a cell is designed in ManufacturingOS, the weld path is planned,
the FANUC program is exported and runs in the R-30iB Plus virtual controller.
- Joint values match. FANUC's J2/J3 interaction convention is handled.
- The weld instructions use the R-30iB ArcTool syntax.
- User frames work.
- The setup notes and cell CAD export make the transfer a few minutes of work.

---

**Göktuğ Nuhoğlu**, Founder & Developer
