import img2pdf
from pathlib import Path
from PIL import Image
import io


def generate_pdf(image_dir: Path, output_path: Path) -> Path:
    """ディレクトリ内の画像を連番順にPDFにまとめる

    PNGをJPEGに変換してからPDF化することで、メモリ使用量とサイズを削減。
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_files = sorted(image_dir.glob("*.png"))
    if not image_files:
        raise RuntimeError(f"No images found in {image_dir}")

    jpeg_data = []
    for img_path in image_files:
        img = Image.open(img_path)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        jpeg_data.append(buf.getvalue())

    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(jpeg_data))

    return output_path
