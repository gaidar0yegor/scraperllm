import json
import requests
import re
from openai import OpenAI
import google.generativeai as genai
from groq import Groq
from api_management import get_api_key
from assets import SYSTEM_MESSAGE, USER_MESSAGE, LLAMA_MODEL_FULLNAME, GROQ_LLAMA_MODEL_FULLNAME, OLLAMA_MODEL_NAME
from data_models import generate_system_message
import streamlit as st

def format_data(data, DynamicListingsContainer, DynamicListingModel, selected_model):
    token_counts = {}
    
    if selected_model in ["gpt-4o-mini", "gpt-4o-2024-08-06"]:
        return handle_openai(data, DynamicListingsContainer, selected_model)
    elif selected_model == "gemini-1.5-flash":
        return handle_gemini(data, DynamicListingsContainer)
    elif selected_model == "Llama3.1 8B":
        return handle_llama(data, DynamicListingModel)
    elif selected_model == "Groq Llama3.1 70b":
        return handle_groq(data, DynamicListingModel)
    elif selected_model == "Ollama":
        return handle_ollama(data, DynamicListingModel)
    else:
        raise ValueError(f"Unsupported model: {selected_model}")

def handle_openai(data, DynamicListingsContainer, selected_model):
    client = OpenAI(api_key=get_api_key('OPENAI_API_KEY'))
    completion = client.beta.chat.completions.parse(
        model=selected_model,
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": USER_MESSAGE + data},
        ],
        response_format=DynamicListingsContainer
    )
    encoder = tiktoken.encoding_for_model(selected_model)
    input_token_count = len(encoder.encode(USER_MESSAGE + data))
    output_token_count = len(encoder.encode(json.dumps(completion.choices[0].message.parsed.dict())))
    token_counts = {
        "input_tokens": input_token_count,
        "output_tokens": output_token_count
    }
    return completion.choices[0].message.parsed, token_counts

def handle_gemini(data, DynamicListingsContainer):
    genai.configure(api_key=get_api_key("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash',
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": DynamicListingsContainer
            })
    prompt = SYSTEM_MESSAGE + "\n" + USER_MESSAGE + data
    input_tokens = model.count_tokens(prompt)
    completion = model.generate_content(prompt)
    usage_metadata = completion.usage_metadata
    token_counts = {
        "input_tokens": usage_metadata.prompt_token_count,
        "output_tokens": usage_metadata.candidates_token_count
    }
    return completion.text, token_counts

def handle_llama(data, DynamicListingModel):
    sys_message = generate_system_message(DynamicListingModel)
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    completion = client.chat.completions.create(
        model=LLAMA_MODEL_FULLNAME,
        messages=[
            {"role": "system", "content": sys_message},
            {"role": "user", "content": USER_MESSAGE + data}
        ],
        temperature=0.7,
    )
    response_content = completion.choices[0].message.content
    parsed_response = json.loads(response_content)
    token_counts = {
        "input_tokens": completion.usage.prompt_tokens,
        "output_tokens": completion.usage.completion_tokens
    }
    return parsed_response, token_counts

def handle_groq(data, DynamicListingModel):
    sys_message = generate_system_message(DynamicListingModel)
    client = Groq(api_key=get_api_key("GROQ_API_KEY"),)
    completion = client.chat.completions.create(
        messages=[
            {"role": "system","content": sys_message},
            {"role": "user","content": USER_MESSAGE + data}
        ],
        model=GROQ_LLAMA_MODEL_FULLNAME,
    )
    response_content = completion.choices[0].message.content
    parsed_response = json.loads(response_content)
    token_counts = {
        "input_tokens": completion.usage.prompt_tokens,
        "output_tokens": completion.usage.completion_tokens
    }
    return parsed_response, token_counts

