# QMOOSA-0955 — Interledger connector tests component

Canonical role: **tests**. Current implemented scope: `interledger_gate/ledger.py` with an exact-integer, per-asset, in-memory accounting invariant checker; `tests/reality_battery.py` with adversarial regressions; `tests/reality_check_harness.py` with an offline smoke check; `src/main.rs` with a bounded Rust arithmetic invariant.

**Not implemented or verified:** ILPv4 packets, connectors, authentication, cross-ledger settlement, x402, QuickNode RPC, NIST PQC algorithms, FIPS validation, Conway automata, Raven/REA, production tokenomics, wallet integration, and live deployments. These remain proposed architecture, not completed features.

**Reality Gate:** distinguish a green offline unit-test workflow from protocol interoperability, security approval, and production readiness. No `100/100` score or security certification is asserted. Review the unverified Solidity contract separately before any use.
