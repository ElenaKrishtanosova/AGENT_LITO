# 🤖 AGENT_LITO - Intelligent Foster Family Resource Bot

A sophisticated LangGraph-based chatbot designed to help foster families discover relevant resources and services. Built with Azure SQL vector search, OpenAI GPT-4, and modern web technologies.

## 🚀 Features

- **Intelligent Query Classification** - LLM-powered request understanding
- **Vector Database Search** - Azure SQL with semantic search capabilities
- **Location-Aware Resource Discovery** - Contextual results based on user location
- **Multi-Modal Search** - Database, web, and URL-based resource discovery
- **Interactive UI** - Streamlit-based testing interface
- **RESTful API** - FastAPI backend for easy integration

## 🏗️ Architecture

The system uses a dynamic LangGraph workflow with the following nodes:

```
User Input → classify_query → check_location → location_response → search_database → generate_response → Final Response
```

### Core Components

1. **classify_query_node** - LLM-powered request classification
2. **check_location_node** - Location requirement validation
3. **location_response_node** - Location processing and routing
4. **search_database_node** - Azure SQL vector search
5. **search_web_node** - Web search via Tavily API
6. **search_url_node** - URL content analysis
7. **handle_unclear_node** - Unclear query processing
8. **generate_response_node** - Response formatting and generation

## 🛠️ Technology Stack

- **LangGraph** - Workflow orchestration
- **LangChain** - LLM integration
- **OpenAI GPT-4o-mini** - Natural language processing
- **Azure SQL** - Vector database with semantic search
- **FastAPI** - REST API backend
- **Streamlit** - Testing UI
- **Tavily API** - Web search capabilities
- **uv** - Python package management

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/ElenaKrishtanosova/AGENT_LITO.git
cd AGENT_LITO
```

2. **Install dependencies**
```bash
uv sync
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Configure your `.env` file**
```env
OPENAI_API_KEY=your_openai_api_key
CONN_STRING=your_azure_sql_connection_string
TAVILY_API_KEY=your_tavily_api_key
```

## 🚀 Quick Start

### Start the API Server
```bash
uv run python testing/api.py
```

### Start the Testing UI
```bash
uv run streamlit run testing/ui.py --server.port 8501
```

### Test Individual Components
```bash
# Test LLM classification
uv run python test_llm_classification.py

# Test location flow
uv run python test_location_flow.py

# Quick test
uv run python quick_test.py
```

## 📊 API Endpoints

- `GET /` - API information
- `POST /classify` - Query classification
- `POST /database-search` - Database search
- `POST /web-search` - Web search
- `POST /url-search` - URL search
- `POST /full-bot` - Complete bot workflow
- `POST /location-response` - Location processing

## 🧪 Testing

The project includes comprehensive testing tools:

- **Streamlit UI** (`testing/ui.py`) - Interactive testing interface
- **API Testing** (`testing/api.py`) - FastAPI server with endpoints
- **Component Tests** - Individual module testing scripts

### Testing Interface Features

1. **LLM Classification Testing** - Test query understanding
2. **Database Search Testing** - Test Azure SQL integration
3. **Web Search Testing** - Test web search capabilities
4. **URL Search Testing** - Test URL content analysis
5. **Full Bot Testing** - End-to-end workflow testing

## 🔧 Configuration

### Azure SQL Setup

The system requires Azure SQL with vector support:

```sql
-- Enable vector support
ALTER DATABASE your_database SET COMPATIBILITY_LEVEL = 160;

-- Create vector table
CREATE TABLE rms.rms_table_view (
    RMS_id INT PRIMARY KEY,
    description NVARCHAR(MAX),
    resource_name NVARCHAR(255),
    VectorBinary VARBINARY(8000)
);
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `CONN_STRING` | Azure SQL connection string | Yes |
| `TAVILY_API_KEY` | Tavily API key | Optional |

## 📁 Project Structure

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
└── README.md           # This file
```

## 🎯 Use Cases

### 1. Database Search
```
User: "Find mental health resources for foster families"
Bot: Searches Azure SQL database and returns relevant resources
```

### 2. Location-Aware Search
```
User: "Where can I find food assistance in Austin, Texas?"
Bot: Searches with location context and returns local resources
```

### 3. Web Search
```
User: "Find recent foster care policies"
Bot: Searches web for current information
```

### 4. URL Analysis
```
User: "Extract information from https://fostercare.gov"
Bot: Analyzes specific URL content
```

## 🔄 Workflow Examples

### Standard Flow
```
Input → Classify → Check Location → Search → Generate Response
```

### Location Required Flow
```
Input → Classify → Request Location → Process Location → Search → Generate Response
```

### Unclear Query Flow
```
Input → Classify → Handle Unclear → Request Clarification → Reclassify
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph** - For the excellent workflow orchestration framework
- **OpenAI** - For powerful language models
- **Microsoft Azure** - For vector database capabilities
- **Streamlit** - For the intuitive testing interface

## 📞 Support

For questions and support:
- Create an issue in this repository
- Check the [architecture documentation](architecture_overview.md)
- Review the [testing guide](testing/README.md)

---

**Built with ❤️ for foster families and the community**
