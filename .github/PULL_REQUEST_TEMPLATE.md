# Plant Assistant Pull Request

## 📋 Summary
<!-- Provide a clear and concise description of what this PR does -->

**What does this PR do?**


**Related Issue(s):** <!-- Link to GitHub issues, e.g., "Fixes #123" or "Closes #456" -->


## 🧠 Context and Motivation
<!-- Why is this change needed? What problem does it solve? -->


## 🔧 Changes Made
<!-- List the main changes in this PR -->

### Backend Changes
- [ ] API endpoints modified/added
- [ ] Database models updated
- [ ] Authentication/authorization changes
- [ ] New dependencies added
- [ ] Configuration changes

### Frontend Changes
- [ ] UI components modified/added
- [ ] Pages or routing changes
- [ ] API client updates
- [ ] Styling updates
- [ ] New dependencies added

### Infrastructure Changes
- [ ] Docker configuration
- [ ] CI/CD pipeline updates
- [ ] Environment variables
- [ ] Database migrations

## 🧪 Testing
<!-- Describe how you tested your changes -->

**Test Coverage:**
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] End-to-end tests added/updated
- [ ] Manual testing performed

**Test Commands Run:**
```bash
# Backend tests
make test-backend

# Frontend tests
make test-frontend

# Full test suite
make test
```

## 📱 Screenshots/Recordings
<!-- If this PR includes UI changes, provide screenshots or recordings -->

### Before
<!-- Screenshot of the UI before your changes -->

### After
<!-- Screenshot of the UI after your changes -->

## 🚀 Deployment Notes
<!-- Any special deployment considerations -->

**Database Changes:**
- [ ] Requires database migration
- [ ] Migration command: `make migrate-db`
- [ ] Data migration required

**Environment Variables:**
- [ ] New environment variables added (document in ENVIRONMENT.md)
- [ ] Environment variables removed/changed

**Breaking Changes:**
- [ ] API breaking changes (increment version)
- [ ] Frontend breaking changes
- [ ] Database schema breaking changes

## 📝 Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Code is properly formatted (`make lint`)
- [ ] No linting errors (`make lint`)
- [ ] TypeScript compilation passes (frontend)
- [ ] Python type checking passes (backend)

### Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Test coverage maintained/improved
- [ ] Manual testing completed

### Documentation
- [ ] README updated (if needed)
- [ ] API documentation updated (if endpoints changed)
- [ ] Code comments added for complex logic
- [ ] CHANGELOG.md updated (for significant changes)

### Security
- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] Authentication/authorization properly handled
- [ ] Dependencies checked for vulnerabilities

### Performance
- [ ] No performance regressions introduced
- [ ] Database queries optimized (if applicable)
- [ ] Frontend bundle size considered
- [ ] API response times acceptable

## 🔍 Review Focus
<!-- Guide reviewers on what to focus on -->

**Areas that need special attention:**


**Known limitations/trade-offs:**


## 📚 Additional Notes
<!-- Any other context, concerns, or notes for reviewers -->


---

## 🏷️ Labels
<!-- These will be added automatically based on changed files -->
- Backend: `backend`, `python`, `fastapi`
- Frontend: `frontend`, `nextjs`, `typescript`
- Infrastructure: `docker`, `ci/cd`, `database`
- Documentation: `documentation`
- Dependencies: `dependencies`