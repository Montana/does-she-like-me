#!/usr/bin/env python3
"""
Generate sample message data for testing the analyzer
"""

import json
from datetime import datetime, timedelta
import random


def generate_sample_conversation(interest_level='high'):
    """
    Generate sample conversation data
    interest_level: 'high', 'medium', or 'low'
    """
    messages = []
    start_date = datetime.now() - timedelta(days=30)

    your_name = "You"
    their_name = "Sarah"

    # Configure behavior based on interest level
    if interest_level == 'high':
        # High interest: quick responses, initiates often, enthusiastic
        response_time_range = (1, 15)  # minutes
        their_initiation_prob = 0.5
        emoji_prob = 0.6
        question_prob = 0.3
        enthusiasm_markers = ['!', 'haha', 'lol', '😊', '😄', '💕', '❤️']
        their_msg_length = (20, 100)
        messages_per_day = 15
    elif interest_level == 'medium':
        # Medium interest: moderate responses
        response_time_range = (15, 90)
        their_initiation_prob = 0.35
        emoji_prob = 0.3
        question_prob = 0.15
        enthusiasm_markers = ['!', 'haha', '😊']
        their_msg_length = (10, 60)
        messages_per_day = 8
    else:  # low
        # Low interest: slow responses, rarely initiates
        response_time_range = (60, 300)
        their_initiation_prob = 0.15
        emoji_prob = 0.1
        question_prob = 0.05
        enthusiasm_markers = ['.']
        their_msg_length = (5, 30)
        messages_per_day = 4

    sample_your_messages = [
        "Hey! How's your day going?",
        "Did you see that new show everyone's talking about?",
        "Want to grab coffee this weekend?",
        "That's so cool!",
        "Haha yeah exactly",
        "What are you up to later?",
        "I was thinking about what you said earlier",
        "How was work today?",
        "Have you been to that new restaurant downtown?",
        "I saw something that reminded me of you today"
    ]

    sample_their_messages_high = [
        "Hey! It's been great! How about yours? 😊",
        "Yes!! I loved it! What did you think?",
        "I'd love to! What time works for you?",
        "Aww thank you! That's so sweet ❤️",
        "Haha right?? 😄",
        "Just relaxing! Want to video chat?",
        "Really? Tell me more!",
        "It was good! Busy but productive. How was yours? 💕",
        "No but I've been dying to try it! We should go together!",
        "That's adorable! What was it? 😊"
    ]

    sample_their_messages_medium = [
        "Pretty good, just busy",
        "Yeah it was alright",
        "Maybe, I'll check my schedule",
        "Thanks!",
        "Lol yeah",
        "Not much, probably just gonna chill",
        "Oh nice",
        "It was fine, kinda tired",
        "Nope, heard it's good though",
        "Haha cool"
    ]

    sample_their_messages_low = [
        "ok",
        "yeah",
        "idk maybe",
        "k",
        "lol",
        "nm",
        "cool",
        "yeah sure",
        "nah",
        "busy rn"
    ]

    if interest_level == 'high':
        their_messages = sample_their_messages_high
    elif interest_level == 'medium':
        their_messages = sample_their_messages_medium
    else:
        their_messages = sample_their_messages_low

    current_time = start_date

    for day in range(30):
        day_start = start_date + timedelta(days=day)

        # Random start time (afternoon/evening)
        current_time = day_start + timedelta(hours=random.randint(14, 20), minutes=random.randint(0, 59))

        daily_messages = random.randint(max(1, messages_per_day - 3), messages_per_day + 3)

        # Decide who starts conversation
        you_start = random.random() > their_initiation_prob

        for i in range(daily_messages):
            if i == 0:
                sender = your_name if you_start else their_name
            else:
                # Alternate mostly, but allow some back-to-back
                last_sender = messages[-1]['sender']
                if random.random() < 0.8:  # 80% alternate
                    sender = their_name if last_sender == your_name else your_name
                else:
                    sender = last_sender

            # Select message
            if sender == your_name:
                text = random.choice(sample_your_messages)
            else:
                text = random.choice(their_messages)

                # Add emojis sometimes
                if random.random() < emoji_prob:
                    text += " " + random.choice(enthusiasm_markers)

                # Add questions sometimes
                if random.random() < question_prob and '?' not in text:
                    text += " What about you?"

            messages.append({
                'text': text,
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'sender': sender
            })

            # Update time
            if sender == their_name and len(messages) > 1 and messages[-2]['sender'] == your_name:
                # They're responding to you
                response_delay = random.randint(*response_time_range)
            else:
                # Your response or continuing
                response_delay = random.randint(2, 30)

            current_time += timedelta(minutes=response_delay)

    return messages


def main():
    """Generate sample data files"""

    print("Generating sample conversation data...\n")

    # Generate high interest example
    print("Creating high interest sample (sample_messages_high.json)...")
    high_interest = generate_sample_conversation('high')
    with open('sample_messages_high.json', 'w') as f:
        json.dump(high_interest, f, indent=2)
    print(f"  ✓ Generated {len(high_interest)} messages")

    # Generate medium interest example
    print("Creating medium interest sample (sample_messages_medium.json)...")
    medium_interest = generate_sample_conversation('medium')
    with open('sample_messages_medium.json', 'w') as f:
        json.dump(medium_interest, f, indent=2)
    print(f"  ✓ Generated {len(medium_interest)} messages")

    # Generate low interest example
    print("Creating low interest sample (sample_messages_low.json)...")
    low_interest = generate_sample_conversation('low')
    with open('sample_messages_low.json', 'w') as f:
        json.dump(low_interest, f, indent=2)
    print(f"  ✓ Generated {len(low_interest)} messages")

    # Create default sample
    with open('sample_messages.json', 'w') as f:
        json.dump(high_interest, f, indent=2)

    print("\n✅ Sample data generated successfully!")
    print("\nTry analyzing with:")
    print("  python app.py sample_messages_high.json Sarah")
    print("  python app.py sample_messages_medium.json Sarah")
    print("  python app.py sample_messages_low.json Sarah")


if __name__ == "__main__":
    main()
