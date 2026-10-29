# Security and acceptance status

**SECURITY_APPROVED: NO. DEPLOYMENT_READY: NO. Production-certified: NO. FIPS validation: NOT CLAIMED.**

The only verified-by-design scope of the new checker is deterministic **offline** accounting invariants for exact integer amounts. It is not a cryptographic protocol, Interledger settlement system, or authorization layer. The in-memory duplicate-ID set is lost on restart; it is **not** durable replay protection. Do not connect this checker to real assets, wallets, payments, public networks, or privileged services.

Review gates before any expansion: authenticated peer identity, ILPv4 packet and fulfillment semantics, atomic durable idempotency, crash/restart recovery, balance reconciliation, audit logging, fuzz/property tests, dependency and CodeQL findings, and independent security review. The Solidity contract in `contracts/` has not been security-audited here. Do not infer bug-bounty eligibility or monetary rewards from repository text.

Report suspected vulnerabilities through GitHub private vulnerability reporting if enabled, or coordinate privately with the repository owner; do not disclose secrets in issues.
