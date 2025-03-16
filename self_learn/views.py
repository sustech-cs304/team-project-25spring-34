import pyautogui
import pytesseract
import time
from PIL import Image, ImageEnhance, ImageFilter
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pynput import mouse
from PIL import Image
from utils.OCR_inspection import auto_format_code_improved



def index(request):
    return render(request, 'self-learn.html')

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

                screenshot = pyautogui.screenshot(region=(start_x, start_y, end_x - start_x, end_y - start_y))
                image_path = 'media/screenshot/screenshot.png'
                screenshot.save(image_path)
                print('Screenshot saved as screenshot.png')

                image = Image.open(image_path)
                image = image.convert('L')  # 转换为灰度图
                image = ImageEnhance.Contrast(image).enhance(2.0)  # 增加对比度
                image = image.filter(ImageFilter.SHARPEN)  # 锐化
                image.save('media/screenshot/improved_screenshot.png')
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

