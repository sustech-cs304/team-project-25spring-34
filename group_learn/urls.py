from django.urls import path
from . import views
from button_lock import views as button_lock_views

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
    path('revise_button/', button_lock_views.revise_button, name='revise_button'),
    path('save_button/', button_lock_views.save_button, name='save_button'),
    path('get_button_state/', button_lock_views.get_button_state, name='get_button_state'),
]
