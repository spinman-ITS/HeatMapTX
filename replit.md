# Texas Household Heat Map

## Overview

This project is a Streamlit-based web application that creates heat maps for Texas households using zip code data. The application visualizes geographic data by plotting zip codes on interactive maps with household-related metrics. It uses geocoding services to convert zip codes to coordinates and displays the results using Plotly visualizations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple single-file architecture pattern typical of data visualization dashboards:

- **Frontend**: Streamlit framework providing the web interface
- **Data Processing**: Pandas for data manipulation and analysis
- **Visualization**: Plotly (Express and Graph Objects) for interactive maps and charts
- **Geocoding**: OpenStreetMap Nominatim API for converting zip codes to coordinates
- **Caching**: Streamlit's built-in caching system for performance optimization

## Key Components

### 1. Web Framework
- **Streamlit**: Chosen for rapid prototyping and easy deployment of data applications
- Configured with wide layout and expanded sidebar for better user experience
- Page configuration includes custom title, icon, and layout settings

### 2. Data Visualization
- **Plotly Express & Graph Objects**: Selected for interactive mapping capabilities
- Supports heat map visualizations with geographic coordinate plotting
- Enables zoom, pan, and hover interactions on maps

### 3. Geocoding Service
- **Nominatim (OpenStreetMap)**: Free geocoding service for converting zip codes to coordinates
- Implements rate limiting (0.1 second delays) to respect API constraints
- Includes proper headers and error handling for API requests
- Focuses specifically on Texas, USA locations with country code filtering

### 4. Data Management
- **Pandas**: Standard library for data manipulation and CSV/Excel file handling
- **Caching Strategy**: Uses Streamlit's `@st.cache_data` decorator to cache geocoding results
- Prevents redundant API calls for the same zip codes across sessions

## Data Flow

1. **Input**: User provides zip code data (likely through file upload or manual entry)
2. **Geocoding**: Application converts zip codes to latitude/longitude coordinates using Nominatim API
3. **Caching**: Coordinates are cached to avoid repeated API calls
4. **Visualization**: Data is processed and displayed as interactive heat maps using Plotly
5. **Display**: Results are rendered in the Streamlit web interface

## External Dependencies

### APIs
- **Nominatim OpenStreetMap**: Free geocoding service for coordinate conversion
  - Rate limited to respect service constraints
  - Includes proper User-Agent headers
  - Timeout protection (10 seconds)

### Python Libraries
- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualization library
- `requests`: HTTP library for API calls
- `json`: JSON data handling
- `time`: Rate limiting functionality
- `typing`: Type hints for better code documentation

## Deployment Strategy

The application is designed for easy deployment on various platforms:

- **Streamlit Cloud**: Natural choice given the framework
- **Local Development**: Can be run locally with `streamlit run app.py`
- **Container Deployment**: Single-file structure makes containerization straightforward
- **Cloud Platforms**: Compatible with Heroku, AWS, GCP, or Azure deployment

### Configuration Considerations
- No database required (stateless application)
- Minimal external dependencies
- Caching implemented for performance optimization
- Rate limiting built-in for API compliance

The architecture prioritizes simplicity and rapid development while maintaining good performance through strategic caching and rate limiting. The single-file approach makes the application easy to understand, modify, and deploy.