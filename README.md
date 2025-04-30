# AmbossToPDF

A Python script that scrapes medical articles from Amboss and converts them to formatted PDF documents.

## Features

- Authenticates with Amboss using Selenium
- Scrapes article content using GraphQL queries
- Processes HTML content including:
  - Text paragraphs
  - Lists (with nested levels)
  - Tables (with colspan/rowspan support)
  - Images (with captions)
  - Special content blocks (case texts, notes, mnemonics)
- Generates well-formatted PDFs with:
  - Custom fonts
  - Proper styling for different content types
  - Image handling and placement

## Requirements

- Python 3.7+
- Firefox browser (for Selenium)
- Required packages (install via `pip install -r requirements.txt`):
  
  ```
  httpx
  selectolax
  selenium
  fpdf2
  pillow
  ```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ambosstopdf.git
   cd ambosstopdf
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `creds.py` file with your Amboss credentials:
   ```python
   email = 'your@email.com'
   password = 'yourpassword'
   ```

## Usage

1. Run the script:
   ```bash
   python amboss_scraper.py
   ```

2. When prompted, paste the URL of the Amboss article you want to convert (e.g., `https://next.amboss.com/de/article/dT0op2`, the ID after article must match!)

3. The script will:
   - Authenticate with Amboss
   - Scrape the article content
   - Generate a PDF with the same name as the article title

## Example Output

The generated PDF will include:
- Article title and synonyms
- Last updated date
- Structured content with proper formatting
- Images with captions
- Properly formatted tables
- Highlighted clinical cases and mnemonics

## Troubleshooting

### Common Issues

1. **Authentication fails**:
   - Verify your credentials in `creds.py`
   - Make sure your account is active

2. **Table formatting issues**:
   - Complex tables may need manual adjustment in the code
   - See `process_table_header()` method for customization

## Limitations

- Requires Firefox installation
- Complex article layouts may not convert perfectly
- Some interactive content won't be captured
- Rate limiting may occur with excessive use

## Disclaimer

This project is for educational purposes only. Please:
- Respect Amboss's terms of service
- Only download content you have legitimate access to
- Don't use this for mass scraping
- Consider supporting Amboss by subscribing if you find their content valuable

