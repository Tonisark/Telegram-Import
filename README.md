# Telegram to WhatsApp Chat Converter

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Convert your Telegram chat exports (JSON format) into WhatsApp-style chat logs (TXT zipped) for easy import back into Telegram. This tool mimics WhatsApp's export format, allowing you to recreate chat history in Telegram via its built-in "Import Chat History" feature. Perfect for archiving, migrating, or simulating chats!

**Note**: Media files are represented as descriptive placeholders (e.g., `<PHOTO OMITTED>`), as Telegram's import doesn't restore actual files

## Features
- **Accurate Formatting**: Generates exact WhatsApp TXT structure with 12-hour timestamps (e.g., `[DD/MM/YY, HH:MM:SS AM/PM]`).
- **Media Placeholders**: Specifies types like `<PHOTO OMITTED>`, `<VIDEO OMITTED>`, or `<DOCUMENT OMITTED: filename.pdf>`.
- **Sender Handling**: Blanks self-messages (WhatsApp style); remap names via JSON config.
- **Replies & Services**: Optional prefixes for replies (e.g., `(reply) Hello`) and service actions (e.g., "User Joined").
- **Auto-Zipping**: Outputs a ready-to-import ZIP like `WhatsApp Chat - JohnDoe.zip` containing `Chat with JohnDoe.txt`.
- **Flexible CLI**: Supports skipping media/replies/services; handles single/multi-chat exports.
- **Error-Resilient**: Sorts messages chronologically; graceful handling of invalid dates/JSON.

## Quick Start

1. **Install Dependencies** (minimal—standard library only):
   ```bash
   # No pip needed! Uses built-in: json, argparse, zipfile, datetime, os.
   ```

2. **Export from Telegram**:
   - In Telegram Desktop: Settings > Advanced > Export Telegram data > Select chat > JSON format.
   - Save as `result.json` (or any path).

3. **Run the Script**:
   ```bash
   python tele.py result.json _chat.txt
   ```
   - It will prompt: `Enter name for the chat (e.g., ToniStark):`
   - Outputs: `WhatsApp Chat - ToniStark.zip`

4. **Import to Telegram**:
   - Mobile/Desktop: Settings > Data and Storage > Import Chat History > Select ZIP.
   - Choose target chat/user.

## Detailed Usage

### Command-Line Options
```bash
python tele.py [INPUT] [OUTPUT] [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `INPUT` | Path to Telegram JSON (e.g., `result.json`). | `result.json` |
| `OUTPUT` | Intermediate TXT path (auto-deleted after zipping). | `_chat.txt` |
| `--mapping MAPPING` | JSON file for name remapping, e.g., `{"Alice": "Bob"}`. | None |
| `--no-media` | Skip media placeholders (omit non-text messages). | Include |
| `--no-replies` | Skip reply prefixes. | Include |
| `--no-service` | Skip service messages (e.g., "User joined"). | Include |

### Name Mapping Example
Create `mapping.json`:
```json
{
  "OriginalName": "NewName",
  "Alice": "Bob"
}
```
Run: `python tele.py result.json _chat.txt --mapping mapping.json`

## Limitations
- **No Real Media**: Placeholders only; re-attach files manually post-import.
- **Self-Detection**: Rough check for self-messages (based on `from_id` vs chat ID)—may need tweaks for groups.
- **Multi-Line Text**: Preserved, but complex formatting (e.g., bold in Telegram) is lost as plain text.
- **Large Exports**: May take time for sorting; test on small chats first.
- **Telegram Import Quirks**: Ensure ZIP has exactly one TXT named `Chat with [Name].txt`.

## Troubleshooting
- **JSON Errors**: Verify export is valid JSON (use `jq` or online validator).
- **Date Issues**: Invalid dates fallback to placeholder—check Telegram export timestamps.
- **No Messages**: Ensure `'messages'` key exists; full export required.
- **ZIP Not Recognized**: Use no extra headers; match WhatsApp exactly.

If issues persist, open a GitHub issue with sample JSON snippet (anonymized)!

## Contributing
1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/add-support`).
3. Commit changes (`git commit -m "Add X feature"`).
4. Push (`git push origin feature/add-support`).
5. Open a Pull Request.

Thanks for contributing! 🚀