def handle_ollama(data, DynamicListingModel):
    print("DEBUG: Entering Ollama branch in format_data function")
    sys_message = generate_system_message(DynamicListingModel)
    
    # Get the Ollama API URL from session state
    ollama_url = st.session_state.get('ollama_url', '').strip()
    
    # Try local Ollama if no URL provided
    if not ollama_url:
        print("DEBUG: No Ollama URL provided, trying local instance")
        ollama_url = 'http://localhost:11434'
    
    print(f"DEBUG: Attempting to use Ollama at {ollama_url}")
    
    prompt = f"""Extract product information from the text and format it as JSON. Each product has three pieces of information marked with specific prefixes:

1. PRODUCT_TITLE: followed by the product name
2. PRODUCT_PRICE: followed by the price (in format "X XXX,XX")
3. PRODUCT_STATUS: followed by the status (if available, otherwise leave it empty)

Format the extracted information as JSON like this:
{{
    "listings": [
        {{
            "title": "The exact product title (without the ## PRODUCT_TITLE: prefix)",
            "price": "The price number without currency symbol",
            "status": "Any availability information found"
        }},
        ...more products...
    ]
}}

Example input:
## PRODUCT_TITLE: CANON EOS R5 Boitier nu
PRODUCT_PRICE: 3999,00
... some description ...
Prochaines dispos au printemps 2025.

Example output:
{{
    "listings": [
        {{
            "title": "CANON EOS R5 Boitier nu",
            "price": "3999,00",
            "status": "Prochaines dispos au printemps 2025"
        }}
    ]
}}

IMPORTANT:
- Only output valid JSON
- Do not include any explanatory text
- Do not include the currency symbol (€) in the price
- Include all products found in the text
- If no products are found, return {{"listings": []}}
- Make sure to capture the COMPLETE price, including all digits and decimal places

Here's the text to process:
{data}
"""

    print(f"DEBUG: Prompt: {prompt}")

    try:
        print(f"DEBUG: Sending request to Ollama API at {ollama_url}")
        response = requests.post(f'{ollama_url}/api/generate', 
            json={
                "model": "tinyllama:latest",
                "prompt": prompt,
                "system": "You are a precise JSON extractor that only outputs valid JSON.",
                "stream": False,
                "temperature": 0.1,
                "top_p": 0.95
            },
            timeout=10  # Add timeout to fail fast if server is unreachable
        )
        print(f"DEBUG: Ollama API response status code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            response_content = response_data.get('response', '')
            print(f"DEBUG: Ollama API response content (first 500 characters): {response_content[:500]}")
            
            # Try to find JSON in the response
            try:
                # First try: direct JSON parsing
                parsed_response = json.loads(response_content)
                print("DEBUG: Successfully parsed JSON directly")
                print(f"DEBUG: Parsed response: {json.dumps(parsed_response, indent=2)}")
            except json.JSONDecodeError:
                print("DEBUG: Failed to parse JSON directly, attempting to find JSON-like structure")
                # Second try: find JSON-like structure
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    try:
                        clean_json = response_content[json_start:json_end]
                        parsed_response = json.loads(clean_json)
                        print("DEBUG: Successfully parsed JSON from extracted structure")
                        print(f"DEBUG: Parsed response: {json.dumps(parsed_response, indent=2)}")
                    except json.JSONDecodeError:
                        print("DEBUG: Failed to parse JSON from extracted structure, using regex fallback")
                        # Use regex as a fallback
                        titles = re.findall(r'## PRODUCT_TITLE:\s*(.*?)(?=\n|$)', data)
                        # Updated price pattern to capture full price including thousands
                        prices = re.findall(r'PRODUCT_PRICE:\s*(\d+\s*\d+(?:,\d+)?)', data)
                        availability_pattern = r'Nouveauté en production ultra tendue\. (.*?)(?=\n|$)'
                        availabilities = re.findall(availability_pattern, data)
                        
                        listings = []
                        for i in range(len(titles)):
                            # Clean up the price by removing spaces
                            price = prices[i].strip().replace(" ", "") if i < len(prices) else ""
                            listing = {
                                "title": titles[i].strip(),
                                "price": price,
                                "status": availabilities[0].strip() if availabilities else "Prochaines dispos au printemps 2025"
                            }
                            listings.append(listing)
                        
                        parsed_response = {"listings": listings}
                else:
                    print("DEBUG: No JSON-like structure found, using regex fallback")
                    # Use regex as a fallback
                    titles = re.findall(r'## PRODUCT_TITLE:\s*(.*?)(?=\n|$)', data)
                    # Updated price pattern to capture full price including thousands
                    prices = re.findall(r'PRODUCT_PRICE:\s*(\d+\s*\d+(?:,\d+)?)', data)
                    availability_pattern = r'Nouveauté en production ultra tendue\. (.*?)(?=\n|$)'
                    availabilities = re.findall(availability_pattern, data)
                    
                    listings = []
                    for i in range(len(titles)):
                        # Clean up the price by removing spaces
                        price = prices[i].strip().replace(" ", "") if i < len(prices) else ""
                        listing = {
                            "title": titles[i].strip(),
                            "price": price,
                            "status": availabilities[0].strip() if availabilities else "Prochaines dispos au printemps 2025"
                        }
                        listings.append(listing)
                    
                    parsed_response = {"listings": listings}
            
            # Ensure the response has the correct structure
            if "listings" not in parsed_response:
                print("DEBUG: 'listings' key not found in parsed response, adding it")
                parsed_response = {"listings": []}
            
            # Estimate token counts
            token_counts = {
                "input_tokens": len((sys_message + prompt).split()),
                "output_tokens": len(response_content.split())
            }
            print(f"DEBUG: Estimated token counts: {token_counts}")
            
            return parsed_response, token_counts
        else:
            print(f"DEBUG: Ollama API request failed with status code: {response.status_code}")
            raise Exception(f"Ollama API request failed with status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("DEBUG: Could not connect to Ollama API")
        if ollama_url == 'http://localhost:11434':
            st.error("No local Ollama instance found. Please install and run Ollama locally, or provide an external Ollama API URL.")
        else:
            st.error(f"Could not connect to Ollama at {ollama_url}. Please check the URL and try again.")
        raise
    except requests.exceptions.Timeout:
        print("DEBUG: Ollama API request timed out")
        st.error("Ollama API request timed out. Please check your connection or try again.")
        raise
    except Exception as e:
        print(f"DEBUG: An error occurred while processing Ollama request: {str(e)}")
        # Use regex as a fallback when API call fails
        titles = re.findall(r'## PRODUCT_TITLE:\s*(.*?)(?=\n|$)', data)
        # Updated price pattern to capture full price including thousands
        prices = re.findall(r'PRODUCT_PRICE:\s*(\d+\s*\d+(?:,\d+)?)', data)
        availability_pattern = r'Nouveauté en production ultra tendue\. (.*?)(?=\n|$)'
        availabilities = re.findall(availability_pattern, data)
        
        listings = []
        for i in range(len(titles)):
            # Clean up the price by removing spaces
            price = prices[i].strip().replace(" ", "") if i < len(prices) else ""
            listing = {
                "title": titles[i].strip(),
                "price": price,
                "status": availabilities[0].strip() if availabilities else "Prochaines dispos au printemps 2025"
            }
            listings.append(listing)
        
        parsed_response = {"listings": listings}
        token_counts = {
            "input_tokens": len(data.split()),
            "output_tokens": len(json.dumps(parsed_response).split())
        }
        return parsed_response, token_counts
