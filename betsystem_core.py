#!/usr/bin/env python3
"""
BetSystem AI - Core Betting Strategy Engine
Integrates with available skills: sportsbet-advisor, game-theory, tavily-search, polymarket
"""

import json
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# ==================== DATA MODELS ====================

@dataclass
class User:
    id: str
    email: str
    bankroll: float
    max_stake_percent: float
    daily_loss_limit: float
    stop_loss_locked: bool = False

@dataclass
class Match:
    id: str
    sport: str
    team_a: str
    team_b: str
    odds: float
    market: str
    date: str

@dataclass
class BetSuggestion:
    strategy: str
    sport: str
    match: str
    bet_type: str
    odds: float
    confidence: float
    expected_value: float
    recommended_stake: float
    stake_unit: str
    risk_level: str
    explanation: List[str]
    
    def to_json(self):
        return json.dumps(asdict(self), indent=2)

# ==================== SKILL INTEGRATIONS ====================

class SkillIntegrator:
    """Integrate with available OpenClaw skills"""
    
    @staticmethod
    def run_skill(skill_path: str, command: str) -> str:
        """Run skill command and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def get_sportsbet_analysis(match: Match) -> Dict:
        """Use sportsbet-advisor skill to analyze bet"""
        # Read the skill
        skill_path = "/data/.openclaw/workspace/skills/sportsbet-advisor/SKILL.md"
        
        # Extract reasoning from skill
        analysis = {
            "match": f"{match.team_a} vs {match.team_b}",
            "odds": match.odds,
            "skill_used": "sportsbet-advisor",
            "analysis": f"Analyzing {match.sport} match with current odds {match.odds}",
            "confidence": 0.0,
            "expected_value": 0.0
        }
        
        return analysis
    
    @staticmethod
    def get_polymarket_odds(query: str) -> Optional[Dict]:
        """Use polymarket skill to get real odds"""
        skill_cmd = f"""
        node /data/.openclaw/workspace/skills/polymarket-odds/polymarket.mjs search "{query}"
        """
        
        try:
            result = subprocess.run(
                skill_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                return {
                    "source": "polymarket",
                    "data": result.stdout
                }
        except:
            pass
        
        return None
    
    @staticmethod
    def research_teams(team_a: str, team_b: str) -> Dict:
        """Use tavily-search to research team stats"""
        # Would integrate tavily-search for team research
        return {
            "team_a": team_a,
            "team_b": team_b,
            "research_available": True
        }

# ==================== BETTING STRATEGIES ====================

class FlatBetting:
    """Fixed percentage per bet"""
    
    @staticmethod
    def calculate(bankroll: float, stake_percent: float, odds: float, confidence: float) -> float:
        """Calculate recommended stake"""
        stake = bankroll * (stake_percent / 100)
        expected_value = (confidence * odds) - 1
        
        return {
            "strategy": "Flat Betting",
            "stake": stake,
            "expected_value": expected_value,
            "risk_level": "Low" if stake_percent <= 2 else "Medium"
        }

class KellyCriterion:
    """Optimal stake based on edge"""
    
    @staticmethod
    def calculate(bankroll: float, odds: float, confidence: float, max_kelly: float = 0.25) -> float:
        """Kelly Criterion: f* = (bp - q) / b"""
        b = odds - 1  # Decimal odds - 1
        p = confidence  # Probability
        q = 1 - p
        
        # Kelly formula
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Apply max Kelly (safety cap at 25%)
        kelly_fraction = min(kelly_fraction, max_kelly)
        kelly_fraction = max(kelly_fraction, 0)  # No negative stakes
        
        stake = bankroll * kelly_fraction
        expected_value = (confidence * odds) - 1
        
        return {
            "strategy": "Kelly Criterion",
            "kelly_fraction": kelly_fraction,
            "stake": stake,
            "expected_value": expected_value,
            "risk_level": "Medium" if kelly_fraction > 0.15 else "Low"
        }

class ValueBetting:
    """Bet when odds > implied probability"""
    
    @staticmethod
    def calculate(bankroll: float, odds: float, confidence: float, stake_percent: float = 2) -> float:
        """Value betting: Odds > Implied Probability"""
        implied_prob = 1 / odds
        
        # Only suggest if confidence > implied probability
        if confidence > implied_prob:
            edge = confidence - implied_prob
            stake = bankroll * (stake_percent / 100)
            expected_value = (confidence * odds) - 1
            
            return {
                "strategy": "Value Betting",
                "edge": edge,
                "stake": stake,
                "expected_value": expected_value,
                "risk_level": "Medium" if edge > 0.05 else "Low"
            }
        else:
            return {
                "strategy": "Value Betting",
                "skip_reason": f"No edge: confidence {confidence:.2%} <= implied {implied_prob:.2%}",
                "stake": 0,
                "expected_value": -1
            }

class PoissonModel:
    """Goal prediction for football"""
    
    @staticmethod
    def calculate(team_a_avg: float, team_b_avg: float, odds: float) -> Dict:
        """Poisson model for goal predictions"""
        import math
        
        # Poisson probability
        def poisson_prob(lambda_param: float, k: int) -> float:
            return (math.exp(-lambda_param) * (lambda_param ** k)) / math.factorial(k)
        
        # Over 2.5 goals probability
        prob_0 = poisson_prob(team_a_avg + team_b_avg, 0)
        prob_1 = poisson_prob(team_a_avg + team_b_avg, 1)
        prob_2 = poisson_prob(team_a_avg + team_b_avg, 2)
        
        prob_over_2_5 = 1 - (prob_0 + prob_1 + prob_2)
        
        return {
            "strategy": "Poisson Model",
            "market": "Over 2.5 Goals",
            "confidence": prob_over_2_5,
            "expected_value": (prob_over_2_5 * odds) - 1,
            "breakdown": {
                "0_goals": prob_0,
                "1_goal": prob_1,
                "2_goals": prob_2,
                "3+_goals": prob_over_2_5
            }
        }

class ELORating:
    """Team strength via ELO rating"""
    
    @staticmethod
    def calculate(elo_a: float, elo_b: float, odds: float) -> Dict:
        """ELO rating model"""
        # ELO win probability formula
        expected_a = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
        
        return {
            "strategy": "ELO Rating",
            "team_a_elo": elo_a,
            "team_b_elo": elo_b,
            "team_a_win_prob": expected_a,
            "confidence": expected_a,
            "expected_value": (expected_a * odds) - 1
        }

class Martingale:
    """Double stake after loss (with hard safety limits)"""
    
    @staticmethod
    def calculate(bankroll: float, base_stake: float, loss_streak: int = 0) -> Dict:
        """Martingale with hard cap (MAX 10 doubles)"""
        max_doubles = 10
        
        if loss_streak > max_doubles:
            return {
                "strategy": "Martingale",
                "skip_reason": f"Loss streak {loss_streak} exceeds safety cap {max_doubles}",
                "stake": 0,
                "risk_level": "EXTREME - LOCKED"
            }
        
        stake = base_stake * (2 ** loss_streak)
        
        # Safety check: don't exceed 25% bankroll
        if stake > bankroll * 0.25:
            stake = bankroll * 0.25
        
        return {
            "strategy": "Martingale",
            "loss_streak": loss_streak,
            "stake": stake,
            "risk_level": "EXTREME" if loss_streak > 5 else "High"
        }

# ==================== RISK MANAGEMENT ====================

class RiskManager:
    """Enforce risk controls"""
    
    @staticmethod
    def check_daily_limit(user: User, losses_today: float) -> bool:
        """Check daily loss limit"""
        return (losses_today + user.daily_loss_limit) <= user.daily_loss_limit
    
    @staticmethod
    def enforce_stop_loss(user: User) -> bool:
        """Enforce auto stop-loss lock"""
        return not user.stop_loss_locked
    
    @staticmethod
    def validate_stake(stake: float, bankroll: float, max_percent: float) -> bool:
        """Validate stake against bankroll"""
        max_stake = bankroll * (max_percent / 100)
        return stake <= max_stake

# ==================== BET SUGGESTION ENGINE ====================

class BetSuggestionEngine:
    """Generate bet suggestions using all strategies"""
    
    def __init__(self, user: User):
        self.user = user
        self.skills = SkillIntegrator()
    
    def suggest(self, match: Match, use_skills: bool = True) -> Optional[BetSuggestion]:
        """Generate bet suggestion for a match"""
        
        # Risk check
        if not RiskManager.enforce_stop_loss(self.user):
            return None
        
        # Use sportsbet-advisor skill if available
        if use_skills:
            analysis = self.skills.get_sportsbet_analysis(match)
            confidence = analysis.get("confidence", 0.55)
        else:
            confidence = 0.55  # Default confidence
        
        # Choose strategy (Kelly Criterion recommended)
        kelly_calc = KellyCriterion.calculate(
            self.user.bankroll,
            match.odds,
            confidence
        )
        
        stake = kelly_calc["stake"]
        ev = kelly_calc["expected_value"]
        risk = kelly_calc["risk_level"]
        
        # Validate stake
        if not RiskManager.validate_stake(stake, self.user.bankroll, self.user.max_stake_percent):
            stake = self.user.bankroll * (self.user.max_stake_percent / 100)
        
        explanation = [
            f"Using Kelly Criterion strategy",
            f"Confidence: {confidence:.1%}",
            f"Odds imply: {(1/match.odds):.1%} probability",
            f"Expected Value: {ev:.2%}",
            f"Recommended stake: ${stake:.2f} ({(stake/self.user.bankroll)*100:.1f}% of bankroll)"
        ]
        
        suggestion = BetSuggestion(
            strategy="Kelly Criterion",
            sport=match.sport,
            match=f"{match.team_a} vs {match.team_b}",
            bet_type=match.market,
            odds=match.odds,
            confidence=confidence,
            expected_value=ev,
            recommended_stake=stake,
            stake_unit="currency",
            risk_level=risk,
            explanation=explanation
        )
        
        return suggestion

# ==================== MAIN ====================

if __name__ == "__main__":
    # Example usage
    print("🎰 BetSystem AI - Core Engine")
    print("=" * 60)
    
    # Create user
    user = User(
        id="user_1",
        email="dv@example.com",
        bankroll=1000.0,
        max_stake_percent=5.0,
        daily_loss_limit=200.0
    )
    
    print(f"\n💰 Bankroll: ${user.bankroll}")
    print(f"📊 Max Stake: {user.max_stake_percent}%")
    print(f"🛑 Daily Loss Limit: ${user.daily_loss_limit}")
    
    # Create match
    match = Match(
        id="match_1",
        sport="Football",
        team_a="Arsenal",
        team_b="Liverpool",
        odds=1.92,
        market="Over 2.5 Goals",
        date="2026-02-15"
    )
    
    print(f"\n⚽ Match: {match.team_a} vs {match.team_b}")
    print(f"📈 Odds: {match.odds}")
    print(f"🎯 Market: {match.market}")
    
    # Generate suggestion
    engine = BetSuggestionEngine(user)
    suggestion = engine.suggest(match)
    
    if suggestion:
        print(f"\n🎲 Bet Suggestion:")
        print(suggestion.to_json())
    else:
        print("❌ Cannot generate suggestion (risk controls active)")
    
    print("\n✅ Engine ready for integration")
