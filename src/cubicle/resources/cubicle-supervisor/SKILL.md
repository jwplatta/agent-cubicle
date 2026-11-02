---
name: cubicle-supervisor
description: Plan shared Cubicle backlog items and coordinate bounded task graphs.
---

# Cubicle supervisor

Use Cubicle MCP to inspect and shape the shared backlog under ~/.cubicle/backlog.
For Cubicle-supervised work, this shared backlog takes precedence over generic
project-backlog skill instructions that point to a repository-local docs/backlog.
Skillex remains an optional external skill source; do not assume a specific private
skills repository or modify a skill installation without the user requesting it. Mark a sufficiently defined
execution task ready before dispatch. Decompose work into bounded nodes with inputs,
outputs, scope, checks and dependencies. Prefer a continuing worker session per task;
inspect each node result and evidence before accepting it or advancing the graph.

The worker launcher is experimental. Do not claim event coverage, safe cancellation,
recovery, or PR automation beyond what the available tools actually report. A coding
task is complete only after its PR is merged and its local branch is safely cleaned up;
a non-coding task is complete only when the user confirms it.
