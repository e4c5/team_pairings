from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ChatSession, ChatMessage
from .mcp import MCPProcessor
import json


class ChatModelTest(TestCase):
    """Test the chat models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_chat_session_creation(self):
        """Test creating a chat session"""
        session = ChatSession.objects.create(user=self.user)
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.created_at)
        
    def test_chat_message_creation(self):
        """Test creating chat messages"""
        session = ChatSession.objects.create(user=self.user)
        
        # User message
        user_message = ChatMessage.objects.create(
            session=session,
            content="Hello AI!",
            is_user=True
        )
        self.assertEqual(user_message.session, session)
        self.assertTrue(user_message.is_user)
        self.assertEqual(user_message.content, "Hello AI!")
        
        # AI message
        ai_message = ChatMessage.objects.create(
            session=session,
            content="Hello! How can I help you?",
            is_user=False,
            model_used="mock",
            tokens_used=10
        )
        self.assertFalse(ai_message.is_user)
        self.assertEqual(ai_message.model_used, "mock")
        self.assertEqual(ai_message.tokens_used, 10)
    
    def test_session_get_title(self):
        """Test session title generation"""
        session = ChatSession.objects.create(user=self.user)
        
        # No messages - should use default title
        self.assertEqual(session.get_title(), f"Chat Session {session.id}")
        
        # Add a message
        ChatMessage.objects.create(
            session=session,
            content="This is a test message for title generation",
            is_user=True
        )
        session.refresh_from_db()
        title = session.get_title()
        self.assertTrue(title.startswith("This is a test message"))


class MCPProcessorTest(TestCase):
    """Test the MCP processor"""
    
    def test_mock_processor(self):
        """Test the mock processor functionality"""
        processor = MCPProcessor()
        
        # Test with mock provider
        response, metadata = processor.process_message("Hello, AI!")
        
        self.assertIsInstance(response, str)
        self.assertIn("mock", response.lower())
        self.assertIn('tokens_used', metadata)
        self.assertIn('provider', metadata)
        self.assertEqual(metadata['provider'], 'mock')
        
    def test_configuration_validation(self):
        """Test configuration validation"""
        processor = MCPProcessor()
        validation = processor.validate_configuration()
        
        self.assertIn('provider_supported', validation)
        self.assertIn('api_key_configured', validation)
        self.assertIn('model_configured', validation)
        self.assertIn('is_valid', validation)


class ChatAPITest(APITestCase):
    """Test the chat API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_chat_endpoint_post(self):
        """Test the main chat endpoint"""
        url = reverse('ai_chat:chat')
        data = {'message': 'Hello, AI assistant!'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertIn('session_id', response.data)
        self.assertIn('message_id', response.data)
        self.assertIn('metadata', response.data)
        
        # Verify session and messages were created
        session_id = response.data['session_id']
        session = ChatSession.objects.get(id=session_id)
        self.assertEqual(session.user, self.user)
        
        messages = session.messages.all()
        self.assertEqual(messages.count(), 2)  # User message + AI response
        
    def test_chat_endpoint_requires_auth(self):
        """Test that the chat endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        url = reverse('ai_chat:chat')
        data = {'message': 'Hello'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_chat_endpoint_missing_message(self):
        """Test chat endpoint with missing message"""
        url = reverse('ai_chat:chat')
        data = {}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_sessions_list_endpoint(self):
        """Test the sessions list endpoint"""
        # Create a session first
        session = ChatSession.objects.create(user=self.user)
        ChatMessage.objects.create(
            session=session,
            content="Test message",
            is_user=True
        )
        
        url = reverse('ai_chat:sessions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sessions', response.data)
        self.assertEqual(len(response.data['sessions']), 1)
        
        session_data = response.data['sessions'][0]
        self.assertEqual(session_data['id'], session.id)
        self.assertIn('title', session_data)
        self.assertIn('message_count', session_data)
        
    def test_session_detail_endpoint(self):
        """Test the session detail endpoint"""
        session = ChatSession.objects.create(user=self.user)
        ChatMessage.objects.create(
            session=session,
            content="User message",
            is_user=True
        )
        ChatMessage.objects.create(
            session=session,
            content="AI response",
            is_user=False
        )
        
        url = reverse('ai_chat:session_detail', kwargs={'session_id': session.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('session', response.data)
        self.assertIn('messages', response.data)
        self.assertEqual(len(response.data['messages']), 2)
        
    def test_status_endpoint(self):
        """Test the status endpoint"""
        url = reverse('ai_chat:status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('provider', response.data)
        self.assertIn('model', response.data)
        self.assertIn('validation', response.data)
