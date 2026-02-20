# -*- coding: utf-8 -*-
from flask import Flask, render_template
import pandas as pd
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

# Google Sheets configuration
GOOGLE_SHEET_ID = '1GSYHcRuGVGW4UBERyHcWX2iS_kW5NgNUq5lpqXFJbE8'
GOOGLE_SHEET_URL = (
    f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}'
    f'/export?format=csv&gid=1686224199'
)


def load_survey_data():
    """Load survey data from Google Sheets"""
    try:
        df = pd.read_csv(GOOGLE_SHEET_URL)
        return df
    except Exception as e:
        print(f"Error loading data from Google Sheets: {e}")
        print("Please ensure the Google Sheet is shared as 'Anyone with the link can view'")
        return None


EXCLUDED_KEYWORDS = ['timestamp', 'email', 'name', 'age', 'are you a resident']


def is_question_col(col):
    col_lower = col.lower().strip()
    return not any(kw in col_lower for kw in EXCLUDED_KEYWORDS)


def clean_text(text):
    return text.strip().replace('  ', ' ')


@app.route('/')
def dashboard():
    df = load_survey_data()
    if df is None:
        return "<h1>Error loading survey data!</h1><p>Make sure the Google Sheet is publicly accessible.</p>"

    total_responses = len(df)
    all_question_cols = [col for col in df.columns if is_question_col(col)]
    total_questions = len(all_question_cols)

    key_insights = []
    for column in all_question_cols:
        if df[column].isna().all():
            continue
        value_counts = df[column].value_counts(dropna=True)
        if len(value_counts) == 0:
            continue
        top_value = value_counts.index[0]
        top_count = int(value_counts.iloc[0])
        percentage = int((top_count / total_responses) * 100)
        key_insights.append({
            'question': clean_text(column),
            'top_answer': clean_text(str(top_value)),
            'percentage': percentage,
            'count': top_count,
            'total': total_responses,
        })

    key_insights.sort(key=lambda x: x['percentage'], reverse=True)

    numerical_cols = [col for col in df.select_dtypes(include=[np.number]).columns if is_question_col(col)]
    avg_rating = float(df[numerical_cols].mean().mean()) if numerical_cols else 0.0

    return render_template(
        'dashboard.html',
        total_responses=total_responses,
        total_questions=total_questions,
        avg_rating=f"{avg_rating:.2f}",
        current_time=datetime.now().strftime('%H:%M:%S'),
        key_insights=key_insights,
    )


@app.route('/download')
def download():
    df = load_survey_data()
    if df is None:
        return "Error: Could not load data", 500
    csv_data = df.to_csv(index=False)
    return csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=survey_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
    }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
