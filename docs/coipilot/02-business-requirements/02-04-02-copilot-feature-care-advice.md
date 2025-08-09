
# Plant Assistant Feature: Care Advice for GitHub Copilot

## Feature Description
- Gather user inputs: Location (ZIP code for USDA hardiness zone lookup or IP-geolocation fallback via geopy library), environment details (indoor/outdoor radio buttons, light exposure slider: 0-10 hours/day with presets like "Low (shade)", humidity percentage input: 20-80% with meter visualization, temperature range: min/max °F/C toggle), plant type (auto-populated from identification results or searchable dropdown pulling from Chroma embeddings for suggestions), user preferences (checkboxes for organic-only, low-maintenance, pet-safe, eco-friendly, beginner-level explanations).
- Generate comprehensive, personalized care plans covering: watering (e.g., "Every 5-7 days, 8 oz until drainage; use finger test for top 1-inch dryness; adjust +2 days in winter"), light requirements (e.g., "Medium to bright indirect, 4-6 hours; rotate weekly to prevent legginess; supplement with grow lights if <3 hours natural"), soil type (e.g., "Loamy, pH 6.0-7.5 with perlite for drainage; amend with compost annually; test kit recommendations"), humidity and temperature (optimal ranges with tolerance buffers, e.g., "50-70% humidity—use humidifier if <40%; 65-75°F, protect from drafts with relocation tips"), fertilizing (e.g., "Balanced 10-10-10 NPK every 4 weeks in growing season; switch to organic bone meal for prefs; dilute to half-strength"), repotting (e.g., "Every 1-2 years when root-bound; step-by-step: choose 2-inch larger pot, fresh soil mix, water post-repot"), pruning (e.g., "Pinch tips in spring for bushiness; remove dead/diseased with sterilized shears; timing based on growth cycle").
- Use LangGraph workflows to chain AI steps: identify plant base data from Chroma → fetch external context (e.g., weather API for location) → personalize with OpenAI (e.g., adjust for user prefs like "Substitute chemical fert with compost tea for eco").
- Include seasonal adjustments (e.g., "Dormancy in fall: reduce water 50%, no fert") and eco-friendly tips (e.g., "Collect rainwater to minimize tap chemicals; use recycled pots").
- Disclaimers: "Personalized based on inputs; observe plant responses and adjust; not a substitute for professional advice."

## User Stories
- As an apartment dweller in a dry climate, I want location-based advice to adapt tropical plant care for low humidity.
- As an eco-conscious parent, I want organic, pet-safe tips prioritized to ensure family safety.
- As a busy professional, I want printable/exportable plans with calendar integrations for reminders.
- As a visually impaired user, I want voice-readable plans with simple language.

## Acceptance Criteria
- Plans 90%+ personalized (e.g., zone 9 adjusts for heat stress); validated via simulated user tests.
- Response includes verifiable sources (e.g., "Based on RHS and USDA guidelines embedded in DB").
- Supports plan updates: Re-generate on input changes, version history in Postgres.
- Eco-tips in 80%+ responses if preference selected; length <1000 words for readability.

## Backend Handling
- **Endpoint**: POST /api/plants/care in routes/plants.py (async, JWT-secured).
- **Request Schema** (Pydantic): CareRequest(plant_id: Optional[UUID], location: str = Field(..., example="90210"), environment: Dict[str, Any] = Field(..., example={"indoor": True, "light_hours": 5}), preferences: List[str] = []).
- **Response Schema**: CareResponse(plan: Dict[str, str], seasonal_adjustments: Dict[str, List[str]], eco_tips: List[str], sources: List[str], disclaimer: str).
- **Service**: plant_service.py with LangGraph graph: 
  - Node 1: validate_inputs (Pydantic + custom checks, e.g., zone lookup via cached USDA data).
  - Node 2: fetch_base (Chroma query: "care_data for {plant_type}", top_k=3).
  - Node 3: integrate_context (Optional OpenWeather API call for real-time/forecast data).
  - Node 4: personalize (OpenAI gpt-4o prompt: "Adapt {base} for {environment} and {preferences}; structure as JSON").
  - Node 5: store_plan (Postgres upsert to Plant.care_plan JSONB with timestamp/version).
- **Example Flow**: Request → Validation → Chroma semantic search (threshold 0.85) → Context integration → OpenAI call (~$0.015) → Storage → Response.
- **Edge Cases**: Invalid ZIP → Fallback to global defaults with warning; conflicting prefs (e.g., low-water but high-humid plant) → Highlight alternatives; no plant_id → Prompt for identification first.
- **Logging/Monitoring**: Log personalization metrics (e.g., adjustment count); Sentry for API failures; cost tracking for OpenAI/Weather APIs.

## Frontend
- **Component**: CareForm.tsx (Shadcn Form with Inputs, Sliders, Selects, Checkboxes; useForm for validation; integrates geolocation API for auto-fill).
- **Display**: Structured as Shadcn Accordion for expandable sections (e.g., "Watering" header with content); icons via Lucide-react; tooltips for terms; "Export PDF" button using react-pdf.
- **Wireframe Description**: Left sidebar: Input form (grouped fields: Location, Environment, Prefs). Right pane: Live preview updating on change. Bottom: Generate button → Full plan in accordion; footer with disclaimer and "Save to Dashboard".
- **User Flow**: From ID results or dashboard → Pre-fill data → User edits → Submit API → Display with editable fields for iterative regen; mobile: Collapsible form.

## Rationale and Scaling
- **Why**: Prevents 70% plant deaths from improper care; personalization boosts engagement per objectives.
- **Accuracy**: Base on embedded verified sources; feedback loop for refinements.
- **Performance**: Cache plans in Redis; async APIs for weather.
- **Success Metrics**: 70% plans saved; 85%+ satisfaction via NPS.
- **Risks/Mitigations**: Inaccurate due to bad inputs → Validation + disclaimers; costs → Quotas per user.
- **Dependencies**: Geopy/OpenWeather in pyproject.toml; react-pdf in pnpm.
- **Extensions**: Calendar exports (ICS); gamified checklists; smart device links (e.g., auto-waterers).
