from selenium_utils import fetch_html_selenium, setup_selenium
from html_processing import html_to_markdown_with_readability
from file_operations import save_raw_data, save_formatted_data
from api_handlers import format_data
from utils import calculate_price, generate_unique_folder_name
from data_models import create_dynamic_listing_model, create_listings_container_model

def scrape_url(url, attended_mode=False, driver=None):
    """
    Scrape a URL and return the raw HTML content.
    This function combines fetch_html_selenium and html_to_markdown_with_readability.
    """
    raw_html = fetch_html_selenium(url, attended_mode=attended_mode, driver=driver)
    return html_to_markdown_with_readability(raw_html)

# Re-export all the functions that streamlit_app.py expects from scraper.py
__all__ = [
    'fetch_html_selenium',
    'save_raw_data',
    'format_data',
    'save_formatted_data',
    'calculate_price',
    'html_to_markdown_with_readability',
    'create_dynamic_listing_model',
    'create_listings_container_model',
    'setup_selenium',
    'generate_unique_folder_name',
    'scrape_url'
]
