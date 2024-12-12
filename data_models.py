from typing import List, Type
from pydantic import BaseModel, create_model

def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    field_definitions = {field: (str, ...) for field in field_names}
    return create_model('DynamicListingModel', **field_definitions)

def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:
    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))

def generate_system_message(listing_model: BaseModel) -> str:
    schema_info = listing_model.model_json_schema()
    field_descriptions = []
    for field_name, field_info in schema_info["properties"].items():
        field_type = field_info["type"]
        field_descriptions.append(f'"{field_name}": "{field_type}"')
    schema_structure = ",\n".join(field_descriptions)

    system_message = f"""You are an intelligent text extraction and conversion assistant specialized in extracting structured data from HTML/text content. Your task is to extract specific fields from the provided text and format them as JSON.

The output must be ONLY valid JSON with no additional text. Follow this exact structure:

{{
    "listings": [
        {{
            {schema_structure}
        }}
    ]
}}

Rules:
1. Only output valid JSON, nothing else
2. Always include the "listings" array, even if empty
3. Each listing must include all specified fields
4. If a field's value cannot be found, use an empty string ("")
5. Do not include any explanations or additional text
6. Ensure the response is properly formatted JSON that can be parsed

Example of correct response format:
{{
    "listings": [
        {{
            {schema_structure}
        }}
    ]
}}"""

    return system_message
