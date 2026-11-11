# ManufacturingOS

**Robot cell design, offline programming and digital twin, in one desktop application.**

Design a robotic cell, plan the motion, verify it against collisions and the cell's signals, then export a program
that runs on the real controller (FANUC / KUKA / Yaskawa / ABB / Universal Robots). The same model also produces
the cycle time, the quote and the layout drawing for the customer.

The long-term goal is one application where a user, or an AI, can simulate a whole manufacturing area and then use
that same model to run real production. Today the focus is the robotic welding cell.

> Closed source. This page is the public overview and devlog of the project.

---

## What it does

```
 CAD / robot library ──► Cell layout ──► Weld seams ──► Motion plan ──► Verification ──► Controller program
   STEP · STL · GLB       robots, rails,    auto-detect     MoveIt 2       collisions,       FANUC .LS
   URDF · vendor CAD      gantries,         or pick on      (in-process)   reach, zones,     KUKA .src/.dat
   import wizards         positioners,      the model                      signals, PLC,     Yaskawa .JBI
                          conveyors, fences                                cycle time        ABB .mod · UR .script
                                                                                             + setup notes
                                       ◄── Read back from the controller (all 5 brands) ──┘
```

### Cell design
- Industrial robot library (FANUC, KUKA, ABB, Yaskawa Motoman, Universal Robots and more), tools attached at runtime with their TCP.
- **Import wizards** for vendor CAD, so the user brings the real models:
  - **robots** from STEP or RobotStudio GLB: links, joint axes and zero pose are suggested from the geometry and checked against the datasheet reach;
  - **tools** (torches, grippers): units, orientation, nozzle / TCP suggestion;
  - **mechanisms** (gantries, positioners): axes found from the contact geometry, multi-solid STEP files split, fused parts cut with one click.
- **Robot carriers**: linear track, column, gantry, column-and-boom. Several robots can share one carrier.
- **Positioners**: turntable, tilt-rotate, two-station (H-type), headstock-tailstock, or an imported real model.
  Workpieces mount on the table and move with it.
- Factory elements: parametric conveyors, diverters, stoppers, sensors, operator buttons, safety fences with doors and light curtains,
  torch service stations, weld power sources.

### Welding (offline programming)
- **STEP workpiece import** with body roles (part / fixture / excluded). Fillet seams are found automatically from the geometry:
  plate intersections, plus arcs and circles such as pipe-to-plate and rim welds. Seams can also be picked by hand.
- **Batch programming from CAD**: throat size (a-dimension) suggested from the plate thickness → weld procedure (schedule + passes),
  balanced weld sequence against distortion, tack welds first.
- **Weld process**: numbered weld schedules (current, voltage, wire feed, crater), weaving, stitch welding, multi-pass,
  touch sensing (up to 3 searches per seam), arc seam tracking, torch cleaning cycles. Each is simulated, not only written to the program.
- **Torch-aware planning**: torch body collision with the part, a continuous IK chain with no wrist flips, corner strategies
  (torch lean or trim) where a seam runs into a wall, safe approach and retract points.
- **Positioner per seam**: the table angle that gives the best weld position. **Coordinated motion**: the positioner rotates while
  the robot welds circles, with weaving and tracking.
- **Multi-robot cells**: seams shared between robots, positioner-synchronised work sharing, assembly welding
  (one robot holds the part, the other tacks and welds), interlock zones generated automatically.
- **Recipes**: the operator picks a product on the HMI, the PLC sends the number, the robot runs that job. Product families that differ
  only in size can share one parametric job with register offsets.
- **Cell cycle**: operator ready / busy handshake per station, alternating two-station cycles, a job queue for multiple stations.

### Verification
- Motion planning with MoveIt 2 (Pilz PTP / LIN / CIRC), running inside the application with no `move_group` process.
- Collision check of every robot against the cell along a time-synchronised trace; automatic interference zones.
- Signal-based simulation: deterministic clock, robot I/O, a user PLC in IEC 61131-3 Structured Text, safety stops.
- **OPC UA** server and client: the virtual cell can be driven by, or drive, a real PLC.
- **Program assistant**: singularities, joint limits, cable twist, long joint moves, with one-click fixes.
- **Weld assistant**: when a seam cannot be welded, it searches for a robot or part move that fixes it, and draws a floor reach map.
- **Simulator trace comparison**: load a joint recording from the vendor simulator and compare it line by line with the plan
  (point, path and time differences).
