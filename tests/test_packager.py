import os
import pytest
from PIL import Image
from packager import check_image, package_set

def make_rgba_image(path, size=(320, 240), color=(255, 0, 0, 128)):
    img = Image.new("RGBA", size, color)
    img.save(path)
    return path

def test_check_image_valid(tmp_path):
    img_path = tmp_path / "test.png"
    make_rgba_image(img_path)
    assert check_image(img_path) is True

def test_check_image_size_exceed(tmp_path):
    img_path = tmp_path / "big.png"
    make_rgba_image(img_path, size=(400, 400))
    with pytest.raises(ValueError):
        check_image(img_path)

def test_check_image_mode(tmp_path):
    img_path = tmp_path / "rgb.png"
    img = Image.new("RGB", (320, 240), (255, 255, 255))
    img.save(img_path)
    with pytest.raises(ValueError):
        check_image(img_path)

def test_package_set(tmp_path):
    # 创建 mock 贴图
    img_paths = []
    for i in range(1, 3):
        p = tmp_path / f"{i:02d}.png"
        make_rgba_image(p)
        img_paths.append(str(p))
    # main.png/tab.png
    main_path = tmp_path / "main.png"
    tab_path = tmp_path / "tab.png"
    make_rgba_image(main_path, size=(240, 240))
    make_rgba_image(tab_path, size=(96, 74))
    img_paths += [str(main_path), str(tab_path)]
    idea = {"character": "测试角色"}
    zip_path = package_set(img_paths, idea, out_dir=str(tmp_path))
    assert os.path.exists(zip_path)
    # 检查 zip 内容
    from zipfile import ZipFile
    with ZipFile(zip_path, 'r') as z:
        names = z.namelist()
        assert "01.png" in names
        assert "main.png" in names
        assert "tab.png" in names