"""
Neutral Moderator - Evaluates Debates and Reaches Conclusions
Objectively assesses bull vs bear arguments and determines final position
"""

import os
from typing import Dict, Optional
import logging
import anthropic

from src.agents.debate_orchestrator import (
    DebateArgument,
    DebateConclusion,
    DebatePosition
)

logger = logging.getLogger(__name__)


class NeutralModerator:
    """
    Neutral Moderator evaluates debates objectively

    Responsibilities:
    - Assess strength of bull vs bear arguments
    - Score each side's case (0-100)
    - Determine final position (LONG/SHORT/NEUTRAL)
    - Calculate confidence level
    - Identify key arguments and risk factors
    - Generate debate summary
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Neutral Moderator

        Args:
            api_key: Anthropic API key (optional, uses env var if not provided)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or provided")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("NeutralModerator initialized")

    async def evaluate_debate(
        self,
        ticker: str,
        opening_arguments: Dict[str, DebateArgument],
        rebuttals: Dict[str, DebateArgument],
        closing_arguments: Dict[str, DebateArgument],
        market_data: Dict,
        fundamental_data: Dict,
        technical_data: Dict,
        alternative_data: Dict = None
    ) -> DebateConclusion:
        """
        Evaluate complete debate and reach conclusion

        Args:
            ticker: Stock ticker symbol
            opening_arguments: Dict with 'bull' and 'bear' opening arguments
            rebuttals: Dict with 'bull' and 'bear' rebuttals
            closing_arguments: Dict with 'bull' and 'bear' closing arguments
            market_data: Market data context
            fundamental_data: Fundamental data context
            technical_data: Technical data context
            alternative_data: Alternative data context (optional)

        Returns:
            DebateConclusion with final position and confidence
        """
        logger.info(f"NeutralModerator evaluating debate for {ticker}")

        prompt = self._build_evaluation_prompt(
            ticker,
            opening_arguments,
            rebuttals,
            closing_arguments,
            market_data,
            fundamental_data,
            technical_data,
            alternative_data
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            evaluation_text = response.content[0].text

            # Parse evaluation into DebateConclusion
            conclusion = self._parse_evaluation(ticker, evaluation_text)

            logger.info(f"Debate conclusion for {ticker}: {conclusion.final_position.value} ({conclusion.confidence:.1f}% confidence)")

            return conclusion

        except Exception as e:
            logger.error(f"Error evaluating debate for {ticker}: {e}")
            return self._create_fallback_conclusion(ticker)

    def _build_evaluation_prompt(
        self,
        ticker: str,
        opening_arguments: Dict[str, DebateArgument],
        rebuttals: Dict[str, DebateArgument],
        closing_arguments: Dict[str, DebateArgument],
        market_data: Dict,
        fundamental_data: Dict,
        technical_data: Dict,
        alternative_data: Dict = None
    ) -> str:
        """Build prompt for debate evaluation"""

        prompt = f"""You are a Neutral Moderator evaluating a structured debate about {ticker}.

DEBATE TRANSCRIPT:

ROUND 1 - OPENING ARGUMENTS:
Bull: {opening_arguments['bull'].argument}
Bear: {opening_arguments['bear'].argument}

ROUND 2 - REBUTTALS:
Bull: {rebuttals['bull'].argument}
Bear: {rebuttals['bear'].argument}

ROUND 3 - CLOSING ARGUMENTS:
Bull: {closing_arguments['bull'].argument}
Bear: {closing_arguments['bear'].argument}

OBJECTIVE DATA CONTEXT:
Market Data: {self._format_dict(market_data)}
Fundamental Data: {self._format_dict(fundamental_data)}
Technical Data: {self._format_dict(technical_data)}
Alternative Data: {self._format_dict(alternative_data or {})}

As a neutral moderator, evaluate this debate and provide your conclusion in this EXACT format:

FINAL_POSITION: [LONG or SHORT or NEUTRAL]
CONFIDENCE: [0-100]
BULL_SCORE: [0-100]
BEAR_SCORE: [0-100]

KEY_ARGUMENTS:
- [List 3-5 most compelling arguments from both sides]
- [Each on a new line]

RISK_FACTORS:
- [List 3-5 key risks regardless of position]
- [Each on a new line]

DEBATE_SUMMARY:
[2-3 sentences summarizing the debate and your reasoning for the final position]

Guidelines for evaluation:
1. Score each side based on argument quality, data citations, and logic
2. LONG if bull score significantly higher (>15 points) and confidence >60%
3. SHORT if bear score significantly higher (>15 points) and confidence >60%
4. NEUTRAL if scores close or confidence low
5. Confidence reflects certainty based on data quality and argument strength
6. Be objective - don't favor either side based on market sentiment

