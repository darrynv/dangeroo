<p align="center">
  <img src=".roo-docs\dangeroo.png" alt="DangerRoo - Boomerang Mode" width="500"/>
</p>

# Dangeroo Mode - (Boomerang) Software Engineering Orchestrator

## Overview

🦘Dangeroo Mode🤖 is an AI-powered system designed to assist with complex software engineering tasks. It operates through a sophisticated orchestration pattern, leveraging specialized AI "modes" to handle different aspects of the software development lifecycle. The central orchestrator, known as "Dangeroo Mode" (internally using Boomerang Mode in RooCode), breaks down large requests into minimal, self-contained subtasks, delegates them to the appropriate specialized mode, tracks progress, manages project context using a persistent memory bank, and implements conditional structured logging for enhanced observability.

The system is designed for robustness, traceability, and high-quality output by combining:
*   **Specialization:** Different modes handle coding, architecture, testing, logging, etc.
*   **Atomicity:** Tasks are broken down into the smallest logical units.
*   **Statefulness:** A structured memory bank (`.roo-docs/`) maintains context, configuration, templates, and logs across sessions.
*   **Advanced Prompting:** Techniques like Step-back, Chain-of-Thought, Self-Consistency, and Structured Outputs are used for clarity and reliability.
*   **Explicit Guardrails:** Specific instructions ensure modes handle failures, safety, and environmental factors predictably.
*   **Conditional Structured Logging:** Detailed task success/failure information is logged in a structured format (using templates) when `DEBUG_MODE` is enabled.

## Core Concepts

### 1. Orchestration (Dangeroo Mode / Boomerang Mode)
Dangeroo Mode acts as the central coordinator. It does not perform specific engineering tasks itself but instead focuses on:
*   **Initial Context Loading:** Delegating to `MemoryKeeper` to load initial state and configuration (including `DEBUG_MODE` status) from `.roo-docs/`.
*   **Task Decomposition:** Applying an "atom-of-thought" approach and evaluating the breakdown for true minimality.
*   **Mode Selection:** Choosing the best specialized mode for each primary subtask.
*   **Instruction Formulation:** Providing detailed, context-rich instructions for primary delegations.
*   **Advanced Prompting:** Utilizing techniques strategically during primary task delegation.
*   **Result Evaluation:** Analyzing the concise `attempt_completion` result from specialized modes to determine success or failure for immediate workflow decisions.
*   **Conditional Logging Orchestration:**
    *   Checking if `DEBUG_MODE` is enabled.
    *   If enabled, delegating a *secondary reporting task* to the *original mode* that completed the primary task, instructing it to fill a standardized JSON template (from `.roo-docs/templates/`) with detailed execution context.
    *   Receiving the filled template data.
    *   Delegating a *logging task* to the dedicated `roo-logger` mode, providing the structured JSON data for persistence.
*   **State Management & Workflow Control:** Deciding the next primary workflow step based on the *core* subtask outcome (e.g., delegate next task, delegate debugging, ask user, delegate core memory updates via `MemoryKeeper`, synthesize).
*   **Synthesis:** Consolidating results upon goal completion and triggering final memory updates.

### 2. Specialized Modes (Delegates)
Each specialized mode is an AI assistant focused on a specific domain, operating strictly under Dangeroo Mode's direction:
*   **`code` (💻 Code):** Writes, modifies, and explains code.
*   **`architect` (🏗️ Architect):** Executes atomic design tasks.
*   **`ask` (❓ Ask):** Answers specific technical questions.
*   **`debug` (🐞 Debug):** Performs specific debugging tasks.
*   **`requirements` (📝 Requirements):** Drafts, clarifies, and documents requirements.
*   **`tester` (🧪 Tester):** Writes tests, generates test data, analyzes results.
*   **`devops` (⚙️ DevOps):** Handles specific CI/CD, infrastructure, build, and deployment tasks.
*   **`writer` (✍️ Technical Writer):** Creates and updates documentation.
*   **`uiux` (🎨 UI/UX Designer):** Provides conceptual UI/UX input.
*   **`security` (🔒 Security Analyst):** Performs specific security reviews.
*   **`memorykeeper` (💾 Memory Keeper):** Executes precise read/write operations on the memory bank files (core context, `.env`, templates).
*   **`roo-logger` (📜 Roo Logger):** Receives pre-formatted JSON log data and appends it to the designated log file(s) (within `.roo-docs/logs/`).

