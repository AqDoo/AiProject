from django.urls import path
from .views import analyze_view

urlpatterns = [
    path('analyze/', analyze_view, name='analyze'),  # Убедитесь, что здесь указано имя 'analyze'
]
