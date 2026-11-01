# Cubicle supervisor and orchestration plan

Status: design sketch, 2026-11-01. This is proposed, not implemented. See [CLI research](../notes/cli-worker-research.md), [graph prompt](../notes/karpathy-inspired-graph-prompt.md), and [existing hook notes](../AGENT_HOOKS.md).

## Purpose and stopping point

One persistent user-facing supervisor plans and prioritizes work across repositories and delegates bounded coding or non-coding tasks. Cubicle owns durable control-plane state; supervisor and execution backends are replaceable. First prove one bounded, supervised cross-repo assignment end to end, with an inspectable run and evaluation. Stop and decide whether the measured benefit justifies further adapters, scheduling, or infrastructure.

## Existing starting point

The wrappers in src/cubicle/cli.py use execvpe to launch Claude, Codex and Antigravity (agy), passing arguments and an environment marker; they are not process managers. Hooks normalize events via default_config.yaml; db.py stores timestamp, session ID, event type, model and raw JSON in ~/.cubicle/data/telemetry.db. Hook exceptions are swallowed, so an absent event is not proof an action did not happen. Claude can recover a model from a session-start row; coverage differs. The Streamlit dashboard queries the same table. The instructions, prompts, agents, workflows, plugins and Skillex provide shared resources; discover effective instructions and skills per backend instead of assuming uniform injection. docs/CLI.md is a design note, not proof its proposed symlinks exist.

The schema migration removes llm_family, though README still documents it. agy is Antigravity, not Gemini CLI; do not infer Gemini hooks work from it. Current Codex mappings must be tested against the installed version and supported hook API. README says init-hooks --force resets the database; do not use it for investigation.

## Architecture and contracts

~~~text
User ↔ replaceable supervisor (initially a CLI agent + Cubicle skill)
                ↓ task/graph operations
Cubicle control plane: backlog references, context assembly, dispatcher, gates, durable state
                ↓ Worker API
   CLI adapter → codex / claude / gemini subprocess
   native adapter → future model + agent loop + tools
                ↓
     results, events, artifacts, evaluations → SQLite / files
~~~

The supervisor skill calls a narrow Cubicle interface to create tasks, inspect state, request dispatch and review results; provider flags and the only copy of state do not belong in the skill. A future custom supervisor uses the same operations. Keep the existing backlog authoritative until ownership and synchronization are established; link tasks rather than silently duplicating priorities. A skill guides behavior, but permissions, paths, isolation and approval gates need enforcement outside the model.

A **task** defines objective, type, project/repo and revision, scoped inputs and allowed changes, acceptance checks, tool/skill permissions, budget/deadline, expected artifacts and dependencies. A **run** is one attempt by a backend, linked to its task, graph node, parent run and retry predecessor. A provider session can span runs; store a separate backend/session mapping and never equate session with run. A graph version contains nodes, input/output contracts, dependencies, checks and decision history. A node is ready only when required upstream outputs pass gates. Parallel nodes need non-conflicting write scopes.

### Worker API, concretely

This is a local logical interface, not necessarily an HTTP service:

~~~python
handle = worker.start(task_spec, context_manifest, execution_policy)
status = worker.status(handle)                 # state and last observed progress
events = worker.events(handle, after=cursor)   # incremental, possibly incomplete
result = worker.result(handle)                 # terminal result, artifacts, evidence
worker.cancel(handle)                          # request; confirm terminal state
handle2 = worker.resume(checkpoint, task_spec, execution_policy)  # if supported
~~~

Advertise capabilities and version: resumability, structured stream, tool events, model selection, cancellation and token reporting differ. Proposed lifecycle: queued → starting → running → succeeded / failed / blocked / cancelled / unknown. Cancellation and recovery are requests, not guaranteed transitions. Succeeded means execution completed; acceptance is a separate gate verdict. Emit run_started, output, observed tool events, artifact, blocked, run_finished and errors where supported, with provenance and explicit unavailable fields. Handle process exit without a result, partial JSON, timeouts, throttling, authentication and permission prompts. On restart reconcile persisted process/session references and mark uncertain work unknown; do not blindly rerun side effects. Resume may create a new attempt tied to the earlier run and does not imply exact replay.

Example: the supervisor creates a read-only research task, snapshots its context manifest and requests start on the Codex adapter. The adapter launches codex exec with scoped cwd and JSON stream, captures its process and provider session ID, translates observed events, and returns output and exit status. A deterministic check verifies the saved report and required sections; the supervisor reviews evidence and accepts or requests a bounded correction. A native adapter implements the same methods but drives its own model/tool loop and emits events directly rather than translating CLI streams; an identical interface does not imply equal capabilities or behavior.

