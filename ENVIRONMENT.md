# Environment Variables

## Backend Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/plant_assistant
TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/plant_assistant_test

# Authentication
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME="Plant Assistant"

# Development
OPENAPI_OUTPUT_FILE=./shared-data/openapi.json
ENVIRONMENT=development
```

## Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:5000

# Environment
NODE_ENV=development
```

## Production Environment Variables

For production deployment, ensure you set:

- Strong `SECRET_KEY` (use `openssl rand -hex 32`)
- Production database URLs
- Real email server configuration
- `ENVIRONMENT=production`

## Security Notes

- Never commit `.env` files to version control
- Use environment-specific values
- Rotate secrets regularly
- Use strong, unique passwords for production
