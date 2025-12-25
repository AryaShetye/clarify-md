# 🚀 CLARIFY.MD - Quick Setup Guide

## Step 1: Get Google API Key (Free)

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

## Step 2: Install Dependencies

```bash
pip install -r requirements_v2.txt
```

## Step 3: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## Step 4: Run the Application

```bash
streamlit run app_v2.py
```

## Step 5: Access the App

Open your browser to: `http://localhost:8501`

## Troubleshooting

### API Key Issues
- Make sure `.env` file is in the root directory
- Verify the key starts with `AIza...`
- Check for extra spaces or quotes

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements_v2.txt`
- Check Python version: `python --version` (should be 3.8+)

### Module Not Found
- Make sure you're in the project root directory
- Check that all agent files are present in `agents/` folder

## Testing

Try this example input:
> "I feel like a rubber band inside my head is being pulled tighter and tighter. I'm afraid it's going to snap."

You should see:
- Metaphor translation
- Emotional signals
- Risk assessment
- Clinical summary

## Next Steps

- Read `README_HACKATHON.md` for full documentation
- Check `DEMO_SCRIPT.md` for demo preparation
- Explore the code to understand the agentic architecture
