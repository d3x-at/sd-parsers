import sys
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from pathlib import Path


def crop_image(file: Path):
    with Image.open(file) as image:

        if image.format == "PNG":
            png_info = PngInfo()
            for key, value in image.text.items():
                png_info.add_text(key, value)

            cropped = Image.new(mode=image.mode, size=(1, 1))
            out_file = file.parent / f"{file.stem}_cropped{file.suffix}"
            cropped.save(out_file, pnginfo=png_info)


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        crop_image(Path(filename))
