"""
Utility functions for the Exotel IVR Dashboard
"""

from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd


def format_phone_number(number: str) -> str:
    """Format phone number for display"""
    if number.startswith('+91'):
        num = number[3:]
        return f"+91 {num[:5]} {num[5:]}"
    return number


def calculate_success_rate(df: pd.DataFrame) -> float:
    """Calculate the call success rate"""
    if len(df) == 0:
        return 0.0
    completed = len(df[df['Status'] == 'completed'])
    return (completed / len(df)) * 100


def get_peak_hours(df: pd.DataFrame) -> List[int]:
    """Get the top 3 peak hours for calls"""
    df['Hour'] = pd.to_datetime(df['DateCreated']).dt.hour
    hourly_counts = df.groupby('Hour').size().sort_values(ascending=False)
    return hourly_counts.head(3).index.tolist()


def format_duration(seconds: int) -> str:
    """Format duration in seconds to readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def filter_by_date_range(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Filter dataframe by date range"""
    df['DateCreated'] = pd.to_datetime(df['DateCreated'])
    mask = (df['DateCreated'].dt.date >= start_date) & (df['DateCreated'].dt.date <= end_date)
    return df[mask]


def get_call_metrics(df: pd.DataFrame) -> Dict:
    """Calculate various call metrics"""
    metrics = {
        'total_calls': len(df),
        'completed_calls': len(df[df['Status'] == 'completed']),
        'failed_calls': len(df[df['Status'].isin(['failed', 'busy', 'no-answer'])]),
        'avg_duration': df[df['Duration'] > 0]['Duration'].mean(),
        'total_duration': df['Duration'].sum(),
        'total_cost': df['Price'].sum(),
        'avg_cost': df['Price'].mean(),
    }
    return metrics


def export_to_csv(df: pd.DataFrame, filename: str = None) -> str:
    """Export dataframe to CSV"""
    if filename is None:
        filename = f"call_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    df.to_csv(filename, index=False)
    return filename
