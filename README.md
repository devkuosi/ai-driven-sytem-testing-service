# AI-driven System Testing Service

An AI-assisted service for generating and executing structured REST API tests.

## Goal

Turn API specifications and business requirements into repeatable tests
with explicit assertions and traceable results.

## First release

- Accept a REST API target configuration.
- Load a manually written test plan.
- Validate supported actions and assertions before execution.
- Send HTTP requests to a test environment.
- Check response status and selected JSON values.
- Verify business outcomes through follow-up API requests.
- Produce a JSON report linked to requirements.
- Generate proposed test plans using AI after the runner works.

## Design principle

AI proposes tests. Explicit assertions determine whether they pass.
Expected behaviour must come from supplied specifications or requirements.

## Demonstration

A user-registration API with these rules:

- Users must be at least 18.
- Email addresses must be unique.
- Required fields must be present.
- Rejected registrations must not create a user.

## Planned technologies

Python, FastAPI, Pydantic, HTTPX, pytest, GitHub Actions, and Docker.

## Status

Requirements and project setup.