Use argument arrays, scoped cwd/environment, no shell interpolation, bounded output and timeout, explicit permission modes, cancellation and child cleanup. Do not pass secrets in prompts or command arguments. Record effective CLI version, model setting, auth type (never credential), and workspace/base revision. Isolation and authorization are explicit policies; mark blocked when an approval cannot be obtained. Subscription use and supported modes are provider-specific; see research before choosing a backend.

## Graph execution and recovery

Use the image's graph prompt as inspiration rather than binding policy: bounded input, artifact and fixed check; gates use saved output and evidence; failures return only to the responsible node with a configurable retry limit (initial proposal three). Persist after each transition: graph version, decisions, completed/running/blocked nodes, checks, artifact locations and next ready action. SQLite can be authoritative with exported graph.md, checks.md, and progress.md views; choose one authoritative store to avoid divergence. Record changed inputs, versions and external dependencies: reproducibility means an auditable rerun, not identical model output. Never silently convert uncertainty into a pass. Human review remains a gate where appropriate. The prompt's request to pause for every graph is inspiration, not a new blanket permission requirement.

## Cognitive core and evaluation

Prefer the least capable, smallest available model that passes a task-specific evaluation; narrow each role, context, tools and output contract. Use deterministic code for objectively specified transformations/checks and model judgment for ambiguity. Smaller models are a hypothesis to test, not an assumption they suffice or cost less. Start with a transparent routing table and escalation on failed checks, ambiguity or risk. Version prompts, context selection, model and policy. Capture representative tasks and baselines; hold out cases, compare comparable tasks and report sample size, success, quality, elapsed time and human review effort. Separate automated checks from blinded human ratings where feasible; track failed attempts, selection bias and changing models. Subscription run cost may be unknown; store measured tokens and separately labeled estimates, never pretend allocated subscription cost is exact.

## Data, telemetry and observability

Evolve existing SQLite with additive, versioned migrations and verified backups; retain raw hook data and dashboard compatibility. Proposed records: tasks; graph versions/nodes/edges/gates; runs and session links; append-only run events with event ID, source, native ID, source and ingest timestamps and ordering; artifacts and hashes; evaluations and evidence. Store prompt/context manifest with paths, hashes, revisions, selected skills, configuration and retention policy; store actual text only under an explicit local policy with redaction/access controls. Track start/end/duration, task type, backend/model and version, tool activity where observable, output/diff, tests, token/cost availability, outcomes and parent-child links. Missing is unknown, not zero.

Correlation needs proof: set a run ID in the child environment only if hooks inherit it, capture session IDs from streams/hooks, and maintain explicit mappings; distinguish native events from wrapper events and avoid double counting through provenance and deduplication. Hook writes are best-effort, while control-plane transitions must be durable and transactional; test lock contention, retries, crash recovery and ordering before concurrent workers. Do not rely on a hook alone for completion, policy enforcement or a complete trace.

Grafana is a visualization/query and alerting UI with an ecosystem of backends (for example Prometheus for metrics, Loki for logs, Tempo for traces); OpenTelemetry is instrumentation, data conventions and transport/collection, not an interchangeable dashboard or durable source of truth. Keep SQLite as the operational audit record. If a concrete question warrants it, instrument dispatcher/runs with OTel and export via OTLP, optionally through a Collector or Grafana Alloy, to existing compatible backends, then view in Grafana. Verify which components actually exist in quant-infra before wiring anything; avoid high-cardinality IDs in metric labels and exporting sensitive prompts. Trace links to run IDs; export failures must not change run truth. Start with SQLite queries and the current dashboard. [OTel/Grafana example](https://opentelemetry.io/docs/languages/dotnet/metrics/getting-started-prometheus-grafana/).

## Milestones and gates

1. **Inventory and contract:** check installed CLI versions, actual supported hooks/auth, backlog ownership and resource discovery; agree task and event schema. Success: one concrete read-only pilot with acceptance criteria and baseline.
2. **One adapter and durable run:** implement minimal task/run records and one CLI worker, safe subprocess lifecycle and correlation, then run the pilot. Success: restart/reconcile, inspect status, output, exit and checks without relying on model narrative.
3. **Supervisor skill and evaluation:** expose operations through a skill; execute one bounded cross-repo workflow and evaluate against baseline. Success: user can inspect graph, evidence and a failed or blocked case.
4. **Expand only on evidence:** add next CLI after capability/auth tests, then routing comparisons; add checkpointing/scheduling or OTel export when a specific workflow needs them. Reassess SQLite concurrency when measured contention warrants it. Consider LangGraph, Temporal or Hermes only for a demonstrated gap with an adoption/operation cost comparison.

Open questions: Which backlog is authoritative and how are changes approved? Which pilot, repo scopes and acceptance checks? What retention and access policy for prompts and raw hooks? How should live approvals reach unattended workers? Which provider/model/account combinations and hook versions work locally? What are acceptable retry/time/concurrency budgets and isolation boundaries? What would justify a scheduler, external telemetry, or replacing SQLite? How will comparable eval cases and human review be selected?
