# Agentic Financial Browser

An AI-powered stock financial analysis tool that uses a mini-browser (via web scraping) with LangChain-style agentic AI to fetch and analyze financial data without relying on traditional APIs.

## Features

- **Mini Browser Scraping**: Intelligent web scraping to fetch financial statements from various financial websites
- **VPN/Proxy Support**: Built-in support for routing requests through proxies/VPNs to bypass IP blocks
- **Agentic Analysis**: LangChain-powered agent that compiles metrics and generates analyst-style narratives
- **Working Capital Metrics**: 
  - Days Sales Outstanding (DSO)
  - Cash-to-AR ratio
  - Cash-to-Debt ratio
  - Revenue & AR growth trends
- **Anomaly Detection**: Automatic flagging of red flags in collections, liquidity, and leverage
- **Beautiful Frontend**: Modern, responsive web interface with real-time results

## Project Structure

```
agentic-fin-browser/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration & thresholds
│   ├── scraping_tools.py    # Web scraping utilities (with proxy support)
│   ├── metrics.py           # Financial metric calculations
│   ├── anomalies.py         # Anomaly detection rules
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment template
│   └── .gitignore
├── frontend/
│   ├── index.html           # Main UI
│   ├── style.css            # Styling
│   └── script.js            # Frontend logic
└── README.md
```

## Setup Instructions

### 1. Clone / Download the Repository

```bash
git clone https://github.com/yourusername/agentic-fin-browser.git
cd agentic-fin-browser
```

### 2. Backend Setup

#### Create a Python Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
# Optional: Set proxy if behind VPN/proxy
# PROXY_URL=http://user:pass@proxy.example.com:8080
```

#### Run the Backend Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Frontend Setup

The frontend is a standalone HTML app. You can open it directly or serve it via a simple HTTP server.

#### Option A: Direct File
Simply open `frontend/index.html` in a web browser.

#### Option B: Python HTTP Server

```bash
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

## Usage

1. **Enter Stock Symbol**: e.g., "TCS", "INFY", "AAPL"
2. **Select Market** (optional): NSE, BSE, NASDAQ, NYSE, or Global
3. **Custom URL** (optional): Override with a specific financial website URL
4. **Click "Run Analysis"**: Wait for the backend to fetch and analyze data

## How It Works

### Scraping Pipeline

1. **URL Building**: Based on symbol + market, constructs a financial website URL
2. **Fetch**: Using `requests` + `BeautifulSoup` (with optional proxy)
3. **Parse**: Extracts tables with revenue, AR, cash, debt, equity data
4. **Compute Metrics**: Calculates DSO, cash ratios, YoY growth
5. **Detect Anomalies**: Flags high DSO, low liquidity, AR growth mismatches
6. **Generate Narrative**: Sends metrics + flags to OpenAI for analyst-style summary

### Proxy / VPN Setup

If your IP is blocked, configure a proxy:

#### Using Residential Proxies (e.g., Bright Data, Oxylabs)

In `.env`:

```
PROXY_URL=http://customer-USER:PASS@proxy-provider.com:PORT
```

#### Self-Hosted VPN

Run a VPN client on your server, expose an HTTP proxy (e.g., with `tinyproxy`), and set:

```
PROXY_URL=http://127.0.0.1:8888
```

## API Endpoints

### POST `/api/analyze`

Request:

```json
{
  "symbol": "TCS",
  "market": "NSE",
  "url": null
}
```

Response:

```json
{
  "symbol": "TCS",
  "market": "NSE",
  "years": [{"label": "FY24", "revenue": 281500, "dso": 65.3, ...}],
  "anomalies": [{"year": "FY24", "color": "red", "condition": "..."}],
  "narrative": "Analyst summary..."
}
```

### GET `/health`

Health check endpoint.

## Customization

### Modify Anomaly Thresholds

Edit `backend/config.py`:

```python
DSO_WARNING = 120  # Raise to 150 for less sensitivity
CASH_DEBT_WARNING = 0.2
CASH_AR_WARNING = 0.5
```

### Add Custom Financial Website Parsers

Add functions in `backend/scraping_tools.py`:

```python
def parse_moneycontrol_financials(html: str) -> List[Dict]:
    # Custom parser for Moneycontrol.com
    ...
```

### Deploy to Production

For Railway, Render, or Heroku:

1. Push code to GitHub
2. Create a `Procfile` in root:
   ```
   web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Configure environment variables in your hosting platform
4. Deploy

## Limitations

- Scraping relies on stable website HTML structure; updates to website layouts may break parsers
- Some financial websites block bots; proxy rotation or IP rotation may be needed
- LLM narrative is rule-based and not financial advice

## Contributing

Contributions welcome! Areas to enhance:

- Support more financial websites
- Better anomaly detection algorithms
- Multi-agent orchestration with LangGraph
- Historical data tracking
- Export reports (PDF, Excel)

## License

MIT License. See LICENSE file.

## Disclaimer

**This tool is for educational and research purposes only.** It does not provide investment advice. Always conduct due diligence and consult with a financial advisor before making investment decisions.
