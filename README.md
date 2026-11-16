# ManufacturingOS

**Robot cell design, offline programming and digital twin, in one desktop application.**

Design a robotic cell, plan the motion, verify it against collisions and the cell's signals, then export a program
that runs on the real controller (FANUC / KUKA / Yaskawa / ABB / Universal Robots). The same model also produces
the cycle time, the quote and the layout drawing for the customer.

The long-term goal is one application where a user, or an AI, can design and simulate a whole production system, from robot
cells to the machines around them, and then use that same model to run real production, whatever the hardware brand.
Today the focus is robotic cells: arc welding, spot welding, handling and machine tending.

> Closed source. This page is the public overview and devlog of the project.

---

## Vision

**One vendor-neutral layer above every machine in the factory.**

A manufacturer should be able to say *"I want to produce this"*, load or design the product and the production system in
ManufacturingOS, simulate it until the result is right, and then go to the physical installation with everything ready:
the robot programs, the PLC code, the safety settings, the layout, the bill of materials and the commissioning steps.

- **Any production system, not only robot arms.** Robot cells today; next, the machines around them: coil winders, press
  brakes, lathes, 3D printers, conveyor lines. Each one is a mechanism with actuators (servo, VFD, pneumatic, hydraulic),
  sensors and its control logic, designed and simulated in the same model.
- **The hardware brand does not matter.** Robots get their native program through a post-processor (FANUC, KUKA, ABB,
  Yaskawa, Universal Robots). PLCs will get theirs the same way: one control program in the application, generated as
  Siemens SCL, CODESYS / TwinCAT (PLCopen XML) and more, then checked in each vendor's virtual controller, just as the robot
  output is checked in ROBOGUIDE, RobotStudio and URSim.
- **Pay for what you use.** Features are separate modules. A small weld shop takes single-robot welding and the post for its
  robot. A car plant takes multi-robot welding, PLC, conveyors and safety. No stack of separate tools and licences.
- **Built to be driven by an AI, too.** The whole model (layout, programs, signals, PLC code) is structured data with
  headless verification, so an agent can design, simulate and check a production system the way an engineer does.
- **From design to operation.** The same model stays connected to the running plant over OPC UA and the controller links:
  live digital twin, SCADA view, and later predictive maintenance.

