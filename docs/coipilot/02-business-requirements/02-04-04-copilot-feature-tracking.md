# Plant Assistant Feature: Tracking & Reminders for GitHub Copilot


## Feature Description
- User dashboard for plant logging: Create entries with name, multiple photos (upload/history), acquisition date, location tags (e.g., "Living room"), notes (free-text), custom attributes (e.g., "Gift from friend", soil type).
- Set/manage reminders: Customizable (e.g., "Water every Monday", "Fertilize monthly on 1st"), recurring via cron-like syntax (e.g., "0 9 * * 1" for weekly), one-off (e.g., "Repot on 2025-09-15"), priorities (low/medium/high with notifications).
- Track progress: Upload timed photos (dated automatically), AI-generated insights via OpenAI Vision (e.g., "Growth +15% in height from last month; leaves greener, RGB delta +20; potential budding detected").
- Notifications: Opt-in email via SendGrid (templates for reminders), push via Firebase (post-MVP); in-app alerts.
- Privacy: Opt-in photo storage (S3 with encryption); delete/export data on request.

## User Stories
- As a forgetful user, I want automated reminders to maintain consistent care.
- As an analyst-type user, I want AI insights from photo series to quantify progress.
- As a multi-plant owner, I want searchable dashboard with filters (e.g., by type, status).
- As a shared account user, I want family access with permissions.

## Acceptance Criteria
- Reminders trigger within ±30min; accuracy 95%+.
- Insights require ≥2 photos; confidence >75%.
- Dashboard loads <1s for 50 plants; pagination if >20.
- Exports in CSV/PDF; deletions cascade logs.

## Backend Handling
- **Endpoint**: /api/plants/track (CRUD operations: POST add, GET list/paginated, PUT update/reminder, DELETE).
- **Request Schema** (e.g., TrackAddRequest): plant_data: Dict[str, Any], reminders: List[Dict[str, str]].
- **Response Schema**: TrackResponse(plants: List[Dict], logs: List[Dict], insights: Optional[Dict[str, Any]]).
- **Service**: plant_service.py: SQLAlchemy models (Plant: id, user_id, name, photos ARRAY[text], traits JSONB; Log: plant_id, date, action, notes, photo); OpenAI for insights (vision compare: "Analyze changes between images"); APScheduler for cron jobs (background reminders).
- **Example Flow**: Add plant → DB insert → Set reminder (store cron) → Photo upload → OpenAI (~$0.01) → Update log with insights.
- **Edge Cases**: Overdue reminders → Notify backlog; photo limits (20/plant) → Enforce with errors.
- **Logging/Monitoring**: Scheduler logs to Postgres; metrics on reminder completions.

## Frontend
- **Component**: Dashboard.tsx (Shadcn Table for plant list, Card for details, Dialog for adds/logs, Calendar for reminders via react-big-calendar).
- **Display**: Plant cards with thumbnails, timelines (Recharts line graphs for growth), reminder badges.
- **Wireframe Description**: Sidebar: Filter/search. Main: Grid/table of plants (columns: Name, Status, Last Action). Detail view: Photo gallery, log table, reminder setup.
- **User Flow**: Login → Dashboard load (API fetch) → Add/log → Sync → In-app toast for insights.

## Rationale and Scaling
- **Why**: Increases retention 20% via habits; data fuels AI improvements.
- **Accuracy**: Cron validation; user-editable insights.
- **Performance**: Indexed DB queries; lazy-load photos.
- **Success Metrics**: 65% users with >5 logs; 85% reminder adherence.
- **Risks/Mitigations**: Notification overload → User controls; storage costs → Compress images.
- **Dependencies**: APScheduler in uv.lock; Recharts/big-calendar in pnpm.
- **Extensions**: Growth charts exports; social sharing; IoT sensor integrations.