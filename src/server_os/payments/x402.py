"""x402 micropayment helpers (mock + interface for real facilitators).

In production this module would:
- Parse PAYMENT-REQUIRED headers
- Construct signed payment payloads
- Call a facilitator or settle on-chain
- Attach PAYMENT-SIGNATURE on retry

The reference implementation uses the built-in `payment` tool and mock 402
responses from the `http` tool so that verification works offline.
"""

from __future__ import annotations

from typing import Any


def parse_payment_required(headers: dict[str, str]) -> dict[str, Any] | None:
    raw = headers.get("PAYMENT-REQUIRED") or headers.get("payment-required")
    if not raw:
        return None
    parts = {}
    for piece in raw.split(";"):
        if "=" in piece:
            k, v = piece.split("=", 1)
            parts[k.strip()] = v.strip()
    return parts or {"raw": raw}


def mock_settle(amount_usd: float, recipient: str) -> dict[str, Any]:
    return {
        "ok": True,
        "protocol": "x402-mock",
        "amount_usd": amount_usd,
        "recipient": recipient,
        "tx_id": f"mock_{hash((amount_usd, recipient)) & 0xFFFFFFFF:08x}",
    }