- **Cycle time** is calibrated against the vendor simulators and kept on the safe side: the estimate may be slightly longer than the
  controller, never shorter.

### Export to the real controller
- **Post-processors**: FANUC `.LS` (ArcTool, GP2 positioner group), KUKA `.src` / `.dat`, Yaskawa `.JBI`, ABB RAPID `.mod`
  (RobotWare Arc / ArcWare data, independent-axis reset), URScript `.script`.
- **Setup notes for the field**: tool and user frame values with their teach points, external axis mapping, weld schedules,
  recipe registers, and warnings for each brand's menu.
- **User frame calibration**: define a 3-point frame on the part and teach the same 3 points on site; *Align from site* moves the digital
  part to its measured position.
- **Reverse post**: read a touched-up program back from the controller (all 5 brands) and verify it in the digital twin.
- **Simulator cell model**: fixtures and tool exported as STL, placed for the robot simulator.

### Sales tools
- **Cost and quote**: cycle time, arc time, wire, gas and energy per part, yearly capacity and ROI, from the user's own price table → PDF.
- **Bill of materials**: robots, positioners, fences, power sources, with the user's product codes and prices.
- **Layout drawing**: ISO technical drawing with hidden-line views, dimensions, title block and parts list → PDF / DXF.

---

## Validation

| Test | Result |
|---|---|
| FANUC ROBOGUIDE (R-30iB Plus, M-10iA, ArcTool): program export | Joint values and TCP match the simulation within **0.1 mm / 0.01°** |
| FANUC ROBOGUIDE: user frame taught from 3 points, part shifted on site | Program follows the re-taught frame. A reach-limit case led to the reach margin check |
| FANUC ROBOGUIDE: 1-axis and 2-axis servo positioners (GP2) | All welds on the seam. Cycle time on the 2-axis cell: robot moves **+0.9 %**, total **+5 %** (safe side) |
| ABB RobotStudio (RobotWare 7, OmniCore, IRB 1600) | Fine points within **0.001° / 0.02 mm**, path within **0.03 mm** of the plan |
| ABB RobotStudio: IRBP positioner, coordinated circle, weaving, ArcWare data | Runs as planned; cycle time slightly longer than RobotStudio by design |
| Automated test suite | **55 test programs**: kinematics, planning, weld planning, post-processor read-back (exported points re-checked with FK), reverse post round trips, calibration, factory flow, PLC, OPC UA |

**Not yet validated:**
- on a physical robot;
- KUKA / Yaskawa / Universal Robots output in their own simulators;
- the FANUC weld package instructions (weaving, seam tracking, touch sensing, multi-pass) in ROBOGUIDE: next test.

---

## Architecture

- **C++17 · Qt 5 · VTK 9** desktop application (~100k lines).
- **ROS 2 Humble · MoveIt 2** used as libraries: an in-process `RobotModel`, Pilz industrial planner, KDL / TRAC-IK kinematics.
- **Pure modules with no UI dependency**, each covered by headless tests:

  | Module | Role |
  |---|---|
  | `weld/` | seam detection, torch model, weld planner, procedures, touch sensing, seam tracking |
  | `post/` | controller code generation and read-back |
  | `planning/` | cell model, collision trace, program assistant |
  | `recipe/` | product recipes and parametric jobs |
  | `factory/` | flow simulation and cell equipment |
  | `plc/` | Structured Text interpreter |
  | `verify/` | simulator trace comparison |
  | `cost/` · `bom/` · `drawing/` | quote, bill of materials, layout drawing |