Modes execute their assigned *primary* task and report back *concisely*. If `DEBUG_MODE` is on, the mode that performed the primary task may receive a *secondary* task to provide detailed structured reporting by filling a JSON template.

### 3. Atom-of-Thought Principle
Remains the same: breaking down work into minimal, traceable, manageable units.

### 4. Memory Bank (`.roo-docs/`)
This directory structure is the cornerstone of Roo's statefulness.
*   **Persistence:** Stores project context, decisions, progress, history, configuration, templates, and detailed logs.
*   **Structure:** Organized into key files and directories:
    *   `.roo-docs/projectbrief.md`: Core goals.
    *   `.roo-docs/productContext.md`: The "why" and user goals.
    *   `.roo-docs/systemPatterns.md`: Architecture and design.
    *   `.roo-docs/techContext.md`: Tech stack, environment details.
    *   `.roo-docs/activeContext.md`: Current focus, recent decisions.
    *   `.roo-docs/progress.md`: High-level status, issues, roadmap.
    *   `.roo-docs/.env`: Configuration variables (e.g., `DEBUG_MODE=TRUE`).
    *   `.roo-docs/templates/`: Contains JSON templates (`task_completion_template.json`, `issue_report_template.json`).
    *   `.roo-docs/logs/`: Contains structured log files (e.g., `activity.log`).
    *   *(Other files/folders as needed)*
*   **Usage:** Dangeroo Mode orchestrates interactions via `MemoryKeeper` (for core files, `.env`, templates) and `roo-logger` (for `logs/`). The memory bank provides context for decision-making and stores detailed operational history when debugging is enabled.

## Workflow Logic (Flowchart)

The following diagram illustrates the updated interaction flow, including the two-stage conditional logging process:

