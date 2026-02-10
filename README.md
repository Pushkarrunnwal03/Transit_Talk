# Transit Talks - Survey Dashboard 🚌

A real-time survey analytics dashboard for analyzing public transport feedback. Built with Streamlit and Seaborn, it automatically refreshes every 10 seconds to display the latest survey data from Google Sheets.

## Features

- 📊 **Real-time Analytics**: Auto-refreshes every 10 seconds to fetch latest data from Google Sheets
- 🌐 **Google Sheets Integration**: Direct connection to live Google Sheets data
- 🚌 **Comprehensive Survey**: Covers all aspects of public transport satisfaction
- 📈 **Dynamic Visualizations**: Automatically adapts to your data structure
  - Categorical distributions (bar charts)
  - Numerical distributions (histograms with KDE)
  - Cross-analysis (heatmaps)
  - Statistical summaries
- 🎨 **Beautiful Graphs**: Uses Seaborn for professional data visualizations
- 💾 **Export Options**: Download data as CSV or Excel format
- 🔄 **Fully Dynamic**: Update Google Sheets, and the dashboard automatically refreshes - no code changes needed!
- 📱 **Responsive Design**: Wide layout optimized for dashboard viewing

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Google Sheets Setup

**IMPORTANT**: The Google Sheet must be publicly accessible for the dashboard to read it.

1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1modLnxoX48zBDSV495GvOepaNcqXHErUAb0gU5sNQxw/edit?usp=sharing

2. Click the **Share** button in the top right

3. Under "General access", select **"Anyone with the link"** and set permission to **"Viewer"**

4. Click **Done**

## Usage

### Running the Streamlit Dashboard (Recommended)

```bash
streamlit run dashboard.py
```

The dashboard will open in your default web browser at `http://localhost:8501` and automatically refresh every 10 seconds.

### Running the Flask Dashboard (Alternative)

```bash
python app.py
```

Open your browser and go to `http://localhost:5000`

## Changing the Google Sheet

To use a different Google Sheet, update the `GOOGLE_SHEET_ID` in both `dashboard.py` and `app.py`:

```python
GOOGLE_SHEET_ID = 'your-google-sheet-id-here'
```

To find your Google Sheet ID:
- Open your Google Sheet
- Look at the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`
- Copy the `SHEET_ID` part

## Data Structure

The Google Sheet should contain survey responses with:
- Column headers in the first row (e.g., `timestamp`, `primary_transport`, `satisfaction_level`, etc.)
- Each row representing one survey response
- Mix of categorical and numerical data supported

## Customizing the Survey

**No code changes required!** Just modify the Google Sheet:

1. **Add/Remove Questions**: Add or remove columns in the Google Sheet
2. **Change Data**: Edit response values directly in Google Sheets
3. **Add New Responses**: Append new rows to the sheet
4. The dashboard will automatically detect and visualize the changes within 10 seconds

## How It Works

The dashboard is **fully dynamic**:
- Connects to Google Sheets via CSV export URL
- Automatically detects categorical vs numerical columns
- Creates appropriate visualizations for each data type
- Adapts the layout based on number of questions
- Generates cross-analysis for categorical variables
- Refreshes every 10 seconds to fetch latest data
- No hardcoded column names or question dependencies

## Technologies Used

- **Streamlit**: Web dashboard framework
- **Flask**: Alternative web framework option
- **Seaborn**: Statistical data visualization
- **Matplotlib**: Plotting library
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **OpenPyXL**: Excel export functionality
- **Google Sheets**: Cloud-based data source

## Troubleshooting

### Error: "Error loading survey data from Google Sheets"

1. **Check if the Google Sheet is publicly accessible**:
   - Open the Google Sheet URL
   - Click "Share" → Set to "Anyone with the link" → "Viewer"

2. **Verify the Google Sheet ID**:
   - Make sure `GOOGLE_SHEET_ID` in the code matches your sheet

3. **Check internet connection**:
   - The dashboard needs internet access to fetch data from Google Sheets

### Dashboard shows "No data available"

- Make sure your Google Sheet has data in it
- Check that column headers are in the first row
- Verify the sheet is the first sheet (or default sheet) in your Google Sheets document
