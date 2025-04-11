from django.shortcuts import render, redirect
from django.shortcuts import reverse
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Annotation
from django.views.decorators.csrf import csrf_exempt
import json


def index(request, group_id):
    return render(request, 'group-learn.html', {'group_id': group_id})

def room(request, group_id):
    print(request.user)
    if not request.user.is_authenticated:
        # return redirect(reverse("chat:login"))
        return redirect(reverse("login"))
    if group_id:
        return render(request, "group-learn.html", {"group_id": group_id})
    else:
        return render(request, "group-learn.html", {"group_id": 0})

@csrf_exempt
def save_annotations(request, group_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        pdf_url = data.get('pdf_url')
        annotations = data.get('annotations')

        if not (pdf_url and annotations):
            return JsonResponse({'error': 'Invalid data'}, status=400)

        # 删除旧记录，确保唯一性
        Annotation.objects.filter(group_id=group_id, pdf_url=pdf_url).delete()

        # 创建新记录
        annotation = Annotation.objects.create(
            group_id=group_id,
            pdf_url=pdf_url,
            data=annotations
        )
        return JsonResponse({'success': True, 'created': True})

@csrf_exempt
def get_annotations(request, group_id):
    if request.method == 'GET':
        pdf_url = request.GET.get('pdf_url')

        if not pdf_url:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        try:
            annotation = Annotation.objects.get(group_id=group_id, pdf_url=pdf_url)
            return JsonResponse({'success': True, 'annotations': annotation.data})
        except Annotation.DoesNotExist:
            return JsonResponse({'success': True, 'annotations': {}})