```mermaid
flowchart TD
    subgraph ProjectMemoryBank [Memory Bank - Single Source of Truth]
        direction LR
        K1[projectbrief.md]
        K2[productContext.md]
        K3[systemPatterns.md]
        K4[techContext.md]
        K5[activeContext.md]
        K6[progress.md]
        K_Env[.env]
        K_Logs[logs/]
        K_Tmpl[templates/]
        K_Other[...]
    end

    subgraph BoomerangOrchestration [Boomerang Orchestration Process]
        direction TB
        A["Start | Receive User Request"] --> B_delegate[Delegate Initial Memory Review/Setup Task]
        B_delegate --> B_exec["MemoryKeeper: Read Context / Create Files"]
        B_exec --> B_res["MemoryKeeper: Return Context / Confirm Setup"]
        B_res -- Provides Initial Context --> C["Atom-of-Thought Breakdown & Evaluation"]

        C --> D[Select Appropriate Specialized Mode]
        D --> J[Formulate Subtask Instructions]

        subgraph SubtaskInstructionDetails [Instructions for Delegated Mode]
            direction TB
            J1["Context (Initial & Ongoing)"]
            J2[Clearly Defined Scope]
            J_EnvAware[Note: Environment Assumptions]
            J3[Constraint: Only Perform Outlined Work]
            J_Safety[Constraint: Safety Check before Risky Tools]
            J_Idem[Note: Strive for Idempotency/Minimal Side Effects]
            J4[Requirement: Signal Completion via 'attempt_completion']
            J4a[Requirement: Report Failures via 'attempt_completion' w/ Details]
            J5["Requirement: Provide Concise Result Summary (Success/Failure)"]
            J6[Rule: These Instructions Override Mode Defaults]
        end

        J --> D_delegate[Delegate Subtask via 'new_task' Tool]
        D_delegate --> S[Specialized Mode Executes Primary Atomic Subtask]

        %% --- Safety Check Loop ---
        S --> S_check{Risky Tool Use?}
        S_check -- Yes --> S_ask[Subtask asks Boomerang]
        S_ask --> E_q[Boomerang Evaluates Safety]
        E_q --> S_confirm[Boomerang Confirms/Denies]
        S_confirm --> S
        %% --- Safety Check Loop END ---

        S_check -- No --> S_comp["Subtask Signals Completion ('attempt_completion')"]

        S_comp --> S_res["Subtask Provides Concise Result Summary (Success/Failure)"]
        S_res --> E[Boomerang: Monitor & Analyze Concise Result]

        %% --- Conditional Logging START ---
        E --> E_checkEnv[Delegate: Read DEBUG_MODE from K_Env]
        E_checkEnv --> E_envRes[MemoryKeeper Returns DEBUG_MODE Status]
        E_envRes --> E_debugDecision{DEBUG_MODE == TRUE?}

        E_debugDecision -- Yes --> L_delegate_report["Delegate Reporting Task\n(to Original Mode)"]
        L_delegate_report --> L_report_exec["Original Mode: Fill Template\n(Reads K_Tmpl, uses task context)"]
        L_report_exec --> L_report_res["Original Mode: Return Filled Template (JSON)"]

        L_report_res -- Provides Filled Template --> L_delegate_log["Delegate Logging Task\n(to RooLogger)"]
        L_delegate_log --> L_exec["RooLogger: Append JSON to Log File (in K_Logs)"]
        L_exec --> L_res["RooLogger: Confirm Log Append"]
        L_res --> F 

        E_debugDecision -- No --> F
        %% --- Conditional Logging END ---


        F{"Significant Result | Decision | State Change Requiring Immediate Core Memory Update?"}
        F -- Yes --> I_delegate[Delegate Core Memory Update Task]
        I_delegate --> I_exec["MemoryKeeper Updates Core File(s) (K1-K6)"]
        I_exec --> G

        F -- No --> G


        G{All Subtasks for Current Goal / Phase Completed?}
        G -- No --> C
        G -- Yes --> H[Boomerang: Synthesize Results for Completed Goal]
        H --> I_final_delegate[Delegate Final/Comprehensive Memory Update Task]
        I_final_delegate --> I_final_exec[MemoryKeeper Performs Comprehensive Update]
        I_final_exec --> Z["Goal Complete | Report Synthesis to User | Await Next Major Task"]
    end

    %% --- Connections ---
    B_exec -- Updates/Reads --> ProjectMemoryBank
    L_report_exec -- Reads --> K_Tmpl
    L_exec -- Writes --> K_Logs
    I_exec -- Updates --> ProjectMemoryBank
    I_final_exec -- Updates --> ProjectMemoryBank


    %% --- Styling ---
    classDef process fill:#e6f5d0,stroke:#6b8e23,stroke-width:2px
    classDef decision fill:#fffacd,stroke:#daa520,stroke-width:2px
    classDef memory fill:#ffe4e1,stroke:#cd5c5c,stroke-width:2px
    classDef instruction fill:#f0f8ff,stroke:#4682b4,stroke-width:2px
    classDef subtask fill:#fff8dc,stroke:#b8860b,stroke-width:2px,stroke-dasharray:5 5
    classDef delegate fill:#e0ffff,stroke:#008b8b,stroke-width:2px
    classDef safety fill:#fff0f5,stroke:#ff69b4,stroke-width:2px
    classDef initial_mem fill:#f5f5dc,stroke:#8b4513,stroke-width:2px
    classDef logging fill:#fafad2,stroke:#b0e0e6,stroke-width:2px
    classDef report fill:#e6e6fa,stroke:#9370db,stroke-width:2px

    class A,C,D,E,H,Z process
    class F,G,S_check,E_debugDecision decision
    class ProjectMemoryBank,K1,K2,K3,K4,K5,K6,K_Env,K_Logs,K_Tmpl,K_Other,I_exec,I_final_exec memory
    class J,J1,J2,J3,J4,J4a,J5,J6,J_EnvAware,J_Safety,J_Idem instruction
    class S,S_comp,S_res subtask
    class D_delegate,I_delegate,I_final_delegate,B_delegate,L_delegate_report,L_delegate_log,E_checkEnv delegate
    class S_ask,E_q,S_confirm safety
    class B_exec,B_res initial_mem
    class L_report_exec,L_report_res report
    class L_exec,L_res logging
    class E_envRes initial_mem
```

