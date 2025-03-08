import os

from django.http import HttpResponse
import subprocess
import tempfile
from django.shortcuts import render
from django.http import JsonResponse


def hello(request):
    return HttpResponse("Hello world ! ")


def index(request):
    # 从本地文件读取代码
    print(os.getcwd())
    try:
        with open('djangoProject/code_test/3.txt', 'r',) as file:
            code = file.read()
            print("code read:", code)
    except FileNotFoundError:
        return render(request, 'index.html', {'code': 'error:File not found'})

    # 渲染主页面，并将代码传递到模板
    return render(request, 'index.html', {'code': code})


def run_code(request):
    if request.method == 'POST':
        # 获取前端传递的代码
        code = request.POST.get('code', '')

        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)

        try:
            # 使用临时文件保存代码并执行
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                temp_file.write(code.encode('utf-8'))
                temp_file_path = temp_file.name

            # 执行代码并捕获输出
            result = subprocess.run(
                ['python', temp_file_path],
                capture_output=True,
                text=True,
                timeout=5  # 设置超时时间为5秒
            )

            # 删除临时文件
            subprocess.run(['rm', temp_file_path], shell=True)

            # 返回执行结果
            return JsonResponse({
                'stdout': result.stdout,  # 标准输出
                'stderr': result.stderr,  # 错误输出
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
