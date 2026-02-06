"""
AI Service - LLM Client with Constraint-Aware Prompting

Provides chat completions with user constraints injected into system prompt.
"""

import os
from typing import Optional
from openai import AsyncOpenAI


class AIService:
    """LLM client wrapper with constraint-aware prompting."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    def _format_constraints(self, constraints: list[dict]) -> str:
        """Format constraints for system prompt."""
        if not constraints:
            return "No constraints specified."
        
        sections = {"Goal": [], "Constraint": [], "Preference": [], "Session": []}
        
        for c in constraints:
            c_type = c.get("type", "Constraint")
            label = c.get("label", "")
            desc = c.get("description", "")
            text = f"- {label}" + (f": {desc}" if desc else "")
            if c_type in sections:
                sections[c_type].append(text)
            else:
                sections["Constraint"].append(text)
        
        lines = []
        if sections["Goal"]:
            lines.append("GOALS:")
            lines.extend(sections["Goal"])
        if sections["Constraint"]:
            lines.append("\nCONSTRAINTS (must respect):")
            lines.extend(sections["Constraint"])
        if sections["Preference"]:
            lines.append("\nPREFERENCES (nice to have):")
            lines.extend(sections["Preference"])
        if sections["Session"]:
            lines.append("\nSESSION CONTEXT:")
            lines.extend(sections["Session"])
        
        return "\n".join(lines)
    
    def _build_system_prompt(self, constraints: list[dict]) -> str:
        """Build system prompt with constraints."""
        constraint_text = self._format_constraints(constraints)
        
        return f"""You are an AI career coach helping users find their next role.

The user has established these requirements:

{constraint_text}

INSTRUCTIONS:
1. Acknowledge and respect ALL constraints in your recommendations
2. If suggesting something that might conflict with a constraint, explicitly note it
3. Focus on realistic, actionable career advice
4. Ask clarifying questions to better understand their needs
5. Be conversational but professional

Do NOT suggest opportunities that violate their constraints unless explicitly asked to reconsider them."""
    
    async def chat(
        self,
        message: str,
        constraints: list[dict],
        history: list[dict],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a chat response with constraint awareness.
        
        Args:
            message: User's current message
            constraints: List of constraint dicts with type, label, description
            history: Previous messages in the conversation
            system_prompt: Optional override for system prompt
        
        Returns:
            LLM response content
        """
        # Build system prompt with constraints
        if system_prompt is None:
            system_prompt = self._build_system_prompt(constraints)
        
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history
        for msg in history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call OpenAI
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create AI service singleton."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
