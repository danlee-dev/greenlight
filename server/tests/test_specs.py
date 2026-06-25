"""Screenshot specs must render at exact pixel dimensions (Apple enforces no
off-by-one tolerance)."""
from greenlight_mcp import screenshots as shots


def test_every_spec_renders_exact_dimensions(tmp_path):
    for spec, meta in shots.SPECS.items():
        out = shots.render_marketing_panel(spec, "Pass review", "subtitle",
                                           tmp_path / f"{spec}.png")
        from PIL import Image
        assert Image.open(out).size == (meta["w"], meta["h"]), spec


def test_feature_graphic_dimensions(tmp_path):
    from PIL import Image
    out = shots.render_feature_graphic("Greenlight", "Ship to both stores",
                                       tmp_path / "feature.png")
    assert Image.open(out).size == (1024, 500)


def test_unknown_spec_raises(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        shots.render_marketing_panel("not_a_spec", "x", "y", tmp_path / "x.png")
