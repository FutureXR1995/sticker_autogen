import os
from PIL import Image
from image_generator import create_stickers

def test_create_stickers_mock(tmp_path):
    idea = {
        "character": "可爱猫君",
        "phrases": ["你好", "加油"],
        "style": "flat pastel, bold outline",
        "palette": ["#FCE99B", "#FFC1C1", "#334D5C"]
    }
    out_dir = tmp_path / "stickers"
    paths = create_stickers(idea, mock=True, out_dir=str(out_dir))
    # 应该有2张贴图+main.png+tab.png
    assert len(paths) == 4
    for p in paths:
        assert os.path.exists(p)
        img = Image.open(p)
        assert img.mode == "RGBA"
    # 检查主图尺寸
    main_img = Image.open(os.path.join(out_dir, "main.png"))
    assert main_img.size == (240, 240)
    # 检查tab图尺寸
    tab_img = Image.open(os.path.join(out_dir, "tab.png"))
    assert tab_img.size == (96, 74)