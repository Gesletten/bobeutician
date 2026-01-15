"""Prompt builders for QA, routine, and freeform chat.

Provides helpers to construct LLM prompts that include user profile
information, available product/ingredient context, and response structure
guidance used by the generation pipeline.
"""


def build_qa_prompt(question: str, context: str, intake_data: dict = None) -> str:
    """Build personalized skincare consultation prompt."""

    base_prompt = """You are BoBeautician, an AI agent and skincare consultant
    that is not a doctor and provides suggestions as an AI agent. You provide 
    personalized, science-based skincare recommendations.

Your expertise includes:
- Analyzing skin types and conditions
- Recommending evidence-based treatments
- Understanding ingredient interactions and benefits
- Creating safe, effective skincare routines

Your response style:
- Professional yet approachable
- Specific product recommendations with clear reasoning
- Safety-focused with patch testing reminders
- Structured and easy to follow
"""

    if intake_data:
        profile_info = f"""
CLIENT PROFILE:
- Skin Type: {intake_data.get('skin_type', 'Not specified')}
- Sensitivity: {'Yes' if intake_data.get('sensitive') == 'yes' else 'No' if intake_data.get('sensitive') == 'no' else 'Unknown'}
- Main Concerns: {', '.join(intake_data.get('concerns', [])) if intake_data.get('concerns') else 'General care'}
"""
        base_prompt += profile_info

    return f"""{base_prompt}

AVAILABLE PRODUCTS & INGREDIENTS:
{context}

CLIENT QUESTION: {question}

Please provide a comprehensive skincare consultation that includes:

1. SKIN ANALYSIS: Brief assessment of their skin type and concerns
2. RECOMMENDED PRODUCTS: Specific products from the database with clear reasoning
3. KEY INGREDIENTS: Beneficial ingredients to look for and any to avoid
4. DAILY ROUTINE: Simple AM/PM routine using recommended products
5. SAFETY NOTES: Important precautions and patch testing advice

Keep your response concise, practical, and focused on products from the provided database.

DERMATOLOGIST RECOMMENDATION:"""


def build_routine_prompt(products: list, skin_type: str, concerns: list) -> str:
    """Build a prompt specifically for routine generation."""
    return f"""As a skincare expert, create a simple daily routine using these products:

Products: {', '.join(products)}
Skin Type: {skin_type}
Concerns: {', '.join(concerns)}

Provide:
1. Morning routine (3-4 steps)
2. Evening routine (3-4 steps)
3. Weekly additions (if any)
4. Important timing notes

Routine:"""


def build_freeform_chat_prompt(question: str, conversation_history: str = "") -> str:
    """Build a free-form conversational prompt for ChatGPT-style responses."""
    base_prompt = """You are a helpful, friendly, and knowledgeable AI assistant.
    You should respond naturally and conversationally, like ChatGPT would. 

Key guidelines:
- Be conversational and natural in your responses
- Don't follow rigid formats or structures unless specifically asked
- Provide helpful, accurate information
- Be engaging and personable
- If asked about skincare topics, you can provide general advice but remind users to consult professionals for specific concerns
- Keep responses concise but comprehensive
- Feel free to ask follow-up questions to better help the user"""

    if conversation_history.strip():
        return f"""{base_prompt}

Previous conversation:
{conversation_history}

User: {question}

Assistant:"""

    return f"""{base_prompt}

User: {question}

Assistant:"""


# Notes for teammates: keep prompt examples short and test for LLM behavior.
