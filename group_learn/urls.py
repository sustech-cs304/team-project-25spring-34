from django.urls import path
from . import views

app_name = 'group_learn'

urlpatterns = [
    path("", views.index, name="index"),
    path("save_annotations/", views.save_annotations, name="save_annotations"),
    path("get_annotations/", views.get_annotations, name="get_annotations"),
    path("get_pdf/", views.get_pdf, name="get_pdf"),
    path("get_room_pdfs/", views.get_room_pdfs, name="get_room_pdfs"),
    path('get_current_pdf/', views.get_current_pdf, name='get_current_pdf'),
    path('set_current_pdf/', views.set_current_pdf, name='set_current_pdf'),
    path('serve_pdf/<str:pdf_id>/', views.serve_pdf, name='serve_pdf'),
]
