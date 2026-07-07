"""Gateway-only context file loading.

Regression coverage for the generic ``gateway.context_files`` seam. The gateway
must load configured files as ephemeral system context, not via hardcoded
Adam-specific filenames or user-message injection.
"""

from gateway import run as gateway_run
from gateway.run import GatewayRunner


class TestGatewayContextFiles:
    def test_load_gateway_context_files_method_exists(self):
        """The static method must exist on GatewayRunner."""
        assert hasattr(GatewayRunner, "_load_gateway_context_files")
        assert callable(getattr(GatewayRunner, "_load_gateway_context_files"))

    def test_load_gateway_context_files_returns_str(self):
        """Method returns a string (empty when no files are configured)."""
        result = GatewayRunner._load_gateway_context_files({"gateway": {"context_files": []}})
        assert isinstance(result, str)
        assert result == ""

    def test_load_gateway_context_files_uses_configured_relative_files(self, tmp_path, monkeypatch):
        """Configured relative paths resolve under the active Hermes home."""
        monkeypatch.setattr(gateway_run, "_hermes_home", tmp_path)
        gateway_dir = tmp_path / "gateway"
        gateway_dir.mkdir()
        (gateway_dir / "SOUL.gateway.md").write_text("gateway soul", encoding="utf-8")
        (gateway_dir / "MEMORY.gateway.md").write_text("gateway memory", encoding="utf-8")

        result = GatewayRunner._load_gateway_context_files(
            {
                "gateway": {
                    "context_files": [
                        {"path": "gateway/SOUL.gateway.md", "label": "SOUL.gateway.md"},
                        "gateway/MEMORY.gateway.md",
                    ]
                }
            }
        )

        assert "Gateway-only context files" in result
        assert "## SOUL.gateway.md\ngateway soul" in result
        assert "## MEMORY.gateway.md\ngateway memory" in result

    def test_load_gateway_context_files_does_not_use_hardcoded_files_without_config(self, tmp_path, monkeypatch):
        """Adam-specific file names are not loaded unless config opts them in."""
        monkeypatch.setattr(gateway_run, "_hermes_home", tmp_path)
        gateway_dir = tmp_path / "gateway"
        gateway_dir.mkdir()
        (gateway_dir / "SOUL.gateway.md").write_text("must not load", encoding="utf-8")

        result = GatewayRunner._load_gateway_context_files({"gateway": {}})

        assert result == ""
