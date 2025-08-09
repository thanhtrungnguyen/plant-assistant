
# Plant Assistant Feature: Conversational Interface for GitHub Copilot

## Feature Description
- Chatbot for natural queries (e.g., "My fern is drooping—what's wrong?"), multi-turn (retain context 15 messages, e.g., follow-ups like "More details on soil?").
- Powered by OpenAI (gpt-4o) orchestrated via LangGraph for routing (e.g., detect intent: ID, advice, diagnose) and integrations (e.g., photo uploads mid-chat trigger vision).
- Personalize with Postgres history (e.g., "For your previously identified Fern... suggest based on logs").
- Support commands (e.g., "/identify [desc]", "/remind water tomorrow"); emojis/reactions for engagement; photo handling via Shadcn.
- Disclaimers: Per-response for AI limits; session timeouts after 30min inactivity.

## User Stories
- As a casual user, I want chat for quick questions without navigating menus.
- As a detailed user, I want multi-turn personalization using my plant history.
- As a visual learner, I want photo uploads in-chat for seamless diagnosis.
- As a non-English speaker, I want auto-translation (post-MVP).

## Acceptance Criteria
- Intent accuracy 96%; handles 10+ turns without loss.
- Photo integration: Upload → Process → Inline response.
- Rate limits: 60 msgs/hour free; queues for OpenAI.
- Conversations storable/searchable.

## Backend Handling
- **Endpoint**: WS /api/chat in routes/plants.py (WebSocket for streaming; polling fallback).
- **Request Schema**: ChatMessage(text: str, images: Optional[List[str]], session_id: UUID).
- **Response Schema**: ChatResponse(messages: List[Dict], suggestions: List[str], actions: Optional[Dict]).
- **Service**: plant_agent.py LangGraph graph (stateful: Redis sessions): nodes for intent_parse (OpenAI classify), route (to features like diagnose), generate_response (prompt with context), update_state.
- **Example Flow**: Msg → Parse → Route/chain → Stream (~$0.005/msg) → Response.
- **Edge Cases**: Long sessions → Summarize; interruptions → Resume via session_id.
- **Logging/Monitoring**: Conversation logs anonymized; usage metrics.

## Frontend
- **Component**: ChatInterface.tsx (Shadcn Chat bubbles, Input bar, Upload button; useWebSocket for real-time).
- **Display**: Bubbles (user/AI with avatars), typing indicator, image previews inline.
- **Wireframe Description**: Header: Back button, title. Body: Scrollable messages (markdown support). Footer: Input + send/upload/voice (post-MVP).
- **User Flow**: Open chat → Type/upload → Responses with quick-reply buttons (e.g., "Yes, more info").

## Rationale and Scaling
- **Why**: 40% users prefer chat; enhances interactivity.
- **Accuracy**: Tune on sample convos; fallback intents.
- **Performance**: Redis for state; limit concurrent sessions.
- **Success Metrics**: Avg 5 turns/session; 80% completion rate.
- **Risks/Mitigations**: Hallucinations → Guardrails; abuse → Filters.
- **Dependencies**: WebSocket in FastAPI; markdown-it in frontend.
- **Extensions**: Voice via Web Speech; multi-lang; bot personas.