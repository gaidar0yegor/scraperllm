# ScrapeMaster - Universal Web Scraper with LLM Support

ScrapeMaster is a Streamlit-based web scraping application that uses LLMs (Language Model Models) to extract structured data from web pages. It supports multiple LLM providers including OpenAI, Gemini, Groq, and Ollama.

## Prerequisites

- Python 3.6 or higher
- Git
- Chrome browser (for Selenium)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gaidar0yegor/scraperllm.git
cd scraperllm
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. In the Streamlit UI's "API Keys" section, you can configure:
   - OpenAI API Key (for GPT models)
   - Gemini API Key (for Google's Gemini models)
   - Groq API Key (for Groq's models)
   - Ollama API URL (for self-hosted or remote Ollama instance)

## Running the Application

1. Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```

2. Open your web browser and go to http://localhost:8501

3. In the Streamlit interface:
   - Select your preferred LLM model
   - Enter the URL(s) you want to scrape
   - Add the fields you want to extract (e.g., title, price, status)
   - Enable pagination if needed
   - Click "LAUNCH SCRAPER"

## Features

- Multiple LLM provider support (OpenAI, Gemini, Groq, Ollama)
- Automatic field extraction
- Pagination support
- Export to JSON and CSV
- Attended mode for interactive scraping
- Progress tracking and error handling
- Token usage and cost tracking

## Output

The scraped data will be saved in the `output` directory in both JSON and Excel formats. The directory name will include the timestamp and domain name of the scraped website.
