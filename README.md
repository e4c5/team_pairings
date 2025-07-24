Zero Configuration Scrabble Pairing app
-

A scrabble pairing app that supports parralel data entry and real time updates of results online. You can start a tournament by simply specifying the number of rounds. That does not mean the tournament is not customizable. You can easily change the pairing system used, number of repeats etc through an easy to use web interface.

## New Features

### AI Chat Assistant
The application now includes an AI-powered chat assistant to help with tournament-related questions. The AI assistant can provide guidance on tournament management, pairing systems, and general tournament administration.

#### Features:
- **Authenticated API**: All chat functionality requires user authentication
- **Session Management**: Chat conversations are organized into sessions per user
- **Multiple LLM Providers**: Supports OpenAI, Anthropic Claude, and mock providers
- **Message History**: Full conversation history is stored and retrievable
- **Configurable**: LLM provider, model, and parameters are configurable via environment variables

#### API Endpoints:
- `POST /api/ai/chat/` - Send a message to the AI assistant
- `GET /api/ai/sessions/` - List user's chat sessions
- `GET /api/ai/sessions/{id}/` - Get session details with message history
- `DELETE /api/ai/sessions/{id}/` - Delete a chat session
- `GET /api/ai/status/` - Check AI system status and configuration

#### Configuration:
Add these environment variables or settings to configure the AI chat:

```python
# AI Chat Configuration
AI_CHAT_PROVIDER = 'openai'  # 'openai', 'anthropic', or 'mock'
AI_CHAT_API_KEY = 'your-api-key-here'
AI_CHAT_MODEL = 'gpt-3.5-turbo'  # or 'claude-3-sonnet-20240229'
AI_CHAT_MAX_TOKENS = 150
AI_CHAT_TEMPERATURE = 0.7
```

For development and testing, you can use the 'mock' provider which doesn't require an API key.

#### Example Usage:
```bash
# Send a chat message
curl -X POST http://localhost:8000/api/ai/chat/ \
  -H "Content-Type: application/json" \
  -u username:password \
  -d '{"message": "How do I set up a Swiss system tournament?"}'

# Get chat sessions
curl -X GET http://localhost:8000/api/ai/sessions/ \
  -u username:password
```

Audience
--
This guide is primarily for those who are familiar with python and django to set up the app on their own servers. A usage guide will be added shortly.

Getting Started
--
Clone the repo, install python requirements described in requirements.txt followed by the javascript requirements from package.json. Int the team_pair folder create a file called settings_local.py which contains your database configuration. This app uses several postgresql specific features and it's unlikely to work against other flavours of SQL.
Then do the usual manage.py migrate to create the table. Lastly before starting the server type `yarn build`. Once you start making your edits to the jsx you will have to use yarn build to make sure that the jsx is automaticaly transpiled each time you make a change.
Finaly you will need to make yourself an account with createsuperuser so that you can login. This app purposely does not include an online signup feature since tournament management should obviously be restricted to designated tournament directors.
