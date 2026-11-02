# CLI worker research

### Integration retest — 2026-11-01

The current 77-test suite passed. A live Codex supervisor used the Cubicle MCP tools
to create and update a backlog item, create a task and node, and start a worker; that
worker succeeded with PostgreSQL events. A separate Codex graph probe completed two
dependent nodes using the same provider session; revising the first reopened both.
Live worker probes persisted all emitted hook spool records to PostgreSQL: Codex
8/8, Claude 8/8, and agy 12/12. Stream observations were also recorded. A separate
Claude `--max-turns 1` probe stopped with `error_max_turns` (the result reported
`num_turns: 2`); elapsed review and quota threshold behavior are covered by automated
tests, rather than a full-duration live test.

Initially the Codex worker emitted no hook files: re-registering Cubicle's hook
definitions had left them pending Codex's hook-trust review. An isolated comparison
confirmed an untrusted hook was skipped and the same hook ran when trust was bypassed.
The 12 installed definitions were verified to point to Cubicle's hook script and
trusted through Codex's hook review UI; the subsequent Codex worker produced 8/8
persisted hooks. Setup now calls out the trust step. These are observed events in
bounded probes, not proof of complete coverage for all provider or nested-agent
operations. Node scope is an instruction, not an enforced security boundary.

### Operational verification — 2026-11-01

The interactive Claude and agy supervisors each made a real `list_backlog_items` MCP
call using the supervisor's server configuration. Claude displayed its one-time
bypass-mode confirmation for the isolated test directory. A separate real GitHub PR was merged into an isolated test base
branch; Cubicle verified the merge, deleted the local task branch and completed its
test task using an isolated SQLite fixture. The temporary remote branches were removed;
main was not changed.

A restart probe used Cubicle's worker manager, simulated CLI workers, and an isolated
PostgreSQL container. Two workers were started, the manager was killed, PostgreSQL was interrupted while
the workers finished, and then restarted. Both terminal markers were replayed into
PostgreSQL as successful runs. Repeating recovery did not duplicate events. Uncertain
runs are never automatically relaunched; `resolve_unknown_run` records reviewed
evidence before reopening the node.

New worker stdout/stderr, prompts in run metadata and hook payloads are redacted before
durable storage using the open-source pygarble secret detector and known environment
secret values. This is best effort: redaction cannot prove all secrets are absent, old
logs remain unchanged, and task/backlog text can contain sensitive information. Source:
https://github.com/brightertiger/pygarble

### Practical worker interface — 2026-11-01

The common approach is a bounded node, a per-task reusable provider session, streamed
events, and a ten-minute default review signal (`limits.max_run_seconds`); the
supervisor polls progress and chooses whether to cancel. The review signal is not a
hard timeout. A requested model can be passed to each backend. Provider options are
additional capabilities, not assumptions that every backend has the same flags.

| Capability | Codex 0.164.0 | Claude 2.1.90 | agy 1.4.12 |
| --- | --- | --- | --- |
| Start / stream | `codex exec --json` | `claude -p --output-format stream-json --verbose` | `agy -p --output-format stream-json` |
| Continue | `codex exec resume SESSION_ID` | `--resume SESSION_ID` | `--conversation SESSION_ID` |
| Session identity | `thread.started` supplies a provider UUID; resume accepts UUID or name. No initial ID flag appears in installed `codex exec --help`. | `--session-id UUID` can choose a new ID; `--resume` continues an existing one. Cubicle currently records the returned ID. | `init`/result supplies conversation ID; `--conversation` resumes it. No initial ID flag appears in installed help. |
| Bound work | No common max-turn flag found in installed help; use the shared review clock. | `--max-turns` works in print mode even though hidden from installed `--help`; Cubicle defaults to 30. | `--print-timeout` is available as an optional hard print-mode limit; Cubicle uses the shared review clock instead. |
| Other useful options | `--model`, `--output-schema`, `-o` final message, `--cd`, `--add-dir`; `--ephemeral` prevents session reuse. | `--model`, `--json-schema`, `--tools`, `--allowed-tools`, `--disallowed-tools`, `--session-id`; newer versions add `--forward-subagent-text` and managed background commands. | `--model`, `--json-schema`, `--settings`, `--add-dir`, `--print-timeout`; stream-json input can send multiple turns in one process. |

