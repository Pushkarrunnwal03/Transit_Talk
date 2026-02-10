from flask import Flask, render_template, send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import io
import base64
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

# Set seaborn style
sns.set_theme(style="whitegrid")
sns.set_palette("husl")

# Google Sheets configuration
GOOGLE_SHEET_ID = '1modLnxoX48zBDSV495GvOepaNcqXHErUAb0gU5sNQxw'
GOOGLE_SHEET_URL = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv'

def load_survey_data():
    """Load survey data from Google Sheets"""
    try:
        df = pd.read_csv(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        print(f"Error loading data from Google Sheets: {e}")
        print("Please ensure the Google Sheet is shared as 'Anyone with the link can view'")
        return None

def get_question_mapping():
    """Get question mappings - returns empty dict if no Questions sheet"""
    # For simplicity, we'll use column names directly
    # You can add a second sheet with gid parameter if needed
    return {}

def create_plot(df, column, questions):
    """Create plot for a column"""
    fig, ax = plt.subplots(figsize=(10, 6))
    question_text = questions.get(column, column.strip())
    
    # Clean and truncate title
    clean_title = question_text.replace('�', '-').replace('  ', ' ')
    if len(clean_title) > 80:
        clean_title = clean_title[:77] + '...'
    
    if df[column].dtype in [np.int64, np.float64]:
        # Numerical data - histogram
        sns.histplot(data=df, x=column, bins=10, kde=True, ax=ax, color='steelblue')
        ax.set_title(clean_title, fontweight='bold', fontsize=9, wrap=True, pad=10)
        ax.set_xlabel('Rating')
        ax.set_ylabel('Frequency')
        mean_val = df[column].mean()
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.1f}')
        ax.legend()
    else:
        # Categorical data - bar chart
        counts = df[column].value_counts()
        # Truncate long labels
        display_labels = [str(label)[:50] + '...' if len(str(label)) > 50 else str(label) for label in counts.index]
        sns.barplot(x=counts.values, y=display_labels, ax=ax, hue=display_labels, palette='viridis', legend=False)
        ax.set_xlabel('Number of Responses')
        ax.set_ylabel('')
        ax.set_title(clean_title, fontweight='bold', fontsize=9, wrap=True, pad=10)
        for i, v in enumerate(counts.values):
            ax.text(v + 0.1, i, str(v), va='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout(pad=2.0)
    
    # Convert plot to base64 string
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    
    return plot_url

def create_cross_analysis(df, col1, col2, questions):
    """Create cross-tabulation heatmap"""
    fig, ax = plt.subplots(figsize=(8, 6))
    try:
        cross_tab = pd.crosstab(df[col1], df[col2])
        sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Count'})
        q1 = questions.get(col1, col1)
        q2 = questions.get(col2, col2)
        ax.set_title(f"{q1[:30]}... vs {q2[:30]}...", fontweight='bold', fontsize=10)
        ax.set_xlabel(col2)
        ax.set_ylabel(col1)
    except:
        ax.text(0.5, 0.5, 'Insufficient data', ha='center', va='center', transform=ax.transAxes)
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    
    return plot_url

@app.route('/')
def dashboard():
    """Main dashboard page"""
    df = load_survey_data()
    
    if df is None:
        return "<h1>Error loading survey data!</h1><p>Make sure the Google Sheet is publicly accessible.</p>"
    
    questions = get_question_mapping()
    
    # Calculate metrics
    total_responses = len(df)
    
    # Get latest timestamp
    timestamp_col = 'Timestamp' if 'Timestamp' in df.columns else 'timestamp' if 'timestamp' in df.columns else None
    if timestamp_col:
        try:
            latest = pd.to_datetime(df[timestamp_col]).max().strftime('%d-%b %H:%M')
        except:
            latest = "N/A"
    else:
        latest = "N/A"
    
    # Calculate average ratings
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    excluded_cols = ['timestamp', 'Timestamp', 'Email Address', 'email', 'Email']
    numerical_cols = [col for col in numerical_cols if col not in excluded_cols]
    
    avg_rating = df[numerical_cols].mean().mean() if numerical_cols else 0
    total_questions = len([col for col in df.columns if col not in excluded_cols])
    
    # Get all question columns
    all_question_cols = [col for col in df.columns if col not in excluded_cols]
    
    # Create plots for all questions
    plots = []
    for column in all_question_cols:
        plot_url = create_plot(df, column, questions)
        plots.append({
            'question': questions.get(column, column.replace('_', ' ').title()),
            'plot': plot_url
        })
    
    # Create cross-analysis plots
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    excluded_cols = ['timestamp', 'Timestamp', 'Email Address', 'email', 'Email']
    categorical_cols = [col for col in categorical_cols if col not in excluded_cols]
    
    cross_plots = []
    if len(categorical_cols) >= 2:
        cross_plot1 = create_cross_analysis(df, categorical_cols[0], categorical_cols[1], questions)
        cross_plots.append(cross_plot1)
        
        if len(categorical_cols) >= 3:
            cross_plot2 = create_cross_analysis(df, categorical_cols[1], categorical_cols[2], questions)
            cross_plots.append(cross_plot2)
    
    return render_template('dashboard.html',
                         total_responses=total_responses,
                         latest=latest,
                         avg_rating=f"{avg_rating:.2f}",
                         total_questions=total_questions,
                         current_time=datetime.now().strftime('%H:%M:%S'),
                         plots=plots,
                         cross_plots=cross_plots)

@app.route('/download')
def download():
    """Download data as CSV"""
    df = load_survey_data()
    if df is None:
        return "Error: Could not load data", 500
    
    # Create CSV in memory
    csv_data = df.to_csv(index=False)
    return csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=survey_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    }

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚌 Transit Talks - Google Sheets Dashboard")
    print("="*60)
    print(f"\n✅ Server starting...")
    print(f"🔗 Data source: Google Sheets (ID: {GOOGLE_SHEET_ID[:20]}...)")
    print(f"🌐 Open your browser and go to: http://localhost:5000")
    print(f"🔄 Dashboard auto-refreshes every 10 seconds")
    print(f"\n⚠️  Make sure Google Sheet is shared publicly")
    print(f"⚠️  Press CTRL+C to stop the server\n")
    print("="*60 + "\n")
    
    # Use environment variable PORT for production (Render) or default to 5000 for local
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
