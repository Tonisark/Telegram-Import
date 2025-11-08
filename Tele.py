import json
import argparse
import zipfile
from datetime import datetime

def convert_telegram_to_whatsapp(
    telegram_export_path: str,
    whatsapp_output_path: str,
    name_mapping: dict = None,
    include_media_placeholders: bool = True,
    include_replies: bool = True,
    include_service_messages: bool = True
):

    if name_mapping is None:
        name_mapping = {}
    
    # Load JSON
    try:
        with open(telegram_export_path, 'r', encoding='utf-8') as file:
            telegram_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON: {e}")
        return
    
    # Extract messages (handle single chat or multi-chat)
    if 'messages' in telegram_data:
        messages = telegram_data['messages']
        chat_title = telegram_data.get('chat', {}).get('title', 'Unknown Chat')
    elif 'chats' in telegram_data:
        messages = []
        for chat in telegram_data['chats'].get('list', []):
            messages.extend(chat.get('messages', []))
        chat_title = 'Multi-Chat Export'
    else:
        messages = []
        print("No messages found.")
        return
    
    # Sort messages by date
    messages.sort(key=lambda m: m.get('date', ''))
    
    # Open output
    with open(whatsapp_output_path, 'w', encoding='utf-8') as output_file:
        # No header by default for clean import
        
        for message in messages:
            date_str = message.get('date', '')
            text = message.get('text', '')
            
            # Format date to exact WhatsApp: [DD/MM/YY, HH:MM:SS AM/PM]
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_formatted = dt.strftime("[%d/%m/%y, %I:%M:%S %p]")
            except ValueError:
                date_formatted = "[DD/MM/YY, HH:MM:SS AM/PM]"
            
            # Extract sender (blank for self in WhatsApp style)
            from_data = message.get('from', {})
            is_self = message.get('from_id') == telegram_data.get('chat', {}).get('id', 0)  # Rough self-check
            if isinstance(from_data, dict):
                from_user = from_data.get('first_name', '') or from_data.get('title', '')
                if not from_user:
                    from_user = ''
            else:
                from_user = str(from_data)
            from_user = name_mapping.get(from_user, from_user)
            sender_prefix = f" - {from_user}" if from_user and not is_self else ""
            
            # Handle service messages
            if message.get('action'):
                action = message['action'].get('action', '')
                if include_service_messages:
                    action_text = action.replace('_', ' ').title()
                    whatsapp_message = f"{date_formatted}{sender_prefix}: {action_text}\n"
                else:
                    continue
            # Handle replies (prefix in text)
            elif include_replies and message.get('reply_to_message_id'):
                reply_prefix = "‎(reply) "
                text = reply_prefix + (text[:100] + '...' if len(text) > 100 else text)
                whatsapp_message = f"{date_formatted}{sender_prefix}: {text}\n"
            # Handle text/media
            else:
                if isinstance(text, str) and text.strip():
                    whatsapp_message = f"{date_formatted}{sender_prefix}: {text}\n"
                else:
                    if not include_media_placeholders:
                        continue
                    # Specific media types (uppercase OMITTED to match WhatsApp style)
                    media_type = '<MEDIA OMITTED>'
                    if message.get('photo'):
                        media_type = '<PHOTO OMITTED>'
                    elif message.get('video'):
                        media_type = '<VIDEO OMITTED>'
                    elif message.get('document'):
                        doc_name = message.get('document', {}).get('file_name', 'file')
                        media_type = f'<DOCUMENT OMITTED: {doc_name}>'
                    elif message.get('audio'):
                        media_type = '<AUDIO OMITTED>'
                    elif message.get('voice'):
                        media_type = '<VOICE MESSAGE OMITTED>'
                    elif message.get('sticker'):
                        media_type = '<STICKER OMITTED>'
                    elif message.get('poll'):
                        poll_question = message.get('poll', {}).get('question', 'Poll')
                        media_type = f'<POLL OMITTED: {poll_question}>'
                    elif message.get('contact'):
                        media_type = '<CONTACT OMITTED>'
                    elif message.get('location'):
                        media_type = '<LOCATION OMITTED>'
                    whatsapp_message = f"{date_formatted}{sender_prefix}: {media_type}\n"
            
            output_file.write(whatsapp_message)

def main():
    parser = argparse.ArgumentParser(description="Convert Telegram JSON to WhatsApp TXT for Telegram import")
    parser.add_argument("input", default="result.json", nargs="?", help="Input JSON path")
    parser.add_argument("output", default="_chat.txt", nargs="?", help="Output TXT path (intermediate)")
    parser.add_argument("--mapping", type=str, help="JSON file with name mappings")
    parser.add_argument("--no-media", action="store_true", help="Skip media")
    parser.add_argument("--no-replies", action="store_true", help="Skip reply prefixes")
    parser.add_argument("--no-service", action="store_true", help="Skip service messages")
    
    args = parser.parse_args()
    
    # Load mapping if provided
    name_mapping = {}
    if args.mapping:
        try:
            with open(args.mapping, 'r') as f:
                name_mapping = json.load(f)
        except Exception as e:
            print(f"Error loading mapping: {e}")
    
    convert_telegram_to_whatsapp(
        args.input,
        args.output,
        name_mapping,
        not args.no_media,
        not args.no_replies,
        not args.no_service
    )
    
    # Prompt for chat name
    name = input("Enter name for the chat (e.g., ToniStark): ").strip()
    if not name:
        name = "Unknown"
    
    # Create TXT with proper name inside ZIP
    txt_name = f"Chat with {name}.txt"
    zip_name = f"WhatsApp Chat - {name}.zip"
    
    # Zip the TXT
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(args.output, txt_name)
        print(f"ZIP created: {zip_name}")
    except Exception as e:
        print(f"Error creating ZIP: {e}")
    
    # Optional: Clean up intermediate TXT
    import os
    os.remove(args.output)
    print(f"Intermediate file {args.output} removed.")

if __name__ == "__main__":
    main()