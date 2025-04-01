from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def embed_chat(request):
    return render(request, 'embed.html')


import fitz  # PyMuPDF

def deepseek_api(request):
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
            full_prompt = f"请根据以下 PDF 内容回答问题：\n\n{pdf_text}\n\n用户的问题是：{prompt}"
        else:
            full_prompt = prompt  # 仅文本提问

        # 调用 DeepSeek
        DEEPSEEK_API_KEY = "sk-2a4a810355a64ca3966364f2c8faba72"
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
            response.raise_for_status()
            return JsonResponse({'response': response.json()["choices"][0]["message"]["content"]})
        except Exception as e:
            return JsonResponse({'error': f"API调用失败: {str(e)}"}, status=500)

    return JsonResponse({'error': '无效的请求方法'}, status=400)
