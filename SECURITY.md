# Security

Agent Skills are executable supply-chain material: an agent may run the bundled scripts on a user's machine. Review every script before running it.

- Never commit credentials, private keys, access tokens, or `.env` files.
- Scripts must not download and execute remote code, or delete files outside their working area.

## Reporting a vulnerability

Please use GitHub's **private vulnerability reporting** (Security tab → "Report a vulnerability") if it is enabled for this repository. Otherwise, open a minimal issue asking for a private contact, without exploit details or secrets.
