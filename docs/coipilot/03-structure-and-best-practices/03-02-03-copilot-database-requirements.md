# Plant Assistant Database Requirements for GitHub Copilot

## Database Requirements
- **Postgres**: For structured data; use SQLAlchemy ORM with typed models (Mapped[int] for ids). Async support via asyncpg.
  - Example Model: class User(Base): id: Mapped[int] = mapped_column(primary_key=True)
- **Pinecone**: For vector embeddings (OpenAI); persist collections in Docker volumes.
- Migrations: Use Alembic for schema changes (alembic init, revision, upgrade).

## Detailed Setup
- Session: Scoped sessions for thread safety.
- Indexing: Add indexes on frequent queries (e.g., user_id).

## Rationale
- Postgres for relational data (users/plants); Pinecone for AI speed (sub-second searches).

## Scaling Considerations
- Sharding for large data; add read replicas. Monitor with pgAdmin.
