# 🔧 GitHub CI Setup Guide

Your GitHub Actions workflows are configured but need secrets to be set up. Here's how to fix the CI issues:

## 🚨 Current CI Issues

The GitHub Actions linter is showing "Context access might be invalid" warnings because the secrets referenced in the workflows don't exist in your repository yet. This is normal - once you add the secrets, these warnings will disappear.

## 🔐 Required GitHub Secrets

To fix the CI issues, you need to add these secrets to your GitHub repository:

### Step 1: Go to Repository Settings
1. Navigate to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**

### Step 2: Add These Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DATABASE_URL` | Main database connection | `postgresql+asyncpg://postgres:your-password@localhost:5432/plant_assistant` |
| `TEST_DATABASE_URL` | Test database connection | `postgresql+asyncpg://postgres:your-password@localhost:5432/plant_assistant_test` |
| `SECRET_KEY` | Main JWT secret key | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ACCESS_SECRET_KEY` | Access token secret | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `RESET_PASSWORD_SECRET_KEY` | Password reset secret | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `VERIFICATION_SECRET_KEY` | Email verification secret | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `your-secure-database-password` |
| `CORS_ORIGINS` | Allowed CORS origins | `["https://your-domain.com"]` |
| `MAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `ENVIRONMENT` | App environment | `production` |
| `API_PREFIX` | API route prefix | `/api/v1` |

### Step 3: Generate Secret Keys

Run these commands to generate secure secret keys:

```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate ACCESS_SECRET_KEY  
python -c "import secrets; print('ACCESS_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate RESET_PASSWORD_SECRET_KEY
python -c "import secrets; print('RESET_PASSWORD_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate VERIFICATION_SECRET_KEY
python -c "import secrets; print('VERIFICATION_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Step 4: Test CI Workflows

After adding all secrets:

1. **Push a commit** to trigger the CI workflow
2. **Check the Actions tab** to see if workflows run successfully
3. **Fix any remaining issues** if workflows still fail

## 🛠️ Quick Setup Script

You can also use this script to generate all the required secrets:

```bash
# Generate all secrets at once
echo "# GitHub Secrets for Plant Assistant"
echo "# Copy these values to your GitHub repository secrets"
echo ""
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "ACCESS_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "RESET_PASSWORD_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "VERIFICATION_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "POSTGRES_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')"
echo ""
echo "# Set these based on your environment:"
echo 'DATABASE_URL=postgresql+asyncpg://postgres:your-password@localhost:5432/plant_assistant'
echo 'TEST_DATABASE_URL=postgresql+asyncpg://postgres:your-password@localhost:5432/plant_assistant_test'
echo 'CORS_ORIGINS=["https://your-domain.com"]'
echo 'MAIL_SERVER=smtp.your-provider.com'
echo 'MAIL_PORT=587'
echo 'ENVIRONMENT=production'
echo 'API_PREFIX=/api/v1'
```

## 🔍 Troubleshooting

### Common Issues:

1. **"Context access might be invalid" warnings**
   - ✅ **Solution**: Add the missing secrets to your repository
   - These warnings are expected until secrets are configured

2. **Workflow fails with "secret not found"**
   - ✅ **Solution**: Double-check secret names match exactly (case-sensitive)

3. **Database connection fails in CI**
   - ✅ **Solution**: Ensure PostgreSQL service is running in workflow
   - Check DATABASE_URL format is correct

4. **Tests fail due to missing environment variables**
   - ✅ **Solution**: All required secrets should have fallback values in the workflow

## ✅ Validation Checklist

After setting up secrets, verify:

- [ ] All secrets are added to GitHub repository
- [ ] Secret names match workflow variable names exactly
- [ ] CI workflow runs without "invalid context" warnings
- [ ] Tests pass in GitHub Actions
- [ ] No sensitive data is logged in workflow outputs

## 🚀 Next Steps

1. **Add all required secrets** to your GitHub repository
2. **Test workflows** by pushing a commit
3. **Monitor Actions tab** for any remaining issues
4. **Update documentation** if you add new environment variables

---

💡 **Pro Tip**: Use environment-specific secrets for staging vs production deployments!
