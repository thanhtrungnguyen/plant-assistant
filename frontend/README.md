# Plant Assistant Frontend

Modern Next.js frontend application for the Plant Assistant platform, providing an intuitive interface for plant care management with full type safety and responsive design.

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- pnpm (recommended) or npm
- Backend API running on http://localhost:5000

### Development Setup

1. **Install dependencies:**
   ```bash
   pnpm install
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Generate API client (if backend is running):**
   ```bash
   pnpm run generate-client
   ```

4. **Start the development server:**
   ```bash
   pnpm dev
   ```

5. **Access the application:**
   - App: http://localhost:3000
   - Development tools: Open browser dev tools

## 📋 Available Scripts

| Script | Description |
|--------|-------------|
| `pnpm dev` | Start development server with hot reload |
| `pnpm build` | Build production application |
| `pnpm start` | Start production server |
| `pnpm lint` | Run ESLint for code quality |
| `pnpm test` | Run Jest test suite |
| `pnpm coverage` | Run tests with coverage report |
| `pnpm prettier` | Format code with Prettier |
| `pnpm tsc` | Run TypeScript type checking |
| `pnpm generate-client` | Generate API client from OpenAPI schema |

## 🏗️ Architecture

### Project Structure
```
frontend/
├── src/
│   ├── app/                    # Next.js 13+ App Router
│   │   ├── layout.tsx          # Root layout component
│   │   ├── page.tsx            # Home page
│   │   ├── globals.css         # Global styles
│   │   ├── dashboard/          # Dashboard pages
│   │   ├── login/              # Authentication pages
│   │   └── fonts/              # Font files
│   ├── components/             # Reusable UI components
│   │   ├── ui/                 # shadcn/ui base components
│   │   ├── actions/            # Server actions
│   │   └── forms/              # Form components
│   ├── lib/                    # Utility libraries
│   │   ├── utils.ts            # General utilities
│   │   ├── clientConfig.ts     # Client configuration
│   │   └── definitions.ts      # Type definitions
│   └── openapi-client/         # Auto-generated API client
├── public/                     # Static assets
├── __tests__/                  # Test files
├── components.json             # shadcn/ui configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── next.config.mjs             # Next.js configuration
└── package.json                # Dependencies and scripts
```

### Key Technologies
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Beautiful and accessible UI components
- **React Hook Form**: Form handling with validation
- **Zod**: Schema validation
- **OpenAPI TypeScript**: Auto-generated API client
- **Jest**: Testing framework

## 🧪 Testing

### Run Tests
```bash
# All tests
pnpm test

# Watch mode
pnpm test:watch

# Coverage report
pnpm coverage

# UI component tests
pnpm test:ui
```

### Test Structure
- `__tests__/` - Test files
- `jest.config.ts` - Jest configuration
- Component tests alongside components (optional)

### Testing Best Practices
- Test user interactions, not implementation details
- Use React Testing Library for component tests
- Mock API calls in tests
- Test accessibility features

## 🎨 UI Components

### shadcn/ui Components
The project uses shadcn/ui for consistent, accessible components:

```bash
# Add new components
pnpm dlx shadcn-ui@latest add button
pnpm dlx shadcn-ui@latest add dialog
pnpm dlx shadcn-ui@latest add form
```

Available components:
- Button, Input, Label
- Dialog, Sheet, Dropdown Menu
- Avatar, Tabs, Form controls
- And many more...

### Custom Components
- `components/ui/` - Base shadcn/ui components
- `components/forms/` - Form-specific components
- `components/actions/` - Server action components

## 🔌 API Integration

### Auto-generated Client
The API client is automatically generated from the backend OpenAPI schema:

```bash
# Regenerate client when backend changes
pnpm run generate-client
```

### Usage Example
```typescript
import { createClientAxios } from '@/openapi-client';

const client = createClientAxios();

// Fetch user data
const { data: user } = await client.GET('/users/me');

// Create new plant
const { data: plant } = await client.POST('/items/', {
  body: { name: 'Monstera', species: 'Monstera deliciosa' }
});
```

### Error Handling
- Global error boundary for unhandled errors
- API error handling with user-friendly messages
- Loading states for better UX

## 🎭 Styling

### Tailwind CSS
Utility-first CSS framework with custom configuration:

```bash
# Key configuration files
- tailwind.config.js  # Theme customization
- src/app/globals.css # Base styles and CSS variables
```

### Design System
- Consistent color palette (primary, secondary, accent)
- Typography scale with custom fonts
- Spacing and sizing utilities
- Dark/light theme support (if implemented)

### CSS Variables
```css
:root {
  --background: 0 0% 100%;
  --foreground: 240 10% 3.9%;
  --primary: 240 5.9% 10%;
  /* ... more variables */
}
```

## 🛠️ Development Tools

### Code Quality
```bash
# Linting
pnpm lint

# Fix linting issues
pnpm lint --fix

# Type checking
pnpm tsc

# Code formatting
pnpm prettier
```

### Build and Deployment
```bash
# Production build
pnpm build

# Start production server
pnpm start

# Analyze bundle
pnpm analyze
```

## 🌍 Environment Variables

Environment variables (`.env.local`):

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:5000` |
| `NODE_ENV` | Environment mode | `development` |

## 📱 Features

### Authentication
- User registration and login
- Password reset functionality
- Protected routes and middleware
- JWT token management

### Plant Management
- Add, edit, and delete plants
- Plant care scheduling
- Photo upload and management
- Care history tracking

### User Interface
- Responsive design (mobile-first)
- Accessible components
- Loading states and error handling
- Smooth animations and transitions

## 🚀 Performance

### Optimization Techniques
- Next.js automatic code splitting
- Image optimization with `next/image`
- Static generation where possible
- Client-side caching strategies

### Bundle Analysis
```bash
# Analyze bundle size
pnpm analyze

# Check performance
pnpm audit
```

## 🐳 Docker Development

```bash
# Start with Docker Compose
docker compose up frontend

# Shell access
docker compose exec frontend sh

# Install dependencies in container
docker compose exec frontend pnpm install
```

## 📱 Progressive Web App (PWA)

If PWA features are implemented:
- Offline functionality
- Push notifications
- Add to home screen
- Service worker caching

## 🔧 Configuration

### Next.js Configuration
Key settings in `next.config.mjs`:
- Image domains for external images
- API rewrites and redirects
- Environment variable exposure
- Build optimization settings

### TypeScript Configuration
- Strict type checking enabled
- Path mapping for clean imports
- Component prop validation
- API response type safety

## 🤝 Contributing

### Development Workflow
1. Create feature branch
2. Implement changes with tests
3. Run linting and type checking
4. Update documentation if needed
5. Submit pull request

### Code Standards
- Use TypeScript for all new code
- Follow React best practices
- Implement responsive design
- Ensure accessibility compliance
- Write meaningful tests

### Adding New Pages
1. Create page in `src/app/`
2. Add necessary components
3. Implement API integration
4. Add tests for functionality
5. Update navigation if needed

### Adding New Components
1. Create in appropriate directory
2. Use TypeScript interfaces
3. Implement accessibility features
4. Add Storybook story (if using)
5. Write component tests

## 🔍 Debugging

### Development Tools
- React Developer Tools
- Next.js DevTools
- Tailwind CSS DevTools
- TypeScript error overlay

### Common Issues
- Check API connectivity
- Verify environment variables
- Clear Next.js cache: `rm -rf .next`
- Check TypeScript compilation: `pnpm tsc`

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Hook Form](https://react-hook-form.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
