import streamlit as st
import pandas as pd
import json
import sys
import os

# Add project root to Python path to allow importing from project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def display_scraping_results(results, show_tags):
    """Display the scraping results including data tables and statistics."""
    if not results:
        return

    all_data = results['data']
    total_input_tokens = results['input_tokens']
    total_output_tokens = results['output_tokens']
    total_cost = results['total_cost']
    output_folder = results['output_folder']
    pagination_info = results['pagination_info']

    # Display scraping details
    if show_tags:
        st.subheader("Scraping Results")
        for i, data in enumerate(all_data, start=1):
            st.write(f"Data from URL {i}:")
            
            try:
                # Convert data to DataFrame
                df = convert_data_to_dataframe(data)
                
                # Display the dataframe
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning(f"No data found for URL {i}")
                
                # Display raw data for debugging
                with st.expander("Show raw data"):
                    st.json(data)
                    
            except Exception as e:
                st.error(f"Error displaying data for URL {i}: {str(e)}")
                st.json(data)  # Show raw data when there's an error

        # Display token usage and cost
        display_token_metrics(total_input_tokens, total_output_tokens, total_cost)

        # Download options
        display_download_options(all_data)

        st.success(f"Scraping completed. Results saved in {output_folder}")

    # Display pagination info if available
    if pagination_info:
        display_pagination_info(pagination_info)

    # Display combined totals if both scraping and pagination were performed
    if show_tags and pagination_info:
        display_combined_totals(total_input_tokens, total_output_tokens, total_cost, pagination_info)

def convert_data_to_dataframe(data):
    """Convert various data formats to a pandas DataFrame."""
    if isinstance(data, str):
        data = json.loads(data)
    
    if isinstance(data, dict):
        if 'listings' in data and isinstance(data['listings'], list):
            return pd.DataFrame(data['listings'])
        elif isinstance(data.get('listings'), dict):
            return pd.DataFrame([data['listings']])
        else:
            return pd.DataFrame([data])
    elif hasattr(data, 'listings') and isinstance(data.listings, list):
        listings = [item.dict() for item in data.listings]
        return pd.DataFrame(listings)
    elif isinstance(data, list):
        return pd.DataFrame(data)
    else:
        return pd.DataFrame([{"error": "Failed to parse data"}])

def display_token_metrics(input_tokens, output_tokens, cost):
    """Display token usage and cost metrics in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Scraping Details")
    st.sidebar.markdown("#### Token Usage")
    st.sidebar.markdown(f"*Input Tokens:* {input_tokens}")
    st.sidebar.markdown(f"*Output Tokens:* {output_tokens}")
    st.sidebar.markdown(f"**Total Cost:** :green-background[**${cost:.4f}**]")

def display_download_options(all_data):
    """Display download buttons for JSON and CSV formats."""
    st.subheader("Download Extracted Data")
    col1, col2 = st.columns(2)
    
    with col1:
        json_data = json.dumps(all_data, default=lambda o: o.dict() if hasattr(o, 'dict') else str(o), indent=4)
        st.download_button(
            "Download JSON",
            data=json_data,
            file_name="scraped_data.json"
        )
    
    with col2:
        # Convert all data to a single DataFrame
        all_listings = []
        for data in all_data:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    continue
            if isinstance(data, dict) and 'listings' in data:
                all_listings.extend(data['listings'])
            elif hasattr(data, 'listings'):
                all_listings.extend([item.dict() for item in data.listings])
            else:
                all_listings.append(data)
        
        combined_df = pd.DataFrame(all_listings)
        st.download_button(
            "Download CSV",
            data=combined_df.to_csv(index=False),
            file_name="scraped_data.csv"
        )

def display_pagination_info(pagination_info):
    """Display pagination information and metrics."""
    st.markdown("---")
    st.subheader("Pagination Information")

    # Display token usage and cost using metrics
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Pagination Details")
    st.sidebar.markdown(f"**Number of Page URLs:** {len(pagination_info['page_urls'])}")
    st.sidebar.markdown("#### Pagination Token Usage")
    st.sidebar.markdown(f"*Input Tokens:* {pagination_info['token_counts']['input_tokens']}")
    st.sidebar.markdown(f"*Output Tokens:* {pagination_info['token_counts']['output_tokens']}")
    st.sidebar.markdown(f"**Pagination Cost:** :blue-background[**${pagination_info['price']:.4f}**]")

    # Display page URLs in a table
    st.write("**Page URLs:**")
    pagination_df = pd.DataFrame(pagination_info["page_urls"], columns=["Page URLs"])
    
    st.dataframe(
        pagination_df,
        column_config={
            "Page URLs": st.column_config.LinkColumn("Page URLs")
        },
        use_container_width=True
    )

    # Download pagination URLs
    st.subheader("Download Pagination URLs")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download Pagination CSV",
            data=pagination_df.to_csv(index=False),
            file_name="pagination_urls.csv"
        )
    with col2:
        st.download_button(
            "Download Pagination JSON",
            data=json.dumps(pagination_info['page_urls'], indent=4),
            file_name="pagination_urls.json"
        )

def display_combined_totals(input_tokens, output_tokens, cost, pagination_info):
    """Display combined totals including both scraping and pagination."""
    st.markdown("---")
    total_input_tokens_combined = input_tokens + pagination_info['token_counts']['input_tokens']
    total_output_tokens_combined = output_tokens + pagination_info['token_counts']['output_tokens']
    total_combined_cost = cost + pagination_info['price']
    
    st.markdown("### Total Counts and Cost (Including Pagination)")
    st.markdown(f"**Total Input Tokens:** {total_input_tokens_combined}")
    st.markdown(f"**Total Output Tokens:** {total_output_tokens_combined}")
    st.markdown(f"**Total Combined Cost:** :rainbow-background[**${total_combined_cost:.4f}**]")
