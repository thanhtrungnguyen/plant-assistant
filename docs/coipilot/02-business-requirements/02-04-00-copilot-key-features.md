# Plant Assistant Key Features Overview for GitHub Copilot

This file overviews MVP features. For details, refer to sub-files:
- copilot-feature-identification.md
- copilot-feature-care-advice.md
- copilot-feature-diagnosis.md
- copilot-feature-tracking.md
- copilot-feature-conversational.md

## Summary
MVP focuses on 5 core features to cover the user journey: discover, learn, fix, monitor, interact. Features are prioritized by user needs (e.g., ID is #1 per surveys). All leverage AI for accuracy, with fallbacks for edge cases.

## Feature Prioritization
- Must-Have: All listed for MVP.
- Nice-to-Have: Voice input, social sharing (post-MVP).
- Integration: Features share data (e.g., ID results feed into care advice).

## Scaling Considerations
- Modular Design: Each feature as separate service for easy updates.
- Future Enhancements: Add AI training on user data (anonymized) for better accuracy.