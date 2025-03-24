import os
import time
import pyautogui
import pytesseract
from pynput import mouse
from django.conf import settings
from utils.pdf_handler import process_pdf
from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image, ImageEnhance, ImageFilter
from django.views.decorators.csrf import csrf_exempt
from utils.OCR_inspection import auto_format_code_improved

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
THUMBNAIL_DIR = os.path.join(UPLOAD_DIR, 'thumbnails')

# 确保缩略图目录存在
os.makedirs(THUMBNAIL_DIR, exist_ok=True)


def index(request):
    return render(request, 'self-learn.html')


def upload_pdf(request):
    """上传 PDF 并转换为图片"""
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        bookmarks = process_pdf(pdf_file)  # ✅ 调用 process_pdf 处理 PDF
        return JsonResponse({"message": "PDF uploaded successfully", "bookmarks": bookmarks})
    return JsonResponse({"error": "Invalid request"}, status=400)


def view_bookmarks(request):
    """展示 PDF 转换后的页面"""
    img_folder = os.path.join(settings.MEDIA_ROOT, "pdf_images")  # ✅ 使用 settings.MEDIA_ROOT
    img_files = sorted(f for f in os.listdir(img_folder) if f.endswith(".jpg"))
    bookmarks = {i + 1: f"/media/pdf_images/{img}" for i, img in enumerate(img_files)}

    return render(request, "self-learn.html", {"bookmarks": bookmarks})


@csrf_exempt
def select_area(request):
    if request.method == 'POST':
        try:
            time.sleep(0.5)
            print('请拖动鼠标选择截屏区域...')
            coordinates = {'start': (-1, -1), 'end': (-1, -1)}

            def on_click(x, y, button, pressed):
                if pressed:
                    coordinates['start'] = (x, y)
                else:
                    coordinates['end'] = (x, y)
                    return False
            with mouse.Listener(on_click=on_click) as listener:
                listener.join()  # 阻塞等待鼠标操作

            if coordinates['start'] != (-1, -1) and coordinates['end'] != (-1, -1):
                start_x, start_y = coordinates['start']
                end_x, end_y = coordinates['end']
                print(f"start_x: {start_x}, start_y: {start_y}, end_x: {end_x}, end_y: {end_y}")

                # 使用MEDIA_ROOT构建路径 ✅
                screenshot_dir = os.path.join(settings.MEDIA_ROOT, 'screenshot')
                os.makedirs(screenshot_dir, exist_ok=True)  # 自动创建目录

                # 截图保存路径
                screenshot_path = os.path.join(screenshot_dir, 'screenshot.png')
                improved_path = os.path.join(screenshot_dir, 'improved_screenshot.png')

                screenshot = pyautogui.screenshot(region=(start_x, start_y, end_x - start_x, end_y - start_y))
                screenshot.save(screenshot_path)
                print('Screenshot saved as screenshot.png')

                image = Image.open(screenshot_path)
                image = image.convert('L')  # 转换为灰度图
                image = ImageEnhance.Contrast(image).enhance(2.0)  # 增加对比度
                image = image.filter(ImageFilter.SHARPEN)  # 锐化
                image.save(improved_path)
                print('Improved screenshot saved as improved_screenshot.png')

                return JsonResponse({
                    'start_x': start_x,
                    'start_y': start_y,
                    'end_x': end_x,
                    'end_y': end_y,
                    'success': True
                })
            else:
                return JsonResponse({'error': 'Mouse selection failed'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def preprocess_image(request):
    if request.method == 'POST':
        try:
            image_path = 'media/screenshot/improved_screenshot.png'
            image = Image.open(image_path)
            code = pytesseract.image_to_string(image, lang='eng+chi_sim', config="--oem 1 --psm 6")
            # reader = easyocr.Reader(['en', 'ch_sim'])  # 加载英文和简体中文
            # text_lines = reader.readtext('media/screenshot/improved_screenshot.png')
            #
            # text = "\n".join([line[1] for line in text_lines])

            with open("media/screenshot/output.txt", "w", encoding="utf-8") as file:
                formed_code = auto_format_code_improved(code)
                file.write(formed_code)
            print(formed_code)

            return JsonResponse({
                'code': formed_code,
                'success': True
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Preprocess image failed'}, status=500)

