"""
Message parsers for different platforms
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any
import os


class MessageParser:
    """Base class for message parsers"""

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse messages from file"""
        raise NotImplementedError


class FacebookMessengerParser(MessageParser):
    """Parser for Facebook/Instagram Messenger JSON exports"""

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Facebook Messenger JSON export
        To export: Settings > Your info > Download your info > Messages (JSON format)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages = []

        # Facebook exports have 'messages' key
        if 'messages' in data:
            for msg in data['messages']:
                if 'content' in msg:  # Text messages only
                    messages.append({
                        'text': msg['content'],
                        'timestamp': datetime.fromtimestamp(msg['timestamp_ms'] / 1000),
                        'sender': msg['sender_name']
                    })

        return messages


class InstagramMessengerParser(MessageParser):
    """Parser for Instagram Messenger JSON exports"""

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse Instagram Messenger JSON export
        Similar format to Facebook Messenger
        """
        # Instagram uses same format as Facebook
        return FacebookMessengerParser().parse(file_path)


class iMessageParser(MessageParser):
    """Parser for iMessage exports"""

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse iMessage export (requires third-party export or manual formatting)
        Expected format: CSV or JSON with columns: text, timestamp, sender
        """
        messages = []

        # Try JSON first
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for msg in data:
                    messages.append({
                        'text': msg.get('text', ''),
                        'timestamp': self._parse_timestamp(msg.get('timestamp')),
                        'sender': msg.get('sender', msg.get('from', 'Unknown'))
                    })

        # Try CSV
        elif file_path.endswith('.csv'):
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    messages.append({
                        'text': row.get('text', row.get('message', '')),
                        'timestamp': self._parse_timestamp(row.get('timestamp', row.get('date'))),
                        'sender': row.get('sender', row.get('from', 'Unknown'))
                    })

        return messages

    def _parse_timestamp(self, ts_str: str) -> datetime:
        """Parse various timestamp formats"""
        if isinstance(ts_str, datetime):
            return ts_str

        # Try common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%m/%d/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(ts_str, fmt)
            except (ValueError, TypeError):
                continue

        # Default to now if parsing fails
        return datetime.now()


class WhatsAppParser(MessageParser):
    """Parser for WhatsApp chat exports"""

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse WhatsApp chat export (.txt format)
        Export: Chat > More > Export Chat
        """
        messages = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # WhatsApp format: [DD/MM/YYYY, HH:MM:SS] Sender: Message
                # or: DD/MM/YYYY, HH:MM - Sender: Message
                match = re.match(r'\[?(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)\]?\s+-?\s*([^:]+):\s*(.+)', line)

                if match:
                    date_str, time_str, sender, text = match.groups()

                    # Parse timestamp
                    try:
                        if len(time_str.split(':')) == 2:
                            timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
                        else:
                            timestamp = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
                    except ValueError:
                        try:
                            timestamp = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M")
                        except ValueError:
                            continue

                    messages.append({
                        'text': text.strip(),
                        'timestamp': timestamp,
                        'sender': sender.strip()
                    })

        return messages


class GenericJSONParser(MessageParser):
    """Parser for generic JSON message format"""

    def parse(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse generic JSON format
        Expected: [{'text': str, 'timestamp': str, 'sender': str}, ...]
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages = []
        for msg in data:
            messages.append({
                'text': msg.get('text', msg.get('message', msg.get('content', ''))),
                'timestamp': self._parse_timestamp(msg.get('timestamp', msg.get('date', msg.get('time')))),
                'sender': msg.get('sender', msg.get('from', msg.get('author', 'Unknown')))
            })

        return messages

    def _parse_timestamp(self, ts) -> datetime:
        """Parse timestamp"""
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(ts)

        # Try parsing as string
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(str(ts), fmt)
            except (ValueError, TypeError):
                continue

        return datetime.now()


def get_parser(file_path: str, platform: str = None) -> MessageParser:
    """Get appropriate parser based on file or platform"""

    if platform:
        platform = platform.lower()
        if 'facebook' in platform or 'messenger' in platform:
            return FacebookMessengerParser()
        elif 'instagram' in platform or 'ig' in platform:
            return InstagramMessengerParser()
        elif 'imessage' in platform or 'apple' in platform:
            return iMessageParser()
        elif 'whatsapp' in platform:
            return WhatsAppParser()

    # Auto-detect from file
    if file_path.endswith('.txt'):
        return WhatsAppParser()
    elif file_path.endswith('.json'):
        # Try to peek at structure
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'messages' in data:
                    return FacebookMessengerParser()
        except:
            pass
        return GenericJSONParser()
    elif file_path.endswith('.csv'):
        return iMessageParser()

    return GenericJSONParser()
