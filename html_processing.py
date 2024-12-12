import re
from bs4 import BeautifulSoup
import html2text

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove header and footer
    for element in soup.find_all(['header', 'footer']):
        element.decompose()
    
    # Find all product listings
    product_listings = []
    
    # Look for product titles (h2 tags with links)
    for title in soup.find_all('h2'):
        if title.find('a'):  # If h2 contains a link
            product_div = title.find_parent()  # Get the parent element
            if product_div:
                # Get the title
                title_text = title.get_text(strip=True)
                
                # Find price - look for the actual price, not the discount
                price_text = ""
                # Look for prices in format "X XXX,XX €"
                text = product_div.get_text()
                # First try to find non-discounted price
                price_matches = re.findall(r'(\d+(?:\s\d{3})*,\d{2})\s*€(?!\s*\d)', text)
                if price_matches:
                    # Get the first non-discounted price
                    for price in price_matches:
                        if not re.search(r'-\d+', price):  # Skip if it's a discount
                            price_text = price.strip()
                            break
                    if not price_text and price_matches:
                        # If no non-discounted price found, use the last price
                        price_text = price_matches[-1].strip()
                
                # Find status (look for "En Stock" or "En réapprovisionnement")
                status_text = ""
                status_elem = product_div.find(text=re.compile(r'En (Stock|réapprovisionnement)'))
                if status_elem:
                    status_text = status_elem.strip()
                
                # Add clear markers
                if title_text:
                    title.string = f"PRODUCT_TITLE: {title_text}"
                if price_text:
                    # Create a new tag for price
                    price_tag = soup.new_tag('p')
                    price_tag.string = f"PRODUCT_PRICE: {price_text}"
                    title.insert_after(price_tag)
                if status_text:
                    # Create a new tag for status
                    status_tag = soup.new_tag('p')
                    status_tag.string = f"PRODUCT_STATUS: {status_text}"
                    title.insert_after(status_tag)
    
    return str(soup)

def html_to_markdown_with_readability(html_content):
    cleaned_html = clean_html(html_content)  
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    markdown_content = markdown_converter.handle(cleaned_html)
    return markdown_content
