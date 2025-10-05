from django.contrib import admin
from django.urls import path,include
from .views import register_view, login_view, logout_view
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, QuestionViewSet

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns  = [
    path('api/auth/register/', register_view, name='register'),  # Add this
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/', include(router.urls)),  # Include the router URLs
]