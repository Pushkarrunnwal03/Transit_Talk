import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time

# Set page configuration
st.set_page_config(
    page_title="Transit Talks",
    page_icon="🚌",
    layout="wide"
)

# Set seaborn style
sns.set_theme(style="whitegrid")
sns.set_palette("husl")

# Add custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Google Sheets configuration
GOOGLE_SHEET_ID = '1modLnxoX48zBDSV495GvOepaNcqXHErUAb0gU5sNQxw'
GOOGLE_SHEET_URL = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv'

# Function to load survey data from Google Sheets
@st.cache_data(ttl=10)  # Cache data for 10 seconds
def load_survey_data():
    """Load survey data from Google Sheets"""
    try:
        df = pd.read_csv(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        st.error(f"⚠️ Error loading survey data from Google Sheets: {str(e)}")
        st.error("Please ensure the Google Sheet is shared as 'Anyone with the link can view'")
        return None

def get_question_mapping():
    """Get question mappings - returns empty dict if no Questions sheet"""
    # For simplicity, we'll use column names directly
    # You can add a second sheet with gid parameter if needed
    return {}

def plot_categorical_distribution(df, column, title, ax, horizontal=True):
    """Plot distribution for categorical data"""
    counts = df[column].value_counts()
    # Truncate long labels for better display
    display_labels = [str(label)[:50] + '...' if len(str(label)) > 50 else str(label) for label in counts.index]
    
    if horizontal:
        sns.barplot(x=counts.values, y=display_labels, ax=ax, hue=display_labels, palette='viridis', legend=False)
        ax.set_xlabel('Number of Responses')
        ax.set_ylabel('')
        for i, v in enumerate(counts.values):
            ax.text(v + 0.1, i, str(v), va='center', fontweight='bold', fontsize=9)
    else:
        sns.barplot(x=display_labels, y=counts.values, ax=ax, hue=display_labels, palette='viridis', legend=False)
        ax.set_ylabel('Number of Responses')
        ax.set_xlabel('')
        ax.tick_params(axis='x', rotation=45)
        for i, v in enumerate(counts.values):
            ax.text(i, v + 0.1, str(v), ha='center', fontweight='bold', fontsize=9)
    # Truncate title and clean special characters
    clean_title = title.strip().replace('�', '-').replace('  ', ' ')
    if len(clean_title) > 80:
        clean_title = clean_title[:77] + '...'
    ax.set_title(clean_title, fontweight='bold', fontsize=9, wrap=True, pad=10)
    return ax

def plot_numerical_distribution(df, column, title, ax):
    """Plot distribution for numerical data"""
    sns.histplot(data=df, x=column, bins=10, kde=True, ax=ax, color='steelblue')
    ax.set_title(title, fontweight='bold', fontsize=10)
    ax.set_xlabel('Rating')
    ax.set_ylabel('Frequency')
    mean_val = df[column].mean()
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.1f}')
    ax.legend()
    return ax

def create_cross_analysis(df, col1, col2, title, ax):
    """Create cross-tabulation heatmap"""
    try:
        cross_tab = pd.crosstab(df[col1], df[col2])
        sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Count'})
        ax.set_title(title, fontweight='bold', fontsize=10)
        ax.set_xlabel(col2)
        ax.set_ylabel(col1)
    except:
        ax.text(0.5, 0.5, 'Insufficient data for cross-analysis', 
                ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title, fontweight='bold', fontsize=10)
    return ax

