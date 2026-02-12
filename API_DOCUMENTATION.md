# Polymarket API Documentation - Phase 1

## Overview

The Polymarket API provides access to prediction market data on various topics, including cryptocurrency price movements. The gamma-api endpoint is public and requires no authentication.

**Base URL:** `https://gamma-api.polymarket.com`

## API Endpoints

### 1. Get All Markets
**Endpoint:** `/markets`  
**Method:** GET  
**Parameters:**
- `limit` (optional, integer): Number of markets to return (default: 500, max: 500+)
- `active` (optional, boolean): Filter for active markets (default: all)
- `category` (optional, string): Filter by category (e.g., "crypto", "politics", "sports")

**Example Request:**
```
GET https://gamma-api.polymarket.com/markets?limit=100&active=true
```

**Response Structure:**
```json
[
  {
    "id": "76",
    "question": "Will $BTC break $20k before 2021?",
    "conditionId": "0xa670159e0a8868ed1ca0013cf026805c1c5ffbf778a1d5030218471620211222",
    "slug": "will-btc-break-20k-before-2021",
    "endDate": "2021-01-01T00:00:00Z",
    "category": "Crypto",
    "liquidity": "1170.71",
    "liquidityNum": 1170.71,
    "volume": "1467610.68",
    "volumeNum": 1467610.68,
    "outcomePrices": "[0.9999998888806887, 1.1111931131046978e-07]",
    "outcomes": "[\"Yes\", \"No\"]",
    "active": true,
    "closed": true,
    "marketType": "normal",
    "createdAt": "2020-10-02T16:10:01.467Z",
    "updatedAt": "2024-04-23T00:49:51.620233Z",
    "image": "https://polymarket-upload.s3.us-east-2.amazonaws.com/...",
    "description": "Market description text...",
    "volume24hr": 0,
    "volume1wk": 0,
    "volume1mo": 0,
    "volume1yr": 0
  }
]
```

### 2. Get Single Market
**Endpoint:** `/markets/{marketId}`  
**Method:** GET  

**Example Request:**
```
GET https://gamma-api.polymarket.com/markets/76
```

Returns same structure as individual market in markets array above.

## Data Fields Explained

### Core Market Information
- **id** (string): Unique market identifier
- **question** (string): The prediction market question
- **conditionId** (string): Unique condition hash (used for order book operations)
- **slug** (string): URL-friendly version of question
- **category** (string): Market category (e.g., "Crypto", "US-current-affairs", "Tech")
- **description** (string): Detailed market description and resolution criteria

### Pricing Data
- **outcomePrices** (string - JSON array): 
  - Array of two values: [YES_price, NO_price]
  - Prices range from 0 to 1 (representing 0% to 100% probability)
  - Format: String representation of JSON array
  - Example: `"[0.65, 0.35]"` = 65% YES, 35% NO
- **outcomes** (string - JSON array): 
  - Array of outcome names: `["Yes", "No"]`

### Volume & Liquidity
- **volumeNum** (float): Total trading volume in USD
- **volume** (string): Total trading volume as string
- **liquidityNum** (float): Available liquidity for trading
- **liquidity** (string): Available liquidity as string
- **volume24hr** (integer): 24-hour trading volume
- **volume1wk** (integer): 1-week trading volume
- **volume1mo** (integer): 1-month trading volume
- **volume1yr** (integer): 1-year trading volume

### Status & Dates
- **active** (boolean): Market is currently accepting trades
- **closed** (boolean): Market has expired/resolved
- **endDate** (ISO 8601 string): Market expiration datetime
- **createdAt** (ISO 8601 string): Market creation timestamp
- **updatedAt** (ISO 8601 string): Last update timestamp
- **marketType** (string): Type of market (normal, etc.)

### Media & Links
- **image** (string): Market image URL
- **icon** (string): Market icon URL
- **twitterCardImage** (string): Twitter card image

## Filtering for Crypto Markets

### Identifying Crypto Markets
Crypto prediction markets can be identified by:

1. **Keywords in question field:**
   - Asset names: "BTC", "ETH", "SOL", "Bitcoin", "Ethereum", "Solana"
   - Crypto mentions: "crypto", "cryptocurrency"

