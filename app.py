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
    initial_sidebar_state="collapsed"
)

# Modern CSS styling with enhanced design system
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --primary-gradient: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #000000 100%);
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --shadow-light: 0 4px 16px rgba(0, 0, 0, 0.3);
    --shadow-medium: 0 8px 24px rgba(0, 0, 0, 0.4);
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.9);
    --text-muted: rgba(255, 255, 255, 0.7);
    --border-radius: 12px;
    --border-radius-sm: 8px;
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background: var(--primary-gradient);
    background-attachment: fixed;
}

.main > div {
    padding-top: var(--spacing-sm);
}

.main-header {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: var(--border-radius);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-lg);
    border: 1px solid var(--glass-border);
    text-align: center;
    color: var(--text-primary);
    box-shadow: var(--shadow-medium);
    transition: all 0.3s ease;
}

.main-header:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 48px rgba(31, 38, 135, 0.3);
}

.main-header h1 {
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: var(--spacing-xs);
}

.main-header p {
    font-weight: 400;
    letter-spacing: 0.01em;
    line-height: 1.6;
}

/* File uploader styling - compact and centered */
.compact-uploader [data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: var(--border-radius-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border: 1px solid var(--glass-border);
    box-shadow: var(--shadow-light);
    transition: all 0.3s ease;
    margin: var(--spacing-md) 0;
}

.compact-uploader [data-testid="stFileUploader"]:hover {
    border-color: #888;
    transform: translateY(-1px);
    box-shadow: var(--shadow-medium);
}

.compact-uploader [data-testid="stFileUploader"] label {
    text-align: center;
    display: block;
    margin-bottom: var(--spacing-xs);
}

.stFileUploader > div {
    background: rgba(255, 255, 255, 0.95);
    border-radius: var(--border-radius-sm);
    border: 2px dashed #667eea;
    padding: var(--spacing-md);
    text-align: center;
    transition: all 0.3s ease;
}

.stFileUploader > div:hover {
    border-color: #764ba2;
    background: rgba(255, 255, 255, 1);
    transform: scale(1.02);
}

.stFileUploader label {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    margin-bottom: var(--spacing-sm) !important;
}

/* Alert styling */
.stAlert > div {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: var(--border-radius-sm);
    border: 1px solid var(--glass-border);
    border-left: 4px solid #667eea;
    color: var(--text-primary);
    box-shadow: var(--shadow-light);
}

/* Metric container styling */
[data-testid="metric-container"] {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    padding: var(--spacing-md);
    border-radius: var(--border-radius-sm);
    color: var(--text-primary);
    box-shadow: var(--shadow-light);
    transition: all 0.3s ease;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
}

[data-testid="metric-container"] > label {
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

[data-testid="metric-container"] > div {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 2rem !important;
}

/* Success/Error/Info/Warning messages */
.stSuccess > div {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    border-radius: var(--border-radius-sm);
    box-shadow: var(--shadow-light);
}

.stError > div {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    border: none;
    border-radius: var(--border-radius-sm);
    box-shadow: var(--shadow-light);
}

.stInfo > div {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: var(--border-radius-sm);
    box-shadow: var(--shadow-light);
}

.stWarning > div {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    border: none;
    border-radius: var(--border-radius-sm);
    box-shadow: var(--shadow-light);
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: var(--border-radius-sm);
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-light);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-medium);
}

/* Progress bar styling */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

/* Spinner styling */
.stSpinner > div {
    border-color: var(--text-primary) !important;
}

/* Data summary section */
.data-summary {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-light);
    margin-top: var(--spacing-lg);
    border: 1px solid var(--glass-border);
    color: var(--text-primary);
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header {
        padding: var(--spacing-md);
        margin-bottom: var(--spacing-md);
    }
    
    .main-header h1 {
        font-size: 1.8rem !important;
    }
    
    [data-testid="metric-container"] > div {
        font-size: 1.5rem !important;
    }
}

/* Smooth animations */
* {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
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
            hovertext=[f"Zip Code: {row['zip_code']}<br>City: {row['city']}<br>Households: {row['households']}" 
                      for _, row in plot_df.iterrows()],
            hoverinfo='text',
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
                hovertext='Trademark Church<br>7101 Trail Lake Dr<br>Fort Worth, TX 76133',
                hoverinfo='text',
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
        ),
        # Fix hover tooltip styling
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="black",
            font_size=12,
            font_family="Inter",
            font_color="black"
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
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">Texas Household Heat Map Generator</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">Powered By Inman Technology Labs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Compact file uploader in header area using columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="compact-uploader">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload a CSV file with Texas zip code household data to generate an interactive heat map",
            type=['csv'],
            help="Upload a CSV file with columns: Zip Codes, City, Number of Households"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sample CSV download button right below uploader
        if uploaded_file is None:
            sample_data = {
                'Zip Codes': ['76123', '76133', '76036', '76116', '76132'],
                'City': ['Fort Worth', 'Fort Worth', 'Crowley', 'Fort Worth', 'Fort Worth'],
                'Number of Households': [74, 52, 42, 22, 21]
            }
            
            sample_df = pd.DataFrame(sample_data)
            csv_sample = sample_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Sample CSV",
                data=csv_sample,
                file_name="sample_texas_households.csv",
                mime="text/csv"
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
            
            # Compact metrics display
            st.markdown("<h3 style='color: #ccc; margin: 0.5rem 0;'>📊 Data Overview</h3>", unsafe_allow_html=True)
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
            
            # Compact data preview
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
            
            # Add spacing before data summary section
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            
            # Consolidated data summary section
            st.markdown("""
            <div class="data-summary">
                <p style="margin: 0.2rem 0 0.5rem 0; font-weight: 600; font-size: 1.2rem; color: var(--text-secondary);">📈 Top 5 Zip Codes by Households</p>
            """, unsafe_allow_html=True)
            
            # Display top zip codes in a consolidated format
            top_5 = processed_df.nlargest(5, 'Number of Households')
            
            summary_content = ""
            for i, (_, row) in enumerate(top_5.iterrows(), 1):
                summary_content += f"""
                <div style="padding: var(--spacing-sm); margin: var(--spacing-xs) 0; 
                            border-left: 3px solid #888; background: rgba(255,255,255,0.03);">
                    <strong style="color: #ccc;">#{i}</strong> 
                    <strong>{row['Zip Codes']}</strong> ({row['City']}) - 
                    <span style="color: #4ade80; font-weight: bold;">{row['Number of Households']} households</span>
                </div>
                """
            
            st.markdown(summary_content + "</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.markdown("Please ensure your CSV file is properly formatted and contains valid data.")
    
    else:
        # Show nothing when no file is uploaded - clean minimal interface
        pass

if __name__ == "__main__":
    main()
