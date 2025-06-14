import os
from pdf2image import convert_from_path
from django.conf import settings

# MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
PDF_FOLDER = os.path.join(settings.MEDIA_ROOT, "pdfs")
IMG_FOLDER = os.path.join(settings.MEDIA_ROOT, "pdf_images")

# ✅ 确保目录存在
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(IMG_FOLDER, exist_ok=True)

def process_pdf(pdf_file):
    """处理上传的 PDF 并转换成图片"""
    pdf_path = os.path.join(PDF_FOLDER, pdf_file.name)

    # ✅ 保存 PDF
    with open(pdf_path, "wb") as f:
        for chunk in pdf_file.chunks():
            f.write(chunk)

    # ✅ 转换 PDF 为图片
    images = convert_from_path(pdf_path)
    bookmarks = {}  # 存储书签（索引 -> 图片路径）

    # 获取 PDF 文件名（去掉扩展名）
    pdf_name = os.path.splitext(pdf_file.name)[0]

    for i, image in enumerate(images):
        # 修改图片命名，包含 PDF 名字
        image_name = f"{pdf_name}_page_{i+1}.jpg"
        image_path = os.path.join(IMG_FOLDER, image_name)
        image.save(image_path, "JPEG")
        bookmarks[i+1] = f"/media/pdf_images/{image_name}"

    return bookmarks