Codex quota: `account/rateLimits/read` on `codex app-server` supplies the account
windows displayed by Codex. Cubicle reads them before dispatch and blocks at
`limits.codex_max_used_percent` (default 80), or if unavailable. On this installed
version, a direct signed-in read succeeded. This is a pre-dispatch guard, not a quota
reservation or a guarantee that already-running work and other clients stop.

References: https://learn.chatgpt.com/docs/developer-commands?surface=cli ;
https://learn.chatgpt.com/docs/app-server ; https://code.claude.com/docs/en/cli-reference ;
https://antigravity.google/docs/cli/reference/ ; https://antigravity.google/docs/cli/headless/ .

### Local CLI controls and status-line quota — 2026-11-01

The installed Claude Code is 2.1.90. A real no-tools print invocation confirmed its
hidden `--max-turns 1` flag works; `--forward-subagent-text` was rejected (the current
reference requires 2.1.211 or later). The current reference documents `claude stop`
for Claude-managed background sessions, not arbitrary `-p` children. This installed
version does not list that command or `--bg` in its help, so Cubicle's existing host
worker should continue using its process-group cancellation until a background adapter
and its returned background ID are tested. `--environment` targets a self-hosted cloud
environment (2.1.224+), not a local environment-variable file. `--permission-mode auto`
is an alternative approval policy, not the bypass previously selected for unattended
workers. `--advisor` is optional specialization and is not assumed. Model selection,
stream-json output and resume are supported; Cubicle now passes an optional model and
defaults Claude node runs to 30 turns, configurable in `limits.claude_max_turns`.
Source: https://code.claude.com/docs/en/cli-reference

An agy 1.4.12 print-mode probe did not invoke a configured status-line command; an
interactive session did, and its quota object became populated after a model request.
Cubicle's agy supervisor now records only quota fractions from that callback and pauses
agy dispatch at the configured threshold or if the last reading is over five minutes
old. The check conservatively considers every reported bucket and does not stop an
already-running worker. Codex's TUI displays usage but exposes no comparable documented
status-line callback; this initial finding was superseded by the Codex app-server
account-window guard described above. Claude account-window gating remains deferred.
Sources: https://antigravity.google/docs/cli/statusline and
https://learn.chatgpt.com/docs/developer-commands

Checked official documentation 2026-11-01. This is a design inventory, not a test of the user's installed versions or account entitlements. CLI output, hooks, login, quotas and policies can change; record version and verify a minimal local test before relying on any adapter.

## Codex CLI

