# BoBeutician Complete Guide

## Overview

Complete SQL-backed retrieval pipeline integration from intake form to AI-powered skincare recommendations using **free OpenRouter models**. The system is fully stateless - all data clears when the tab is closed.

## Architecture

```

Frontend (Next.js)     Backend (FastAPI)           Free LLM (OpenRouter)
├── Intake Form        ├── SQL Database             ├── meta-llama/llama-3.3-70b:free
├── Chat Interface  ←→ ├── SQL Retrieval       →  └── (fallback models available)
├── Stateless Storage  ├── Context Composition
└── Session Management └── Personalized Response


```

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Start Dev Container
Click in the bottom left corner the two greater and less than signs and clikc "reopen in dev container"""

# Get free API key from https://openrouter.ai/
echo "OPENROUTER_API_KEY=your_free_api_key_here" >> .env

# Seed the database with cosmetic products
python scripts/seed_db.py

# Start the backend server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# You can view the frontend link in the ports section and it should be the 3000 port
```

# Test the Integration

```bash
# Test frontend
cd frontend && npm test -- frontend/tests

# Backend: create venv (first time)
cd backend
python3 -m venv .venv

# Install packages using the venv's python (no need to activate the shell)
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pip install pytest-asyncio

# Run backend tests from the repo root (recommended) so imports in tests
# that rely on the repository layout resolve consistently. From repo root:
./backend/.venv/bin/python -m pytest backend/tests -q -r s

# Or, from inside the backend/ directory you can run:
./.venv/bin/python -m pytest tests -q -r s

# Access the API docs
open http://localhost:8000/docs
```

## Notes about running backend tests

```
- Some backend tests run in-process using FastAPI's `TestClient` and do NOT
   require a running `uvicorn` server (these are the health/intake in-process
   tests). Running `pytest` will execute those directly.

- For tests that contact the live server or call external models, start the
   backend in a separate terminal with:

   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Recommended commands to run tests (no activation required):

  ```bash
  # Run all backend tests using the venv python
  ./backend/.venv/bin/python -m pytest backend/tests -q -r s

  # Run a single test file (fast)
  ./backend/.venv/bin/python -m pytest backend/tests/test_integration.py -q -r s -s

  # Run only the API endpoints test
  ./backend/.venv/bin/python -m pytest backend/tests/test_api_endpoints.py -q -r s -s
  ```

## Running Pylint

```bash
   # Run pylint using the project's backend virtualenv (from repo root)
   # Ensure the venv exists: see "Test the Integration" for venv setup steps.
   ./backend/.venv/bin/pylint backend/app backend/scripts backend/tests

```

## Running ESLINT

```bash
   # From the repo root run eslint in the frontend folder. Uses npx so no global
   # install is required (Node and npm must be available).
   cd frontend && npx eslint . --ext .ts,.tsx,.js,.jsx
```

If you prefer activating the venv first, use `cd backend && source .venv/bin/activate` then run `pytest tests -q -r s`.

## Key Components

### Backend Components

1. **SQL Retrieval** (`app/core/hybrid_retrieve.py`)

   - Intake form priority extraction
   - Multi-query SQL approach (skin type, concerns, ingredients)
   - Product rating filtering (3.5+ stars)
   - Intelligent category mapping
2. **Smart Context Composition** (`app/core/compose.py`)

   - User profile integration
   - Perfect match highlighting
   - Routine suggestion generation
   - Confidence scoring
3. **Free LLM Integration** (`app/core/generate.py`)

   - Multiple free model fallbacks
   - Optimized prompts for free models
   - Robust error handling
   - 800 token limit optimization
4. **Chat API Endpoints** (`app/api/endpoints/chat.py`)

   - `/api/chat/ask` - Main chat endpoint
   - `/api/chat/intake` - Intake form processing
   - `/api/chat/health` - Health check

### Frontend Components

1. **Enhanced API Integration** (`lib/api.ts`)

   - Chat API functions
   - Intake form submission
   - Proper error handling
   - TypeScript types
2. **Stateless Storage** (`lib/storage.ts`)

   - SessionStorage-based (clears on tab close)
   - Chat session management
   - Intake form persistence
   - Profile summary generation
3. **Smart Chat Hook** (`hooks/useChat.ts`)

   - Real-time message handling
   - Intake data integration
   - Loading and error states
   - Session management

## Free Models Configuration

The system automatically uses free OpenRouter models with fallbacks:

```python
free_models = [
    "meta-llama/llama-3.3-70b-instruct:free",
]
```

## Complete User Flow

1. **User visits site** → Frontend loads
2. **Completes intake form** → Data saved to sessionStorage
3. **Asks skincare question** → Chat hook processes
4. **Backend receives request** → SQL retrieval pipeline executes:
   - Extracts user attributes (skin type, concerns)
   - Queries SQL database for relevant products
   - Retrieves beneficial ingredients
   - Composes personalized context
   - Calls free LLM with optimized prompt
5. **AI responds** → Personalized recommendation returned
6. **Frontend updates** → Chat UI shows response with confidence
7. **User closes tab** → All data automatically cleared

## Frontend Integration

### Using the Chat Hook

```typescript
import useChat from '../hooks/useChat'

function ChatComponent() {
  const {
    messages,
    loading,
    error,
    hasIntakeData,
    sendMessage,
    clearChat,
    getUserProfile
  } = useChat()

  const handleSend = async (question: string) => {
    await sendMessage(question)
  }

  // Rest of component...
}
```

### Using Stateless Storage

```typescript
import { skincareStorage } from '../lib/storage'

// Save intake form
skincareStorage.saveIntakeForm({
  skin_type: 'oily',
  sensitive: 'no',
  concerns: ['acne']
})

// Get user profile
const profile = skincareStorage.getUserProfileSummary()
// Returns: "Oily skin | non-sensitive | concerns: acne"

// Clear everything (new session)
skincareStorage.clearAll()
```

## Key Features

**Cost-Free**: Uses only free OpenRouter models
**Stateless**: All data clears on tab close
**Personalized**: Intake form drives recommendations
**Intelligent**: Multi-query SQL retrieval
**Resilient**: Fallback models and error handling
**Fast**: Optimized for free model constraints
**Complete**: Full integration from form to AI response

## Privacy & Data

- **No persistent storage**: Data only in sessionStorage
- **No user tracking**: Each session is independent
- **No data retention**: Everything clears on tab close
- **Local processing**: Intake forms processed client-side
- **Secure API**: Backend validates all inputs

## Performance Optimization

- **SQL Query Optimization**: Rating filters, proper indexing
- **Context Budget Management**: 500 token context limit
- **Model Fallbacks**: Automatic retry with different models
- **Error Recovery**: Graceful degradation to manual responses
- **Caching**: Session-based storage for performance

## Customization

### Add New Skin Concerns

1. Update concern mappings in `hybrid_retrieve.py`:

```python
concern_mappings = {
    "acne": ["Cleanser", "Treatment"],
    "your_new_concern": ["Your", "Categories"]
}
```

2. Add to frontend types in `models.ts`:

```typescript
export type SkinConcern = 
  | 'acne'
  | 'your_new_concern'
```

### Switch to Paid Models

Simply update the model

```bash
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

### Success!

You now have a complete, cost-free, stateless skincare consultation system that:

- Processes intake forms intelligently
- Queries your product database
- Generates personalized recommendations
- Uses free AI models
- Clears data on tab close
- Provides professional skincare advice
