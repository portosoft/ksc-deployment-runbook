# KSC Deployment Runbook — DevSecOps Agent Rules & Governance Context

This document provides persistent context and mandatory DevSecOps governance rules for AI coding agents (Antigravity, Jules, Claude Code) and human developers working in the `portosoft/ksc-deployment-runbook` repository.

---

## Language & Documentation Guidelines

1. **Automation Code & Git Metadata**: All Python scripts, Bash scripts, GitHub Actions workflows, inline comments, commit messages, and PR descriptions MUST follow professional engineering standards.
2. **Operational Documentation & Runbooks**: Technical deployment guides and runbooks in `docs/` are written in **Brazilian Portuguese (`pt-BR`)** to serve operational sysadmins and engineers deploying Kaspersky Security Center in Portuguese-speaking enterprise environments.
3. **Agent Communication & Reviews**: Interactions with automated reviewers, bots, PR review comments, and issue tracking should remain clear, technical, and aligned with team conventions.

---

## DevSecOps Core Principles & Security Invariants

1. **Zero Plaintext Secrets**: No database passwords, license `.key` files, SSH private keys, API tokens, or certificates may ever be committed to git. Use environment variables, secret files outside the git tree (e.g. `~/.secrets/*.env`), or HashiCorp Vault.
2. **Continuous Secret Scanning**: Every change must pass `detect-secrets` against `.secrets.baseline`. Never bypass baseline validation with dummy ignores without technical justification.
3. **Defense in Depth**: Configurations for PostgreSQL and KSC must enforce least-privilege permissions (`0600`/`0700`), TLS encryption, firewall restrictions, and audit logging.
4. **Least Privilege CLI & Scripting**: Avoid dangerous shell commands (`rm -rf`, raw string interpolations in `psql`, unquoted shell arguments). Validate inputs and use structured commands or APIs.
5. **Idempotence & Safety**: Deployment scripts and automation tasks must be safe to re-run, check preconditions before execution, and provide deterministic exit codes.

---

## Branch & Commit Strategy

### Branches

Default branch: **`develop`** (aligned with `barahn`, `catnet-io`, and `app` DevSecOps standard).

| Branch | Purpose | Protection & Rules |
|---|---|---|
| **`develop`** *(default)* | Active integration branch & target for all PRs | Protected. Requires signed commits & passing CI status checks. |
| **`main`** | Production-ready, signed releases | Strictly protected. Requires manual review from Code Owner (`@mendsec`), signed commits, strict status checks, and passing `Enforce Main Branch Rules` check. **NO auto-merge allowed.** |
| **`feat/*`** or **`feature/*`** | New features, lab setups, automation modules | Created from `develop`, PR targets `develop`. |
| **`fix/*`** or **`bugfix/*`** | Bug fixes and runtime corrections | Created from `develop`, PR targets `develop`. |
| **`security/*`** | Security remediations, CVE fixes | Created from `develop`, PR targets `develop`. |
| **`docs/*`** | Documentation, ADRs, runbooks | Created from `develop`, PR targets `develop`. |
| **`ci/*`** or **`chore/*`** | CI/CD workflows, linters, housekeeping | Created from `develop`, PR targets `develop`. |

### Crucial Branch Invariants

1. **Pull Requests MUST target `develop`**: All PRs created by developers or AI agents MUST target the `develop` branch. Never create or direct PRs directly to `main`.
2. **Promotion to `main` is Automated via Release PR**: Only automated release PRs from `develop` to `main` (opened by `github-actions[bot]` or authorized maintainer `@mendsec`) are allowed to merge into `main`.
3. **No Direct Pushes to `main` or `develop`**: All modifications must pass through a pull request and code review.
4. **Automatic Synchronization**: Whenever a release PR is merged into `main`, `main` must be automatically merged back into `develop` via `sync-develop.yml` to prevent history drift.

---

## Merge Strategy

- **NEVER use `squash and merge`** (`gh pr merge --squash` / `-s`) for merges between `develop` and `main`, or for significant integration branches.
- Always use **standard merge commit** (`gh pr merge --merge` / `-m`) or **rebase** (`gh pr merge --rebase` / `-r`) to preserve commit history, cryptographic signatures, and auditability.

---

## Commit Guidelines — Conventional Commits & Signatures

### Conventional Commits Format

```
<type>(<scope>): <description>

Types: feat, fix, docs, refactor, test, chore, security, perf, ci
Scopes: infra, ops, ksc, postgres, cli, auth, docs, test, ci, security
```

Examples:
```
feat(infra): add proxmox local test environment and documentation (#204)
fix(ops): harden psql command execution and SQL ownership handling
security(db): restrict postgres listen_addresses and enforce md5/scram
docs(runbook): add troubleshooting section for network agent connection
chore(ci): enforce DevSecOps branch rules and commit signature verification
```

### Cryptographic Signatures

- **100% of commits MUST be signed** using SSH (`gpg.format = ssh`) or GPG.
- Unsigned commits are rejected by branch protection rules and by the `Enforce Main Branch Rules` CI check.

---

## Dependency & Version Policy

1. **Strict Anti-Downgrade Rule**: Version downgrades in `requirements.txt` or `.github/workflows/*.yml` are **STRICTLY PROHIBITED** without explicit written authorization from the maintainer (`@mendsec`).
2. **Dependabot Management**: Dependabot PRs target `develop` and must be validated by running tests before merging.
3. **Pinned GitHub Actions**: Third-party GitHub Actions should be pinned to full commit SHAs or verified release tags.

---

## Local-First Verification Policy

1. **Local-First Verification**: Before pushing or creating PRs, run local verification checks (pre-commit hooks, secret scan, linters, pytest) locally whenever possible.
2. **Resilience & Autonomy**: Local verification guarantees continuous quality control regardless of remote CI billing quotas or network availability.

---

## Agent Governance & Human Approval Policy

1. **Mandatory Explicit Authorization**: Any modification to `.agents/AGENTS.md`, architectural specifications, or security boundaries NOT explicitly requested in writing by the maintainer MUST be flagged as **"Requer aprovação humana"** in the commit/PR description.
2. **Code Owner Review Required**: All PRs merging into `main` require explicit review and approval by `@mendsec`.
