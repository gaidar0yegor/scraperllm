from typing import List
from selenium_utils import fetch_html_selenium
from html_processing import html_to_markdown_with_readability
from data_models import create_dynamic_listing_model, create_listings_container_model
from api_handlers import format_data
from file_operations import save_raw_data, save_formatted_data
from utils import generate_unique_folder_name, calculate_price

def scrape_url(url: str, fields: List[str], selected_model: str, output_folder: str, file_number: int, markdown: str):
    try:
        save_raw_data(markdown, output_folder, f'rawData_{file_number}.md')
        DynamicListingModel = create_dynamic_listing_model(fields)
        DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
        formatted_data, token_counts = format_data(markdown, DynamicListingsContainer, DynamicListingModel, selected_model)
        save_formatted_data(formatted_data, output_folder, f'sorted_data_{file_number}.json', f'sorted_data_{file_number}.xlsx')
        input_tokens, output_tokens, total_cost = calculate_price(token_counts, selected_model)
        return input_tokens, output_tokens, total_cost, formatted_data
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
        return 0, 0, 0, None

def main(url: str, fields: List[str], selected_model: str):
    output_folder = generate_unique_folder_name(url)
    html_content = fetch_html_selenium(url)
    markdown = html_to_markdown_with_readability(html_content)
    input_tokens, output_tokens, total_cost, formatted_data = scrape_url(url, fields, selected_model, output_folder, 1, markdown)
    
    print(f"Scraping completed for {url}")
    print(f"Input tokens: {input_tokens}")
    print(f"Output tokens: {output_tokens}")
    print(f"Total cost: ${total_cost:.6f}")
    
    return formatted_data

if __name__ == "__main__":
    # Example usage
    url = "https://www.example.com"
    fields = ["title", "price", "status"]
    selected_model = "Ollama"
    
    result = main(url, fields, selected_model)
    print("Scraping result:", result)