- **OpenCASCADE** for STEP, **open62541** for OPC UA, **Assimp** for meshes.
- Z-up (REP-103) everywhere. Tools, carriers and positioners are added to an in-memory URDF, and the vendor files are never modified.
- Project files are versioned, with migration, atomic save, autosave and crash recovery.
- Work modes: Engineering (full editing), Operation (run and monitor), SCADA (view only).

---

## Roadmap

- ROBOGUIDE test of the weld package instructions on a headstock-tailstock cell
- Rail and multi-robot validation in the vendor simulators; URSim
- Safety distance calculation (ISO 13855)
- Native Windows build and installer
- Physical robot pilot with an integrator
- Controller connection: upload, start and monitor over the network → live digital twin and SCADA view
- Point cloud input: scan → mesh → seams, on the same planning path

---

## Devlog

### 2026-11-11: Headstock-tailstock positioner
A new positioner type: a driven faceplate on the headstock and an idle tailstock that supports the far end of a long part.
The tailstock turns with the part but is not a controller axis. Long parts are laid along the axis automatically, and a flanged
pipe on the faceplate is welded with a coordinated circle plus positioned rib seams. This cell will host the next ROBOGUIDE test.

### 2026-11-01: Positioner timing checked in two simulators, read-back for all brands
- **FANUC ROBOGUIDE, 2-axis servo positioner**: all welds on the seam. A line-by-line timing comparison with register time stamps
  showed that FANUC scales the positioner with the joint move speed, and that weld start / end take a fixed time. Both are now in the
  cycle-time model: robot moves within +0.9 %, total cycle +5 %.
- **ABB RobotStudio, IRBP positioner**: coordinated welds as split moves with per-step external axis speed, independent-axis
  revolution reset, the positioner returns to zero at the end of the cycle.
- **Reverse post** now reads KUKA, Yaskawa, ABB and URScript programs, not only FANUC.

### 2026-10-29: ABB RobotStudio and simulator trace comparison
The ABB RAPID output runs in RobotStudio. A new tool loads the joint recording from the simulator and compares it with the plan
line by line. The first comparisons found three timing differences in our motion model (slow-speed scaling, acceleration scaling,
ABB's MoveJ speed meaning). All three are fixed.

### 2026-10-25: Reading programs back from the controller
FANUC `.LS` programs can be imported: Cartesian points are solved to the same arm configuration, weld instructions and our own
counter / job-queue patterns come back as editable lines. A program touched up on site can be checked in the digital twin.

### 2026-10-24: Real equipment in the cell
- Import wizards for real robots (STEP / GLB) and real positioners, including two-station positioners.
- Cell cycle: operator buttons, station handshake, job queue, home position for every process.
- ABB RAPID and URScript post-processors.

### 2026-10-22: Sales tools
Cost and quote with ROI, bill of materials, ISO layout drawing, weld power source object. The numbers come from the planned
program, the prices from the user.

### 2026-10-21: Recipes and batch programming from CAD
Weld procedure from the throat size, balanced sequence and tack welds. Product recipes selected by the PLC, with one parametric
job for a family of sizes. A program assistant and a weld assistant that suggests where to move the robot or the part.

### 2026-10-20: Weld process package
Numbered weld schedules, weaving, stitch welding, multi-pass, touch sensing, arc seam tracking and a torch service station.
Each feature is simulated, written to the controller program where the brand has an instruction for it, and listed in the setup notes.

### 2026-10-19: Positioners in ROBOGUIDE, multi-robot cells
A positioner (GP2) program runs in ROBOGUIDE. Several robots can share the seams of one part, also while the positioner turns,
with interlock zones and handshake signals generated automatically. First pick-and-place process (palletizing).

### 2026-10-15: Validated in FANUC ROBOGUIDE
The first end-to-end loop is closed: a cell is designed in ManufacturingOS, the weld path is planned,
the FANUC program is exported and runs in the R-30iB Plus virtual controller.
- Joint values match. FANUC's J2/J3 interaction convention is handled.
- The weld instructions use the R-30iB ArcTool syntax.
- User frames work.
- The setup notes and cell CAD export make the transfer a few minutes of work.

---

**Göktuğ Nuhoğlu**, Founder & Developer
