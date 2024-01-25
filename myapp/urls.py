# myapp/urls.py
from django.urls import path
from . import views
from .views import input_values

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('graph/', views.input_values, name='show_graph'),
    path('dashboard/', views.dashnoard, name='dashboard'),
    path('test/', views.test),
    #path('graph/', views.input_values(), name='show_graph'),
    path('/input_values/', input_values, name='input_values'),
    path('second_formula/', views.second_formula, name="second_formula")

]
