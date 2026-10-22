# Agentic AI Distributed Computing Platform

An enterprise-style Django application that implements the concepts from:

`14 Agentic AI Framework for Adaptive Distributed Computing Architecture.pdf`

The project demonstrates:

- Agentic AI workflow orchestration
- Multi-agent planning and coordination
- Monitoring, preprocessing, feature selection, and prediction
- Distributed execution and feedback loops
- Groq-first LLM integration with OpenRouter fallback
- SQLite-backed persistence for agents, workflows, executions, memory, and traces

## Project Overview

This repository started as a simple identity-oriented Django app. It now includes a paper-aligned agentic workflow layer that presents the research concepts as a functional enterprise platform:

- `users` app for operator access, workflow studio, and execution monitor
- `admins` app for governance and registry oversight
- `agentic` app for the LangGraph-based execution engine and workflow data model

The UI remains a polished enterprise dashboard, but the backend now stores and executes workflow state instead of serving static demo content.

## Research Paper Objective

The paper proposes an adaptive distributed computing architecture that uses:

- real-time telemetry monitoring
- sliding-window normalization
- missing-value imputation
- mRMR feature selection
- XGBoost prediction
- agentic decision-making
- Kubernetes orchestration

This implementation translates those ideas into a practical software demo with:

- planner, coordinator, executor, validator, monitoring, and feedback agents
- execution history and traceability
- sample workflows and metrics
- visual workflow graphs

## Implemented Architecture

### Apps

- `users`
  - agent workspace
  - workflow studio
  - execution monitor
  - login and registration
- `admins`
  - governance console
  - user registry actions
- `agentic`
  - workflow models
  - execution engine
  - demo seeding
  - snapshot metrics

### LangGraph Workflow

The workflow engine uses a `StateGraph` with these nodes:

- `memory`
- `planner`
- `coordinator`
- `executor`
- `monitor`
- `validator`
- `feedback`

Execution flow:

1. Memory node loads prior context.
2. Planner node creates a paper-aligned plan.
3. Coordinator node distributes work to agents.
4. Executor node runs tasks in parallel.
5. Monitoring node aggregates metrics.
6. Validator node determines completion or re-plan.
7. Feedback node stores memory and closes the loop.

## Technology Stack

- Django
- SQLite
- LangGraph
- Groq API
- OpenRouter API
- Bootstrap 5
- Font Awesome
- Mermaid.js

## Folder Structure

```text
AgenticAIDistributedComputing/
  AgenticAIDistributedComputing/
    settings.py
    urls.py
    views.py
  admins/
    views.py
    admin.py
  users/
    views.py
    forms.py
    admin.py
    models.py
  agentic/
    models.py
    services.py
    admin.py
    management/
      commands/
        seed_agentic_demo.py
  assets/
    templates/
    static/
  db.sqlite3
```

## Database Schema

The new `agentic` app adds these tables:

- `AgentProfile`
- `WorkflowDefinition`
- `WorkflowExecution`
- `AgentTask`
- `MemoryStore`
- `ExecutionTrace`

### Key Fields

- `AgentProfile`
  - role, specialization, status, health score, load
- `WorkflowDefinition`
  - objective, description, Mermaid diagram, sample prompt
- `WorkflowExecution`
  - prompt, summary, status, metrics, snapshot, duration
- `AgentTask`
  - task order, assigned agent, output snapshot, duration
- `MemoryStore`
  - memory key/value pairs with importance
- `ExecutionTrace`
  - node-level decision trace for execution history

## Groq and OpenRouter Integration

The LLM helper in `agentic/services.py` works in this order:

1. Groq
2. OpenRouter
3. deterministic local fallback

The code reads configuration from `settings.py`:

- `GROQ_API_KEY`
- `GROQ_MODEL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`

If both APIs are unavailable, the engine still runs using a deterministic response generator so the demo remains usable.

## New Menus

The `users` app now exposes three paper-aligned menus:

- `Agent Workspace`
- `Workflow Studio`
- `Execution Monitor`

These are available through the user navigation after login.

## Dashboard Pages

### Agent Workspace

Shows:

- active agents
- running workflows
- completed workflows
- failed workflows
- agent health
- resource utilization
- workflow catalog
- recent execution history

### Workflow Studio

Shows:

- workflow selector
- execution form
- Mermaid workflow graph
- workflow catalogue
- recent workflow executions

### Execution Monitor

Shows:

- execution history
- selected workflow details
- decision trace
- task breakdown
- metrics panel

## Demo Data

Populate the demo catalogue and create a sample execution with:

```bash
python manage.py seed_agentic_demo --run-sample
```

This seeds:

- 6 demo agents
- 2 workflow definitions
- 1 sample workflow execution

The sample execution runs in offline fallback mode if external LLM access is unavailable.

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Seed demo data:

```bash
python manage.py seed_agentic_demo --run-sample
```

5. Start the server:

```bash
python manage.py runserver
```

## Configuration

Relevant settings in `AgenticAIDistributedComputing/settings.py`:

- `GROQ_API_KEY`
- `GROQ_MODEL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `STATICFILES_DIRS`
- `MEDIA_ROOT`

## Sample Inputs

Use prompts like:

- `Analyze resource contention across distributed nodes and propose a proactive scaling plan.`
- `Handle a latency spike and node failure while keeping the response-time target stable.`
- `Create an adaptive orchestration plan for a heterogeneous distributed cluster.`

## Expected Outputs

The platform will show:

- a planning summary
- distributed task assignment
- execution traces
- workflow metrics
- a final report

If LLM APIs are unavailable, the platform still generates deterministic output and stores the workflow state.

## Example Execution Flow

1. User opens `Workflow Studio`.
2. User selects a workflow definition.
3. User submits a distributed task prompt.
4. Planner creates a structured execution plan.
5. Coordinator assigns tasks to agents.
6. Executor runs tasks in parallel.
7. Monitor records runtime metrics.
8. Validator decides whether the flow completes or replans.
9. Feedback node stores execution memory.
10. Execution Monitor shows history and traces.

## Screenshots

Add screenshots here when preparing a final report:

- `docs/screenshots/agent-workspace.png`
- `docs/screenshots/workflow-studio.png`
- `docs/screenshots/execution-monitor.png`
- `docs/screenshots/governance-console.png`

## Future Enhancements

- True persisted agent communication channels
- Live charts for metrics
- More detailed task replay and rerun controls
- Per-agent memory segmentation
- Dockerized deployment
- Better production secret management

## Limitations

- The project is a research-to-product demo, not a full distributed cluster manager.
- External LLM calls depend on configured API keys and network availability.
- The current workflow focuses on educational traceability and UI demonstration.
- Authentication remains simple and should be hardened for real production use.

## Troubleshooting

- If migrations are missing, run `python manage.py migrate`.
- If the pages show no workflows or agents, run `python manage.py seed_agentic_demo --run-sample`.
- If Groq and OpenRouter are unavailable, the engine falls back to deterministic text generation.

## References

- `14 Agentic AI Framework for Adaptive Distributed Computing Architecture.pdf`
- LangGraph documentation
- Django documentation
- Groq API documentation
- OpenRouter API documentation
