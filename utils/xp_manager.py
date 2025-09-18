# utils/xp_manager.py
import json
from typing import Any, Dict, Iterable, Union

Number = Union[int, float]

class XPManager:
    def __init__(self, schema_module):
        # Raw xp_balance dictionary from narrative_schema
        schema = getattr(schema_module, "schema", {}) or {}
        self._xp: Dict[str, Any] = schema.get("xp_balance", {}) or {}

    # ----- Public API ---------------------------------------------------------
    def get_reward(self, spec: Any) -> int:
        """
        Resolve an XP 'spec' into an integer amount.

        Accepted forms:
          - number:  50, 75.0
          - str:     "discovery_base", "quest_multipliers.secondary",
                     "base_quest_xp * quest_multipliers.secondary * 2"
          - list/tuple: ["discovery_base", "quest_multipliers.secondary"]
          - dict:    {"base": "base_quest_xp", "mult": "quest_multipliers.secondary"}
        """
        try:
            if spec is None:
                return 0

            # numbers pass through
            if isinstance(spec, (int, float)):
                return max(0, int(spec))

            # list/tuple -> sum of parts
            if isinstance(spec, (list, tuple)):
                total = sum(self._resolve_token(tok) for tok in spec)
                return max(0, int(total))

            # dict -> base * mult (optionally * extra)
            if isinstance(spec, dict):
                base = self._resolve_token(spec.get("base", 0))
                mult = self._resolve_token(spec.get("mult", 1))
                extra = self._resolve_token(spec.get("extra", 0))
                return max(0, int(base * mult + extra))

            # strings -> direct token or simple "*" expression
            if isinstance(spec, str):
                spec = spec.strip()
                if "*" in spec:
                    # very small parser for multiplicative chains:
                    # e.g., "base_quest_xp * quest_multipliers.secondary * 2"
                    product: float = 1.0
                    for part in spec.split("*"):
                        product *= float(self._resolve_token(part.strip()))
                    return max(0, int(product))
                else:
                    return max(0, int(self._resolve_token(spec)))

            # unknown type
            return 0
        except Exception:
            # Fail closed, not noisy: bad spec yields 0 xp but doesn’t crash UI
            return 0

    # ----- Internals ----------------------------------------------------------
    def _resolve_token(self, token: Any) -> float:
        """Resolve a single token to a float amount."""
        if token is None:
            return 0.0

        # numeric already
        if isinstance(token, (int, float)):
            return float(token)

        if not isinstance(token, str):
            return 0.0

        token = token.strip()
        if token == "":
            return 0.0

        # direct key in xp_balance (e.g., "discovery_base" or "base_quest_xp")
        if token in self._xp:
            return float(self._xp[token])

        # dot-path lookup inside xp_balance (e.g., "quest_multipliers.secondary")
        val = self._get_by_path(self._xp, token)
        if val is not None:
            # If the leaf is numeric, use it.
            if isinstance(val, (int, float)):
                return float(val)
            # If the leaf is a string that might itself be a token/number, recurse once
            if isinstance(val, str):
                return float(self._resolve_token(val))

        # try parsing as bare number string ("2", "1.5")
        try:
            return float(token)
        except ValueError:
            return 0.0

    @staticmethod
    def _get_by_path(root: Dict[str, Any], path: str) -> Any:
        """Safely walk a dot-separated path in a nested dict; return None if missing."""
        cur: Any = root
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return None
            cur = cur[part]
        return cur
