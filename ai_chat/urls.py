from django.urls import path
from . import views

app_name = 'ai_chat'

urlpatterns = [
    # Main chat API endpoint
    path('chat/', views.ChatAPIView.as_view(), name='chat'),
    
    # Session management endpoints
    path('sessions/', views.ChatSessionListView.as_view(), name='sessions'),
    path('sessions/<int:session_id>/', views.ChatSessionDetailView.as_view(), name='session_detail'),
    
    # System status endpoint
    path('status/', views.chat_status_view, name='status'),
]