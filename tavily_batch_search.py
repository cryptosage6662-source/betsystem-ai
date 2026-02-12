#!/usr/bin/env python3
"""
Tavily Batch Search - Rate Limit Workaround
Batch multiple searches with intelligent delays
"""

import subprocess
import json
import time
import os
from typing import List, Dict

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TAVILY_SCRIPT = "/data/.openclaw/workspace/skills/tavily-search/scripts/search.mjs"

# Rate limiting
MIN_DELAY_BETWEEN_REQUESTS = 2  # seconds
BATCH_DELAY = 5  # seconds between batches

class TavilyBatchSearch:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.last_request_time = 0
        self.request_count = 0
        self.batch_count = 0
    
    def _wait_for_rate_limit(self):
        """Enforce minimum delay between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < MIN_DELAY_BETWEEN_REQUESTS:
            wait_time = MIN_DELAY_BETWEEN_REQUESTS - elapsed
            print(f"⏳ Rate limit: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
    
    def search(self, query: str, num_results: int = 5, deep: bool = False) -> Dict:
        """Search a single query"""
        self._wait_for_rate_limit()
        
        cmd = [
            "node", TAVILY_SCRIPT, query,
            "-n", str(num_results)
        ]
        
        if deep:
            cmd.append("--deep")
        
        env = os.environ.copy()
        env['TAVILY_API_KEY'] = self.api_key
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
            self.last_request_time = time.time()
            self.request_count += 1
            
            if result.returncode == 0:
                return {
                    "query": query,
                    "success": True,
                    "result": result.stdout,
                    "request_num": self.request_count
                }
            else:
                return {
                    "query": query,
                    "success": False,
                    "error": result.stderr,
                    "request_num": self.request_count
                }
        except Exception as e:
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "request_num": self.request_count
            }
    
    def batch_search(self, queries: List[str], num_results: int = 5) -> List[Dict]:
        """Search multiple queries with rate limiting"""
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n🔍 [{i}/{len(queries)}] Searching: {query}")
            result = self.search(query, num_results)
            results.append(result)
            
            if result["success"]:
                print(f"✅ Success (request #{result['request_num']})")
            else:
                print(f"❌ Failed: {result['error']}")
            
            # Delay between batches
            if i < len(queries):
                print(f"⏳ Batch delay: {BATCH_DELAY}s...")
                time.sleep(BATCH_DELAY)
        
        return results

# Example usage
if __name__ == "__main__":
    if not TAVILY_API_KEY:
        print("❌ Error: TAVILY_API_KEY not set")
        print("Set it with: export TAVILY_API_KEY='your-key'")
        exit(1)
    
    search = TavilyBatchSearch(TAVILY_API_KEY)
    
    # Batch search example
    queries = [
        "polymarket bitcoin prediction",
        "crypto trading strategies 2026",
        "mean reversion trading",
    ]
    
    print("🚀 Starting batch search with rate limiting...")
    print(f"Queries: {len(queries)}")
    print(f"Min delay: {MIN_DELAY_BETWEEN_REQUESTS}s between requests")
    print(f"Batch delay: {BATCH_DELAY}s between batches\n")
    
    results = search.batch_search(queries, num_results=3)
    
    # Summary
    print("\n" + "="*60)
    print("📊 BATCH SEARCH SUMMARY")
    print("="*60)
    successful = sum(1 for r in results if r["success"])
    print(f"Total queries: {len(queries)}")
    print(f"Successful: {successful}/{len(queries)}")
    print(f"Total requests: {search.request_count}")
    print(f"Time elapsed: ~{MIN_DELAY_BETWEEN_REQUESTS * len(queries) + BATCH_DELAY * (len(queries)-1):.0f}s")
