import img2pdf
from pathlib import Path


def generate_pdf(image_dir: Path, output_path: Path) -> Path:
    """ディレクトリ内の画像を連番順にPDFにまとめる"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_files = sorted(image_dir.glob("*.png"))
    if not image_files:
        raise RuntimeError(f"No images found in {image_dir}")

    image_bytes = [open(f, "rb").read() for f in image_files]

    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(image_bytes))

    return output_path