## Workflow Explanation (Updated)
1.  Dangeroo Mode initiates context loading via `MemoryKeeper` (`B_delegate` -> `B_res`).
2.  It breaks down the user request (`C`), ensuring atomicity.
3.  It delegates the primary subtask (`D_delegate`) to a specialized mode (`S`).
4.  **Safety Check:** The mode checks for risky operations (`S_check`) and requests confirmation from Dangeroo if needed (`S_ask` loop).
5.  **Completion:** The mode completes the primary task, reporting a *concise* success/failure summary (`S_comp` -> `S_res`).
6.  **Evaluation:** Dangeroo analyzes this concise result (`E`).
7.  **Conditional Logging:**
    *   Dangeroo checks `DEBUG_MODE` (`E_checkEnv` -> `E_debugDecision`).
    *   If TRUE, Dangeroo delegates a secondary 'reporting' task to the *original mode* (`L_delegate_report`).
    *   The original mode fills the relevant JSON template (Success/Failure) using its recent context (`L_report_exec`) and returns the filled JSON (`L_report_res`).
    *   Dangeroo delegates a 'logging' task to `roo-logger`, passing the filled JSON (`L_delegate_log`).
    *   `roo-logger` appends the JSON to the log file (`L_exec` -> `L_res`).
8.  **Core Workflow Continuation:** The flow proceeds to decision point `F`, based on the *concise result* from step 5.
9.  **Core Memory Update:** Dangeroo decides if an *immediate* update to core memory files (like `progress.md`) is needed based on the concise result (`F`) and delegates to `MemoryKeeper` if required (`I_delegate` -> `I_exec`).
10. **Next Step Decision:** Dangeroo determines if more primary subtasks are needed (`G`). If yes, loop back to breakdown (`C`). If no (goal complete), proceed to synthesis (`H`).
11. **Finalization:** Synthesize results (`H`), delegate final comprehensive core memory updates (`I_final_delegate` -> `I_final_exec`), and report to the user (`Z`).

## Advanced Prompting Techniques (Includes minor clarification)

Dangeroo Mode employs several techniques to improve the quality and reliability of the workflow:

-   **Step-back Prompting:** Used by Dangeroo Mode when a user request is ambiguous or a path forward isn't clear. It involves asking clarifying questions or exploring options *before* delegating subtasks.
    ```mermaid
    flowchart LR
        A["Ambiguous User Request"] --> B["Dangeroo Mode Steps Back"]
        B --> C["Clear Path Forward"]
        B --> D["Ask Clarifying Questions"]
        D -->|"Clarification"| B

        classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px,color:#333
        classDef focus fill:#d4e6f1,stroke:#2874a6,stroke-width:2px,color:#000

        class B focus
    ```
-   **Chain-of-Thought (CoT):** Dangeroo Mode may explicitly request specialized modes to include concise reasoning steps in their *concise* result summary or, more likely, request it as part of the *detailed reporting task* (when `DEBUG_MODE` is on). This aids transparency and debugging. CoT results may be stored in the memory bank or the detailed logs.
    ```mermaid
    flowchart LR
        A["Complex Task"] --> B["Dangeroo Mode Requests CoT\n(in primary or reporting task)"]
        B --> C["Specialized Mode Execution"]
        C --> D["Transparent Result/Report"]

        C --> E["Include reasoning steps\nin summary/template"]
        E --> B

        classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px,color:#333
        classDef focus fill:#d4e6f1,stroke:#2874a6,stroke-width:2px,color:#000
        classDef reasoning fill:#d5f5e3,stroke:#1e8449,stroke-width:2px,color:#000

        class B focus
        class E reasoning
    ```
