# Security

The local toolkit reads dataset files and saved predictions. Network requests occur only when the explicit `run` command is invoked with an endpoint. API keys should be supplied through the environment, and local `.env` and `outputs/` files are ignored by Git.

Do not place live credentials, personal data, private endpoints, or confidential model logs in public issue reports. If the repository is hosted later, use that host's private vulnerability-reporting channel when available. Otherwise provide a minimal redacted reproduction through an authorized maintainer contact.

The runner is a small evaluation client. It does not provide a sandbox for untrusted providers or legal documents. Review the endpoint and file paths before running it in a sensitive environment.
