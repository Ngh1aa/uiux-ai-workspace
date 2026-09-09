from pathlib import Path


SERVER_SOURCE = (
    Path(__file__).resolve().parents[1] / "apps" / "web" / "server.py"
).read_text(encoding="utf-8")


def test_console_does_not_emit_nonstandard_allowall_frame_header() -> None:
    assert "ALLOWALL" not in SERVER_SOURCE
    assert 'self.send_header("X-Frame-Options", "DENY")' in SERVER_SOURCE
    assert '"frame-ancestors \'none\'"' in SERVER_SOURCE


def test_console_preserves_preview_content_security_policy_through_proxy() -> None:
    assert '"Content-Security-Policy"' in SERVER_SOURCE
    assert "PROXY_RESPONSE_HEADERS" in SERVER_SOURCE
    assert "response.headers.get(header)" in SERVER_SOURCE


def test_console_csp_allows_only_local_bridge_as_extra_connection_origin() -> None:
    assert "BRIDGE_ORIGIN = _bridge_origin()" in SERVER_SOURCE
    assert "connect-src 'self'" in SERVER_SOURCE
    assert "frame-src 'self'" in SERVER_SOURCE