2. **Price prediction patterns:**
   - Directional: "break", "above", "below", "higher", "lower"
   - Example questions:
     - "Will $BTC break $50k before April 1st, 2021?"
     - "Will ETH be above $2000 on March 1st, 2021?"
     - "Will Solana reach $100?"

3. **Category field:**
   - May contain "Crypto" category value

### Market Types
Polymarket crypto markets focus on:
- **Price targets**: Will asset reach X price by Y date?
- **Price ranges**: Will asset be above/below X price at Y date?
- **Market capitalization**: Will asset's market cap exceed X?
- **Volume predictions**: Will trading volume exceed X?

## Python Module API (`polymarket_api.py`)

### PolymarketAPI Class

#### Methods

**`__init__(base_url, timeout)`**
- Initialize API client
- Parameters: base_url (default: gamma-api), timeout (default: 10s)

**`fetch_all_markets(limit=1000)`**
- Fetch raw market data from API
- Returns: List of market dictionaries

**`is_crypto_market(market)`**
- Filter helper to identify crypto prediction markets
- Returns: Boolean

**`parse_outcome_prices(prices_str)`**
- Parse outcome prices from JSON string
- Returns: Dict with YES/NO probability pairs

**`extract_market_data(market)`**
- Clean and format market data for analysis
- Returns: Simplified market dictionary with key fields

**`discover_crypto_markets(limit=1000)`**
- Main method: discover and return filtered crypto markets
- Returns: List of formatted crypto market data

**`export_to_json(markets, filepath)`**
- Export market data to JSON file
- Creates timestamp and count metadata

**`get_market_by_id(market_id)`**
- Fetch single market by ID
- Returns: Market dictionary or None

## Usage Example

```python
from polymarket_api import PolymarketAPI
import json

# Initialize
api = PolymarketAPI()

# Discover crypto markets
markets = api.discover_crypto_markets(limit=2000)

# Export to file
api.export_to_json(markets, "my_markets.json")

# Work with data
for market in markets[:10]:
    print(f"Question: {market['question']}")
    print(f"YES Price: {market['yes_price']:.2%}")
    print(f"Volume: ${market['volume']:,.0f}")
    print(f"Expires in {market['days_to_expiry']} days\n")
```

## Rate Limiting & Best Practices

1. **No authentication required** - Public API
2. **Avoid aggressive polling** - Use reasonable intervals (≥30 seconds between full market syncs)
3. **Batch requests** - Use limit parameter to get multiple markets in one call
4. **Cache results** - Store market data locally to reduce API calls
5. **Handle timeouts** - Implement retry logic with exponential backoff

## Known Limitations

1. **Historical markets**: The API contains many expired/closed markets from past years
2. **Sparse updates**: Live pricing updates may lag slightly
3. **Volume as cumulative**: volumeNum appears to be historical total, not current order book
4. **Price decimals**: Outcome prices are extremely precise floats (may contain floating-point artifacts)

## Data Schema Summary

```
Market {
  id: string
  question: string
  conditionId: string
  slug: string
  category: string
  
  Pricing {
    outcomePrices: string (JSON)  // [YES_price, NO_price]
    outcomes: string (JSON)        // ["Yes", "No"]
  }
  
  Activity {
    volumeNum: float
    liquidityNum: float
    volume24hr: integer
  }
  
  Status {
    active: boolean
    closed: boolean
    endDate: ISO8601 string
    createdAt: ISO8601 string
    updatedAt: ISO8601 string
  }
  
  Media {
    image: string (URL)
    description: string
  }
}
```

## Phase 2 Readiness

With this Phase 1 complete, you now have:
- ✅ API connection module with no external dependencies
- ✅ Market discovery for crypto prediction markets
- ✅ Data extraction and formatting
- ✅ Sample market data (sample_markets.json)
- ✅ Understanding of API structure

**Next Phase 2 will implement:**
- Strategy module for paper trading rules
- Real-time price monitoring
- Signal generation (entry/exit rules)
- Position tracking
- Performance metrics
