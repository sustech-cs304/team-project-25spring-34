import os
import sys

import cv2
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings  # ✅ 让 Django 读取 settings.py 里的 MEDIA_ROOT
from django.views.decorators.csrf import csrf_exempt
import pyautogui
import pytesseract
import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pynput import mouse
import json
import time
import re

from pynput import mouse
from PIL import Image

# ✅ 直接指定 pdf_handler.py 的绝对路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ✅ 确保正确导入 process_pdf
from pdf_handler import process_pdf


@csrf_exempt
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

    return render(request, "viewer.html", {"bookmarks": bookmarks})


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


# ***********************************************************************


def detect_indent_unit(lines):
    """
    检测代码中最小的非零缩进空格数，作为单级缩进单位
    """
    indentations = [len(line) - len(line.lstrip(' ')) for line in lines if line.strip()]
    nonzero = [i for i in indentations if i > 0]
    if nonzero:
        return min(nonzero)
    return 4  # 如果没有缩进，默认返回 4


def balance_code(code):
    """
    对代码中未闭合的括号、方括号和花括号进行简单补全，
    直接在代码末尾追加缺失的闭合符号。
    """
    counts = {'(': 0, ')': 0, '[': 0, ']': 0, '{': 0, '}': 0}
    for char in code:
        if char in counts:
            counts[char] += 1
    # 按顺序补全：先圆括号，再方括号，再花括号
    if counts['('] > counts[')']:
        code += ')' * (counts['('] - counts[')'])
    if counts['['] > counts[']']:
        code += ']' * (counts['['] - counts[']'])
    if counts['{'] > counts['}']:
        code += '}' * (counts['{'] - counts['}'])
    return code


def fix_dictionary_key_quotes(code):
    """
    修正字典 key 中的引号问题，包括：
      1. 如果字典 key 前后引号不匹配，则统一转换为默认的单引号。
         匹配模式解释：
           ([{\s,])       匹配左大括号、逗号或空白字符（作为键前缀）
           (["'])        捕获开头的引号（单或双引号）
           ([A-Za-z_][A-Za-z0-9_]*)  匹配有效的标识符
           (["'])        捕获结尾的引号（可能与前面不同）
           (\s*:)        匹配冒号之前的可选空白字符
      2. 如果字典 key 后错误地附加了额外字母（例如：{'text's 或 'text's），
         则去除这些额外字母并加上正确的冒号分隔符。
    """

    # 修正引号不匹配问题
    def repl(match):
        prefix = match.group(1)
        quote1 = match.group(2)
        key = match.group(3)
        quote2 = match.group(4)
        suffix = match.group(5)
        if quote1 != quote2:
            fixed_quote = "'"  # 统一使用单引号
            return f"{prefix}{fixed_quote}{key}{fixed_quote}{suffix}"
        else:
            return match.group(0)

    code = re.sub(r'([{\s,])(["\'])([A-Za-z_][A-Za-z0-9_]*)(["\'])(\s*:)', repl, code)

    # 修正 key 后错误附加一串字母的情况
    code = re.sub(r"([\{\s])([A-Za-z_][A-Za-z0-9_]*)'([A-Za-z]+)(\s+)", r"\1'\2':\4", code)
    code = re.sub(r"('(?:\w+)')([A-Za-z]+)(\s+)", r"\1:\3", code)

    return code


def fix_mismatched_quotes_in_comparisons(code):
    """
    修正代码中比较语句中引号不匹配的问题，
    适用于形如：if xxx == "somevalue' 或 if xxx == 'somevalue"
    统一将引号修正为默认的单引号。

    匹配模式解释：
      (==\s*)                 匹配比较操作符及紧随的空白字符
      (["'])([^"']+?)(["'])   分别捕获开头的引号、内容和结束的引号
    """

    def repl(match):
        operator = match.group(1)
        quote1 = match.group(2)
        content = match.group(3).strip()  # 去除两侧空白
        quote2 = match.group(4)
        if quote1 != quote2:
            fixed_quote = "'"  # 默认使用单引号
        else:
            fixed_quote = quote1
        print("123")
        return f"{operator}{fixed_quote}{content}{fixed_quote}"

    return re.sub(r'(==\s*)(["\'])([^"\']+?)(["\'])', repl, code)


def fix_extra_spaces(code):
    """
    移除对象属性调用中的多余空格，
    例如将 "request .POST" 修正为 "request.POST"
    """
    return re.sub(r'(\w+)\s+\.(\w+)', r'\1.\2', code)


def auto_format_code_improved(code_str):
    """
    自动补全缩进并检查符号缺失的代码格式化函数（改进版）
    功能：
      1. 替换中文引号为英文引号
      2. 自动为需要的行补全缺失的冒号
      3. 根据检测到的实际缩进单位，结合原始缩进层级（base_level）来调整缩进，
         保持部分正确缩进信息，同时统一输出为每层4个空格
      4. 后处理：修正字典中识别错误导致的缺失冒号问题
      5. 简单补全未闭合的括号
    """
    # 1. 替换中文引号为英文引号
    code_str = re.sub(r'[‘’]', "'", code_str)
    code_str = re.sub(r'[“”]', '"', code_str)

    # 2. 分割代码行，并检测缩进单位
    lines = code_str.splitlines()
    indent_unit = detect_indent_unit(lines)

    formatted_lines = []
    indent_level = 0  # 维护的全局缩进级别

    # 定义关键字
    block_keywords = ('def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally', 'with')
    dedent_trigger_keywords = ('elif', 'else', 'except', 'finally')
    dedent_line_keywords = ('return', 'break', 'continue', 'pass', 'raise')

    for line in lines:
        # 计算原始缩进层级
        orig_indent = len(line) - len(line.lstrip(' '))
        base_level = orig_indent // indent_unit if indent_unit else 0
        # 如果原有缩进层级高于当前维护的缩进，则采用原有的
        if base_level > indent_level:
            indent_level = base_level

        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
            continue

        # 如果行以 dedent_trigger_keywords 开头，则先降低缩进
        if any(stripped.startswith(kw) for kw in dedent_trigger_keywords):
            indent_level = max(indent_level - 1, 0)

        # 自动补全冒号：如果行以 block_keywords 开头但没有以冒号结尾，则加上
        words = stripped.split()
        if words and words[0] in block_keywords and not stripped.endswith(':'):
            stripped += ':'

        # 使用当前缩进级别（统一为4空格）输出行
        formatted_lines.append(' ' * (indent_level * 4) + stripped)

        # 根据行结尾调整缩进
        if stripped.endswith(':'):
            indent_level += 1
        elif any(stripped.startswith(kw) for kw in dedent_line_keywords):
            if indent_level > 0:
                indent_level -= 1

    formatted_code = "\n".join(formatted_lines)

    formatted_code = fix_extra_spaces(formatted_code)
    formatted_code = fix_mismatched_quotes_in_comparisons(formatted_code)
    formatted_code = fix_dictionary_key_quotes(formatted_code)
    formatted_code = balance_code(formatted_code)

    return formatted_code
