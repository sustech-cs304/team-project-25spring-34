from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.views.decorators.clickjacking import xframe_options_exempt


@xframe_options_exempt
def embed_chat(request):
    return render(request, 'embed.html')


def deepseek_api(request):
    if request.method == 'POST':
        prompt = request.POST.get('message')
        # 这里替换成你的API密钥
        DEEPSEEK_API_KEY = "sk-9979a581a5234ff39af6e5d816693a6e"
        API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        try:
            response = requests.post(API_ENDPOINT, json=payload, headers=headers)
            response.raise_for_status()
            return JsonResponse({'response': response.json()["choices"][0]["message"]["content"]})
        except Exception as e:
            return JsonResponse({'error': f"API调用失败: {str(e)}"}, status=500)

    return JsonResponse({'error': '无效的请求方法'}, status=400)
