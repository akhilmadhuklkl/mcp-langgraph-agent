# Security Policy

## Supported versions

The `main` branch is the actively maintained version of this project.

## Reporting a vulnerability

Please do not open a public issue for a suspected security vulnerability.
Instead, contact the repository owner privately through GitHub with:

- A description of the issue and its impact
- Steps to reproduce the issue
- Any suggested mitigation

Allow reasonable time for investigation and remediation before public
disclosure.

## Credential safety

- Never commit OAuth client JSON files, access tokens, API keys, or `.env` files.
- Use environment variables or a local secret manager for credentials.
- The live verification scripts perform read-only checks by default.
- Mutating MCP tools require an explicit approval decision in the workflow.
- Execution traces redact common credential and message-body fields.