The first step on the machine side is a PLC code generator and a demo factory that builds a robot: a coil winding machine and
a press brake, each tended by a robot arm, conveyors merging into one line, and cobots assembling on a table.

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
- **Tools**: arc welding torches, grippers (vacuum, parallel, magnet, vendor models, imported STEP) with **several TCPs on one gripper**
  that grip independently, and **spot welding guns** (parametric C and X guns, or the maker's STEP with its moving arm picked in the wizard).
- Factory elements: parametric conveyors, diverters, stoppers, sensors, operator buttons, safety fences with doors and light curtains,
  torch service stations, weld power sources, process stations (CNC / press / test bench as a black box with a cycle time), part trays
  refilled by an operator, line stations that hold a car body while robots work on it.

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

### Handling and machine tending
- **Pick and place / palletizing**: from a conveyor stopper or a picked point to a pallet pattern, with approach and grip checks.
- **Machine tending with a dual gripper**: take the raw part, unload the finished part from the machine, load the raw one, put the finished
  part on the output tray, with the machine's start / done signals wired. A single-TCP variant is generated too.
- **Held parts are obstacles**: while the gripper holds a part, the part itself is checked against the cell during planning.

### Spot welding (body-in-white demo)
- A parametric car body (88 sheets and profiles, 6 build stages) and a 62 m body line with 5 stations: framing gate with side-panel loaders,
  roof, respot, doors, hood and decklid, 19 robots, 38 spot welds.
- Spot points are placed like on a real line: the fixed electrode on the inner face of the sheet stack, the gun throat open to the free edge,
  approach and retract in the sheet plane. The moving electrode stops on the first sheet it meets during closing.
- Station handshakes (body ready → robots → done) and the car body at the station is an obstacle for every robot plan.

### Verification
- Motion planning with MoveIt 2 (Pilz PTP / LIN / CIRC), running inside the application with no `move_group` process.
- Collision check of every robot against the cell along a time-synchronised trace; automatic interference zones.
- Signal-based simulation: deterministic clock, robot I/O, a user PLC in IEC 61131-3 Structured Text, safety stops.
- **OPC UA** server and client: the virtual cell can be driven by, or drive, a real PLC.
- **Program assistant**: singularities, joint limits, cable twist, long joint moves, with one-click fixes.
- **Weld assistant**: when a seam cannot be welded, it searches for a robot or part move that fixes it, and draws a floor reach map.
- **Simulator trace comparison**: load a joint recording from the vendor simulator and compare it line by line with the plan
  (point, path and time differences).
- **Live collision monitoring** during the simulation, adaptive to how far the robots moved since the last check.
- **Robot-to-robot interlock zones** without a PLC (master / slave handshake over wired I/O), or through a PLC.
- **Cycle time** is calibrated against the vendor simulators and kept on the safe side: the estimate may be slightly longer than the
  controller, never shorter.
- **Safety distances (ISO 13855)**: light curtains, doors and fences checked against each robot's hazard zone, with the stopping
  times from the user → report.
- **Safety configuration proposals**: FANUC DCS joint / Cartesian limits from the program, and Universal Robots safety planes,
  tool limits and reduced-mode speed / force values from ISO/TS 15066.

### Export to the real controller
- **Post-processors**: FANUC `.LS` (ArcTool, GP2 positioner group, Touch Sensing, TAST, crater schedules), KUKA `.src` / `.dat`, Yaskawa `.JBI`, ABB RAPID `.mod`
  (RobotWare Arc / ArcWare data, independent-axis reset), URScript `.script`.
- **Setup notes for the field**: tool and user frame values with their teach points, external axis mapping, weld schedules,
  recipe registers, and warnings for each brand's menu.
- **User frame calibration**: define a 3-point frame on the part and teach the same 3 points on site; *Align from site* moves the digital
  part to its measured position.
- **Reverse post**: read a touched-up program back from the controller (all 5 brands) and verify it in the digital twin.
- **Simulator cell model**: fixtures and tool exported as STL, placed for the robot simulator.

### Commissioning
A step-by-step commissioning window for each robot, for the day the cell is installed:
- **Speed calibration**: the application writes a short test program with timer registers; the user runs it on the controller (or in the
  vendor simulator), types the register values back, and the cycle-time model is fitted to that controller. No line of the fitted model is
  faster than the measurement. Input checks catch a skipped register or the wrong kind of value.
- **Touch-up comparison**: the program read back from the controller is matched line by line with the digital twin; a common shift of
  many points is recognised as a moved part or frame, and the twin can follow it.
- **Tool payload** (mass, centre of gravity, inertia) computed from the tool CAD, written in each brand's units.
- **External axis guide**: positioner and track axes with limits, directions and speeds, and the controller menu steps for each brand.
- **External axis measurement**: the robot touches one fixed point with the axes in different positions; direction, scale, tilt and pivot
  errors of tracks and positioners are found and applied to the twin.
- **Controller axis limits** entered per robot, so the planner never uses a range the real controller refuses.
- **Universal Robots live link**: RTDE connection that mirrors the robot's joints and I/O in the twin, and *Send to robot* for the script.

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
| FANUC ROBOGUIDE: headstock-tailstock cell (1-axis servo positioner + follower) | Weaving, crater fill, TAST seam tracking, multi-station job queue and recipe selection run. Timing findings fed back into the model |
| FANUC ROBOGUIDE: speed calibration on R-2000iC/165F (38 test moves) | Library model **+2.8 %**, fitted model **+1.9 %**, no line shorter than measured |
| FANUC ROBOGUIDE: Touch Sensing, 3 searches, part shifted by (3, −2, 1) mm | Offset found within the simulator's contact resolution (~1 mm); TAST follows the shifted seam |
| FANUC ROBOGUIDE: Touch Sensing on a part rotated about all three axes | Search direction recorded by the controller is **identical** to the planned one (touch frame from the search directions) |
| FANUC ROBOGUIDE: integrated linear rail (M-10iA + 3 m rail) | Joint values within **0.01°**, rail axis correct, four seams on the part |
| FANUC ROBOGUIDE: two robots on two controllers, interlock zone without a PLC | The generated wired DO / DI handshake runs on both controllers as planned |
| Universal Robots URSim: cycle time on 13 models (e-Series, CB3, UR15–UR30) | e-Series plan **+0.6…0.8 %**, CB3 **+2.5…2.8 %** longer than URSim (safe side); points within **0.01 mm** |
| URSim: weld cell (UR5e, MIG torch, weaving) and pick and place (UR5e, Robotiq 2F-85) | Total **+0.1 %**; joint points within **0.001°** |
| Two URSims: assembly cell (one UR10e holds the tube, the other tacks and welds) | Lines within **±0.05 s**, the four weld arcs on the circle within **0.00 mm**; interlock zone with simultaneous requests, no conflict |
| URSim: programs written in PolyScope read back | Taught joints, frames, loops and the Script node come back as the original program |
| Automated test suite | **83 test programs**: kinematics, planning, weld planning, post-processor read-back (exported points re-checked with FK), reverse post round trips, calibration, factory flow, spot welding line, PLC, OPC UA |

FANUC and Universal Robots outputs are now closed on the simulator side; the next changes come from field feedback.

**Not yet validated:**
- on a physical robot;
- KUKA / Yaskawa output in their own simulators;
- Robotiq URCap mode and real fieldbus PLC on site.

---

## Architecture

- **C++17 · Qt 5 · VTK 9** desktop application (~100k lines of C++).
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

- **PLC code generation**: one control program → Siemens SCL, CODESYS / TwinCAT (PLCopen XML), checked in the vendors' virtual PLCs
- **Machine layer**: actuators (servo, VFD, pneumatic, hydraulic), sensors and PLCopen motion blocks (gearing, cams) for any machine
- Demo factory: coil winder and press brake tended by robots, merging conveyors, cobot assembly table
- KUKA and Yaskawa simulator validation
- Commissioning report (PDF)
- Native Windows build and installer
- Physical robot pilot with an integrator
- Controller connection: upload, start and monitor over the network → live digital twin and SCADA view
- Point cloud input: scan → mesh → seams, on the same planning path

---

## Devlog

### 2026-11-16: Spot welding line, machine tending, faster simulation
- **Spot welding**: parametric C and X guns, or the gun maker's STEP. A parametric car body and a 62 m body-in-white line with 19 robots
  and 38 spot welds run end to end with zero collisions in the cell check. The car body waiting at a station, the gantry posts and the
  part a robot is holding are all obstacles for the planner.
- **Machine tending**: a dual gripper (two TCPs) unloads and loads a process station in one visit; the program and the signal wiring are
  generated together.
- **Simulation speed**: profiling the body line showed that drawing cost depends on the number of scene objects, not triangles, and that
  every robot step updated every tool in the scene. After the fixes the 19-robot line runs at 0.9–1.0× real time (before: 0.6–0.9×), at 5× the
  frame rate went from 1–3 to 8–12 fps, and the toolbar shows the achieved speed whenever the computer cannot keep up with the selected one.

### 2026-11-15: Universal Robots validated in URSim
The UR output was checked in URSim on 13 robot models: a timing model fitted to the UR controller (cycle times now slightly longer than
URSim, never shorter), weld and pick-and-place cells, an assembly cell on two URSims connected through their I/O, weaving, PLC register mode,
safety proposals from ISO/TS 15066, payload charts, a live RTDE link and reading back programs written by hand in PolyScope.

### 2026-11-14: Integrated rail and robot-to-robot interlock in ROBOGUIDE
A robot on an integrated 3 m rail welds its four seams in ROBOGUIDE with the joint values of the plan. Two robots on two separate
controllers share an interlock zone with a wired handshake and no PLC. External axes can be measured on site with one fixed point.

### 2026-11-14: Touch sensing validated in ROBOGUIDE
Weld seams can now be found by touching the part with the wire before welding, using the FANUC Touch Sensing instructions.
The application writes the searches, the shifted weld lines, the touch frames and schedules, and the mastering steps.
A test cell with a T-joint (one side touch sensing, the other TAST) was checked in ROBOGUIDE in three steps: aligned part, part rotated
30°, and part rotated about all three axes. The search directions computed by the application match the controller exactly. The
measured offsets agree within the simulator's contact resolution.

### 2026-11-13: Commissioning window and speed calibration
A new window guides the installation of a cell: tool payload, frames, speed calibration, comparison with the program on the
controller. The speed calibration fits the cycle-time model to the real controller from one short test program. On a FANUC
R-2000iC/165F in ROBOGUIDE the fitted model is within +1.9 %, and still never faster than the controller.

### 2026-11-12: Weld package on a headstock-tailstock cell, ISO 13855
The full weld package (weaving, crater, TAST, job queue, recipes) was run in ROBOGUIDE on a 1-axis positioner with a tailstock.
The test found the FANUC crater schedule rule, the weave dwell type, and the arc end time. All are now in the post-processor and
the cycle-time model. Safety distances of light curtains and doors are calculated to ISO 13855.

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