- [Non-interactive mode](https://developers.openai.com/codex/noninteractive/) documents codex exec, JSONL events via --json, structured output and codex exec resume with an explicit session ID or --last. The subprocess exit and final structured event should both be checked. The default sandbox and approval policy matter for writes and unattended execution.
- [Hooks](https://developers.openai.com/codex/hooks/) document lifecycle and tool events including SessionStart and PreToolUse; hooks have event-specific behavior and limitations. Compare installed Codex's supported events and settings with Cubicle's mapping and TOML registration; an entry in Cubicle's YAML is not proof of an emitted event.
- [Codex authentication](https://developers.openai.com/codex/auth/) describes ChatGPT and API-key sign-in. A locally authenticated CLI and an unattended environment may have different credential availability and limits. Do not extract or log tokens. [App-server](https://developers.openai.com/codex/app-server/) is a possible later structured integration for persistent conversations and approvals, not required by the initial subprocess adapter. Its use and entitlement must be separately validated. The [app-server documentation](https://learn.chatgpt.com/docs/app-server) describes active-turn steering, interruption, thread token usage and account rate-limit reads; support depends on version and account.

## Claude Code

- [Programmatic mode](https://code.claude.com/docs/en/headless) supports claude -p, JSON output including session ID, and newline-delimited stream-json; use --verbose with the documented streaming options. Resume an explicit session with --resume. Its documentation describes permission-denial events and modes for situations without an interactive approver; a blocked/denied task must remain visible. Background work may delay process exit, so process lifetime and completion events must be handled distinctly.
- [Hooks reference](https://code.claude.com/docs/en/hooks) describes tool, session and other lifecycle hooks, their input/output and behavior. Preserve native payloads and distinguish pre-tool intent from actual completion. The CLI reference documents --include-hook-events with exceptions; the result stream can contain usage/cost metadata, but whether those values represent actual subscription spending needs separate interpretation.
- [Authentication and legal](https://code.claude.com/docs/en/legal-and-compliance): Anthropic describes ordinary individual use of the unmodified Claude Code binary with the user's own subscription, and separately restricts third-party products routing other users' subscription credentials or collecting/intermediating credentials. A personal local wrapper is not automatically equivalent to a hosted third-party service; verify the exact deployment and terms before expansion. Do not build custom OAuth credential handling on assumptions. API-based custom agents use their own supported authentication/billing.

## Antigravity CLI (agy)

[CLI reference](https://antigravity.google/docs/cli/reference/) and [headless mode](https://antigravity.google/docs/cli/headless/) document print mode, JSON and stream-json output, conversation resume, permission bypass, and streaming input. The stream has init, step_update and result events, with tool activity and step/result token usage when available; session results can be cumulative. For streaming input, the docs say to wait for the result before submitting the next prompt; in-flight steering is not established. [Hooks](https://antigravity.google/docs/hooks?tab=cli) include SessionStart, PreToolUse, PostToolUse, PreInvocation, PostInvocation and Stop. Validate event fields, authentication, nested activity, token totals and installed-version behavior in a controlled pilot.

## Subprocess and integration decisions

Use the provider's published binary and documented noninteractive interface as a child process, with explicit cwd, argument list, bounded output, environment allowlist, timeout, signal handling and durable run identity. Prompt input mechanisms and streaming formats are provider-specific; verify stdin behavior before relying on it. Capture stderr separately, parse defensively, save provider session ID, and distinguish exit status from a gate verdict. Test cancellation, concurrent sessions, hooks, resume, quota and an unavailable approval without modifying production settings or leaking credentials. Authentication, terms, budgets and observable event fields are capabilities to verify per account and version, not a blanket entitlement to automate every deployment.

## Local experiments — 2026-11-01

These were small live calls against the installed, authenticated CLIs from `/tmp`; they consumed subscription usage and may have invoked existing global hooks. No project files were edited by the test prompts. They establish only the observations below, not general reliability or permission-policy coverage. Versions: Codex 0.164.0, Claude Code 2.1.90, agy 1.4.7. Documentation may describe newer versions.

### 1. Non-interactive structured output and session reuse

For each CLI, sent a no-tools prompt requesting the exact marker `CUBICLE_ALPHA`, read its machine-readable output and recorded the session ID. Then resumed the same ID in a second invocation and asked for the previous marker. All three exited successfully, returned the marker both times, reported the same session ID and exposed a usage object.

| CLI | First invocation | Resume invocation | Observed |
| --- | --- | --- | --- |
| Codex | `codex exec --skip-git-repo-check --sandbox read-only --json` | `codex exec ... --json resume SESSION_ID` | JSONL included thread.started, item events and turn.completed with input, cached and output token counts. |
| Claude | `claude -p ... --output-format stream-json --verbose --include-hook-events --tools ''` | `claude -p ... --resume SESSION_ID --output-format json --tools ''` | Stream contained system, assistant, rate_limit_event and result events; result included usage. |
| agy | `agy -p ... --output-format stream-json --print-timeout 60s` | `agy --conversation SESSION_ID -p ... --output-format json --print-timeout 50s` | Stream contained init, step_update and result; result contained usage and SUCCESS. |

The observed results support using a continuing session for sequential node assignments. They do not establish concurrent node control, active-turn steering, cancellation, or that all instructions and context are reconstructed perfectly.

### 2. Tool visibility and a correlation marker

Launched each CLI with a harmless `CUBICLE_EXPERIMENT_ID=NODE_PROBE_42` environment variable and asked it to run `printenv CUBICLE_EXPERIMENT_ID`. Codex used its read-only sandbox, Claude used an allowed `Bash(printenv:*)` rule, and agy used its permission-bypass flag. All three processes exited zero.

- **Codex:** two command-execution item events appeared, but the marker was **not observed** in the parsed item payloads. This may reflect environment filtering, command behavior or stream contents; this test alone does not isolate the cause. Do not assume a run ID passed via the parent environment reaches a Codex shell or appears in its event stream.
- **Claude:** the stream included tool-use evidence, the marker and ten hook-lifecycle events. This establishes that the marker appeared somewhere in the parsed stream, not which hook inherited it or whether nested agents do.
- **agy:** two tool step updates appeared and the marker appeared somewhere in the stream; terminal result was SUCCESS. This does not establish which hook or nested process received it.

These probes do not verify reliable event-to-node attribution, because a session may span multiple node assignments and children/hooks may run asynchronously. Future tests should inspect sanitized individual event shapes and hook payloads, compare per-assignment correlation strategies, and test concurrent workers, nested subagents, failures, timeout/cancellation, restart recovery, quota thresholds, MCP and PR workflow. Avoid storing secrets or whole transcripts in test notes.

### Codex attribution follow-up — 2026-11-01

Using Codex CLI 0.164.0, synthetic markers and read-only prompts in `/tmp`, investigated the missing shell marker. No global settings were changed. The active Codex user configuration contains a `shell_environment_policy.include_only` allowlist.

1. With `CUBICLE_PROBE_ID=RUN_PROBE_42` in the parent environment, the emitted completed command item showed `printenv CUBICLE_PROBE_ID`, exit code 1 and empty output. The earlier absence was a real absence from that shell, not merely omitted event output.
2. Adding only `-c 'shell_environment_policy.set.CUBICLE_PROBE_ID="RUN_PROBE_42"'` still yielded exit 1 and empty output under the existing allowlist. An explicit set entry alone is insufficient in this configuration.
3. A temporary invocation override `-c 'shell_environment_policy.include_only=["CUBICLE_PROBE_ID","PATH","HOME"]'` produced `RUN_PROBE_42` and exit 0 in the completed command event. This replacement was for an isolated test, not a recommended production configuration: replacing an allowlist can omit required variables or broaden access. Compute a minimal policy compatible with the effective configuration and test it instead.
4. A temporary SessionStart command hook, supplied only for the test and explicitly trusted with `--dangerously-bypass-hook-trust`, received the parent marker and provider `session_id` even without changing the shell allowlist. Hooks and agent shell commands therefore behaved differently in this local test. A second experiment launched two separate Codex exec processes for the same resumed session, with markers `ASSIGNMENT_A` and `ASSIGNMENT_B`: both SessionStart hooks observed their respective marker and the same session ID, with source `startup` and `resume` respectively.

**Design implication:** for the first Codex adapter, start/resume a separate process per sequential node assignment; pass a non-secret Cubicle run ID in its environment, capture the JSONL thread/session ID and associate both with the manager's run record, and let compatible hooks attach the marker. Confirm mapping on every invocation. Do not assume shell commands inherit this marker, or that SessionStart proves all tool hooks, nested agents, asynchronous work or long-lived app-server sessions inherit it. Test PreToolUse/PostToolUse hooks, concurrent assignments and delayed subagents before relying on it for complete event attribution. Uncertain or late events remain session-level/unknown. Never use the correlation marker as an authorization credential. Existing Codex hook trust and per-user config may affect deployment; no trust or configuration was persisted by this experiment.

Sources: [shell environment policy](https://learn.chatgpt.com/docs/config-file/config-advanced), [Codex hooks](https://learn.chatgpt.com/docs/hooks).

### Control, nested-agent and recovery probes — 2026-11-01

All tests used harmless prompts in `/tmp` and synthetic markers. Installed versions at this follow-up: Codex 0.164.0, Claude Code 2.1.90, agy 1.4.12 (changed from 1.4.7 in the earlier test). The model calls consumed subscription usage. These are feasibility samples, not production-grade reliability tests.

**Node attribution and nested agents.** For Codex, installed temporary per-invocation SessionStart, PreToolUse, PostToolUse, SubagentStart and SubagentStop hooks; explicitly bypassed hook trust only for that controlled test. Asked a subagent to run `printf CHILD_OK`. All nine observed callbacks carried the synthetic assignment marker and parent session ID. Subagent start/stop and its Bash pre/post callbacks also carried the same child agent ID. This demonstrates correlatable callbacks for one parent/child flow in one process; it does not prove complete nested coverage, delayed descendants or reliable attribution after overlapping assignments.

For Claude, supplied a temporary `--settings` hook configuration for the same lifecycle events, used permission bypass and asked for the same harmless subagent task. Seven callbacks were observed: the parent Agent tool and child Bash pre/post events, subagent start/stop, and SessionStart. All carried the synthetic assignment marker and parent session ID; child callbacks shared an agent ID. Again, this is a single observed flow, not a completeness guarantee. The temporary files were removed; global hook configuration and trust were not modified.

For agy 1.4.12, a similar prompt returned SUCCESS and its stream exposed the `invoke_subagent` tool plus the child marker. This demonstrates a subagent invocation and output in the parent stream, **not** child hook coverage, child IDs or attribution to node IDs. Those remain unverified.

**Live steering and cancellation.** A throwaway local Codex app-server client initialized a thread, began a turn, and sent `turn/steer` with a marker. The server acknowledged the same turn ID and the marker appeared in subsequent output before a `completed` turn. A first interrupt test raced a turn that had already finished and returned `no active turn to interrupt`; repeating with a longer-running turn returned an empty success response followed by `turn/completed` with status `interrupted`. This validates the protocol behavior for this sample, not guaranteed termination of every shell descendant or reversal of external actions. No comparable live in-flight steering test was established for Claude or agy.

Separate host process-group SIGTERM probes requested a harmless `sleep 25`: Claude produced tool-use evidence and exited 143; agy produced tool-step evidence and exited 1; neither process group remained visible immediately after waiting. The Codex CLI probe exited 0 and had no remaining process group; because it may have completed before the signal, it is **inconclusive** for CLI process cancellation. These checks do not prove escaped descendants are gone, or that durable cancellation state is recorded.

**Concurrent-worker recovery.** A throwaway manager launched two separate read-only Codex workers with distinct markers, each writing JSONL to a separate file, and wrote a small process manifest. The test killed the manager while both workers were running. Both detached workers subsequently emitted their own session IDs, marker and `turn.completed`; neither output contained the other worker's marker. This proves the particular processes and output files survived the manager death. It does **not** test a real Cubicle manager restart, PostgreSQL persistence, hook reattachment, PID reuse, node-state reconciliation, worker crashes, duplicate ingestion or orphan cleanup. Those are implementation acceptance tests, not completed functionality.

**Implications:** represent backend capabilities explicitly. A first Codex implementation may choose app-server for confirmed in-flight steering/interrupt or exec/resume for isolated per-node process correlation; compare complexity and version support before choosing. Retain separate worker session and per-node run IDs, keep a durable event sink independent of the manager, and handle uncertain process/child state without automatic replay. Test agy child hooks, Claude/agy live control, concurrent hook attribution across resume, and full durable restart/recovery when the worker manager exists.

### Attribution and recovery design tests — 2026-11-01

**Two node assignments in one Codex session.** Two sequential `codex exec`/`exec resume` invocations used the same provider session, separate synthetic run IDs, and temporary SessionStart, PreToolUse and PostToolUse hooks. Both processes exited 0. The first invocation's three callbacks carried `NODE_RUN_A`; the resumed invocation's three callbacks carried `NODE_RUN_B`; both tool callback pairs identified Bash and the same provider session. This is stronger evidence than a session-start-only probe. It still does not establish attribution of late background processes, concurrent turns within the same session, or every CLI/backend.

**PostgreSQL replay prototype.** A throwaway manager launched two detached Codex workers into separate JSONL files; their running records were inserted into a uniquely named temporary schema in the existing `cubicle` database, then the manager was killed. Both produced terminal events and provider session IDs. A replacement test process read both files, inserted each event twice using a stable `(run ID, file line)`-derived ID and `ON CONFLICT DO NOTHING`, and reconciled both run records to succeeded. PostgreSQL contained 12 events and 12 distinct event IDs, with both runs succeeded. A separate owned `sleep` process group was identified via its live Popen handle, sent SIGTERM, reaped with exit -15 and no longer visible as a process group. The temporary schema was dropped; no persistent application tables were created. This is a simulated restart/reconciliation, not an actual Cubicle restart. It does not validate simultaneous ingestion, partial writes, database outages, PID reuse, power loss, launch crash windows, child processes that escape the group, or PostgreSQL-backed production code. The orphan probe used a known owned process, not an unknown PID found after a real restart.

**Proposed initial node attribution.** The supervisor creates a run record before dispatch with task, graph, node, worker-session and run IDs. Run one node assignment per CLI process, resuming the same provider session when appropriate. Prohibit simultaneous active assignments in the same provider session; independent workstreams have separate sessions. Start a run-specific host wrapper as a separate process group. It sets a non-secret run ID and destination for that process's hooks, captures CLI stdout/stderr separately to a run-specific durable spool under `~/.cubicle/runs/<run-id>/`, records the provider session/turn and writes a terminal status marker atomically. The manager tags each captured stream event using the spool's run identity; trusted hooks carry the run marker and provider IDs when verified. Existing Codex shell environment filtering means the marker is not guaranteed in agent shell commands, even though tested hooks received it. Link by explicit marker/provider IDs only; missing, conflicting or unverified late events remain session-level/unknown. The hook test used an ephemeral trusted configuration, not a validated installation procedure. Claude and agy need the equivalent sequential-resume and hook tests; app-server's shared long-lived process needs provider thread/turn mapping rather than a per-process environment ID.

Run lifecycle and worker session are separate: a resumed CLI process is a new run within the same worker session. Never reassign the same provider session while the prior wrapper or its background work is still active; if that cannot be determined, leave the new assignment blocked or record uncertainty. Worker subagents may have their own IDs; do not promote them automatically to supervisor graph nodes. A tool event seen in both stream and hook is two observations; retain source and link where provider call IDs support it, not a guessed unique action.

**Event delivery and restart.** The wrapper/collector, not the supervisor conversation, owns durable spool files and worker lifecycle. Give each event an ID assigned and persisted before retry (for source without an ID, use a run-scoped immutable spool segment/offset with recovery rules); ingest in a transaction with a unique event ID, and atomically commit acknowledged progress with the corresponding database insert. On failure, retry the same IDs; no silent hook errors. Concurrent hook callbacks need separate per-event files or another proven atomic framing mechanism, not uncoordinated writes to one JSONL file. Preserve unacknowledged spool until recovery; test disk-full and partial-tail behavior. One manager uses a lease/fencing token to avoid two managers dispatching/reconciling the same run; stale lease and process identity require verification. Database sequences are allocated before commit: an identity value is **not** by itself a safe commit-order high-water cursor. For the first version, poll unacknowledged spool entries or use a transactional queue/outbox; test out-of-order commits and replay before adopting a cursor.

On manager restart, inspect durable run records, wrapper process identity (PID plus host boot/process start identity, not PID alone), terminal marker, provider session and spool. Reattach to a verified running wrapper or ingest its completed result; missing, inconsistent or unverifiable evidence becomes `unknown`/`needs_attention`, never silently succeeded and never automatically relaunched. Distinguish a manager crash from a wrapper/host crash. At the dispatch boundary, DB commit, OS spawn and external work cannot be made one transaction: use a durable `starting` intent and wrapper handshake, then reconcile without blind retries. Process death before a provider session ID is known is an ambiguous launch, not a reason to duplicate a potentially side-effecting action.

Orphan cleanup: only stop a worker when the manager has positive ownership and a matching process identity, using its dedicated process group; request SIGTERM, wait, escalate if still owned/running, reap when parent, and record outcome. A restarted manager generally cannot reap a process it did not parent; it can inspect/monitor and record disappearance. Unknown processes or potentially reused PIDs require attention rather than killing. A clean task branch/worktree is a separate user-authorized task lifecycle step, not process cleanup.

**Initial steering and cancellation decision.** Do not require live in-flight steering for version one. The supervisor observes events and directs the next bounded node or a correction after the current assignment; for a stuck run it requests cancellation and waits for a confirmed terminal/unknown state before reassignment. This provides useful control without making app-server mandatory. Prefer graceful provider interruption where the adapter supports it, otherwise signal the owned process group and confirm what can be confirmed; cancellation cannot undo completed external actions. Codex app-server steering and interruption succeeded in one local probe and may be an optional future adapter. Claude/agy live steering is not established. Usage thresholds should pause new dispatch and prompt investigation; cancellation of a current run needs the configured policy and observed evidence, not guessed per-task usage.

**Remaining acceptance tests when Cubicle exists:** actual two-workstream manager crash/restart against its PostgreSQL schema; crash before/after spawn and before terminal-state commit; duplicate and concurrent hook ingest with partial spool writes and unavailable DB; provider resume and per-node attribution for all backends; confirmed cancellation including nested processes and escaped children; worker crash, host restart, stale lease/PID reuse and safe orphan reconciliation. These cannot be certified by the throwaway prototype.
