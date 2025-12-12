# 🔑 API Keys Setup Guide

This guide will walk you through obtaining the required API keys for the League of Legends Q&A application.

## 📋 Required API Keys

1. **OpenAI API Key** (Required) - For LLM and embeddings
2. **LangSmith API Key** (Optional but Recommended) - For monitoring and tracing

---

## 🤖 Getting Your OpenAI API Key

### Step 1: Create an OpenAI Account
1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Click **"Sign up"** or **"Log in"** if you already have an account
3. Complete the registration process

### Step 2: Add Payment Method
1. Navigate to **Settings** → **Billing**
2. Click **"Add payment method"**
3. Add a credit card or other payment method
   - ⚠️ **Note**: OpenAI charges based on usage. You'll need to add credits to your account.
   - 💡 **Tip**: Start with a small amount ($5-10) to test the application

### Step 3: Generate API Key
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click **"Create new secret key"**
3. Give it a name (e.g., "League of Legends Q&A App")
4. Click **"Create secret key"**
5. **⚠️ IMPORTANT**: Copy the key immediately! You won't be able to see it again.
6. The key will look like: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 4: Check Your Usage Limits
1. Go to **Settings** → **Limits**
2. Review your rate limits and usage quotas
3. For testing, the default limits should be sufficient

### 💰 OpenAI Pricing (as of 2024)
- **GPT-4o-mini**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **Embeddings (text-embedding-3-small)**: ~$0.02 per 1M tokens
- **Estimated cost**: ~$0.01-0.05 per 100 queries (depending on query length)

---

## 📊 Getting Your LangSmith API Key

### Step 1: Create a LangSmith Account
1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Click **"Sign up"** or **"Log in"**
3. You can sign up with:
   - GitHub account
   - Google account
   - Email address

### Step 2: Create an API Key
1. Once logged in, click on your **profile icon** (top right)
2. Select **"Settings"** or go directly to [https://smith.langchain.com/settings](https://smith.langchain.com/settings)
3. Scroll down to **"API Keys"** section
4. Click **"Create API Key"**
5. Give it a name (e.g., "League of Legends Q&A")
6. Click **"Create"**
7. **⚠️ IMPORTANT**: Copy the key immediately!
8. The key will look like: `lsv2_pt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Create a Project (Optional)
1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Click **"Create Project"** or use the default project
3. Name it (e.g., "lolqa")
4. This project name should match the `LANGSMITH_PROJECT` in your `.env` file

### 💡 LangSmith Benefits
- **Free tier available** for personal projects
- Monitor all LLM calls and their costs
- Debug and optimize your application
- Track performance metrics
- View traces and logs

---

## 🔧 Setting Up Your .env File

1. **Create a `.env` file** in the project root directory (if it doesn't exist)

2. **Add your API keys**:
```env
# OpenAI API Key (Required)
OPENAI_API_KEY=sk-proj-your-actual-key-here

# LangSmith API Key (Optional but Recommended)
LANGSMITH_API_KEY=lsv2_pt_your-actual-key-here

# LangSmith Project Name (Optional)
LANGSMITH_PROJECT=lolqa

# LangSmith Endpoint (Optional, defaults to https://api.smith.langchain.com)
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

3. **Replace the placeholder values** with your actual API keys

4. **⚠️ Security Note**: 
   - Never commit your `.env` file to version control
   - The `.gitignore` file already excludes `.env` files
   - Don't share your API keys publicly

---

## ✅ Verifying Your Setup

### Test OpenAI API Key
```bash
# Install OpenAI Python package if not already installed
pip install openai

# Test the key (replace with your actual key)
python -c "from openai import OpenAI; client = OpenAI(api_key='your-key-here'); print('✅ OpenAI API key is valid!')"
```

### Test LangSmith API Key
1. Run your application: `streamlit run app.py`
2. Ask a question in the app
3. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
4. Check if traces appear in your project dashboard
5. If you see traces, your LangSmith integration is working! ✅

---

## 🆘 Troubleshooting

### "Invalid API key" Error
- ✅ Double-check that you copied the entire key (no spaces, no line breaks)
- ✅ Make sure the key starts with `sk-proj-` (OpenAI) or `lsv2_pt_` (LangSmith)
- ✅ Verify the key hasn't expired or been revoked
- ✅ Check that you're using the correct key type (API key, not organization key)

### "Insufficient credits" Error (OpenAI)
- ✅ Add credits to your OpenAI account
- ✅ Go to [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
- ✅ Add payment method and purchase credits

### LangSmith Not Showing Traces
- ✅ Verify `LANGSMITH_API_KEY` is set correctly in `.env`
- ✅ Check that `LANGCHAIN_TRACING_V2=true` is set (automatically set in `app.py`)
- ✅ Ensure the project name matches in LangSmith dashboard
- ✅ Wait a few seconds for traces to appear (they're not instant)

### Environment Variables Not Loading
- ✅ Make sure `.env` file is in the project root directory
- ✅ Verify `python-dotenv` is installed: `pip install python-dotenv`
- ✅ Check that `.env` file has no syntax errors
- ✅ Restart your application after changing `.env` file

---

## 🔒 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** (`.env` file) for local development
3. **Use secret management** for production deployments:
   - Streamlit Cloud: Add secrets in dashboard
   - Railway: Use environment variables in dashboard
   - Render: Use environment variables in dashboard
   - Heroku: Use `heroku config:set` command
4. **Rotate keys regularly** if compromised
5. **Monitor usage** to detect unauthorized access
6. **Set usage limits** in OpenAI dashboard to prevent unexpected charges

---

## 📚 Additional Resources

- [OpenAI Documentation](https://platform.openai.com/docs)
- [OpenAI Pricing](https://openai.com/pricing)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangSmith Pricing](https://smith.langchain.com/pricing)

---

## 💡 Quick Start Checklist

- [ ] Created OpenAI account
- [ ] Added payment method to OpenAI
- [ ] Generated OpenAI API key
- [ ] Created LangSmith account
- [ ] Generated LangSmith API key
- [ ] Created `.env` file with both keys
- [ ] Tested the application
- [ ] Verified traces appear in LangSmith

Once you've completed these steps, you're ready to run the application! 🚀

