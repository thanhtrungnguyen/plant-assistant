# Plant Assistant Feature: Plant Identification for GitHub Copilot

## Feature Description
- Users can upload 1-5 photos (supported formats: JPEG, PNG, HEIC, WEBP; max total size 10MB, enforced via server-side validation to prevent abuse) or provide detailed text descriptions (max 750 characters, e.g., "Broad-leafed shrub with purple flowers, thorny stems, in temperate climate").
- Leverage OpenAI Vision API (model: gpt-4o or latest equivalent) to perform in-depth image analysis, extracting attributes such as leaf morphology (shape, margin, venation), flower structure (petal count, color, symmetry), stem/bark characteristics, root visibility if applicable, and contextual elements (e.g., soil type, pot material, background foliage for habitat inference).
- Identification outputs include: common name (e.g., "Lavender"), scientific name (e.g., "Lavandula angustifolia"), taxonomic classification (family: Lamiaceae, genus: Lavandula), native origin/range (e.g., "Mediterranean region, zones 5-9"), key traits (e.g., drought-tolerant, fragrant oils used in aromatherapy, bee-attractor, potential toxicity to cats per ASPCA database, air-purifying efficiency rated high by NASA clean air study), growth habits (e.g., perennial, height 1-2 ft, spread 1-3 ft), and a confidence score (0-100%, broken down by factors: visual match 92%, trait correlation 88%).
- Integrate Pinecone vector DB for advanced semantic search: Generate embeddings from OpenAI (1536 dimensions) based on the analysis results and query a pre-seeded collection ('plant_embeddings', initialized with 25k+ entries from reliable sources like USDA PLANTS database, Royal Horticultural Society, and Wikipedia extracts). If primary confidence <85%, suggest 3-7 alternatives with similarity scores (e.g., cosine similarity >0.8) and key differentiators (e.g., "Similar to Rosemary but leaves narrower and flowers blue").
- Enhance user engagement with: fun facts (e.g., "Lavender was used by ancient Romans for bathing and is derived from 'lavare' meaning 'to wash'"), basic introductory info (e.g., "Evergreen shrub ideal for borders or containers; blooms summer"), and interactive prompts (e.g., "Want care tips for this plant? Or add to your tracking dashboard?").
- Include mandatory disclaimers: "This identification is AI-generated and may not be 100% accurate, especially for hybrids or rare variants; always cross-verify with a botanist or extension service for edible, medicinal, or invasive species concerns."

## User Stories
- As a novice plant owner, I want to upload a smartphone photo of a mystery houseplant so I can quickly learn its name and if it's safe for my pets.
- As an experienced horticulturist, I want text-based identification for describing field observations without photos, including suggestions for similar species to refine my knowledge.
- As a mobile user, I want seamless camera integration to capture live images directly in the app for instant identification.
- As a user with accessibility needs, I want voice-to-text support for descriptions to make the feature inclusive.

## Acceptance Criteria
- API response time <1.8s for 95% of requests (measured via New Relic or similar monitoring).
- Identification accuracy >93% on a diverse validation dataset (e.g., 300 images/texts covering common, exotic, damaged, and seasonal variations).
- Handles multi-photo inputs by aggregating results (e.g., weighted average confidence based on image quality).
- Alternatives provided only when necessary, with clear explanations; user feedback option (e.g., "Correct?" thumbs up/down) logs to Postgres for model improvement.
- Disclaimers rendered prominently in UI; errors (e.g., invalid file) return user-friendly messages with retry suggestions.
- Supports edge inputs like partial plants (e.g., single leaf) with reduced confidence and prompts for more details.

