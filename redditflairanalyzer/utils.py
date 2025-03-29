"""
Utility functions for the Reddit Flair Analyzer.

This module provides helper functions for data processing,
file operations, and other common tasks.
"""

import os
import json
import pandas as pd
from datetime import datetime
from .logger import get_logger

# Get module logger
logger = get_logger("utils")

def export_results(results, format="csv", filename=None):
    """
    Export analysis results to file.
    
    Args:
        results (dict): Analysis results from FlairAnalyzer
        format (str, optional): Export format (csv, excel, json). Defaults to "csv".
        filename (str, optional): Custom filename. Defaults to auto-generated.
        
    Returns:
        str: Path to exported file
    """
    # Extract data from results
    flair_stats = results.get('flair_stats')
    posts_df = results.get('posts_df')
    viral_threshold = results.get('viral_threshold')
    subreddit = results.get('subreddit')
    metrics = results.get('metrics', {})
    
    if flair_stats is None or flair_stats.empty:
        logger.error("No flair statistics available for export")
        return None
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{subreddit}_flair_analysis_{timestamp}"
    
    # Ensure the directory exists
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # Export based on format
    if format.lower() == 'csv':
        # Export flair stats to CSV
        csv_path = f"{filename}.csv"
        flair_stats.to_csv(csv_path, index=False)
        logger.info(f"Exported flair statistics to CSV: {csv_path}")
        
        # Export posts to a separate CSV if available
        if posts_df is not None:
            posts_csv_path = f"{filename}_posts.csv"
            posts_df.to_csv(posts_csv_path, index=False)
            logger.info(f"Exported posts to CSV: {posts_csv_path}")
        
        return csv_path
    
    elif format.lower() == 'excel':
        # Create Excel writer
        excel_path = f"{filename}.xlsx"
        with pd.ExcelWriter(excel_path) as writer:
            # Write flair stats to sheet
            flair_stats.to_excel(writer, sheet_name='Flair Statistics', index=False)
            
            # Write metadata to a sheet
            metadata = pd.DataFrame([
                {'Key': 'Subreddit', 'Value': subreddit},
                {'Key': 'Analysis Date', 'Value': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {'Key': 'Total Posts', 'Value': metrics.get('total_posts', 0)},
                {'Key': 'Total Flairs', 'Value': metrics.get('total_flairs', 0)},
                {'Key': 'Viral Threshold', 'Value': viral_threshold},
                {'Key': 'Most Viral Flair', 'Value': metrics.get('most_viral_flair', 'N/A')},
                {'Key': 'Most Viral Rate', 'Value': metrics.get('most_viral_rate', 0)},
                {'Key': 'Highest Avg Score Flair', 'Value': metrics.get('highest_avg_score_flair', 'N/A')},
                {'Key': 'Highest Avg Score', 'Value': metrics.get('highest_avg_score', 0)}
            ])
            metadata.to_excel(writer, sheet_name='Analysis Metadata', index=False)
            
            # Write posts to a sheet if available
            if posts_df is not None:
                posts_df.to_excel(writer, sheet_name='Posts Data', index=False)
        
        logger.info(f"Exported analysis results to Excel: {excel_path}")
        return excel_path
    
    elif format.lower() == 'json':
        # Create JSON structure
        json_data = {
            'metadata': {
                'subreddit': subreddit,
                'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'viral_threshold': viral_threshold,
                'metrics': metrics
            },
            'flair_stats': flair_stats.to_dict('records')
        }
        
        # Export to JSON file
        json_path = f"{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exported analysis results to JSON: {json_path}")
        return json_path
    
    else:
        logger.error(f"Unsupported export format: {format}")
        return None

def ensure_directory(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        bool: True if the directory exists or was created, False otherwise
    """
    if not directory_path:
        return False
    
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            logger.debug(f"Created directory: {directory_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory {directory_path}: {e}")
            return False
    
    return True

def validate_reddit_credentials(client_id, client_secret, user_agent):
    """
    Validate Reddit API credentials format.
    
    Args:
        client_id (str): Reddit API client ID
        client_secret (str): Reddit API client secret
        user_agent (str): Reddit API user agent
        
    Returns:
        tuple: (is_valid, error_message)
    """
    is_valid = True
    error_message = None
    
    # Check client_id
    if not client_id or not isinstance(client_id, str) or len(client_id) < 5:
        is_valid = False
        error_message = "Client ID is missing or invalid"
    
    # Check client_secret
    elif not client_secret or not isinstance(client_secret, str) or len(client_secret) < 5:
        is_valid = False
        error_message = "Client secret is missing or invalid"
    
    # Check user_agent
    elif not user_agent or not isinstance(user_agent, str) or len(user_agent) < 5:
        is_valid = False
        error_message = "User agent is missing or invalid"
    
    return is_valid, error_message

def format_table_for_console(dataframe, max_rows=10, max_width=120):
    """
    Format a DataFrame as a pretty console table.
    
    Args:
        dataframe (pandas.DataFrame): DataFrame to format
        max_rows (int, optional): Maximum number of rows to display. Defaults to 10.
        max_width (int, optional): Maximum width of the table. Defaults to 120.
        
    Returns:
        str: Formatted table string
    """
    from tabulate import tabulate
    
    # Limit rows
    if len(dataframe) > max_rows:
        half_rows = max_rows // 2
        df_display = pd.concat([dataframe.head(half_rows), dataframe.tail(half_rows)])
    else:
        df_display = dataframe.copy()
    
    # Format numeric columns
    for col in df_display.select_dtypes(include=['float']).columns:
        if 'rate' in col.lower() or 'ratio' in col.lower() or 'percentage' in col.lower():
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2%}")
        else:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}")
    
    # Create table
    table = tabulate(
        df_display, 
        headers=df_display.columns,
        tablefmt="pretty",
        showindex=False
    )
    
    # Truncate table width if necessary
    if max_width > 0:
        table_lines = table.split('\n')
        if any(len(line) > max_width for line in table_lines):
            truncated_lines = []
            for line in table_lines:
                if len(line) > max_width:
                    truncated_lines.append(line[:max_width-3] + '...')
                else:
                    truncated_lines.append(line)
            table = '\n'.join(truncated_lines)
    
    # Add row count indicator if rows were omitted
    if len(dataframe) > max_rows:
        table += f"\n(Showing {max_rows} of {len(dataframe)} rows)"
    
    return table

def format_timestamp(timestamp, format="%Y-%m-%d %H:%M:%S"):
    """
    Format a timestamp.
    
    Args:
        timestamp (datetime or float): Timestamp to format
        format (str, optional): Format string. Defaults to "%Y-%m-%d %H:%M:%S".
        
    Returns:
        str: Formatted timestamp
    """
    if isinstance(timestamp, (int, float)):
        timestamp = datetime.fromtimestamp(timestamp)
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime(format)
    
    return str(timestamp)

def sanitize_filename(filename):
    """
    Sanitize a filename to be safe for all operating systems.
    
    Args:
        filename (str): Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename