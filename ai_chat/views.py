from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .mcp import MCPProcessor
import logging

logger = logging.getLogger(__name__)


class ChatAPIView(APIView):
    """
    Main API endpoint for AI chat functionality.
    Handles POST requests with user messages and returns AI responses.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Process a chat message and return AI response.
        
        Expected payload:
        {
            "message": "User's message text",
            "session_id": "optional existing session ID"
        }
        
        Returns:
        {
            "response": "AI response text",
            "session_id": "session ID for this conversation",
            "message_id": "ID of the AI response message",
            "metadata": {
                "model_used": "gpt-3.5-turbo",
                "tokens_used": 150,
                "response_time": 1.23
            }
        }
        """
        try:
            message_text = request.data.get('message')
            session_id = request.data.get('session_id')
            
            if not message_text:
                return Response(
                    {"error": "Message text is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create chat session
            if session_id:
                try:
                    session = ChatSession.objects.get(
                        id=session_id, 
                        user=request.user,
                        is_active=True
                    )
                except ChatSession.DoesNotExist:
                    return Response(
                        {"error": "Invalid session ID"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                session = ChatSession.objects.create(user=request.user)
            
            # Save user message
            user_message = ChatMessage.objects.create(
                session=session,
                content=message_text,
                is_user=True
            )
            
            # Get chat history for context
            recent_messages = session.messages.order_by('created_at')[:20]
            chat_history = [
                {
                    'content': msg.content,
                    'is_user': msg.is_user
                }
                for msg in recent_messages
            ]
            
            # Process with MCP
            processor = MCPProcessor()
            ai_response, metadata = processor.process_message(message_text, chat_history[:-1])  # Exclude current message
            
            # Save AI response
            ai_message = ChatMessage.objects.create(
                session=session,
                content=ai_response,
                is_user=False,
                model_used=metadata.get('model_used'),
                tokens_used=metadata.get('tokens_used'),
                response_time=metadata.get('response_time')
            )
            
            # Update session timestamp
            session.save()  # This will update the updated_at field
            
            return Response({
                "response": ai_response,
                "session_id": session.id,
                "message_id": ai_message.id,
                "metadata": metadata
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ChatAPIView: {str(e)}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatSessionListView(APIView):
    """
    API endpoint to list user's chat sessions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Get list of user's chat sessions.
        
        Returns:
        {
            "sessions": [
                {
                    "id": 1,
                    "title": "Session title or preview",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                    "message_count": 10
                }
            ]
        }
        """
        sessions = ChatSession.objects.filter(
            user=request.user,
            is_active=True
        ).prefetch_related('messages')
        
        session_data = []
        for session in sessions:
            session_data.append({
                "id": session.id,
                "title": session.get_title(),
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": session.messages.count()
            })
        
        return Response({"sessions": session_data}, status=status.HTTP_200_OK)


class ChatSessionDetailView(APIView):
    """
    API endpoint to get details of a specific chat session.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        """
        Get chat session with all messages.
        
        Returns:
        {
            "session": {
                "id": 1,
                "title": "Session title",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            },
            "messages": [
                {
                    "id": 1,
                    "content": "Message text",
                    "is_user": true,
                    "created_at": "2023-01-01T00:00:00Z",
                    "model_used": null,
                    "tokens_used": null
                }
            ]
        }
        """
        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user,
            is_active=True
        )
        
        messages = session.messages.all()
        message_data = []
        for message in messages:
            message_data.append({
                "id": message.id,
                "content": message.content,
                "is_user": message.is_user,
                "created_at": message.created_at,
                "model_used": message.model_used,
                "tokens_used": message.tokens_used,
                "response_time": message.response_time
            })
        
        return Response({
            "session": {
                "id": session.id,
                "title": session.get_title(),
                "created_at": session.created_at,
                "updated_at": session.updated_at
            },
            "messages": message_data
        }, status=status.HTTP_200_OK)

    def delete(self, request, session_id):
        """
        Delete (deactivate) a chat session.
        """
        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user,
            is_active=True
        )
        
        session.is_active = False
        session.save()
        
        return Response(
            {"message": "Session deleted successfully"}, 
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chat_status_view(request):
    """
    Get the status of the AI chat system.
    
    Returns configuration validation and system health.
    """
    processor = MCPProcessor()
    validation = processor.validate_configuration()
    
    return Response({
        "status": "active" if validation['is_valid'] else "configuration_error",
        "provider": processor.provider,
        "model": processor.model,
        "validation": validation
    }, status=status.HTTP_200_OK)
