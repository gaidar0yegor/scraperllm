import streamlit as st
import os
import sys

# Add project root to Python path to allow importing from project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from scraper import (
    fetch_html_selenium,
    save_raw_data,
    format_data,
    save_formatted_data,
    calculate_price,
    html_to_markdown_with_readability,
    create_dynamic_listing_model,
    create_listings_container_model,
    setup_selenium,
    generate_unique_folder_name
)
from pagination_detector import detect_pagination_elements

def handle_scraping(settings, credentials=None, cookie_selectors=None):
    """Handle the main scraping process."""
    with st.spinner('Scraping in progress...'):
        # Initialize output folder
        output_folder = os.path.join('output', generate_unique_folder_name(settings['urls'][0]))
        os.makedirs(output_folder, exist_ok=True)

        # Initialize counters and data containers
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0
        all_data = []
        pagination_info = None

        driver = st.session_state.get('driver', None)
        
        try:
            if settings['attended_mode'] and driver is not None:
                results = handle_attended_mode_scraping(
                    driver, settings, credentials, cookie_selectors, output_folder
                )
            else:
                results = handle_unattended_mode_scraping(
                    settings, credentials, cookie_selectors, output_folder
                )
            
            # Update totals
            total_input_tokens += results['input_tokens']
            total_output_tokens += results['output_tokens']
            total_cost += results['cost']
            all_data.extend(results['data'])
            pagination_info = results.get('pagination_info')

        finally:
            # Clean up driver if used
            if driver:
                driver.quit()
                st.session_state['driver'] = None

        # Return results
        return {
            'data': all_data,
            'input_tokens': total_input_tokens,
            'output_tokens': total_output_tokens,
            'total_cost': total_cost,
            'output_folder': output_folder,
            'pagination_info': pagination_info
        }

def handle_attended_mode_scraping(driver, settings, credentials, cookie_selectors, output_folder):
    """Handle scraping in attended mode."""
    # Fetch HTML from the current page
    raw_html = fetch_html_selenium(
        settings['urls'][0],
        attended_mode=True,
        driver=driver,
        cookie_selectors=cookie_selectors,
        credentials=credentials
    )
    markdown = html_to_markdown_with_readability(raw_html)
    save_raw_data(markdown, output_folder, f'rawData_1.md')

    current_url = driver.current_url
    results = {
        'input_tokens': 0,
        'output_tokens': 0,
        'cost': 0,
        'data': []
    }

    # Handle pagination if enabled
    if settings['use_pagination']:
        pagination_results = handle_pagination(
            current_url,
            settings['pagination_details'],
            settings['model_selection'],
            markdown
        )
        results['pagination_info'] = pagination_results

    # Process data if scraping is enabled
    if settings['show_tags']:
        data_results = process_page_data(
            markdown,
            settings['fields'],
            settings['model_selection'],
            output_folder,
            1
        )
        results.update(data_results)

    return results

def handle_unattended_mode_scraping(settings, credentials, cookie_selectors, output_folder):
    """Handle scraping in unattended mode."""
    results = {
        'input_tokens': 0,
        'output_tokens': 0,
        'cost': 0,
        'data': []
    }

    for i, url in enumerate(settings['urls'], start=1):
        # Fetch HTML
        raw_html = fetch_html_selenium(
            url,
            attended_mode=False,
            cookie_selectors=cookie_selectors,
            credentials=credentials
        )
        markdown = html_to_markdown_with_readability(raw_html)
        save_raw_data(markdown, output_folder, f'rawData_{i}.md')

        # Handle pagination for first URL only
        if settings['use_pagination'] and i == 1:
            pagination_results = handle_pagination(
                url,
                settings['pagination_details'],
                settings['model_selection'],
                markdown
            )
            results['pagination_info'] = pagination_results

        # Process data if scraping is enabled
        if settings['show_tags']:
            data_results = process_page_data(
                markdown,
                settings['fields'],
                settings['model_selection'],
                output_folder,
                i
            )
            results['input_tokens'] += data_results['input_tokens']
            results['output_tokens'] += data_results['output_tokens']
            results['cost'] += data_results['cost']
            results['data'].extend(data_results['data'])

    return results

def handle_pagination(url, pagination_details, model_selection, markdown):
    """Handle pagination detection and processing."""
    pagination_data, token_counts, pagination_price = detect_pagination_elements(
        url, pagination_details, model_selection, markdown
    )
    
    # Extract page URLs
    if isinstance(pagination_data, dict):
        page_urls = pagination_data.get("page_urls", [])
    else:
        page_urls = pagination_data.page_urls
    
    return {
        "page_urls": page_urls,
        "token_counts": token_counts,
        "price": pagination_price
    }

def process_page_data(markdown, fields, model_selection, output_folder, index):
    """Process data from a single page."""
    # Create dynamic models
    DynamicListingModel = create_dynamic_listing_model(fields)
    DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
    
    # Format data
    formatted_data, token_counts = format_data(
        markdown, DynamicListingsContainer, DynamicListingModel, model_selection
    )
    
    # Calculate costs
    input_tokens, output_tokens, cost = calculate_price(token_counts, model_selection)
    
    # Save formatted data
    save_formatted_data(formatted_data, output_folder, f'sorted_data_{index}.json', f'sorted_data_{index}.xlsx')
    
    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'cost': cost,
        'data': [formatted_data]
    }
