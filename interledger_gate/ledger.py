"""Bounded offline accounting invariants, NOT an Interledger/ILPv4 settlement implementation."""
from dataclasses import dataclass

MAX_BALANCE = 2**63 - 1

class SettlementError(ValueError):
    """A transfer was rejected without changing ledger state."""

@dataclass(frozen=True)
class Transfer:
    tx_id: str
    source: str
    destination: str
    asset: str
    amount: int

def _name(value: str, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 128:
        raise SettlementError(f"INVALID_{field.upper()}")
    return value

def _amount(value: int, *, positive: bool) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < int(positive) or value > MAX_BALANCE:
        raise SettlementError("INVALID_AMOUNT")
    return value

class OfflineLedger:
    """In-memory, exact-integer, per-asset transfer invariant checker. No persistence/network."""
    def __init__(self, balances: dict[tuple[str, str], int]):
        self._balances: dict[tuple[str, str], int] = {}
        self._seen: set[str] = set()
        for (account, asset), amount in balances.items():
            _name(account, "account")
            self._asset(asset)
            self._balances[(account, asset)] = _amount(amount, positive=False)

    @staticmethod
    def _asset(asset: str) -> str:
        _name(asset, "asset")
        if not (3 <= len(asset) <= 12 and asset.isascii() and asset.isalnum() and asset.upper() == asset):
            raise SettlementError("INVALID_ASSET")
        return asset

    def snapshot(self) -> dict[tuple[str, str], int]:
        return dict(self._balances)

    def totals(self) -> dict[str, int]:
        totals: dict[str, int] = {}
        for (_, asset), balance in self._balances.items():
            totals[asset] = totals.get(asset, 0) + balance
        return totals

    def transfer(self, item: Transfer) -> None:
        if not isinstance(item, Transfer):
            raise SettlementError("INVALID_TRANSFER")
        tx_id = _name(item.tx_id, "tx_id")
        source = _name(item.source, "source")
        destination = _name(item.destination, "destination")
        asset = self._asset(item.asset)
        amount = _amount(item.amount, positive=True)
        if source == destination:
            raise SettlementError("SELF_TRANSFER")
        if tx_id in self._seen:
            raise SettlementError("DUPLICATE_TX_ID")
        src, dst = (source, asset), (destination, asset)
        if src not in self._balances or dst not in self._balances:
            raise SettlementError("UNKNOWN_ACCOUNT_ASSET")
        if self._balances[src] < amount:
            raise SettlementError("INSUFFICIENT_FUNDS")
        if self._balances[dst] > MAX_BALANCE - amount:
            raise SettlementError("BALANCE_OVERFLOW")
        # All checks precede state mutation; no partially applied transfer.
        self._balances[src] -= amount
        self._balances[dst] += amount
        self._seen.add(tx_id)

    def apply_batch(self, items: list[Transfer]) -> None:
        if not isinstance(items, list) or not items:
            raise SettlementError("INVALID_BATCH")
        candidate = OfflineLedger(self._balances)
        candidate._seen = self._seen.copy()
        for item in items:
            candidate.transfer(item)
        self._balances = candidate._balances
        self._seen = candidate._seen
