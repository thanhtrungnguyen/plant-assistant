# Plant Assistant AI-Specific Practices for GitHub Copilot

## AI-Specific
- **LangGraph**: Stateful graphs for multi-step (e.g., identify → advise). Example: StateGraph with nodes/edges.
- **OpenAI**: Handle rate limits (retry logic); disclaimers for advice ("AI-generated, verify").
- **Vector DB**: Embed plant data with OpenAI for semantic search (e.g., collection.add with metadata).

## Detailed Practices
- Prompt Engineering: System prompts for consistency (e.g., "Respond as botanist").
- Cost Optimization: Batch queries, cache responses.

## Rationale
- Ensures accurate, efficient AI; reduces hallucinations.

## Scaling Considerations
- Fine-tune models on dataset; add hybrid search.