# Main dashboard
def main():
    # Header
    st.markdown('<div class="main-header">🚌 Transit Talks</div>', unsafe_allow_html=True)
    
    # Last updated timestamp
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        st.info(f"🔄 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Load data
    with st.spinner('Loading survey data from Google Sheets...'):
        df = load_survey_data()
    
    if df is None:
        st.stop()
    
    # Get question mappings
    questions = get_question_mapping()
    
    # Key Metrics
    st.subheader("📈 Survey Overview")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric("Total Responses", len(df))
    
    with metric_cols[1]:
        timestamp_col = 'Timestamp' if 'Timestamp' in df.columns else 'timestamp' if 'timestamp' in df.columns else None
        if timestamp_col:
            try:
                latest = pd.to_datetime(df[timestamp_col]).max()
                st.metric("Latest Response", latest.strftime('%d-%b %H:%M'))
            except:
                st.metric("Data Source", "Google Sheets")
        else:
            st.metric("Data Source", "Google Sheets")
    
    # Calculate average ratings (for numerical columns)
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    excluded_cols = ['timestamp', 'Timestamp', 'Email Address', 'email', 'Email']
    for col in excluded_cols:
        if col in numerical_cols:
            numerical_cols.remove(col)
    
    with metric_cols[2]:
        if numerical_cols:
            avg_rating = df[numerical_cols].mean().mean()
            st.metric("Avg Rating", f"{avg_rating:.2f}")
        else:
            st.metric("Question Types", "Multiple Choice")
    
    with metric_cols[3]:
        question_cols = [col for col in df.columns if col not in ['Timestamp', 'timestamp', 'Email Address', 'email', 'Email']]
        st.metric("Total Questions", len(question_cols))
    
    
    st.divider()
    
    # Dynamic Visualizations based on Excel data
    st.subheader("📊 Survey Results Analysis")
    
    # Separate columns into categorical and numerical
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    excluded_cols = ['timestamp', 'Timestamp', 'Email Address', 'email', 'Email']
    categorical_cols = [col for col in categorical_cols if col not in excluded_cols]
    
    # Create visualizations dynamically
    all_question_cols = [col for col in df.columns if col not in excluded_cols]
    
    # Plot all questions in a grid
    num_questions = len(all_question_cols)
    cols_per_row = 2
    num_rows = (num_questions + cols_per_row - 1) // cols_per_row
    
    for row_idx in range(num_rows):
        viz_cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            question_idx = row_idx * cols_per_row + col_idx
            
            if question_idx < num_questions:
                column_name = all_question_cols[question_idx]
                
                with viz_cols[col_idx]:
                    # Get question text from mapping or use column name
                    question_text = questions.get(column_name, column_name.strip())
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Determine if numerical or categorical
                    if df[column_name].dtype in [np.int64, np.float64]:
                        plot_numerical_distribution(df, column_name, question_text, ax)
                    else:
                        plot_categorical_distribution(df, column_name, question_text, ax, horizontal=True)
                    
                    plt.tight_layout(pad=2.0)
                    st.pyplot(fig)
                    plt.close()
    
    st.divider()
    
    # Cross-Analysis Section (if we have categorical columns)
    if len(categorical_cols) >= 2:
        st.subheader("🔍 Cross-Analysis")
        
        cross_cols = st.columns(2)
        
        # Select two categorical columns for cross-analysis
        with cross_cols[0]:
            if len(categorical_cols) >= 2:
                fig, ax = plt.subplots(figsize=(8, 6))
                q1 = questions.get(categorical_cols[0], categorical_cols[0])
                q2 = questions.get(categorical_cols[1], categorical_cols[1])
                create_cross_analysis(df, categorical_cols[0], categorical_cols[1], 
                                    f"{q1[:30]}... vs {q2[:30]}...", ax)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
        
        with cross_cols[1]:
            if len(categorical_cols) >= 3:
                fig, ax = plt.subplots(figsize=(8, 6))
                q1 = questions.get(categorical_cols[1], categorical_cols[1])
                q2 = questions.get(categorical_cols[2], categorical_cols[2])
                create_cross_analysis(df, categorical_cols[1], categorical_cols[2], 
                                    f"{q1[:30]}... vs {q2[:30]}...", ax)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()
        
        st.divider()
    
    # Summary Statistics
    with st.expander("📊 Statistical Summary"):
        st.subheader("Numerical Data Summary")
        if numerical_cols:
            st.dataframe(df[numerical_cols].describe(), use_container_width=True)
        else:
            st.info("No numerical data available")
        
        st.subheader("Categorical Data Summary")
        if categorical_cols:
            for cat_col in categorical_cols:
                st.write(f"**{questions.get(cat_col, cat_col)}**")
                st.write(df[cat_col].value_counts())
                st.write("---")
        else:
            st.info("No categorical data available")
    
    # Raw Data Section (Expandable)
    with st.expander("📋 View Raw Survey Data"):
        st.dataframe(df, use_container_width=True)
        
        # Download button for CSV
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv_data,
            file_name=f"survey_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Download button for Excel
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Survey Data')
        output.seek(0)
        
        st.download_button(
            label="📥 Download Data as Excel",
            data=output,
            file_name=f"survey_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Auto-refresh message
    st.markdown("---")
    st.caption("⏱️ Dashboard auto-refreshes every 10 seconds to fetch latest data from Google Sheets")
    
    # Trigger auto-refresh after 10 seconds
    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    main()