-   **Self-Consistency:** For critical or error-prone subtasks, Dangeroo Mode may ask a mode to generate multiple distinct solutions/outputs during the *primary* task. Dangeroo Mode then analyzes these for consistency or correctness *before* proceeding (Step `E` in main flowchart). Validation outcomes can be stored in the memory bank or logs.
    ```mermaid
    flowchart TD
        A["Critical Task"] --> B["Dangeroo Mode Requests Multiple Solutions"]

        B --> C["Solution A"]
        B --> D["Solution B"]
        B --> E["Solution C"]

        C --> F["Dangeroo Mode Analyzes Consistency (Step E)"]
        D --> F
        E --> F

        F --> G["Final Validated Result/Decision"]

        classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px,color:#333
        classDef focus fill:#d4e6f1,stroke:#2874a6,stroke-width:2px,color:#000
        classDef solution fill:#d5f5e3,stroke:#1e8449,stroke-width:1px,color:#000
        classDef result fill:#ebdef0,stroke:#8e44ad,stroke-width:2px,color:#000

        class B,F focus
        class C,D,E solution
        class G result
    ```

-   **Structured Outputs:** Dangeroo Mode instructs modes to return the *concise* result summary reliably, and explicitly requires JSON format for the *detailed reporting task* (when `DEBUG_MODE` is on) via templates.
    ```mermaid
    flowchart LR
        A["Need for Reliable Data"] --> B["Dangeroo Mode Uses Templates"]

        B --> C["Concise Summary\n(from attempt_completion)"]
        B --"If DEBUG_MODE=TRUE"--> D["Detailed JSON Report\n(from Reporting Task)"]


        C --> F["Input for Immediate\nWorkflow Decision (Step E)"]
        D --> G["Input for Logging\n& Deep Analysis"]

        classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px,color:#333
        classDef focus fill:#d4e6f1,stroke:#2874a6,stroke-width:2px,color:#000
        classDef format fill:#fdebd0,stroke:#d35400,stroke-width:1px,color:#000

        class B focus
        class C,D format
    ```
**Important Note:** Specialized modes focus on their primary task and concise reporting. They only perform detailed template filling when explicitly given a secondary reporting task by Dangeroo Mode.

## Explicit Guardrails & Failure Handling

Remains the same: Explicit instructions for Failure Reporting, Tool Safety Check, Environment Awareness, and Idempotency/Side Effects ensure predictable and robust behavior from specialized modes.

## Usage

Remains the same: Interact with Dangeroo Mode, provide high-level goals.

## Structured Logging Templates

JSON templates for successful task completion and issue reporting are stored in `.roo-docs/templates/`. These are filled by the original specialized mode during the secondary reporting task (if `DEBUG_MODE` is enabled) and then passed to `roo-logger` for persistence in `.roo-docs/logs/`. This provides detailed, structured data for observability and future analysis.

## `.roomodes.initialise` (Note)

The `.roomodes.initialise` prompt mentioned previously serves as a conceptual starting point for bootstrapping the *initial content* of the `.roo-docs/` memory bank by analyzing an existing codebase. It would need to be adapted and executed (likely via Dangeroo Mode delegating analysis tasks) when starting work on a pre-existing project.

## Conclusion

The Dangeroo AI system, orchestrated by Dangeroo Mode, represents a structured and robust approach to leveraging LLMs for software engineering. By combining specialization, atomicity, persistent memory, advanced prompting, explicit guardrails, and conditional structured logging, it aims to provide reliable, traceable, observable, and high-quality assistance across the development lifecycle.