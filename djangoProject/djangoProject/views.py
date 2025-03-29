import os
import re
from django.http import HttpResponse
import subprocess
import tempfile
from django.shortcuts import render
from django.http import JsonResponse

file_path = 'djangoProject/code_test/8_java.txt'

def determine_file_type(file_path):
    """
    根据文件路径确定文件类型。
    如果文件名的 '.txt' 前面是 'java'，则返回 'java'，否则返回 'python'。

    :param file_path: 文件的完整路径
    :return: 文件类型 ('java' 或 'python')
    """
    # 获取文件名（不包括路径）
    filename = os.path.basename(file_path)

    # 检查是否以 '.txt' 结尾
    if filename.endswith('.txt'):
        # 分割文件名和扩展名
        name_without_ext, ext = os.path.splitext(filename)

        # 检查 '.txt' 前面的部分是否为 'java'
        if name_without_ext.endswith('java'):
            return 'java'

    # 默认返回 'python'
    return 'python'

def extract_class_name(java_code):
    """
    从Java代码中提取公共类名
    """
    match = re.search(r'public\s+class\s+([A-Za-z_$][A-Za-z\d_$]*)', java_code)
    if match:
        return match.group(1)
    return None

def lesson(request):
    return render(request, 'lesson.html')


def hello(request):
    return HttpResponse("Hello world ! ")


def index(request):
    # 从本地文件读取代码
    print(os.getcwd())
    try:
        with open(file_path, 'r', ) as file:
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

        file_type = determine_file_type(file_path)
        print("code type:",file_type)

        #run之前保存代码
        with open(file_path, 'w') as f:
            f.write(code)

        if file_type == 'java':
            class_name = extract_class_name(code)
            print("class name:", class_name)
            temp_path = os.path.join('djangoProject','code_test', class_name+".java")

            with open(temp_path, 'w') as f:
                f.write(code)
            #TODO:
            # 编译 Java 代码
            compile_result = subprocess.run(
                ['javac', temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            # 处理编译错误
            if compile_result.returncode != 0:
                return JsonResponse({
                    'error': 'Java compilation failed',
                    'stderr': compile_result.stderr
                }, status=400)

            # 执行 Java 程序
            run_result = subprocess.run(
                ['java', '-cp', os.path.dirname(temp_path),class_name],
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
                # 执行代码并捕获输出
                result = subprocess.run(
                    ['python', file_path],
                    capture_output=True,
                    text=True,
                    timeout=5  # 设置超时时间为5秒
                )

                # 返回执行结果
                return JsonResponse({
                    'stdout': result.stdout,  # 标准输出
                    'stderr': result.stderr,  # 错误输出
                })

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
