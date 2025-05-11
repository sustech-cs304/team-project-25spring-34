from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.views.decorators.clickjacking import xframe_options_exempt
import re
import os
import uuid
import asyncio
import sys
from playwright.async_api import async_playwright
from IDEframework import settings
import fitz  # PyMuPDF

# pip install playwright
# playwright install chromium  # 自动下载内置的 Chromium

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@xframe_options_exempt
def embed_chat(request):
    return render(request, 'embed.html')


Mind_map = False
Test = False

Mind_map_tem = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>思维导图</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.0.0/dist/mermaid.esm.min.mjs';
    </script>
</head>
<body>
    <h1>tem_title</h1>

    <div class="mermaid">
        graph TD;

    </div>

    <script type="text/javascript">
        mermaid.initialize({ startOnLoad: true });
    </script>
</body>
</html>
"""

Test_tem = """
<!DOCTYPE html>
<html lang="en">
    <title>...</title>
    <style>
        .question {margin-bottom: 20px;}
        .score {color: green; font-weight: bold;}
        .explanation {color: #666; display: none;}
        .correct {background-color: #e6ffe6;}
        .wrong {background-color: #ffe6e6;}
    </style>
</head>
<body>
    <h2>...</h2>

    <!-- Fill in the Blanks -->
    <div class="question">
        <h3>填空题</h3>
        <p>1. ...：<input type="text" size="15">...</p>
    </div>

    <!-- Multiple Choice -->
    <div class="question">
        <h3>选择题</h3>
        <div>
            <p>1....</p>
            <input type="radio" name="q4" value="A"> A. ...<br>
            <input type="radio" name="q4" value="B"> B. ...<br>
            <input type="radio" name="q4" value="C"> C. ...<br>
            <input type="radio" name="q4" value="D"> D. ...
            ...
        </div>
    </div>

    <button onclick="checkAnswers()">提交答案</button>
    <div id="score"></div>

    <!-- Answers and Explanations -->
    <div id="answers" style="display:none;">
        <h3>答案解析</h3>
        <p>1. 答案：...<br>
           解析：...</p>
        ...
    </div>

    <script>
        function checkAnswers() {
            let score = 0;
            
            // Check填空

            // Check选择

            // Show results
            document.getElementById('score').innerHTML = `得分: <span class="score">${score}</span>/15`;
            document.getElementById('answers').style.display = 'block';
        }
    </script>
</body>
</html>
"""

# AI-generated-content
# tool: DeepSeek
# version: latest
# usage：如何使用playwright和chromium将html文件在合适的位置自动识别边界并保存
async def html_to_png(html_path: str, output_png_path: str):
    """将 HTML 文件转为 PNG 图片（智能裁剪）"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 设置更合理的视口
        await page.set_viewport_size({"width": 1600, "height": 900})

        await page.goto(f"file://{html_path}")

        # 等待核心元素渲染
        await page.wait_for_selector(".mermaid svg", timeout=10000)  # 增加超时时间
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        # 获取元素边界框
        bbox = await page.locator(".mermaid svg").bounding_box()

        # 动态计算裁剪区域（扩展 20px 边距）
        clip = {
            "x": bbox["x"] - 20,
            "y": bbox["y"] - 20,
            "width": bbox["width"] + 40,
            "height": bbox["height"] + 40
        }

        # 截图并直接保存
        await page.screenshot(
            path=output_png_path,
            full_page=False,
            clip=clip,  # 关键裁剪参数
            type="png",
        )
        await browser.close()


# ai end
def deepseek_api(request):
    global Mind_map
    global Test
    if request.method == 'POST':
        prompt = request.POST.get('message', '')
        pdf_file = request.FILES.get('pdf')  # 支持可选 PDF 上传

        # 读取 PDF 内容（如果有）
        pdf_text = ''
        if pdf_file:
            try:
                with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
                    for page in doc:
                        pdf_text += page.get_text()
            except Exception as e:
                return JsonResponse({'error': f"读取 PDF 失败: {str(e)}"}, status=400)

        # 构造最终 prompt
        if pdf_text:
            if (any(word in prompt for word in ["画", "给", "用",
                                                "建", "拿", "创",
                                                "造", "成", "生",
                                                "总", "结", "表",
                                                "示", "看"]) and
                    any(word in prompt for word in ["思维导图", "思维图", "导图"])):
                Mind_map = True
                full_prompt = (
                    f"以{Mind_map_tem}为模板，总结\n{pdf_text}\n，只填充<body>中类似<h1>和<div class=\"mermaid\">的相关部分，并回复完整html代码(注意：节点和子节点不超过4个)。\n用户的要求是：{prompt}")
            elif((any(word in prompt for word in ["出", "建", "给", "创", "生", "成", "总", "结", "测", "试", "考", "查", "检", "验"]) and
                 any(word in prompt for word in ["题", "试", "卷", "测"])) or any(word in prompt for word in ["小测"])):
                Test = True
                full_prompt = (
                    f"总结\n{pdf_text}\n，以{Test_tem}为模板出题，要求务必回复完整html代码。\n用户的要求是：{prompt}")
            else:
                Mind_map = False
                Test = False
                full_prompt = f"请根据以下 PDF 内容回答问题：\n\n{pdf_text}\n\n用户的问题是：{prompt}"
        else:
            Mind_map = False
            Test = False
            full_prompt = prompt  # 仅文本提问

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

        try:
            response = requests.post(API_ENDPOINT, json=payload, headers=headers)
            if Mind_map or Test:
                response_data = response.json()
                response_text = response_data["choices"][0]["message"]["content"]
                print("response_text:\n", response_text)
                html_match = re.search(r'<!DOCTYPE html>.*?</html>', response_text, re.DOTALL)
                if not html_match:
                    return JsonResponse({'error': '未找到有效的HTML内容'}, status=500)

                html_content = html_match.group()
                file_id = uuid.uuid4().hex
                if Mind_map:
                    html_filename = f"mind_html_{file_id}.html"
                    png_filename = f"mind_png_{file_id}.png"

                    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

                    save_dir_map = os.path.join(current_dir, 'media', 'mind_maps')
                    save_dir_pic = os.path.join(current_dir, 'media', 'mind_pics')
                    os.makedirs(save_dir_map, exist_ok=True)
                    os.makedirs(save_dir_pic, exist_ok=True)
                    html_path = os.path.join(save_dir_map, html_filename)
                    png_path = os.path.join(save_dir_pic, png_filename)
                    print("mind_html_path:", html_path)
                    print('mind_png_url:', png_path)
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    # AI-generated-content
                    # tool: ChatGPT
                    # version: latest
                    # usage：如何调用html_to_png？需要异步吗？为什么？
                    # ai start
                    try:
                        asyncio.run(html_to_png(html_path, png_path))
                    except Exception as e:
                        error_msg = str(e) if str(e) else "Unknown error (empty exception message)"
                        print("Error details:", repr(e), "Args:", e.args)

                        return JsonResponse({
                            'error': f"生成思维导图失败: {error_msg}",
                            'debug': {
                                'html_path': html_path,
                                'png_path': png_path,
                                'dir_exists': os.path.exists(os.path.dirname(png_path)),
                                'exception_type': type(e).__name__,  # 异常类型（如 ValueError）
                                'exception_args': e.args  # 异常参数
                            }
                        }, status=500)
                    png_url = f'{settings.MEDIA_URL}mind_pics/{png_filename}'
                    html_url = f'{settings.MEDIA_URL}mind_maps/{html_filename}'
                    print(f"物理存储路径: {png_path} | 是否存在: {os.path.exists(png_path)}")
                    print(f"浏览器访问 URL: {png_url}")
                    # ai end
                    return JsonResponse({
                        # 'response': f'思维导图已生成：<img src="{png_url}">',
                        'response': f'<a href="{html_url}" target="_blank">查看思维导图</a>',
                        'html_url': html_url,
                        'png_url': png_url
                    })
                elif Test:

                    html_filename = f"test_html_{file_id}.html"

                    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

                    save_dir_test = os.path.join(current_dir, 'media', 'test')
                    os.makedirs(save_dir_test, exist_ok=True)
                    html_path = os.path.join(save_dir_test, html_filename)
                    print("test_html_path:", html_path)
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)

                    html_url = f'{settings.MEDIA_URL}test/{html_filename}'

                    return JsonResponse({
                        # 'response': f'思维导图已生成：<img src="{png_url}">',
                        'response': f'<a href="{html_url}" target="_blank">查看测试题目</a>',
                        'html_url': html_url,
                    })
            else:
                response.raise_for_status()
                return JsonResponse({'response': response.json()["choices"][0]["message"]["content"]})
        except Exception as e:
            return JsonResponse({'error': f"API调用失败: {str(e)}"}, status=500)

    return JsonResponse({'error': '无效的请求方法'}, status=400)
