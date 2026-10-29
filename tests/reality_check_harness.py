"""A real offline smoke check; never claim live ILP, RPC, PQC or settlement."""
from interledger_gate.ledger import OfflineLedger, Transfer

def main():
    ledger = OfflineLedger({("alice", "USD"): 100, ("bob", "USD"): 0})
    initial = ledger.totals()
    ledger.transfer(Transfer("smoke-1", "alice", "bob", "USD", 25))
    assert ledger.snapshot() == {("alice", "USD"): 75, ("bob", "USD"): 25}
    assert ledger.totals() == initial
    print("PASS: offline exact-integer balance conservation only; no network or production acceptance")

if __name__ == "__main__":
    main()