## Backend Handling
- **Endpoint**: POST /api/plants/identify in routes/plants.py (FastAPI router, async-enabled, protected by JWT authentication middleware for user-specific history).
- **Request Schema** (Pydantic model): IdentifyRequest(images: List[str] = Field(default=[], max_items=5, description="Base64-encoded images"), description: Optional[str] = None, user_metadata: Optional[Dict[str, Any]] = None  # e.g., {'location': 'Seattle'} for context).
- **Response Schema** (Pydantic): IdentifyResponse(plant_details: Dict[str, Any], confidence: float, alternatives: List[Dict[str, Any]], fun_facts: List[str], basic_info: str, disclaimer: str).
- **Service**: plant_service.py orchestrates a LangGraph workflow graph (stateful with session persistence in Redis for multi-step interactions):
  - Node 1: preprocess_images (async using Pillow: resize to max 1024x1024, auto-rotate via EXIF, enhance sharpness/contrast if low quality detected via OpenCV metrics).
  - Node 2: vision_analysis (OpenAI client.chat.completions.create with vision-enabled prompt: "Extract detailed plant features and identify in structured JSON format: {output_schema}", including temperature=0.2 for consistency).
  - Node 3: generate_embeddings (openai.embeddings.create on concatenated analysis text, batch if multiple).
  - Node 4: Pinecone_operations (collection.get_or_create('plant_embeddings'); upsert new embedding if novel with metadata {'source': 'user_upload', 'timestamp': now()}; query with top_k=7, include_metadata=True, min_distance=0.2, filters for user-specific if authenticated).
  - Node 5: refine_and_enrich (secondary OpenAI call: "Refine identification with alternatives; add fun facts and disclaimers", structured output via JSON mode).
- **Example Flow**: Incoming request → Pydantic validation → Preprocess (parallel async for images) → OpenAI vision call (cost ~$0.025 per image) → Embedding generation → Pinecone upsert/query (latency target <150ms) → Refinement → Optional Postgres save (link to user_id if authenticated, with plant_id UUID) → JSON response.
- **Edge Cases**: Blurry/overexposed images → Detect via image metrics (e.g., variance of Laplacian for blur) and respond with "Photo unclear—try better lighting?"; empty inputs → 400 Bad Request with guidance; rate limiting (e.g., 12 requests/min per user via FastAPI middleware); OpenAI errors → Fallback to basic Pinecone search using description embedding; large files → Compress on-the-fly.
- **Logging/Monitoring**: Use structlog for detailed logs (e.g., confidence levels, query times); integrate Sentry for exceptions; track metrics like API call costs and accuracy via Prometheus/Grafana dashboards.

## Frontend
- **Component**: UploadPhoto.tsx (built with Shadcn UI Dropzone for intuitive drag-and-drop/multi-file uploads; includes file validation hooks, preview thumbnails with zoom, and error toasts via Shadcn Toast component; supports direct camera access using navigator.mediaDevices.getUserMedia for mobile devices; integrates with react-hook-form for description input).
- **Display**: Results presented in a Shadcn Card component with responsive Tabs (e.g., "Primary ID" tab for main details, "Traits & Facts" for bullets/lists, "Alternatives" for carousel of cards); use Next.js Image for optimized loading/previews; include interactive elements like Tooltips for trait explanations and Buttons for actions (e.g., "Add to My Plants" linking to tracking endpoint).
- **Wireframe Description** (Text-based):
  - Header: Feature title "Identify Your Plant" with close modal button and help icon (popover with tips).
  - Body Section 1: Dropzone area (dashed border, upload icon, text "Drag photos or click to browse; or describe below"; supports paste from clipboard).
  - Body Section 2: Textarea for description input (Shadcn Textarea with character counter, autosuggest for common terms).
  - Footer: Submit button (Shadcn Button, variant primary) and cancel.
  - Post-Submission: Shadcn Skeleton loader during processing → Results Card: Top row image carousel (if multi-photos, with navigation arrows), middle grid (left: plant name/image, right: details table with columns for Trait/Value, expandable rows), bottom horizontal scroll for alternative cards (each with mini-image, name, similarity %, diff bullets).
- **User Flow**: From dashboard or chat interface → Open modal/dialog → User inputs (upload/describe) → On submit, fetch API with progress indicator (Shadcn Progress) → Parse response and render animated reveal (using framer-motion for transitions); handle errors with retry button. Accessibility: ARIA labels for all interactive elements, keyboard navigation support, high-contrast modes via Tailwind, screen reader compatibility tested with VoiceOver.

## Rationale and Scaling
- **Why**: Serves as the primary onboarding feature, addressing 50% of user queries in comparable apps (e.g., based on PlantSnap and PictureThis analytics); empowers users to start their plant journey confidently, aligning with business goals for user acquisition.
- **Accuracy**: Target 93%+ through hybrid AI-DB approach; implement continuous improvement via user feedback endpoint (/api/feedback/identify) that labels data for periodic Pinecone retraining or OpenAI fine-tuning (post-MVP); benchmark against internal datasets quarterly.
- **Performance**: Optimize with async parallelism for image processing; cache frequent identifications (e.g., top-200 common plants) in Redis with TTL 7 days; monitor OpenAI costs (aim < $0.03 per request average) via budget alerts.
- **Success Metrics**: 75%+ conversion rate from ID to other features (e.g., care advice); user-reported accuracy >90% via in-app surveys; track via Mixpanel events like "id_completed" and "id_to_care".
- **Risks/Mitigations**: Potential misidentifications (e.g., poisonous lookalikes) → Strict disclaimers and confidence thresholds (<70% blocks actions); high traffic spikes → Auto-scaling with Kubernetes (post-MVP); data privacy → Anonymize embeddings, opt-in for photo storage with S3 encryption and GDPR consent flows.
- **Dependencies**: OpenAI API key in .env; Pillow and openai packages in pyproject.toml (managed via UV); Pinecone client initialized in vector_db.py with persistent Docker volume; frontend deps like framer-motion in pnpm-lock.yaml.
- **Extensions**: Real-time AR camera integration using WebRTC and MediaPipe for overlaying ID labels; support for video inputs to capture dynamic traits (e.g., leaf movement in wind); affiliate integrations (e.g., links to buy seeds from Amazon); multi-language names via OpenAI translations; post-MVP batch processing for album uploads.
