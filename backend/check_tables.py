#!/usr/bin/env python3
"""Check database tables."""

from sqlalchemy import text

from src.database.session import session_scope


def main():
    """List all tables in the database."""
    with session_scope() as db:
        result = db.execute(
            text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"
            )
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables created: {len(tables)}")
        for table in tables:
            print(f"- {table}")


if __name__ == "__main__":
    main()
