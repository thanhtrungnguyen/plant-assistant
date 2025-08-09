# Plant Assistant Backend

FastAPI backend service for the Plant Assistant application.

## Features

- FastAPI with automatic OpenAPI documentation
- User authentication and management
- PostgreSQL database integration
- Email functionality with MailHog for development
- Hot reload for development

## Development

Run the development server:

```bash
uv run fastapi dev src/app/main.py --host 0.0.0.0 --port 5000 --reload
```

## API Documentation

Visit http://localhost:5000/docs for interactive API documentation.
