"""
Polymarket API Module - Phase 1: Market Discovery
Connects to Polymarket's gamma-api to discover active crypto prediction markets
No authentication required (public data only)
Uses built-in urllib to avoid external dependencies
"""

import json
import urllib.request
import urllib.error
from typing import List, Dict, Optional
from datetime import datetime, timezone
import ssl

class PolymarketAPI:
    """Client for Polymarket API interactions"""
    
    BASE_URL = "https://gamma-api.polymarket.com"
    TIMEOUT = 10
    
    # Crypto assets we're interested in
    CRYPTO_ASSETS = ["BTC", "ETH", "SOL"]
    # Market direction keywords
    DIRECTIONS = ["Up", "Down", "Higher", "Lower"]
    
    def __init__(self, base_url: str = BASE_URL, timeout: int = TIMEOUT):
        """Initialize Polymarket API client"""
        self.base_url = base_url
        self.timeout = timeout
        # Handle SSL for urllib
        self.context = ssl.create_default_context()
    
    def fetch_all_markets(self, limit: int = 1000) -> List[Dict]:
        """
        Fetch all active markets from Polymarket API
        
        Args:
            limit: Maximum number of markets to fetch
            
        Returns:
            List of market dictionaries
        """
        try:
            url = f"{self.base_url}/markets?limit={limit}&active=true"
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, context=self.context, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            markets = data if isinstance(data, list) else [data]
            return markets
        
        except urllib.error.URLError as e:
            print(f"Error fetching markets: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing markets JSON: {e}")
            return []
    
    def is_crypto_market(self, market: Dict) -> bool:
        """
        Check if market is a crypto prediction market
        
        Args:
            market: Market dictionary from API
            
        Returns:
            True if market is crypto-related prediction market
        """
        question = (market.get("question") or "").upper()
        
        # Check for crypto mentions (BTC/ETH/SOL or bitcoin/ethereum/solana)
        crypto_keywords = ["BTC", "ETH", "SOL", "BITCOIN", "ETHEREUM", "SOLANA", "CRYPTO"]
        has_crypto = any(keyword in question for keyword in crypto_keywords)
        
        # Price direction/movement markets (Up, Down, Higher, Lower, Break, Price, Above, Below)
        direction_keywords = ["UP", "DOWN", "HIGHER", "LOWER", "BREAK", "ABOVE", "BELOW", "PRICE"]
        has_direction = any(keyword in question for keyword in direction_keywords)
        
        # Include active markets (closed status doesn't matter as much if market had activity)
        is_active = market.get("active", False)
        has_volume = float(market.get("volumeNum", market.get("volume", 0))) > 0
        
        # Return markets that mention crypto, are price-based, and either active or have trading volume
        return has_crypto and has_direction and (is_active or has_volume)
    
    def parse_outcome_prices(self, prices_str) -> Dict[str, float]:
        """
        Parse outcome prices from JSON string format
        
        Args:
            prices_str: JSON string like '["0.65", "0.35"]' or already parsed list
            
        Returns:
            Dictionary with YES and NO prices
        """
        try:
            # Handle both string and already parsed formats
            if isinstance(prices_str, str):
                prices = json.loads(prices_str)
            else:
                prices = prices_str
            
            if isinstance(prices, list) and len(prices) >= 2:
                return {
                    "YES": float(prices[0]) if prices[0] else 0.0,
                    "NO": float(prices[1]) if prices[1] else 0.0,
                }
            return {"YES": 0.0, "NO": 0.0}
        
        except (json.JSONDecodeError, ValueError, TypeError):
            return {"YES": 0.0, "NO": 0.0}
    
    def extract_market_data(self, market: Dict) -> Optional[Dict]:
        """
        Extract relevant fields from market dictionary
        
        Args:
            market: Raw market data from API
            
        Returns:
            Cleaned market data or None if invalid
        """
        try:
            # Parse prices
            prices_raw = market.get("outcomePrices", "[]")
            prices = self.parse_outcome_prices(prices_raw)
            
            # Parse volume
            volume = float(market.get("volumeNum", market.get("volume", 0)))
            liquidity = float(market.get("liquidityNum", market.get("liquidity", 0)))
            
            # Parse expiration date
            end_date_str = market.get("endDate", "")
            try:
                end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            except:
                end_date = None
            
            # Calculate days until expiration
            days_to_expiry = None
            if end_date:
                now = datetime.now(timezone.utc)
                delta = end_date - now
                days_to_expiry = max(0, delta.days)
            
            return {
                "market_id": market.get("id"),
                "condition_id": market.get("conditionId"),
                "question": market.get("question", ""),
                "slug": market.get("slug", ""),
                "yes_price": prices["YES"],
                "no_price": prices["NO"],
                "volume": volume,
                "liquidity": liquidity,
                "expiration_date": end_date_str,
                "days_to_expiry": days_to_expiry,
                "category": market.get("category", ""),
                "active": market.get("active", False),
                "closed": market.get("closed", False),
                "image_url": market.get("image", ""),
                "description": market.get("description", "")[:200],  # Truncate description
            }
        
        except Exception as e:
            print(f"Error extracting market data: {e}")
            return None
    
    def discover_crypto_markets(self, limit: int = 1000) -> List[Dict]:
        """
        Discover all active crypto prediction markets
        
        Args:
            limit: Max markets to fetch
            
        Returns:
            List of formatted crypto market data
        """
        print(f"Fetching markets from {self.base_url}...")
        markets = self.fetch_all_markets(limit=limit)
        print(f"Fetched {len(markets)} total markets")
        
        # Filter for crypto markets
        crypto_markets = [m for m in markets if self.is_crypto_market(m)]
        print(f"Found {len(crypto_markets)} crypto prediction markets")
        
        # Extract and format data
        formatted = []
        for market in crypto_markets:
            data = self.extract_market_data(market)
            if data:
                formatted.append(data)
        
        # Sort by volume (descending)
        formatted.sort(key=lambda x: x["volume"], reverse=True)
        
        return formatted
    
    def get_market_by_id(self, market_id: str) -> Optional[Dict]:
        """
        Fetch a specific market by ID
        
        Args:
            market_id: Market ID to fetch
            
        Returns:
            Market data or None if not found
        """
        try:
            url = f"{self.base_url}/markets/{market_id}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, context=self.context, timeout=self.timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            print(f"Error fetching market {market_id}: {e}")
            return None
    
    def export_to_json(self, markets: List[Dict], filepath: str = "sample_markets.json"):
        """
        Export market data to JSON file
        
        Args:
            markets: List of market data dictionaries
            filepath: Output file path
        """
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(markets),
            "markets": markets
        }
        
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"Exported {len(markets)} markets to {filepath}")


def main():
    """Main execution for market discovery"""
    
    # Initialize API client
    api = PolymarketAPI()
    
    # Discover crypto markets
    markets = api.discover_crypto_markets(limit=2000)
    
    # Display summary
    print(f"\n{'='*60}")
    print(f"CRYPTO MARKET DISCOVERY SUMMARY")
    print(f"{'='*60}")
    print(f"Total markets found: {len(markets)}")
    
    if markets:
        print(f"\nTop 5 markets by volume:")
        for i, market in enumerate(markets[:5], 1):
            print(f"\n{i}. {market['question']}")
            print(f"   Market ID: {market['market_id']}")
            print(f"   YES Price: {market['yes_price']:.2%} | NO Price: {market['no_price']:.2%}")
            print(f"   Volume: ${market['volume']:,.0f} | Days to Expiry: {market['days_to_expiry']}")
    
    # Export to JSON
    api.export_to_json(markets, "sample_markets.json")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
