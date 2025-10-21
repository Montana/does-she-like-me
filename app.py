#!/usr/bin/env python3
"""
Love Interest Analyzer - Main Application
Analyzes messaging patterns to gauge interest level
"""

import sys
import os
from message_analyzer import MessageAnalyzer, format_results
from message_parsers import get_parser


def print_banner():
    """Print application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           💬 LOVE INTEREST ANALYZER 💬                   ║
║                                                           ║
║     Using ML/AI to analyze messaging patterns            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """Print usage instructions"""
    help_text = """
USAGE:
    python app.py <message_file> <their_name> [platform]

ARGUMENTS:
    message_file    Path to your exported message file
    their_name      The name/identifier of the person in the messages
    platform        (Optional) Platform: facebook, instagram, imessage, whatsapp

SUPPORTED FORMATS:
    - Facebook Messenger (JSON export)
    - Instagram Messenger (JSON export)
    - iMessage (JSON or CSV export)
    - WhatsApp (TXT export)
    - Generic JSON format

EXPORT INSTRUCTIONS:

Facebook/Instagram Messenger:
    1. Settings > Your Facebook Information > Download Your Information
    2. Select "Messages" only
    3. Format: JSON
    4. Download and extract the file

WhatsApp:
    1. Open chat with the person
    2. Tap chat name > More > Export Chat
    3. Choose "Without Media"
    4. Save the .txt file

iMessage:
    1. Use a third-party export tool or create JSON/CSV with:
       - text: message content
       - timestamp: message date/time
       - sender: who sent it

Generic JSON format:
    [
        {
            "text": "message content",
            "timestamp": "2024-01-01 12:00:00",
            "sender": "Name"
        },
        ...
    ]

EXAMPLES:
    python app.py messages.json "Sarah" facebook
    python app.py chat.txt "John" whatsapp
    python app.py export.json "Alex"

PRIVACY NOTE:
    All analysis happens locally on your computer.
    No data is sent to external servers.
"""
    print(help_text)


def main():
    """Main application entry point"""
    print_banner()

    # Check arguments
    if len(sys.argv) < 3:
        print("ERROR: Not enough arguments provided\n")
        print_help()
        sys.exit(1)

    if sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        sys.exit(0)

    file_path = sys.argv[1]
    target_sender = sys.argv[2]
    platform = sys.argv[3] if len(sys.argv) > 3 else None

    # Validate file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)

    print(f"\n📂 Loading messages from: {file_path}")
    print(f"👤 Analyzing interest from: {target_sender}")
    if platform:
        print(f"📱 Platform: {platform}")

    try:
        # Parse messages
        parser = get_parser(file_path, platform)
        messages = parser.parse(file_path)

        if not messages:
            print("\n❌ No messages found in file. Please check the format.")
            sys.exit(1)

        print(f"✅ Loaded {len(messages)} messages")

        # Analyze
        print("\n🔍 Analyzing messaging patterns...")
        print("   - Response times")
        print("   - Message lengths")
        print("   - Emoji usage")
        print("   - Question asking")
        print("   - Conversation initiation")
        print("   - Enthusiasm levels")
        print("   - Consistency")
        print("   - Reciprocity")

        analyzer = MessageAnalyzer()
        df = analyzer.load_messages(messages)
        results = analyzer.calculate_overall_interest(df, target_sender)

        # Display results
        print(format_results(results))

        # Additional insights
        print("💡 INSIGHTS:")
        signal_breakdown = results['signal_breakdown']

        if signal_breakdown['response_time'] < 50:
            print("   - They take a while to respond. Might be busy or not prioritizing")
        elif signal_breakdown['response_time'] > 80:
            print("   - Quick responses! They're engaged and interested")

        if signal_breakdown['conversation_initiation'] < 40:
            print("   - They rarely start conversations. You're doing most of the work")
        elif signal_breakdown['conversation_initiation'] > 70:
            print("   - They regularly initiate conversations. Great sign!")

        if signal_breakdown['enthusiasm'] < 50:
            print("   - Messages lack enthusiasm. Keep an eye on this")
        elif signal_breakdown['enthusiasm'] > 75:
            print("   - High enthusiasm in messages! They're excited to talk")

        if signal_breakdown['reciprocity'] < 60:
            print("   - Imbalanced conversation. One person is putting in more effort")

        if signal_breakdown['question_asking'] < 40:
            print("   - They don't ask many questions about you. Less personal interest")
        elif signal_breakdown['question_asking'] > 70:
            print("   - Asks lots of questions. Wants to know more about you!")

        print("\n" + "="*60)
        print("Remember: This is just data analysis. Real relationships are complex!")
        print("Use this as one data point, not the whole story.")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("\nIf you're having trouble, try:")
        print("  - Check the file format matches your platform")
        print("  - Ensure the sender name exactly matches what's in the file")
        print("  - Run with --help for more information")
        sys.exit(1)


if __name__ == "__main__":
    main()
