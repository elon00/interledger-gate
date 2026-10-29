"""Implementation-coupled adversarial tests for offline accounting only."""
import unittest
from interledger_gate.ledger import MAX_BALANCE, OfflineLedger, SettlementError, Transfer

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.ledger = OfflineLedger({
            ("alice", "USD"): 100, ("bob", "USD"): 10,
            ("alice", "EUR"): 20, ("bob", "EUR"): 0,
        })

    def tx(self, tx_id="tx1", source="alice", destination="bob", asset="USD", amount=25):
        return Transfer(tx_id, source, destination, asset, amount)

    def test_exact_transfer_and_asset_conservation(self):
        before = self.ledger.totals()
        self.ledger.transfer(self.tx())
        self.assertEqual(self.ledger.snapshot()[("alice", "USD")], 75)
        self.assertEqual(self.ledger.snapshot()[("bob", "USD")], 35)
        self.assertEqual(self.ledger.totals(), before)

    def test_duplicate_replay_rejected_without_mutation(self):
        self.ledger.transfer(self.tx())
        before = self.ledger.snapshot()
        with self.assertRaisesRegex(SettlementError, "DUPLICATE_TX_ID"):
            self.ledger.transfer(self.tx())
        self.assertEqual(self.ledger.snapshot(), before)

    def test_insufficient_funds_fail_closed(self):
        before = self.ledger.snapshot()
        with self.assertRaisesRegex(SettlementError, "INSUFFICIENT_FUNDS"):
            self.ledger.transfer(self.tx(amount=101))
        self.assertEqual(self.ledger.snapshot(), before)

    def test_zero_negative_float_and_bool_rejected(self):
        for amount in (0, -1, 1.5, True):
            with self.subTest(amount=amount), self.assertRaises(SettlementError):
                self.ledger.transfer(self.tx(amount=amount))

    def test_unknown_account_and_asset_rejected(self):
        for item in (self.tx(source="unknown"), self.tx(destination="unknown"), self.tx(asset="GBP")):
            with self.subTest(item=item), self.assertRaises(SettlementError):
                self.ledger.transfer(item)

    def test_self_transfer_rejected(self):
        with self.assertRaisesRegex(SettlementError, "SELF_TRANSFER"):
            self.ledger.transfer(self.tx(destination="alice"))

    def test_invalid_identifiers_and_asset_rejected(self):
        for item in (self.tx(tx_id=" "), self.tx(source=" alice"), self.tx(asset="usd"), self.tx(asset="US-D")):
            with self.subTest(item=item), self.assertRaises(SettlementError):
                self.ledger.transfer(item)

    def test_overflow_rejected(self):
        ledger = OfflineLedger({("alice", "USD"): 2, ("bob", "USD"): MAX_BALANCE})
        with self.assertRaisesRegex(SettlementError, "BALANCE_OVERFLOW"):
            ledger.transfer(self.tx(amount=1))

    def test_initial_negative_and_bool_balance_rejected(self):
        for bad in (-1, True, MAX_BALANCE + 1):
            with self.subTest(bad=bad), self.assertRaises(SettlementError):
                OfflineLedger({("alice", "USD"): bad})

    def test_batch_atomic_rollback_on_insufficient_funds(self):
        before = self.ledger.snapshot()
        with self.assertRaisesRegex(SettlementError, "INSUFFICIENT_FUNDS"):
            self.ledger.apply_batch([self.tx(amount=90), self.tx(tx_id="tx2", amount=11)])
        self.assertEqual(self.ledger.snapshot(), before)
        self.ledger.transfer(self.tx())
        self.assertEqual(self.ledger.snapshot()[("alice", "USD")], 75)

    def test_batch_atomic_rollback_on_duplicate(self):
        before = self.ledger.snapshot()
        with self.assertRaisesRegex(SettlementError, "DUPLICATE_TX_ID"):
            self.ledger.apply_batch([self.tx(), self.tx()])
        self.assertEqual(self.ledger.snapshot(), before)

    def test_batch_success_and_asset_isolation(self):
        before = self.ledger.totals()
        self.ledger.apply_batch([self.tx(), self.tx(tx_id="tx2", asset="EUR", amount=10)])
        self.assertEqual(self.ledger.totals(), before)
        self.assertEqual(self.ledger.snapshot()[("bob", "EUR")], 10)

    def test_snapshot_is_defensive_copy(self):
        snapshot = self.ledger.snapshot()
        snapshot[("alice", "USD")] = 999
        self.assertEqual(self.ledger.snapshot()[("alice", "USD")], 100)

    def test_invalid_batch_rejected(self):
        for batch in ([], None, (self.tx(),)):
            with self.subTest(batch=batch), self.assertRaises(SettlementError):
                self.ledger.apply_batch(batch)

    def test_duplicate_across_batches_rejected(self):
        self.ledger.apply_batch([self.tx()])
        before = self.ledger.snapshot()
        with self.assertRaisesRegex(SettlementError, "DUPLICATE_TX_ID"):
            self.ledger.apply_batch([self.tx()])
        self.assertEqual(self.ledger.snapshot(), before)

if __name__ == "__main__":
    unittest.main()
