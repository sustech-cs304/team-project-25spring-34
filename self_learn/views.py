import os
import re
import time
import pyautogui
import pytesseract
from pynput import mouse
from django.conf import settings
from utils.pdf_handler import process_pdf
from django.http import JsonResponse
from PIL import Image, ImageEnhance, ImageFilter
from django.views.decorators.csrf import csrf_exempt
from utils.OCR_inspection import auto_format_code_improved
import subprocess
from django.http import HttpResponse
from django.shortcuts import render
import json
import requests

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
THUMBNAIL_DIR = os.path.join(UPLOAD_DIR, 'thumbnails')
BOOKMARKS_FILE = os.path.join(UPLOAD_DIR, 'bookmarks.json')

# 确保缩略图目录存在
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# 确保书签文件存在
if not os.path.exists(BOOKMARKS_FILE):
    with open(BOOKMARKS_FILE, 'w') as f:
        json.dump({}, f)

# location
file_path = ''



@csrf_exempt
def delete_pdf(request, data_course):
    """删除 PDF 文件"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pdf_name = data.get("pdf_name")
            username = request.user.username

            if not pdf_name:
                return JsonResponse({"error": "缺少 pdf_name"}, status=400)

            # 构造 PDF 文件路径
            user_course_dir = os.path.join(settings.MEDIA_ROOT, data_course, username)
            pdf_path = os.path.join(user_course_dir, pdf_name)

            if os.path.exists(pdf_path):
                os.remove(pdf_path)

                # 删除缩略图（如果存在）
                thumb_path = os.path.join(settings.MEDIA_ROOT, "pdf_images", pdf_name.replace(".pdf", "_page_1.jpg"))
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)

                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"error": "文件不存在"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "无效请求"}, status=400)



def index(request, data_course):
    code = ''
    # 渲染主页面，并将代码传递到模板
    return render(request, 'self-learn.html', {'code': code, 'data_course': data_course})

def get_bookmarks_file(data_course):
    """获取当前课程的专属书签文件路径"""
    course_dir = os.path.join(UPLOAD_DIR, 'bookmarks', data_course)
    os.makedirs(course_dir, exist_ok=True)
    return os.path.join(course_dir, 'bookmarks.json')

def ensure_bookmarks_file(data_course):
    """确保书签文件存在"""
    bookmarks_file = get_bookmarks_file(data_course)
    if not os.path.exists(bookmarks_file):
        with open(bookmarks_file, 'w') as f:
            json.dump({}, f)
    return bookmarks_file

def extract_class_name(java_code, data_course):
    """
    从Java代码中提取公共类名.必须是public class xxx才能提取到.且提取第一个
    """
    """
     * AI-generated-content
     * tool:Hunyuan
     * version: latest
     * usage: I used the prompt "从Java代码中提取公共类名.必须是public class xxx才能提取到.且提取第一个", and
     * directly copy the code from its response
    """
    match = re.search(r'public\s+class\s+([A-Za-z_$][A-Za-z\d_$]*)', java_code)
    if match:
        return match.group(1)
    return None

def lesson(request, data_course):
    return render(request, 'lesson.html')


def hello(request, data_course):
    return HttpResponse("Hello world ! ")


def run_code(request, data_course):
    """
     * AI-generated-content
     * tool:Hunyuan
     * version: latest
     * usage: I used the prompt "读取txt并返回运行结果到前端", and
     * use the framework it provides, but modify some of the details
    """
    if request.method == 'POST':
        code = request.POST.get('code', '')
        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)

        formed_code, type = auto_format_code_improved(code)
        file_type = type
        print("code type:", file_type)

        if file_type == "j":
            file_path = r"media\screenshot\output_java.txt"
        else:
            file_path = r"media\screenshot\output_python.txt"

        with open(file_path, 'w') as f:
            f.write(code)

        if file_type == 'j':
            class_name = extract_class_name(code, data_course)
            print("class name:", class_name)
            temp_path = os.path.join('self_learn', 'code_test', class_name + ".java")

            with open(temp_path, 'w') as f:
                f.write(code)

            compile_result = subprocess.run(
                ['javac', temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            if compile_result.returncode != 0:
                print("compile error:", compile_result)
                return JsonResponse({
                    'error': 'Java compilation failed',
                    'stderr': compile_result.stderr
                }, status=400)

            run_result = subprocess.run(
                ['java', '-cp', os.path.dirname(temp_path), class_name],
                capture_output=True,
                text=True,
                timeout=5
            )

            class_file = temp_path.replace('.java', '.class')
            if os.path.exists(class_file):
                os.remove(class_file)

            return JsonResponse({
                'stdout': run_result.stdout,
                'stderr': run_result.stderr,
            })
        else:
            try:
                result = subprocess.run(
                    ['python', file_path],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return JsonResponse({
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                })
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def upload_pdf(request, data_course):
    """上传 PDF 并根据课程和用户名分类存储"""
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        if not pdf_file.name.endswith('.pdf'):
            return JsonResponse({"error": "仅支持 PDF 文件"}, status=400)
        
        bookmarks = process_pdf(pdf_file)  # ✅ 调用 process_pdf 处理 PDF

        # 动态生成存储路径
        user_course_dir = os.path.join(settings.MEDIA_ROOT, data_course, request.user.username)
        os.makedirs(user_course_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(user_course_dir, pdf_file.name)
        with open(file_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        return JsonResponse({"message": "PDF 上传成功！"}, status=200)

    return JsonResponse({"error": "无效请求"}, status=400)

def view_bookmarks(request, data_course):
    """展示 PDF 转换后的页面"""
    pdf_name = request.GET.get('pdf_name', 'sample.pdf')  # 默认加载 sample.pdf
    img_folder = os.path.join(settings.MEDIA_ROOT, "pdf_images")  # ✅ 使用 settings.MEDIA_ROOT
    img_files = sorted(f for f in os.listdir(img_folder) if f.endswith(".jpg"))
    bookmarks = {i + 1: f"/media/pdf_images/{img}" for i, img in enumerate(img_files)}

    return render(request, "self-learn.html", {
        "pdf_name": pdf_name,
        "bookmarks": bookmarks
    })



def view_bookmarks(request, data_course):
    """展示 PDF 转换后的页面"""
    pdf_name = request.GET.get('pdf_name', 'sample.pdf')  # 默认加载 sample.pdf
    img_folder = os.path.join(settings.MEDIA_ROOT, "pdf_images")  # ✅ 使用 settings.MEDIA_ROOT
    img_files = sorted(f for f in os.listdir(img_folder) if f.endswith(".jpg"))
    bookmarks = {i + 1: f"/media/pdf_images/{img}" for i, img in enumerate(img_files)}

    return render(request, "self-learn.html", {
        "pdf_name": pdf_name,
        "bookmarks": bookmarks
    })


# AI-generated-content
# tool: ChatGPT
# version: latest
# usage：生成鼠标拖动时，将鼠标选择框住的位置截屏并保存的python代码架构？
@csrf_exempt
def select_area(request, data_course):
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


def preprocess_image(request, data_course):
    global file_path
    if request.method == 'POST':
        try:
            image_path = 'media/screenshot/improved_screenshot.png'
            image = Image.open(image_path)
            code = pytesseract.image_to_string(image, lang='eng+chi_sim', config="--oem 1 --psm 6")
            formed_code, type = auto_format_code_improved(code)
            if type == "p":
                with open("media/screenshot/output_python.txt", "w", encoding="utf-8") as file:
                    file.write(formed_code)
                    file_path = "media/screenshot/output_python.txt"
            if type == "j":
                with open("media/screenshot/output_java.txt", "w", encoding="utf-8") as file:
                    file.write(formed_code)
                    file_path = "media/screenshot/output_java.txt"
            print(formed_code)
            return JsonResponse({
                'code': formed_code,
                'success': True
            })
        except Exception as e:
            print(f"Error in preprocess_image: {e}")  # 打印详细错误
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Preprocess image failed'}, status=500)


def intelligent_preprocess_image(request, data_course):
    global file_path
    if request.method == 'POST':
        try:
            image_path = 'media/screenshot/improved_screenshot.png'
            image = Image.open(image_path)
            code = pytesseract.image_to_string(image, lang='eng+chi_sim', config="--oem 1 --psm 6")
            formed_code, type = auto_format_code_improved(code)
            standard_code = deepseek_intelligent_code_repair(formed_code, type, data_course)
            if type == "p":
                with open("media/screenshot/output_python.txt", "w", encoding="utf-8") as file:
                    file.write(standard_code)
                    file_path = "media/screenshot/output_python.txt"
            if type == "j":
                with open("media/screenshot/output_java.txt", "w", encoding="utf-8") as file:
                    file.write(standard_code)
                    file_path = "media/screenshot/output_java.txt"
            print(standard_code)
            return JsonResponse({
                'code': standard_code,
                'success': True
            })
        except Exception as e:
            print(f"Error in intelligent_preprocess_image: {e}")  # 打印详细错误
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Preprocess image failed'}, status=500)


def deepseek_intelligent_code_repair(code, type, data_course):
    try:
        if type == "p":
            prompt = "严格遵守以下原则并回答问题：\n一、修复python代码格式、语法问题并严格保留代码内容\n二、并补全代码上下文使其能够正常编译(包括psvm最外层的类)，能够正常运行（标准为看到输出）\n三、你只需要返回修复后的代码，不需要再返回任何内容\n代码如下：\n"
        else:
            prompt = "严格遵守以下原则并回答问题：\n一、修复java代码格式、语法问题并严格保留代码内容\n二、并补全代码上下文使其能够正常编译(包括psvm最外层的类)，能够正常运行（标准为看到输出）\n三、你只需要返回修复后的代码，不需要再返回任何内容\n代码如下：\n"

        full_prompt = prompt + code  # 仅文本提问

        # 调用 DeepSeek
        DEEPSEEK_API_KEY = "sk-a82d853f78ec4dfa9dc73debce4f68b6"
        API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.7
        }

        response = requests.post(API_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        code = response.json()["choices"][0]["message"]["content"]

        lines = code.split('\n')
        filtered_lines = lines[1:-1]
        result = '\n'.join(filtered_lines)

        return result
    except Exception as e:
        print(e)


@csrf_exempt
def get_pdf_list(request, data_course):
    """获取当前课程和用户名下的 PDF 文件列表"""
    user_course_dir = os.path.join(settings.MEDIA_ROOT, data_course, request.user.username)
    if not os.path.exists(user_course_dir):
        return JsonResponse({"pdfs": []}, status=200)

    # 获取文件列表
    pdf_files = [f for f in os.listdir(user_course_dir) if f.endswith('.pdf')]
    return JsonResponse({"pdfs": pdf_files}, status=200)
#  /*
#      * AI-generated-content
#      * tool: GitHub Copilot
#      * version: latest
#      * usage: I used Copilot to fix syntax errors and standardize code.
#      */
@csrf_exempt
def get_bookmarks(request, data_course):
    """获取指定 PDF 的书签"""
    pdf_name = request.GET.get('pdf_name')
    bookmarks_file = ensure_bookmarks_file(data_course)

    with open(bookmarks_file, 'r') as f:
        bookmarks = json.load(f)

    if pdf_name not in bookmarks:
        bookmarks[pdf_name] = []
        with open(bookmarks_file, 'w') as f:
            json.dump(bookmarks, f)

    return JsonResponse(bookmarks.get(pdf_name, []), safe=False)


@csrf_exempt
def add_bookmark(request, data_course):
    """添加书签"""
    data = json.loads(request.body)
    pdf_name = data.get('pdf_name')
    description = data.get('description', '').strip()
    category = data.get('category', '').strip()
    page = data.get('page')

    if not (pdf_name and description and category and isinstance(page, int) and page > 0):
        return JsonResponse({'error': '缺少必要参数或参数无效'}, status=400)

    bookmarks_file = ensure_bookmarks_file(data_course)
    with open(bookmarks_file, 'r') as f:
        bookmarks = json.load(f)

    if pdf_name not in bookmarks:
        bookmarks[pdf_name] = []

    bookmarks[pdf_name].append({
        'description': description,
        'category': category,
        'page': page,
        'course': data_course  # 添加课程标识
    })

    with open(bookmarks_file, 'w') as f:
        json.dump(bookmarks, f)
    return JsonResponse({'success': True})


@csrf_exempt
def delete_bookmark(request, data_course):
    """删除书签"""
    data = json.loads(request.body)
    pdf_name = data.get('pdf_name')
    index = data.get('index')

    bookmarks_file = ensure_bookmarks_file(data_course)
    with open(bookmarks_file, 'r') as f:
        bookmarks = json.load(f)

    if pdf_name in bookmarks and 0 <= index < len(bookmarks[pdf_name]):
        bookmarks[pdf_name].pop(index)
        with open(bookmarks_file, 'w') as f:
            json.dump(bookmarks, f)
        return JsonResponse({'success': True})

    return JsonResponse({'error': '书签不存在'}, status=404)


def load_bookmarks(data_course):
    """加载书签文件"""
    print(f"加载书签文件: {BOOKMARKS_FILE}")  # 调试日志
    with open(BOOKMARKS_FILE, 'r') as f:
        return json.load(f)


def save_bookmarks(bookmarks, data_course):
    """保存书签到文件"""
    print(f"保存书签到文件: {BOOKMARKS_FILE}")  # 调试日志
    with open(BOOKMARKS_FILE, 'w') as f:
        json.dump(bookmarks, f)
