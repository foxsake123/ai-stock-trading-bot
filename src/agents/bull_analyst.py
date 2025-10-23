"""
Bull Analyst - Generates Bullish Arguments in Debates
Constructs data-backed bull cases for stocks with specific citations
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import logging
import anthropic

from src.agents.debate_orchestrator import DebateArgument, DebateRound

logger = logging.getLogger(__name__)


class BullAnalyst:
    """
    Bull Analyst generates bullish arguments in structured debates

    Focuses on:
    - Growth potential and catalysts
    - Positive fundamentals (revenue growth, profitability)
    - Technical strength (uptrends, momentum)
    - Market sentiment and positioning
    - Competitive advantages
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Bull Analyst

        Args:
            api_key: Anthropic API key (optional, uses env var if not provided)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or provided")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info("BullAnalyst initialized")

    async def generate_opening_argument(self, debate_context: Dict) -> DebateArgument:
        """
        Generate opening bullish argument

        Args:
            debate_context: Dictionary with ticker, market_data, fundamental_data, technical_data

        Returns:
            DebateArgument with 100-200 word opening statement
        """
        ticker = debate_context['ticker']
        logger.info(f"BullAnalyst generating opening argument for {ticker}")

        prompt = self._build_opening_prompt(debate_context)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            argument_text = response.content[0].text
            citations = self._extract_citations(argument_text)

            return DebateArgument(
                round_type=DebateRound.OPENING,
                side='bull',
                argument=argument_text,
                data_citations=citations
            )

        except Exception as e:
            logger.error(f"Error generating bull opening argument for {ticker}: {e}")
            return self._create_fallback_argument(DebateRound.OPENING, ticker)

    async def generate_rebuttal(
        self,
        debate_context: Dict,
        opponent_argument: DebateArgument
    ) -> DebateArgument:
        """
        Generate rebuttal to bear's opening argument

        Args:
            debate_context: Dictionary with ticker and data
            opponent_argument: Bear's opening argument to rebut

        Returns:
            DebateArgument with rebuttal (100-200 words)
        """
        ticker = debate_context['ticker']
        logger.info(f"BullAnalyst generating rebuttal for {ticker}")

        prompt = self._build_rebuttal_prompt(debate_context, opponent_argument)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            argument_text = response.content[0].text
            citations = self._extract_citations(argument_text)

            return DebateArgument(
                round_type=DebateRound.REBUTTAL,
                side='bull',
                argument=argument_text,
                data_citations=citations
            )

        except Exception as e:
            logger.error(f"Error generating bull rebuttal for {ticker}: {e}")
            return self._create_fallback_argument(DebateRound.REBUTTAL, ticker)

    async def generate_closing_argument(
        self,
        debate_context: Dict,
        previous_arguments: List[DebateArgument],
        opponent_arguments: List[DebateArgument]
    ) -> DebateArgument:
        """
        Generate closing bullish argument

        Args:
            debate_context: Dictionary with ticker and data
            previous_arguments: This side's previous arguments
            opponent_arguments: Opponent's arguments

        Returns:
            DebateArgument with closing statement (100-200 words)
        """
        ticker = debate_context['ticker']
        logger.info(f"BullAnalyst generating closing argument for {ticker}")

        prompt = self._build_closing_prompt(
            debate_context,
            previous_arguments,
            opponent_arguments
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            argument_text = response.content[0].text
            citations = self._extract_citations(argument_text)

            return DebateArgument(
                round_type=DebateRound.CLOSING,
                side='bull',
                argument=argument_text,
                data_citations=citations
            )

        except Exception as e:
            logger.error(f"Error generating bull closing argument for {ticker}: {e}")
            return self._create_fallback_argument(DebateRound.CLOSING, ticker)

    def _build_opening_prompt(self, debate_context: Dict) -> str:
        """Build prompt for opening argument"""
        ticker = debate_context['ticker']
        market_data = debate_context.get('market_data', {})
        fundamental_data = debate_context.get('fundamental_data', {})
        technical_data = debate_context.get('technical_data', {})
        alternative_data = debate_context.get('alternative_data', {})

        prompt = f"""You are a professional Bull Analyst in a structured debate about {ticker}.

Generate a compelling BULLISH opening argument (100-200 words) based on the following data:

MARKET DATA:
{self._format_dict(market_data)}

FUNDAMENTAL DATA:
{self._format_dict(fundamental_data)}

TECHNICAL DATA:
{self._format_dict(technical_data)}

ALTERNATIVE DATA:
{self._format_dict(alternative_data)}

Your argument should:
1. Present the strongest bullish case with specific data citations
2. Focus on growth catalysts, competitive advantages, and positive trends
3. Use concrete numbers and metrics (e.g., "Revenue grew 25% YoY to $X")
4. Be 100-200 words
5. Include data citations in [brackets] like [P/E: 18.5x]

Write your opening argument now:"""

        return prompt

    def _build_rebuttal_prompt(
        self,
        debate_context: Dict,
        opponent_argument: DebateArgument
    ) -> str:
        """Build prompt for rebuttal"""
        ticker = debate_context['ticker']

        prompt = f"""You are a professional Bull Analyst in a structured debate about {ticker}.

The Bear Analyst just presented this opening argument:
---
{opponent_argument.argument}
---

Generate a compelling rebuttal (100-200 words) that:
1. Directly addresses the bear's concerns
2. Provides counter-evidence with specific data citations
3. Highlights why the bearish view is incomplete or incorrect
4. Reinforces the bullish case with additional supporting data
5. Uses concrete numbers in [brackets] like [Debt/EBITDA: 2.1x, below industry avg 3.5x]

Write your rebuttal now:"""

        return prompt

    def _build_closing_prompt(
        self,
        debate_context: Dict,
        previous_arguments: List[DebateArgument],
        opponent_arguments: List[DebateArgument]
    ) -> str:
        """Build prompt for closing argument"""
        ticker = debate_context['ticker']

        prompt = f"""You are a professional Bull Analyst in a structured debate about {ticker}.

YOUR PREVIOUS ARGUMENTS:
Opening: {previous_arguments[0].argument if len(previous_arguments) > 0 else 'N/A'}
Rebuttal: {previous_arguments[1].argument if len(previous_arguments) > 1 else 'N/A'}

OPPONENT'S ARGUMENTS:
Opening: {opponent_arguments[0].argument if len(opponent_arguments) > 0 else 'N/A'}
Rebuttal: {opponent_arguments[1].argument if len(opponent_arguments) > 1 else 'N/A'}

Generate a powerful closing argument (100-200 words) that:
1. Summarizes your strongest 2-3 bullish points
2. Addresses any unresolved bearish concerns
3. Provides a clear investment thesis with risk/reward assessment
4. Uses specific data citations in [brackets]
5. Concludes with conviction about the long opportunity

Write your closing argument now:"""

        return prompt

    def _format_dict(self, data: Dict) -> str:
        """Format dictionary for prompt inclusion"""
        if not data:
            return "No data available"

        lines = []
        for key, value in data.items():
            lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def _extract_citations(self, argument_text: str) -> List[str]:
        """
        Extract data citations from argument text

        Looks for patterns like [P/E: 18.5x] or [Revenue: $100M, +25% YoY]

        Returns:
            List of citation strings
        """
        import re

        # Find all citations in [brackets]
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, argument_text)

        return matches if matches else []

    def _create_fallback_argument(
        self,
        round_type: DebateRound,
        ticker: str
    ) -> DebateArgument:
        """Create fallback argument when API call fails"""
        fallback_text = f"Unable to generate {round_type.value} argument for {ticker} due to technical issues."

        return DebateArgument(
            round_type=round_type,
            side='bull',
            argument=fallback_text,
            data_citations=[]
        )
