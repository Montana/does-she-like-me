"""
Message Interest Analyzer
Analyzes messaging patterns to gauge interest level
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from textblob import TextBlob
import emoji


class MessageAnalyzer:
    """Analyzes messaging patterns to determine engagement and interest level"""

    def __init__(self):
        self.engagement_signals = {
            'response_time': 0,
            'message_length': 0,
            'emoji_usage': 0,
            'question_asking': 0,
            'conversation_initiation': 0,
            'enthusiasm': 0,
            'consistency': 0,
            'reciprocity': 0
        }

    def load_messages(self, messages: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Load messages into a DataFrame
        Expected format: [{'text': str, 'timestamp': str/datetime, 'sender': str}, ...]
        """
        df = pd.DataFrame(messages)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        return df

    def analyze_response_time(self, df: pd.DataFrame, target_sender: str) -> float:
        """Analyze how quickly they respond to your messages (0-100 score)"""
        response_times = []

        for i in range(len(df) - 1):
            if df.iloc[i]['sender'] != target_sender and df.iloc[i + 1]['sender'] == target_sender:
                time_diff = (df.iloc[i + 1]['timestamp'] - df.iloc[i]['timestamp']).total_seconds() / 60
                response_times.append(time_diff)

        if not response_times:
            return 50.0

        avg_response = np.mean(response_times)

        # Faster responses = higher score
        # < 5 min = 100, 5-30 min = 80-100, 30-60 min = 60-80, 1-3 hr = 40-60, > 3 hr = lower
        if avg_response < 5:
            score = 100
        elif avg_response < 30:
            score = 100 - (avg_response - 5) * 0.8
        elif avg_response < 60:
            score = 80 - (avg_response - 30) * 0.67
        elif avg_response < 180:
            score = 60 - (avg_response - 60) * 0.17
        else:
            score = max(20, 40 - (avg_response - 180) / 60)

        return min(100, max(0, score))

    def analyze_message_length(self, df: pd.DataFrame, target_sender: str) -> float:
        """Analyze message length and detail (0-100 score)"""
        their_messages = df[df['sender'] == target_sender]['text']
        your_messages = df[df['sender'] != target_sender]['text']

        if len(their_messages) == 0:
            return 0.0

        their_avg_length = their_messages.str.len().mean()
        your_avg_length = your_messages.str.len().mean() if len(your_messages) > 0 else 50

        # Ratio of their length to your length
        ratio = their_avg_length / max(your_avg_length, 1)

        # Ideal is around 1.0 (equal effort), score decreases if much less
        if ratio >= 0.8:
            score = 100
        elif ratio >= 0.5:
            score = 70 + (ratio - 0.5) * 100
        else:
            score = max(30, ratio * 140)

        return min(100, score)

    def analyze_emoji_usage(self, df: pd.DataFrame, target_sender: str) -> float:
        """Analyze emoji usage as indicator of enthusiasm (0-100 score)"""
        their_messages = df[df['sender'] == target_sender]['text']

        if len(their_messages) == 0:
            return 0.0

        emoji_count = 0
        positive_emoji_count = 0

        positive_emojis = {'❤️', '💕', '💖', '😊', '😍', '🥰', '😘', '💗', '💓', '💝',
                          '😄', '😁', '🙂', '😉', '🥺', '✨', '💫', '⭐'}

        for msg in their_messages:
            emojis = emoji.emoji_list(msg)
            emoji_count += len(emojis)
            positive_emoji_count += sum(1 for e in emojis if e['emoji'] in positive_emojis)

        avg_emojis = emoji_count / len(their_messages)
        positive_ratio = positive_emoji_count / max(emoji_count, 1)

        # Base score on emoji frequency
        if avg_emojis >= 0.5:
            base_score = 90
        elif avg_emojis >= 0.3:
            base_score = 70
        elif avg_emojis >= 0.1:
            base_score = 50
        else:
            base_score = 30

        # Bonus for positive emojis
        bonus = positive_ratio * 20

        return min(100, base_score + bonus)

    def analyze_question_asking(self, df: pd.DataFrame, target_sender: str) -> float:
        """Analyze how many questions they ask (shows interest in you) (0-100 score)"""
        their_messages = df[df['sender'] == target_sender]['text']

        if len(their_messages) == 0:
            return 0.0

        question_count = sum(1 for msg in their_messages if '?' in msg)
        question_ratio = question_count / len(their_messages)

        # 20-40% questions is ideal (shows interest without interrogating)
        if 0.2 <= question_ratio <= 0.4:
            score = 100
        elif 0.1 <= question_ratio < 0.2:
            score = 50 + (question_ratio - 0.1) * 500
        elif 0.4 < question_ratio <= 0.6:
            score = 100 - (question_ratio - 0.4) * 100
        else:
            score = max(20, 60 * question_ratio)

        return min(100, score)

    def analyze_conversation_initiation(self, df: pd.DataFrame, target_sender: str) -> float:
        """Analyze how often they start conversations (0-100 score)"""
        if len(df) < 2:
            return 50.0

        # Find conversation breaks (> 4 hours between messages)
        df['time_gap'] = df['timestamp'].diff().dt.total_seconds() / 3600
        conversation_starts = df[df['time_gap'] > 4]

        if len(conversation_starts) == 0:
            return 50.0

        their_initiations = sum(conversation_starts['sender'] == target_sender)
        initiation_ratio = their_initiations / len(conversation_starts)

        # 40-60% is ideal (mutual interest)
        if 0.4 <= initiation_ratio <= 0.6:
            score = 100
        elif 0.3 <= initiation_ratio < 0.4:
            score = 70 + (initiation_ratio - 0.3) * 300
        elif 0.6 < initiation_ratio <= 0.7:
            score = 100 - (initiation_ratio - 0.6) * 100
        else:
            score = max(30, initiation_ratio * 150)

        return min(100, score)

    def analyze_enthusiasm(self, df: pd.DataFrame, target_sender: str) -> float:
        """Analyze enthusiasm through sentiment and expression (0-100 score)"""
        their_messages = df[df['sender'] == target_sender]['text']

        if len(their_messages) == 0:
            return 0.0

        sentiments = [TextBlob(str(msg)).sentiment.polarity for msg in their_messages]
        avg_sentiment = np.mean(sentiments)

        # Check for enthusiasm markers
        enthusiasm_markers = ['!', 'haha', 'lol', 'omg', 'wow', 'love', 'amazing', 'awesome']
        enthusiasm_count = sum(
            1 for msg in their_messages
            for marker in enthusiasm_markers
            if marker in str(msg).lower()
        )
        enthusiasm_ratio = enthusiasm_count / len(their_messages)

        # Sentiment score (0 to 1 mapped to 0 to 60)
        sentiment_score = (avg_sentiment + 1) / 2 * 60

        # Enthusiasm markers (0 to 40)
        enthusiasm_score = min(40, enthusiasm_ratio * 100)

        return sentiment_score + enthusiasm_score

    def analyze_consistency(self, df: pd.DataFrame, target_sender: str) -> float:
        """Analyze consistency of messaging over time (0-100 score)"""
        their_messages = df[df['sender'] == target_sender].copy()

        if len(their_messages) < 5:
            return 50.0

        # Calculate daily message counts
        their_messages['date'] = their_messages['timestamp'].dt.date
        daily_counts = their_messages.groupby('date').size()

        # Consistency = low variance in daily messaging
        if len(daily_counts) < 2:
            return 70.0

        cv = daily_counts.std() / daily_counts.mean()  # Coefficient of variation

        # Lower CV = more consistent = higher score
        if cv < 0.5:
            score = 100
        elif cv < 1.0:
            score = 100 - (cv - 0.5) * 60
        else:
            score = max(30, 70 - cv * 20)

        return score

    def analyze_reciprocity(self, df: pd.DataFrame, target_sender: str) -> float:
        """Analyze reciprocity in conversation (0-100 score)"""
        if len(df) < 2:
            return 50.0

        their_count = sum(df['sender'] == target_sender)
        your_count = len(df) - their_count

        if your_count == 0:
            return 100.0 if their_count > 0 else 0.0

        ratio = their_count / your_count

        # Ideal is 0.8 to 1.2 (roughly equal exchange)
        if 0.8 <= ratio <= 1.2:
            score = 100
        elif 0.5 <= ratio < 0.8:
            score = 60 + (ratio - 0.5) * 133
        elif 1.2 < ratio <= 1.5:
            score = 100 - (ratio - 1.2) * 50
        else:
            score = max(20, min(100, ratio * 70))

        return score

    def calculate_overall_interest(self, df: pd.DataFrame, target_sender: str) -> Dict[str, Any]:
        """Calculate overall interest percentage and detailed breakdown"""

        # Calculate all signals
        self.engagement_signals['response_time'] = self.analyze_response_time(df, target_sender)
        self.engagement_signals['message_length'] = self.analyze_message_length(df, target_sender)
        self.engagement_signals['emoji_usage'] = self.analyze_emoji_usage(df, target_sender)
        self.engagement_signals['question_asking'] = self.analyze_question_asking(df, target_sender)
        self.engagement_signals['conversation_initiation'] = self.analyze_conversation_initiation(df, target_sender)
        self.engagement_signals['enthusiasm'] = self.analyze_enthusiasm(df, target_sender)
        self.engagement_signals['consistency'] = self.analyze_consistency(df, target_sender)
        self.engagement_signals['reciprocity'] = self.analyze_reciprocity(df, target_sender)

        # Weighted average (some signals matter more)
        weights = {
            'response_time': 0.18,
            'conversation_initiation': 0.15,
            'enthusiasm': 0.15,
            'reciprocity': 0.13,
            'message_length': 0.12,
            'question_asking': 0.10,
            'emoji_usage': 0.09,
            'consistency': 0.08
        }

        overall_score = sum(
            self.engagement_signals[signal] * weights[signal]
            for signal in self.engagement_signals
        )

        # Interpret the score
        if overall_score >= 80:
            interpretation = "Strong interest - Very positive signs!"
        elif overall_score >= 65:
            interpretation = "Good interest - Looking promising"
        elif overall_score >= 50:
            interpretation = "Moderate interest - Could go either way"
        elif overall_score >= 35:
            interpretation = "Low interest - Not looking great"
        else:
            interpretation = "Minimal interest - Might want to move on"

        return {
            'overall_percentage': round(overall_score, 1),
            'interpretation': interpretation,
            'signal_breakdown': {k: round(v, 1) for k, v in self.engagement_signals.items()},
            'message_count': len(df),
            'their_message_count': sum(df['sender'] == target_sender),
            'your_message_count': len(df) - sum(df['sender'] == target_sender)
        }


def format_results(results: Dict[str, Any]) -> str:
    """Format results for display"""
    output = f"""
{'='*60}
INTEREST LEVEL ANALYSIS
{'='*60}

Overall Interest: {results['overall_percentage']}%
{results['interpretation']}

{'='*60}
DETAILED BREAKDOWN
{'='*60}

Response Time:              {results['signal_breakdown']['response_time']}%
Conversation Initiation:    {results['signal_breakdown']['conversation_initiation']}%
Enthusiasm:                 {results['signal_breakdown']['enthusiasm']}%
Reciprocity:                {results['signal_breakdown']['reciprocity']}%
Message Length:             {results['signal_breakdown']['message_length']}%
Question Asking:            {results['signal_breakdown']['question_asking']}%
Emoji Usage:                {results['signal_breakdown']['emoji_usage']}%
Consistency:                {results['signal_breakdown']['consistency']}%

{'='*60}
MESSAGE STATISTICS
{'='*60}

Total Messages:    {results['message_count']}
Their Messages:    {results['their_message_count']}
Your Messages:     {results['your_message_count']}

{'='*60}
"""
    return output
