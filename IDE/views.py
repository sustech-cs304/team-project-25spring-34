from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from IDE.models import Course
from django.contrib.auth.models import User
import json

@csrf_exempt
def index(request):
    context = {
        'username': request.user.username if request.user.is_authenticated else ''
    }
    return render(request, 'IDE.html', context)

@csrf_exempt
def course_view(request, data_course):
    return render(request, 'lesson.html', {
        'data_course': data_course
    })

@csrf_exempt
@login_required
def get_courses(request):
    courses = Course.objects.all()
    data = [{'name': course.name, 'slug': course.slug} for course in courses]
    return JsonResponse({'courses': data})

@csrf_exempt
@login_required
def add_course(request):
    # if not request.user.is_superuser:
    #     return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            if not name:
                return JsonResponse({'error': 'Course name is required'}, status=400)

            slug = name.lower().replace(' ', '-')
            if Course.objects.filter(slug=slug).exists():
                return JsonResponse({'error': 'Course already exists'}, status=400)

            course = Course.objects.create(
                name=name,
                slug=slug,
                creator=request.user
            )
            return JsonResponse({'status': 'ok', 'name': course.name, 'slug': course.slug})
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required
def delete_course(request):
    # Only allow admin user to delete courses
    if request.user.username != 'admin':
        return JsonResponse({'error': 'Permission denied. Only admin can delete courses.'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            slug = data.get('slug', '').strip()
            if not slug:
                return JsonResponse({'error': 'Course slug is required'}, status=400)

            try:
                course = Course.objects.get(slug=slug)
                course.delete()
                return JsonResponse({'status': 'ok', 'message': 'Course deleted successfully'})
            except Course.DoesNotExist:
                return JsonResponse({'error': 'Course not found'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
