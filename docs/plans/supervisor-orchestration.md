# Cubicle supervisor: initial design

Status: design, 2026-11-01. Cubicle is an independent harness for working across projects, including quant-infra. Details and candidate schema: [execution draft](execution-events-and-storage.md). CLI research and tests: [CLI worker research](../notes/cli-worker-research.md).

## Goal and first milestone

One supervisor helps the user plan and prioritize the shared backlog, mark tasks ready, and coordinate their execution. `cubicle supervisor` starts it using Codex by default; configuration or an argument selects another supported backend. A Cubicle skill gives the supervisor its workflow. Later, a custom supervisor or native worker can use the same Cubicle operations.

The first milestone is two concurrent workstreams, for example tasks in separate repositories. The supervisor can inspect each, handle a failure or stop one without losing the other, and carry a coding task through review, merge and safe cleanup. A non-coding task stays open until the user says it is complete. Assess the result before adding complexity.

## Local setup and backlog

`cubicle init` creates `~/.cubicle/config.yaml`, backlog, context, logs, runs and artifact directories without overwriting existing user data. Shared environment and secrets are supplied by Cubicle, initially using its existing `.env`; record references, never secret values. PostgreSQL holds execution state and events; a separate empty `cubicle` database exists on the local shared PostgreSQL instance. Establish isolated credentials and backups before using it.

Keep one central Markdown backlog under `~/.cubicle/backlog`, with stable IDs and project/repository metadata. Adapt the existing backlog skill for that location. The same supervisor shapes drafts, marks tasks ready, and starts work; readiness does not itself start execution. It may delegate an investigation while planning. Back up the backlog and avoid duplicating existing repo backlogs without a migration plan.

## Graph and worker lifecycle

A **task** defines the outcome, scope and acceptance criteria. The supervisor breaks it into a few meaningful bounded **nodes**, each with inputs, constraints, outputs, checks and dependencies. Each node is assigned to a worker; it may involve many tool and model calls. The supervisor evaluates each result and then advances, requests correction or changes direction. A simple task can have one node. Persist the graph, changes, results and gate evidence.

Prefer one continuing worker session per backlog task across sequential nodes. Distinct IDs identify the backlog item, task, graph version, node, worker session and each node run or retry. Provider session IDs are linked to Cubicle session IDs. The supervisor can use additional workers for independent parallel nodes, with isolated write scopes. Session resumption is backend-specific; if unavailable, create a linked replacement with the relevant graph context and outputs.

A coding task is complete only after its PR is merged and the task-owned local branch is safely cleaned up. Review feedback returns the relevant node for correction and affected checks. Merge requires user authorization or an established authorized policy; do not remove unrelated or unmerged work. A non-coding task is complete only on explicit user confirmation. Record pending review, merge, cleanup and blocked states separately from node completion.

## Interfaces and context

Cubicle's MCP server exposes backlog and supervisor-owned graph operations; Python services beneath it also support CLI access. Workers can report decisions, progress, outputs, checks and blockers for their assigned node and inspect its evidence. They do not construct the supervisor's graph. Provider hooks and streams record operational events independently of agent MCP calls.

A small Worker API starts or resumes assignments, reports status and events, returns a result, and requests cancellation. Adapters advertise differences in session reuse, steering, tool events and usage rather than pretending all backends behave alike. CLI workers run on the host; eventual native agents can implement the same interface.

Each run records a context manifest: shared instructions and skills, task/node instructions, input files and revisions, relevant prior artifacts, selected backend/model, execution policy and deployed prompt version. Mark what was made available separately from what was observed as loaded. Skills can initially come from Skillex without making Cubicle dependent on the user's private skills repository.

Prompts and Cubicle-owned skills are authored in the Cubicle repository. Install/init deploys them under `~/.cubicle` with source revision and content hashes; each run records the deployed versions and rendered prompt or protected reference. Preserve prior versions needed to interpret historical runs.

## Evidence, control and usage

The worker manager records run lifecycle; CLI adapters capture structured output; hooks capture available tool and session events. Store these events separately from the supervisor's graph and link them to the node run when correlation is reliable. In a reused session, a launch-time run ID may be stale on later nodes; test per-assignment correlation and leave ambiguous events unassigned. Retain native provenance, handle duplicates and record hook errors instead of swallowing them. Shell descendants and nested agent activity may not be completely visible.

Record backend/model, times, prompts/context, observed tool use, outputs/diffs, checks, PR, outcome, human assessment and reported usage. Capture token counts and account-window snapshots only where available, with source and scope; shared account usage is not a per-task bill. Configurable usage and elapsed-time thresholds trigger supervisor review or pause further dispatch. Cancellation must confirm process state or mark it unknown and preserve partial work. Initially, ordinary direction changes happen between bounded nodes; live in-flight steering is optional.

Workers use the requested unattended permission-bypass modes. Their effects differ: Codex's bypass also disables its sandbox. A shared tool policy is a design goal, but CLI tool filters and shell access are not equivalent enforcement; report unsupported restrictions and verify each adapter. Use isolated worktrees where appropriate.

## Delivery and unresolved decisions

1. Validate installed CLI sessions, events, hooks, usage and resume; choose two scoped pilot tasks.
2. Build the minimal backlog, node/run records, one adapter and host process manager; exercise two concurrent workstreams, including a failure and cancellation.
3. Add supervisor skill/MCP access and demonstrate review, authorized merge, cleanup and explicit non-coding completion.

Before implementation, settle the supervisor-to-manager interface and lifetime, database role and backups, backlog backup, PR/branch ownership, and the permission policy for unattended work. The [CLI research](../notes/cli-worker-research.md) proposes per-assignment attribution and durable recovery; validate them end to end during implementation. See the execution draft for candidate tables and CLI tests for what has actually been observed.
