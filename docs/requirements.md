# Requirements

Status: Initial draft

## Scope

The first release supports REST APIs with JSON request and response bodies.
It runs against explicitly configured test environments.

## Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Accept a target base URL and request timeout. |
| FR-02 | Load a structured test plan from a JSON file. |
| FR-03 | Validate the plan before sending requests. |
| FR-04 | Execute supported HTTP requests. |
| FR-05 | Check response status codes and selected JSON values. |
| FR-06 | Reuse values from earlier responses in later requests. |
| FR-07 | Support setup and cleanup steps. |
| FR-08 | Report passed assertions, failed assertions, and execution errors separately. |
| FR-09 | Include requirement references and sanitised evidence in JSON reports. |
| FR-10 | Return a non-zero command exit code when a run fails. |
| FR-11 | Accept an API specification and business requirements for planning. |
| FR-12 | Generate proposed plans using AI and validate them before execution. |

## Quality requirements

- Credentials must not appear in Git, AI prompts, or reports.
- Requests must have configurable timeouts.
- Execution must remain within the configured target.
- Plans and reports must record their format version.
- The example workflow must run without an AI API key.

## First implementation milestone

Run a manually written test plan against the demonstration API
and produce a JSON report.

## Release acceptance criteria

- The documented example runs from a clean setup.
- Tests pass against the correct demonstration API.
- Tests detect deliberately introduced age-validation and duplicate-email defects.
- A rejected registration is checked for unintended data creation.
- Invalid plans are rejected before any target request.
- Generated plans reference supplied requirements.
