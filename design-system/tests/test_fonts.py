"""Exact font supply and coverage regressions; no additional runtime dependency."""
import importlib.util
import json
from pathlib import Path
import shutil

DS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_fonts", DS / "scripts/check-fonts.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def test_bundled_pair_has_vietnamese_and_dong_without_fallback():
    assert checker.check()["status"] == "PASS"
    manifest = json.loads((DS / "fonts/manifest.json").read_text(encoding="utf-8"))
    for item in manifest["fonts"]:
        data = (DS / "fonts" / item["file"]).read_bytes()
        for character in "ỂỖẬỮỜẲẴẶỪỸểỗậữờẳẵặừỹĐđ₫":
            assert checker.has_glyph(data, ord(character)), (item["family"], character)
        assert not checker.has_glyph(data, 0x10ffff)


def test_changed_binary_is_rejected(tmp_path):
    fonts = tmp_path / "fonts"
    shutil.copytree(DS / "fonts", fonts)
    manifest = json.loads((fonts / "manifest.json").read_text(encoding="utf-8"))
    file = fonts / manifest["fonts"][0]["file"]
    file.write_bytes(file.read_bytes() + b"tampered")
    result = checker.check(fonts)
    assert result["status"] == "FAIL"
    assert result["fonts"][0]["binary_hash"] is False


def test_uncovered_character_is_rejected(tmp_path):
    fonts = tmp_path / "fonts"
    shutil.copytree(DS / "fonts", fonts)
    path = fonts / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["fonts"][0]["glyph_probe"] += chr(0x10ffff)
    path.write_text(json.dumps(manifest), encoding="utf-8")
    result = checker.check(fonts)
    assert result["status"] == "FAIL"
    assert chr(0x10ffff) in result["fonts"][0]["missing_glyphs"]
