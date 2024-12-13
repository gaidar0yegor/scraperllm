from selenium_utils import fetch_html_selenium, setup_selenium
from html_processing import html_to_markdown_with_readability
from file_operations import save_raw_data, save_formatted_data
from api_handlers import format_data
from utils import calculate_price, generate_unique_folder_name
from data_models import create_dynamic_listing_model, create_listings_container_model
from pagination_detector import detect_pagination_elements
import os
import time

def scrape_url(url, attended_mode=False, driver=None):
    """
    Scrape a URL and return the raw HTML content.
    This function combines fetch_html_selenium and html_to_markdown_with_readability.
    """
    raw_html = fetch_html_selenium(url, attended_mode=attended_mode, driver=driver)
    return html_to_markdown_with_readability(raw_html)

def scrape_with_pagination(initial_url, model_selection, fields, output_folder, pagination_details=""):
    """
    Scrape multiple pages starting from the initial URL.
    
    Args:
        initial_url (str): The starting URL to scrape
        model_selection (str): The AI model to use
        fields (list): Fields to extract from each page
        output_folder (str): Where to save the results
        pagination_details (str): Optional hints about pagination structure
    
    Returns:
        tuple: (all_data, total_tokens, total_cost)
    """
    # Initialize counters and data containers
    all_data = []
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0
    processed_urls = set()
    
    # Create dynamic models
    DynamicListingModel = create_dynamic_listing_model(fields)
    DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
    
    # Setup driver for consistent session
    driver = setup_selenium(attended_mode=False)
    
    try:
        # Process initial page
        current_url = initial_url
        page_num = 1
        
        while current_url and current_url not in processed_urls:
            try:
                # Mark URL as processed
                processed_urls.add(current_url)
                
                # Scrape current page
                markdown = scrape_url(current_url, driver=driver)
                save_raw_data(markdown, output_folder, f'rawData_{page_num}.md')
                
                # Format and save data
                formatted_data, token_counts = format_data(
                    markdown, DynamicListingsContainer, DynamicListingModel, model_selection
                )
                input_tokens, output_tokens, cost = calculate_price(token_counts, model_selection)
                total_input_tokens += input_tokens
                total_output_tokens += output_tokens
                total_cost += cost
                
                # Save formatted data
                save_formatted_data(formatted_data, output_folder, 
                                 f'sorted_data_{page_num}.json', 
                                 f'sorted_data_{page_num}.xlsx')
                all_data.append(formatted_data)
                
                # Get next page URL if this is the first page
                if page_num == 1:
                    pagination_data, p_token_counts, p_cost = detect_pagination_elements(
                        current_url, pagination_details, model_selection, markdown
                    )
                    
                    # Update totals with pagination detection costs
                    total_input_tokens += p_token_counts['input_tokens']
                    total_output_tokens += p_token_counts['output_tokens']
                    total_cost += p_cost
                    
                    # Get list of pages to process
                    if hasattr(pagination_data, 'page_urls'):
                        next_urls = pagination_data.page_urls
                    elif isinstance(pagination_data, dict):
                        next_urls = pagination_data.get('page_urls', [])
                    else:
                        next_urls = []
                    
                    # Filter out already processed URLs
                    next_urls = [url for url in next_urls if url not in processed_urls]
                    
                    if next_urls:
                        current_url = next_urls[0]  # Get the next URL to process
                    else:
                        current_url = None  # No more pages to process
                else:
                    current_url = None  # Stop after processing additional pages
                
                page_num += 1
                time.sleep(2)  # Small delay between pages
                
            except Exception as e:
                print(f"Error processing page {current_url}: {str(e)}")
                current_url = None  # Stop on error
                
    finally:
        if driver:
            driver.quit()
    
    return all_data, {
        'input_tokens': total_input_tokens,
        'output_tokens': total_output_tokens,
        'total_cost': total_cost
    }

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
    'scrape_url',
    'scrape_with_pagination'
]
