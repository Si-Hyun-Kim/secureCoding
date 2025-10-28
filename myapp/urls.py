# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 메인 홈
    path('', views.index, name='index'),

    # DB 데이터 목록
    path('list/', views.student_list, name='student_list'),

    # 보안 취약점 테스트 페이지들
    path('sql-injection/', views.sql_injection, name='sql_injection'),
    path('command-injection/', views.command_injection, name='command_injection'),
    path('directory-traversal/', views.directory_traversal, name='directory_traversal'),
    path('reflected-xss/', views.reflected_xss, name='reflected_xss'),
    path('stored-xss/', views.stored_xss, name='stored_xss'),
    path('dom-xss/', views.dom_xss, name='dom_xss'),
]