# POC — VRF RL Training

## Charts

- [State Machine](#state-machine)
- [01 — Create VRF Scenario (Sequence)](#01--create-vrf-scenario-sequence)
- [02 — Create Red-Skies Scenario (Sequence)](#02--create-red-skies-scenario-sequence)
- [03 — Training Mode Lockstep (Sequence)](#03--training-mode-lockstep-sequence)
- [04 — Inference Mode Async (Sequence)](#04--inference-mode-async-sequence)

## State Machine

Source: `state_machine.md`

```mermaid
stateDiagram-v2
    direction LR

    [*] --> Idle

    Idle --> LoadingScenario : load_scenario()
    LoadingScenario --> Frozen : scenario_loaded

    Frozen --> InitializingRedSkies : initialize_redskies()
    note right of InitializingRedSkies
        set_entity_state(lat, lon, heading, speed)
        set_step_speed(20Hz / 50ms)
    end note

    InitializingRedSkies --> BroadcastState : init_complete

    BroadcastState : broadcast entity_state

    %% Training: freeze immediately after broadcast.
    BroadcastState --> Frozen : training_mode

    %% Training: each tick progresses one step.
    Frozen --> ProcessingStep : training_tick

    %% Inference: after broadcast, continue stepping.
    BroadcastState --> ProcessingStep : inference_mode

    %% After step, check if an action was provided.
    ProcessingStep --> ProcessingAction : action_provided(entity_id, autopilot_cmd)
    ProcessingStep --> BroadcastState : no_action

    ProcessingAction --> BroadcastState : action_applied

    Frozen --> Idle : reset_engine()

    ProcessingAction --> Idle : stop_scenario()
```

## 01 — Create VRF Scenario (Sequence)

Source: `01_create_vrf_scenario.sequence.md`

```mermaid
sequenceDiagram
autonumber

actor User
participant VRFEditor as VRF Scenario Editor (UI/CLI)
participant VRFStore as VRF Scenario/Mission Store

note over User,VRFStore: Use-case 1: Create VRF scenario file + basic mission
note over User,VRFStore: For POC: 1 blue player + 1 red player
note over User,VRFStore: Outputs: mission_id/file_id + entity_id(s)

User->>VRFEditor: Create simple VRF scenario
VRFEditor->>VRFEditor: Add entities
note right of VRFEditor: Examples:<br/>Blue jet aircraft<br/>Red jet aircraft<br/>Anti-aircraft entity (optional)

User->>VRFEditor: Create basic mission
note right of VRFEditor: Define objectives / rules / start conditions

User->>VRFEditor: Manually place blue_entity
note right of VRFEditor: Choose desired location<br/>(lat/lon/alt/heading or editor coordinates)

VRFEditor->>VRFStore: Save scenario/mission
VRFStore-->>VRFEditor: Return IDs
note right of VRFEditor: mission_id or file_id<br/>blue_entity_id (+ optional red_entity_id)

VRFEditor-->>User: Provide mission_id/file_id and blue_entity_id
```

## 02 — Create Red-Skies Scenario (Sequence)

Source: `02_create_red_skies_scenario.sequence.md`

```mermaid
sequenceDiagram
autonumber

actor User
participant RSAuthor as Red-Skies Scenario Authoring
participant ObjectsYaml as objects.yaml (config file)
participant VRFStore as VRF Scenario/Mission Store

note over User,ObjectsYaml: Use-case 2: Create Red-Skies scenario
note over User,ObjectsYaml: Inputs: VRF mission_id/file_id + blue_entity_id
note over User,ObjectsYaml: For POC: mission_id/file_id is set manually

User->>RSAuthor: Create Red-Skies scenario definition
RSAuthor->>ObjectsYaml: Write objects.yaml
note right of ObjectsYaml: Fields (example intent):<br/>vrf_mission_id or vrf_file_id<br/>blue_entity_id (entity_id)<br/>team/role mappings (blue/red)

RSAuthor->>VRFStore: (Optional) Verify VRF IDs exist
VRFStore-->>RSAuthor: OK (mission/file + entity exists)

RSAuthor-->>User: Scenario ready
note right of User: Result:<br/>Red-Skies scenario references VRF mission/file<br/>Red-Skies scenario pins blue entity_id
```

## 03 — Training Mode Lockstep (Sequence)

Source: `03_training_mode_lockstep.sequence.md`

```mermaid
sequenceDiagram
autonumber

actor User
participant Trainer as Experiment Runner (Training Mode)
participant VRFEngine as VRF Engine (Lockstep Sim)
participant VRFAdapter as VRF Adapter (gRPC/Protobuf)
participant RLAgent as RL Agent

User->>User: Use-case 3 - training mode (lockstep)
User->>User: step_time = 0.02
User->>User: actions = [{entity_id, heading_change_deg}] where heading_change_deg in [-30, +30]

User->>Trainer: Start experiment training mode
Trainer->>Trainer: step_time=0.02
Trainer->>Trainer: load scenario config

Trainer->>VRFAdapter: Initialize
VRFAdapter->>VRFEngine: Load scenario/mission
VRFEngine-->>VRFAdapter: Ready + initial state

loop Each tick (dt=0.02)
Trainer->>VRFEngine: Step 1 tick lockstep
VRFEngine-->>Trainer: Tick complete paused
VRFEngine-->>VRFAdapter: Emit entity_state world_state
VRFAdapter->>VRFAdapter: Forward full world state to RL agent
VRFAdapter->>RLAgent: Observations gRPC Protobuf
RLAgent->>RLAgent: Observations include all entities or full world state
RLAgent->>RLAgent: Compute action
RLAgent->>RLAgent: heading_change only clamp to +/-30 deg
RLAgent->>VRFAdapter: step actions array
VRFAdapter->>VRFAdapter: actions = [{entity_id, heading_change_deg}]
alt entity_id not found
VRFAdapter-->>RLAgent: Error entity_id not found
VRFAdapter-->>Trainer: Report error
else entity_id found
VRFAdapter->>VRFEngine: Apply heading_change to entity
VRFEngine-->>VRFAdapter: Applied
end
VRFAdapter-->>Trainer: Tick finished all processes complete
end

Trainer-->>User: Experiment done (metrics/logs/artifacts)
```

## 04 — Inference Mode Async (Sequence)

Source: `04_inference_mode_async.sequence.md`

```mermaid
sequenceDiagram
autonumber

actor User
participant Runner as Experiment Runner (Inference Mode)
participant VRFEngine as VRF Engine
participant VRFAdapter as VRF Adapter (gRPC/Protobuf)
participant ActionQueue as Action Queue
participant RLAgent as RL Agent

User->>Runner: Start inference run
Runner->>VRFAdapter: Initialize
VRFAdapter->>VRFEngine: Load scenario/mission
VRFEngine-->>VRFAdapter: Ready + initial state

loop Each tick (dt = 0.02)
  VRFEngine-->>VRFAdapter: Emit entity_state / world_state
  VRFAdapter->>RLAgent: Observations gRPC Protobuf
  RLAgent-->>VRFAdapter: (async) action (entity_id, heading_change_deg)
  VRFAdapter->>ActionQueue: enqueue(action)

  note over VRFAdapter,VRFEngine: Adapter checks for a new action just before stepping
  VRFAdapter->>ActionQueue: dequeue_latest_if_any()
  alt action available
    VRFAdapter->>VRFEngine: Apply heading_change to entity
    VRFEngine-->>VRFAdapter: Applied
  else no action
    VRFAdapter->>VRFAdapter: continue
  end

  VRFAdapter->>VRFEngine: step(dt)
  VRFEngine-->>VRFAdapter: step_complete
end

Runner-->>User: Run complete
```
