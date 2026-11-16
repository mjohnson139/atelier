# Security

Please report a vulnerability privately through [GitHub's security advisories](https://github.com/mjohnson139/atelier/security/advisories/new), not in a public issue. You'll get a reply within a week.

Areas that matter most here:

- the `sketch` tool, which runs model-written Python in a sandbox (escaping its directory, its timeout or its no-network rule)
- anything that sends a spec, an image or repository content to a host other than the user's own machine
- secrets, which never belong in this repository
