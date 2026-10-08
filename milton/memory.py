import json

from . import config


def _default_state():
    return {
        "active_app": None,
        "last_targets": [],
        "last_actions": [],
        "pending_confirmation": None,
        "user_corrections": [],
        "language_profile": "unknown",
    }


class Memory:
    """Persistent turn-to-turn memory matching the brain's expected schema."""

    def __init__(self, path=None):
        self.path = path or config.MEMORY_FILE
        self.state = self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return _default_state()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def as_dict(self):
        return self.state

    def apply_update(self, update, timestamp):
        """Apply a brain-produced memory_update object and persist it."""
        if not update:
            return

        if update.get("active_app"):
            self.state["active_app"] = update["active_app"]

        last_target = update.get("last_target")
        if last_target:
            entry = dict(last_target)
            entry["timestamp"] = timestamp
            self.state["last_targets"].append(entry)
            self.state["last_targets"] = self.state["last_targets"][-config.MAX_LAST_TARGETS :]

        action_log = update.get("append_action_log")
        if action_log:
            entry = dict(action_log)
            entry["timestamp"] = timestamp
            self.state["last_actions"].append(entry)
            self.state["last_actions"] = self.state["last_actions"][-config.MAX_LAST_ACTIONS :]

        # pending_confirmation is always set explicitly by the brain; None clears it.
        self.state["pending_confirmation"] = update.get("pending_confirmation")

        correction = update.get("append_correction")
        if correction:
            entry = dict(correction)
            entry["timestamp"] = timestamp
            self.state["user_corrections"].append(entry)

        self.save()
