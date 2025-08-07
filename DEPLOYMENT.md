# 🚀 Deployment Instructions

## Creating GitHub Repository

Since automatic repository creation failed, please follow these manual steps:

### 1. Create Repository on GitHub

1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Set repository name: `AGENT_LITO`
4. Set description: `Intelligent LangGraph-based chatbot for foster family resource discovery with Azure SQL integration`
5. Make it **Public**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### 2. Update Remote URL

Replace `yourusername` with your actual GitHub username:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/AGENT_LITO.git
```

### 3. Push to GitHub

```bash
git push -u origin master
```

## Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
# Create repository
gh repo create AGENT_LITO --public --description "Intelligent LangGraph-based chatbot for foster family resource discovery with Azure SQL integration"

# Push code
git push -u origin master
```

## Repository Structure

After pushing, your repository will contain:

```
AGENT_LITO/
├── agent_lito/           # Core bot implementation
│   ├── bot.py           # Main LangGraph workflow
│   ├── classification.py # Query classification
│   ├── data_types.py    # Data models
│   └── search/          # Search modules
├── testing/             # Testing tools
│   ├── api.py          # FastAPI server
│   ├── ui.py           # Streamlit UI
│   └── start_testing.py # Testing utilities
├── architecture_graph.py # Architecture documentation
├── architecture_overview.md # Detailed architecture
├── pyproject.toml      # Project configuration
├── README.md           # Project documentation
├── LICENSE             # MIT License
├── env.example         # Environment variables template
└── DEPLOYMENT.md       # This file
```

## Next Steps

1. **Update README.md** - Replace `yourusername` with your actual GitHub username
2. **Set up GitHub Pages** (optional) - For documentation
3. **Configure GitHub Actions** (optional) - For CI/CD
4. **Add Issues Templates** (optional) - For better project management

## Environment Setup

After cloning the repository:

```bash
# Install dependencies
uv sync

# Copy environment template
cp env.example .env

# Edit .env with your API keys
nano .env
```

## Testing the Deployment

```bash
# Start API server
uv run python testing/api.py

# Start UI (in another terminal)
uv run streamlit run testing/ui.py --server.port 8501

# Test individual components
uv run python test_llm_classification.py
uv run python test_location_flow.py
uv run python quick_test.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the [architecture documentation](architecture_overview.md)
- Review the [testing guide](testing/README.md) 