# CLI worker research

Checked official documentation 2026-11-01. This is a design inventory, not a test of the user's installed versions or account entitlements. CLI output, hooks, login, quotas and policies can change; record version and verify a minimal local test before relying on any adapter.

## Codex CLI

- [Non-interactive mode](https://developers.openai.com/codex/noninteractive/) documents codex exec, JSONL events via --json, structured output and codex exec resume with an explicit session ID or --last. The subprocess exit and final structured event should both be checked. The default sandbox and approval policy matter for writes and unattended execution.
- [Hooks](https://developers.openai.com/codex/hooks/) document lifecycle and tool events including SessionStart and PreToolUse; hooks have event-specific behavior and limitations. Compare installed Codex's supported events and settings with Cubicle's mapping and TOML registration; an entry in Cubicle's YAML is not proof of an emitted event.
- [Codex authentication](https://developers.openai.com/codex/auth/) describes ChatGPT and API-key sign-in. A locally authenticated CLI and an unattended environment may have different credential availability and limits. Do not extract or log tokens. [App-server](https://developers.openai.com/codex/app-server/) is a possible later structured integration for persistent conversations and approvals, not required by the initial subprocess adapter. Its use and entitlement must be separately validated.

## Claude Code

- [Programmatic mode](https://code.claude.com/docs/en/headless) supports claude -p, JSON output including session ID, and newline-delimited stream-json; use --verbose with the documented streaming options. Resume an explicit session with --resume. Its documentation describes permission-denial events and modes for situations without an interactive approver; a blocked/denied task must remain visible. Background work may delay process exit, so process lifetime and completion events must be handled distinctly.
- [Hooks reference](https://code.claude.com/docs/en/hooks) describes tool, session and other lifecycle hooks, their input/output and behavior. Preserve native payloads and distinguish pre-tool intent from actual completion. The result stream can contain usage/cost metadata, but whether those values represent actual subscription spending needs separate interpretation.
- [Authentication and legal](https://code.claude.com/docs/en/legal-and-compliance): Anthropic describes ordinary individual use of the unmodified Claude Code binary with the user's own subscription, and separately restricts third-party products routing other users' subscription credentials or collecting/intermediating credentials. A personal local wrapper is not automatically equivalent to a hosted third-party service; verify the exact deployment and terms before expansion. Do not build custom OAuth credential handling on assumptions. API-based custom agents use their own supported authentication/billing.

## Gemini CLI

- [Headless mode](https://geminicli.com/docs/cli/headless/) supports noninteractive prompts and JSON or stream-json output. [CLI reference](https://geminicli.com/docs/cli/cli-reference/) documents model and output options; [session management](https://geminicli.com/docs/cli/session-management/) documents --resume by UUID. Use the original project directory when resolving project-scoped sessions, and persist the ID instead of assuming latest refers to the desired run.
- [Hooks](https://geminicli.com/docs/hooks/) include BeforeTool, AfterTool, BeforeAgent, AfterAgent and session/model events. Hook outputs and trust differ from Claude/Codex. Cubicle's agy hook is for Antigravity and uses different event names and response shapes; Gemini needs a separately tested adapter.
- [Authentication](https://geminicli.com/docs/get-started/authentication/) says headless mode can use a cached existing authentication credential; without one configure an API key or Vertex AI. Cached Google sign-in is not a guarantee of durable unattended access: expiry, quota, account type, terms and credential refresh must be checked for the actual setup.

## Subprocess and integration decisions

Use the provider's published binary and documented noninteractive interface as a child process, with explicit cwd, argument list, bounded output, environment allowlist, timeout, signal handling and durable run identity. Prompt input mechanisms and streaming formats are provider-specific; verify stdin behavior before relying on it. Capture stderr separately, parse defensively, save provider session ID, and distinguish exit status from a gate verdict. Test cancellation, concurrent sessions, hooks, resume, quota and an unavailable approval without modifying production settings or leaking credentials. Authentication, terms, budgets and observable event fields are capabilities to verify per account and version, not a blanket entitlement to automate every deployment.
