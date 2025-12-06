# GitHub Personal Access Token Guide

## Quick Steps to Create a Token

1. **Go to GitHub Token Settings**
   - Direct link: https://github.com/settings/tokens
   - Or: Profile → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Click "Generate new token" → "Generate new token (classic)"**

3. **Configure the token:**
   - **Note**: Give it a name like "Push to personal-ai-assistant"
   - **Expiration**: Choose 90 days or custom
   - **Scopes**: Check `repo` (this gives full repository access)

4. **Click "Generate token"** at the bottom

5. **Copy the token immediately** - you won't see it again!

## Using the Token

When you push to GitHub and it asks for credentials:
- **Username**: Your GitHub username (mmammadali)
- **Password**: Paste your Personal Access Token (NOT your GitHub password)

## Security Tips

- ✅ Keep your token secret - treat it like a password
- ✅ Use different tokens for different purposes
- ✅ Set expiration dates
- ✅ Revoke tokens you no longer need
- ❌ Never commit tokens to your repository
- ❌ Don't share tokens publicly

## Revoking a Token

If you need to revoke a token:
1. Go to https://github.com/settings/tokens
2. Find your token in the list
3. Click "Revoke" next to it

## Alternative: GitHub CLI

You can also use GitHub CLI (`gh`) for authentication:
```bash
gh auth login
```

This will guide you through authentication interactively.