Provide your evaluation now:"""

        return prompt

    def _parse_evaluation(self, ticker: str, evaluation_text: str) -> DebateConclusion:
        """
        Parse evaluation text into DebateConclusion object

        Args:
            ticker: Stock ticker
            evaluation_text: Raw evaluation text from Claude

        Returns:
            DebateConclusion object
        """
        import re

        # Extract final position
        position_match = re.search(r'FINAL_POSITION:\s*(LONG|SHORT|NEUTRAL)', evaluation_text, re.IGNORECASE)
        if position_match:
            position_str = position_match.group(1).upper()
            final_position = DebatePosition[position_str]
        else:
            final_position = DebatePosition.NEUTRAL

        # Extract confidence
        confidence_match = re.search(r'CONFIDENCE:\s*(\d+)', evaluation_text)
        confidence = float(confidence_match.group(1)) if confidence_match else 50.0

        # Extract bull score
        bull_score_match = re.search(r'BULL_SCORE:\s*(\d+)', evaluation_text)
        bull_score = float(bull_score_match.group(1)) if bull_score_match else 50.0

        # Extract bear score
        bear_score_match = re.search(r'BEAR_SCORE:\s*(\d+)', evaluation_text)
        bear_score = float(bear_score_match.group(1)) if bear_score_match else 50.0

        # Extract key arguments
        key_args_section = re.search(r'KEY_ARGUMENTS:(.*?)(?:RISK_FACTORS:|$)', evaluation_text, re.DOTALL)
        key_arguments = []
        if key_args_section:
            lines = key_args_section.group(1).strip().split('\n')
            key_arguments = [line.strip('- ').strip() for line in lines if line.strip() and line.strip().startswith('-')]

        # Extract risk factors
        risk_section = re.search(r'RISK_FACTORS:(.*?)(?:DEBATE_SUMMARY:|$)', evaluation_text, re.DOTALL)
        risk_factors = []
        if risk_section:
            lines = risk_section.group(1).strip().split('\n')
            risk_factors = [line.strip('- ').strip() for line in lines if line.strip() and line.strip().startswith('-')]

        # Extract debate summary
        summary_match = re.search(r'DEBATE_SUMMARY:(.*?)$', evaluation_text, re.DOTALL)
        debate_summary = summary_match.group(1).strip() if summary_match else "Debate evaluation completed."

        return DebateConclusion(
            ticker=ticker,
            final_position=final_position,
            confidence=confidence,
            bull_score=bull_score,
            bear_score=bear_score,
            key_arguments=key_arguments or [f"Bull score: {bull_score:.1f}, Bear score: {bear_score:.1f}"],
            risk_factors=risk_factors or ["Standard market risks apply"],
            debate_summary=debate_summary
        )

    def _format_dict(self, data: Dict) -> str:
        """Format dictionary for prompt inclusion"""
        if not data:
            return "No data available"

        lines = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")

        return ", ".join(lines)

    def _create_fallback_conclusion(self, ticker: str) -> DebateConclusion:
        """Create fallback conclusion when evaluation fails"""
        return DebateConclusion(
            ticker=ticker,
            final_position=DebatePosition.NEUTRAL,
            confidence=0.0,
            bull_score=50.0,
            bear_score=50.0,
            key_arguments=["Unable to evaluate debate due to technical issues"],
            risk_factors=["Analysis incomplete"],
            debate_summary=f"Debate evaluation for {ticker} encountered an error"
        )

    def calculate_position_from_scores(
        self,
        bull_score: float,
        bear_score: float,
        min_score_difference: float = 15.0,
        min_confidence: float = 60.0
    ) -> DebatePosition:
        """
        Calculate position based on bull vs bear scores

        Args:
            bull_score: Bull case score (0-100)
            bear_score: Bear case score (0-100)
            min_score_difference: Minimum score difference to take a position
            min_confidence: Minimum confidence to take a position

        Returns:
            DebatePosition (LONG/SHORT/NEUTRAL)
        """
        score_diff = abs(bull_score - bear_score)

        if score_diff < min_score_difference:
            return DebatePosition.NEUTRAL

        # Calculate confidence based on winning score and margin
        winning_score = max(bull_score, bear_score)
        if winning_score < min_confidence:
            return DebatePosition.NEUTRAL

        if bull_score > bear_score:
            return DebatePosition.LONG
        else:
            return DebatePosition.SHORT

    def calculate_confidence(
        self,
        bull_score: float,
        bear_score: float,
        data_quality_score: float = 80.0
    ) -> float:
        """
        Calculate confidence level based on scores and data quality

        Args:
            bull_score: Bull case score (0-100)
            bear_score: Bear case score (0-100)
            data_quality_score: Quality of underlying data (0-100)

        Returns:
            Confidence level (0-100)
        """
        # Winning score
        winning_score = max(bull_score, bear_score)

        # Score margin (larger margin = more confidence)
        score_margin = abs(bull_score - bear_score)

        # Confidence calculation: weighted average
        confidence = (
            winning_score * 0.5 +
            score_margin * 0.3 +
            data_quality_score * 0.2
        )

        return min(100.0, max(0.0, confidence))
