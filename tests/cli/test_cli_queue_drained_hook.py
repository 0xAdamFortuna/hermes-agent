"""Tests for the cli_queue_drained plugin hook.

The hook fires after a successful CLI turn when the interactive input queue
is empty — the agent has finished all queued work and is about to await
new input. This is the point where completion cues (bell, voice TTS) are
safe to emit without interrupting pending queued turns.
"""

from hermes_cli.plugins import VALID_HOOKS


def test_cli_queue_drained_in_valid_hooks():
    """The hook name must be registered in VALID_HOOKS."""
    assert "cli_queue_drained" in VALID_HOOKS


def test_completion_voice_defaults_do_not_live_in_core_config():
    """Completion voice is plugin-owned; core config only exposes the generic hook."""
    from hermes_cli.config import DEFAULT_CONFIG

    display = DEFAULT_CONFIG.get("display", {})
    assert "completion_voice" not in display
