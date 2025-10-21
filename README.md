# Does She Like Me?

DSLM is an ML/AI-powered tool that analyzes messaging patterns from various platforms (Facebook Messenger, Instagram, iMessage, WhatsApp, etc.) to determine the likelihood that someone is interested in you.

## Features

- **Multi-Platform Support**: Works with Facebook Messenger, Instagram, iMessage, WhatsApp, and generic message exports
- **8 Engagement Signals**: Analyzes response time, message length, emoji usage, question asking, conversation initiation, enthusiasm, consistency, and reciprocity
- **Weighted Scoring**: Uses a sophisticated algorithm to weigh different signals appropriately
- **Privacy-Focused**: All analysis happens locally on your machine - no data is sent anywhere

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Command

```bash
python app.py <message_file> <their_name> [platform]
```

### Examples

```bash
# Facebook Messenger
python app.py messages.json "Sarah" facebook

# WhatsApp
python app.py chat.txt "John" whatsapp

# iMessage
python app.py imessage_export.json "Alex" imessage

# Auto-detect format
python app.py messages.json "Casey"
```

## Exporting Your Messages

### Facebook/Instagram Messenger

1. Go to Settings > Your Facebook Information > Download Your Information
2. Select only "Messages"
3. Format: JSON
4. Quality: High
5. Download and extract the ZIP file
6. Find the conversation JSON file in the messages folder

### WhatsApp

1. Open the chat with the person
2. Tap their name at the top
3. Tap "More" > "Export Chat"
4. Choose "Without Media"
5. Save the .txt file

### iMessage

iMessage requires third-party export tools or manual formatting. Create a JSON file with this format:

```json
[
    {
        "text": "Hey, how are you?",
        "timestamp": "2024-01-01 12:00:00",
        "sender": "You"
    },
    {
        "text": "I'm great! How about you?",
        "timestamp": "2024-01-01 12:02:00",
        "sender": "Them"
    }
]
```

## What It Analyzes

### Response Time (18% weight)
How quickly they respond to your messages. Faster = more interested.

### Conversation Initiation (15% weight)
How often they start new conversations. Regular initiation shows active interest.

### Enthusiasm (15% weight)
Sentiment analysis and enthusiasm markers (exclamation points, "haha", "love", etc.)

### Reciprocity (13% weight)
Balance in message exchange. Healthy relationships have roughly equal back-and-forth.

### Message Length (12% weight)
Compares their message length to yours. Detailed responses show investment.

### Question Asking (10% weight)
How many questions they ask about you. Shows genuine interest in learning more.

### Emoji Usage (9% weight)
Frequency and type of emojis. Positive emojis indicate warmth and affection.

### Consistency (8% weight)
How consistent their messaging patterns are over time. Regular engagement is positive.

## Score Interpretation

- **80-100%**: Strong interest - Very positive signs
- **65-79%**: Good interest - Looking promising
- **50-64%**: Moderate interest - Could go either way
- **35-49%**: Low interest - Not looking great
- **0-34%**: Minimal interest - Might want to move on

## Privacy & Ethics

- **All processing is local**: Your messages never leave your computer
- **No external API calls**: No data is sent to any server
- **Use responsibly**: This tool provides data-driven insights but remember:
  - Real relationships are complex and nuanced
  - Use this as ONE data point, not the complete picture
  - Respect people's privacy - only analyze your own conversations
  - Don't make major decisions based solely on this analysis

## Testing

Try it with sample data:

```bash
python sample_data_generator.py
python app.py sample_messages.json "Sarah"
```

## Technical Details

- **Language**: Python 3.8+
- **ML/NLP**: TextBlob for sentiment analysis
- **Data Processing**: Pandas, NumPy
- **Pattern Recognition**: Custom algorithms analyzing temporal, linguistic, and behavioral patterns

## Limitations

- Requires sufficient message history (at least 20-30 messages for accurate results)
- Context matters: Some people are naturally less expressive in text
- Cultural differences in communication styles aren't accounted for
- Can't detect sarcasm, inside jokes, or relationship context
- Works best with recent, consistent conversations

## Contributing

Found a bug or have a suggestion? Feel free to open an issue or submit a pull request!

## License

MIT License - feel free to use and modify as needed

## Disclaimer

This tool is for entertainment and informational purposes. Human relationships are complex and can't be reduced to a percentage. Use your judgment, communicate openly, and don't let an algorithm make relationship decisions for you.
