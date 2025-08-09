# Plant Assistant Feature: Diagnosis & Troubleshooting for GitHub Copilot

## Feature Description
- Users input symptoms via text (max 1000 characters, e.g., "Leaves curling inward, sticky residue on undersides, slow growth") or upload photos (up to 4, max 8MB total, focused on affected areas like close-ups of spots or pests).
- Use OpenAI to analyze and identify issues: Categorize problems (e.g., pest infestation like aphids, disease such as root rot, environmental stress from cold, nutrient deficiency like iron chlorosis) with root causes (e.g., overwatering leading to fungal growth), severity levels (mild/moderate/severe based on extent), probability estimates (e.g., 75% pest, 25% virus), and differential diagnoses (e.g., "Rule out scale insects vs. mealybugs").
- Suggest remedies in prioritized order: Organic first (e.g., "Mix 1 tsp neem oil with water, spray weekly for 3 weeks; introduce beneficial insects like ladybugs"), chemical alternatives if needed (e.g., "If persistent, use insecticidal soap—dilute per label"), step-by-step instructions (e.g., "1. Isolate plant. 2. Prune affected parts. 3. Apply treatment. 4. Monitor daily"), and timelines (e.g., "Improvement expected in 5-7 days").
- Leverage Chroma for similar case searches: Embed symptoms/descriptions and query anonymized historical data (user-submitted cases, pre-seeded with 5k+ entries from sources like extension services); return insights (e.g., "In 70% similar cases, improved with better drainage—see anonymized examples").
- Include prevention steps (e.g., "Sterilize tools between uses; quarantine new plants for 2 weeks") and eco-tips (e.g., "Use companion planting with marigolds to deter pests naturally").
- Disclaimers: "AI-generated diagnosis; not a replacement for lab testing or professional consultation, especially for pet/child safety or widespread issues."

## User Stories
- As a frustrated user with a wilting plant, I want photo-based diagnosis to get immediate organic remedies.
- As a community gardener, I want historical case matches to learn from others' experiences anonymously.
- As a beginner, I want simple explanations and visual guides in remedies to avoid mistakes.
- As an international user, I want metric/imperial unit toggles in instructions.

## Acceptance Criteria
- Diagnosis accuracy >87% on test sets (e.g., 200 symptom-photo pairs); severity correctly assessed in 80%+ cases.
- Remedies include at least 3 steps, prioritized organic; prevention in every response.
- Similar cases returned only if relevance >0.7; anonymized fully.
- Response <800 words; includes confidence and when to seek pro help.

## Backend Handling
- **Endpoint**: POST /api/plants/diagnose in routes/plants.py (async, authenticated).
- **Request Schema**: DiagnoseRequest(symptoms: Optional[str], images: List[str] = [], plant_id: Optional[UUID]).
- **Response Schema**: DiagnoseResponse(issues: List[Dict[str, Any]], remedies: List[Dict[str, List[str>]], prevention: List[str], similar_cases: int, severity: int, disclaimer: str).
- **Service**: plant_service.py LangGraph chain: 
  - Node 1: parse_inputs (OpenAI structured extraction for symptoms).
  - Node 2: vision_analysis (if images: OpenAI prompt for feature detection like "Describe lesions, colors, patterns").
  - Node 3: embed_and_query (Chroma 'diagnosis_cases': upsert anonymized, query top_k=10).
  - Node 4: synthesize (OpenAI: "Diagnose {data}; suggest remedies prioritizing organic; include prevention").
- **Example Flow**: Inputs → Parse/embed → Chroma (filters for plant_type if known) → OpenAI (~$0.02) → Response.
- **Edge Cases**: Vague symptoms → Prompt for more via response; no images → Text-only mode; high severity → Urgent disclaimer.
- **Logging/Monitoring**: Track diagnosis types for trends; Sentry alerts on low confidence.

## Frontend
- **Component**: DiagnosisForm.tsx (Shadcn Textarea for symptoms, Dropzone for photos; Zod validation).
- **Display**: Shadcn Alert for summary (color-coded by severity: green mild, red severe); Tabs for "Issues", "Remedies" (numbered lists), "Prevention"; similarity badge.
- **Wireframe Description**: Top: Symptom input + upload. Middle: Submit. Results: Alert banner, tabs with structured content (e.g., remedies as ordered list with checkboxes).
- **User Flow**: From chat/dashboard → Form submit → API → Render with "Log to Tracking" button.

## Rationale and Scaling
- **Why**: Addresses 30% troubleshooting queries; early fixes improve satisfaction.
- **Accuracy**: Feedback-labeled data for Chroma; expert-seeded cases.
- **Performance**: Limit queries to recent cases; async vision.
- **Success Metrics**: 75% issues resolved per user logs; 90% feedback positive.
- **Risks/Mitigations**: Wrong diagnosis → Disclaimers + pros referral; privacy → Hash cases.
- **Dependencies**: Zod in frontend; Chroma collection in vector_db.py.
- **Extensions**: Video for pest movement; affiliate remedy purchases.