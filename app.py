import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import time
from typing import Dict, List, Tuple, Optional

# Set page configuration
st.set_page_config(
    page_title="Texas Household Heat Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Sidebar content styling */
    .css-1d391kg .stMarkdown, .css-1cypcdb .stMarkdown {
        color: white;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Metric cards styling */
    [data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Upload section styling */
    .upload-section {
        background-color: rgba(255,255,255,0.15);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Info section styling */
    .info-section {
        background-color: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar text styling */
    .upload-section h3, .info-section h3 {
        color: white !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .info-section p, .info-section li {
        color: rgba(255,255,255,0.9) !important;
    }
    
    /* Success/warning/error message styling */
    .stSuccess, .stWarning, .stError {
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    /* Data summary section */
    .data-summary {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Cache for zip code coordinates to avoid repeated API calls
@st.cache_data
def get_church_coordinates(address: str) -> Optional[Tuple[float, float]]:
    """
    Get latitude and longitude coordinates for a specific address.
    Returns (lat, lon) tuple or None if geocoding fails.
    """
    base_url = "https://nominatim.openstreetmap.org/search"
    
    try:
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us'
        }
        
        headers = {
            'User-Agent': 'Texas-Household-HeatMap/1.0'
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
    
    except Exception as e:
        st.warning(f"Could not geocode address {address}: {str(e)}")
    
    return None

@st.cache_data
def get_zip_coordinates(zip_codes: List[str]) -> Dict[str, Tuple[float, float]]:
    """
    Get latitude and longitude coordinates for zip codes using a geocoding service.
    Returns a dictionary mapping zip codes to (lat, lon) tuples.
    """
    coordinates = {}
    
    # Use a free geocoding service (Nominatim)
    base_url = "https://nominatim.openstreetmap.org/search"
    
    for zip_code in zip_codes:
        try:
            # Add a small delay to respect rate limits
            time.sleep(0.1)
            
            params = {
                'q': f"{zip_code}, Texas, USA",
                'format': 'json',
                'limit': 1,
                'countrycodes': 'us'
            }
            
            headers = {
                'User-Agent': 'Texas-Household-HeatMap/1.0'
            }
            
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    coordinates[zip_code] = (lat, lon)
            
        except Exception as e:
            st.warning(f"Could not geocode zip code {zip_code}: {str(e)}")
            continue
    
    return coordinates

def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that the uploaded CSV has the correct structure.
    Returns (is_valid, error_message).
    """
    required_columns = ['Zip Codes', 'City', 'Number of Households']
    
    # Check if all required columns exist
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check if zip codes column contains valid data
    if df['Zip Codes'].isnull().all():
        return False, "Zip Codes column contains no valid data"
    
    # Check if Number of Households column contains numeric data
    try:
        pd.to_numeric(df['Number of Households'], errors='raise')
    except ValueError:
        return False, "Number of Households column must contain numeric values"
    
    # Check for negative household numbers
    if (pd.to_numeric(df['Number of Households']) < 0).any():
        return False, "Number of Households cannot contain negative values"
    
    return True, ""

def clean_and_process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and process the uploaded data.
    """
    # Create a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Convert zip codes to string and pad with leading zeros if needed
    processed_df['Zip Codes'] = processed_df['Zip Codes'].astype(str).str.zfill(5)
    
    # Convert number of households to numeric
    processed_df['Number of Households'] = pd.to_numeric(processed_df['Number of Households'])
    
    # Remove rows with null zip codes or cities
    processed_df = processed_df.dropna(subset=['Zip Codes', 'City'])
    
    # Group by zip code and sum households (in case of duplicates)
    processed_df = processed_df.groupby(['Zip Codes', 'City'], as_index=False)['Number of Households'].sum()
    
    return processed_df

def create_heat_map(df: pd.DataFrame, coordinates: Dict[str, Tuple[float, float]]) -> go.Figure:
    """
    Create an interactive heat map using Plotly.
    """
    # Prepare data for plotting
    plot_data = []
    
    for _, row in df.iterrows():
        zip_code = row['Zip Codes']
        if zip_code in coordinates:
            lat, lon = coordinates[zip_code]
            plot_data.append({
                'zip_code': zip_code,
                'city': row['City'],
                'households': row['Number of Households'],
                'lat': lat,
                'lon': lon
            })
    
    if not plot_data:
        # Return empty figure if no data to plot
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="No geographical data available for the provided zip codes",
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white'
        )
        return fig
    
    plot_df = pd.DataFrame(plot_data)
    
    # Create a heat map using go.Scattermap for more control
    fig = go.Figure()
    
    # Add household data points with traditional heat map colors
    fig.add_trace(
        go.Scattermap(
            lat=plot_df['lat'],
            lon=plot_df['lon'],
            mode='markers+text',
            marker=dict(
                size=plot_df['households'] * 2 + 10,  # Scale marker size
                color=plot_df['households'],
                colorscale=[[0, 'yellow'], [0.5, 'orange'], [1, 'red']],  # Custom heat map: yellow to red
                reversescale=False,  # Red for high values, yellow for low values
                colorbar=dict(
                    title="Number of Households",
                    x=1.02
                ),
                showscale=True,
                opacity=0.8
            ),
            text=plot_df['households'].astype(str),  # Show household numbers
            textposition='middle center',
            textfont=dict(size=10, color='black'),
            hovertemplate='<b>Zip Code:</b> %{customdata[0]}<br>' +
                         '<b>City:</b> %{customdata[1]}<br>' +
                         '<b>Households:</b> %{customdata[2]}<extra></extra>',
            customdata=plot_df[['zip_code', 'city', 'households']].values,
            name='Household Data',
            showlegend=False
        )
    )
    
    # Add Trademark Church marker
    church_address = "7101 Trail Lake Dr, Fort Worth TX 76133"
    church_coords = get_church_coordinates(church_address)
    
    if church_coords:
        church_lat, church_lon = church_coords
        # Add Trademark Church marker with TM logo
        fig.add_trace(
            go.Scattermap(
                lat=[church_lat],
                lon=[church_lon],
                mode='markers+text',
                marker=dict(
                    size=30,
                    color='darkblue',
                    opacity=1.0
                ),
                text=['TM'],
                textposition='middle center',
                textfont=dict(size=12, color='white', family='Arial Black'),
                hovertemplate='<b>Trademark Church</b><br>7101 Trail Lake Dr<br>Fort Worth, TX 76133<extra></extra>',
                name='Trademark Church (TM)',
                showlegend=True
            )
        )
    
    # Update layout for the map
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        map=dict(
            style='open-street-map',
            center=dict(lat=32.8, lon=-97.0),  # Center closer to Fort Worth area
            zoom=8
        ),
        title=dict(
            text='Texas Household Heat Map with Trademark Church',
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def main():
    """
    Main application function.
    """
    # Modern header section
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🗺️ Texas Household Heat Map Generator</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">Powered By Inman Technology Labs</p>
        <p style="margin: 1rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">Upload a CSV file with Texas zip code household data to generate an interactive heat map</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Modern sidebar for file upload and information
    with st.sidebar:
        st.markdown("""
        <div class="upload-section">
            <h3 style="color: white; margin-top: 0; font-weight: 600;">📁 File Upload</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file with columns: Zip Codes, City, Number of Households"
        )
        

    
    # Main content area
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            with st.spinner("Reading CSV file..."):
                df = pd.read_csv(uploaded_file)
            
            # Display basic information about the file
            st.success(f"✅ Successfully loaded {len(df)} rows from the CSV file")
            
            # Validate CSV structure
            is_valid, error_message = validate_csv_structure(df)
            
            if not is_valid:
                st.error(f"❌ Invalid CSV structure: {error_message}")
                st.markdown("**Expected CSV structure:**")
                st.code("Zip Codes,City,Number of Households\n76123,Fort Worth,74\n76133,Fort Worth,52")
                return
            
            # Process the data
            with st.spinner("Processing data..."):
                processed_df = clean_and_process_data(df)
            
            # Modern metrics display
            st.markdown("<h3 style='color: #667eea; margin-bottom: 1rem;'>📊 Data Overview</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Zip Codes", len(processed_df))
            
            with col2:
                st.metric("Total Households", f"{processed_df['Number of Households'].sum():,}")
            
            with col3:
                st.metric("Unique Cities", processed_df['City'].nunique())
            
            with col4:
                avg_households = processed_df['Number of Households'].mean()
                st.metric("Avg Households/Zip", f"{avg_households:.1f}")
            
            # Show data preview
            with st.expander("📊 Data Preview", expanded=False):
                st.dataframe(processed_df.head(10), use_container_width=True)
            
            # Get coordinates for zip codes
            zip_codes = processed_df['Zip Codes'].unique().tolist()
            
            with st.spinner(f"Geocoding {len(zip_codes)} zip codes... This may take a moment."):
                coordinates = get_zip_coordinates(zip_codes)
            
            # Check if we got coordinates
            geocoded_count = len(coordinates)
            if geocoded_count == 0:
                st.error("❌ Could not geocode any zip codes. Please check that the zip codes are valid Texas zip codes.")
                return
            elif geocoded_count < len(zip_codes):
                missing_count = len(zip_codes) - geocoded_count
                st.warning(f"⚠️ Could not geocode {missing_count} zip codes. Showing data for {geocoded_count} zip codes.")
            else:
                st.success(f"✅ Successfully geocoded all {geocoded_count} zip codes")
            
            # Create and display the heat map
            with st.spinner("Generating heat map..."):
                fig = create_heat_map(processed_df, coordinates)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Modern data summary section
            st.markdown("""
            <div class="data-summary">
                <h3 style="color: #667eea; margin-top: 0;">📈 Data Summary</h3>
                <h4 style="color: #555; margin-bottom: 1rem;">Top 5 Zip Codes by Households</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Display top zip codes in a modern format
            top_5 = processed_df.nlargest(5, 'Number of Households')
            
            for i, (_, row) in enumerate(top_5.iterrows(), 1):
                st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 0.8rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid #667eea;">
                    <strong style="color: #667eea;">#{i}</strong> 
                    <strong>{row['Zip Codes']}</strong> ({row['City']}) - 
                    <span style="color: #28a745; font-weight: bold;">{row['Number of Households']} households</span>
                </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.markdown("Please ensure your CSV file is properly formatted and contains valid data.")
    
    else:
        # Modern welcome section when no file is uploaded
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; background-color: #f8f9fa; border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: #667eea; margin-bottom: 1rem;">Welcome to the Texas Household Heat Map Generator</h3>
            <p style="font-size: 1.1rem; color: #666; margin-bottom: 2rem;">Upload a CSV file using the sidebar to generate an interactive heat map visualization</p>
            <div style="background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 2rem auto; max-width: 600px;">
                <h4 style="color: #667eea; margin-top: 0;">📋 Sample CSV Format</h4>
                <p style="color: #666; margin-bottom: 1.5rem;">Your CSV file should have the following structure:</p>
        """, unsafe_allow_html=True)
        
        sample_data = {
            'Zip Codes': ['76123', '76133', '76036', '76116', '76132'],
            'City': ['Fort Worth', 'Fort Worth', 'Crowley', 'Fort Worth', 'Fort Worth'],
            'Number of Households': [74, 52, 42, 22, 21]
        }
        
        sample_df = pd.DataFrame(sample_data)
        st.dataframe(sample_df, use_container_width=True)
        
        # Download sample CSV with modern styling
        csv_sample = sample_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Sample CSV",
            data=csv_sample,
            file_name="sample_texas_households.csv",
            mime="text/csv"
        )
        
        st.markdown("</div></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
