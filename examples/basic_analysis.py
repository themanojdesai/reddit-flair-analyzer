#!/usr/bin/env python3
"""
Basic Analysis Example - Reddit Flair Analyzer

This example demonstrates how to use the Reddit Flair Analyzer
to perform a basic analysis of which flairs have the highest
chance of going viral in a subreddit.

To run this example:
1. Create a Reddit API application at https://www.reddit.com/prefs/apps
2. Set your API credentials in the script or as environment variables:
   - REDDIT_CLIENT_ID
   - REDDIT_CLIENT_SECRET
   - REDDIT_USER_AGENT
3. Run the script: python basic_analysis.py
"""

import os
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from redditflairanalyzer import RedditAnalyzer

# Set your Reddit API credentials here or use environment variables
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'Basic Analysis Example v1.0')

# Configuration
SUBREDDIT = 'datascience'  # Subreddit to analyze
POST_LIMIT = 200           # Number of posts to retrieve
TIME_FILTER = 'month'      # Time filter (all, day, week, month, year)
VIRAL_THRESHOLD = 90       # Percentile threshold for viral posts

def main():
    """Run a basic analysis of subreddit flairs."""
    # Check credentials
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: Reddit API credentials are required.")
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables")
        print("or edit this script to provide them directly.")
        return 1

    print(f"Analyzing r/{SUBREDDIT}...")
    
    # Initialize the analyzer
    analyzer = RedditAnalyzer(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    
    # Create output directory
    output_dir = f"./analysis_results/{SUBREDDIT}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the analysis
    results = analyzer.analyze_subreddit(
        subreddit=SUBREDDIT,
        post_limit=POST_LIMIT,
        time_filter=TIME_FILTER,
        viral_threshold=VIRAL_THRESHOLD
    )
    
    # Extract results
    flair_stats = results.get('flair_stats')
    posts_df = results.get('posts_df')
    viral_threshold = results.get('viral_threshold')
    metrics = results.get('metrics', {})
    
    # Print summary results
    print("\n" + "="*60)
    print(f"ANALYSIS RESULTS FOR r/{SUBREDDIT}")
    print("="*60)
    print(f"Total posts analyzed: {metrics.get('total_posts', 0):,}")
    print(f"Unique flairs found: {metrics.get('total_flairs', 0):,}")
    print(f"Viral threshold score: {viral_threshold:,.0f}")
    print(f"Most viral flair: {metrics.get('most_viral_flair', 'N/A')} ({metrics.get('most_viral_rate', 0):.1%} viral rate)")
    
    # Display top flairs
    print("\nTOP FLAIRS BY VIRAL RATE:")
    if not flair_stats.empty:
        top_flairs = flair_stats.head(10)
        for i, (_, flair) in enumerate(top_flairs.iterrows(), 1):
            print(f"{i}. {flair['flair']}: {flair['viral_rate']:.1%} viral rate, {flair['total_posts']} posts")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    viz_files = analyzer.visualize(
        results,
        output_dir=output_dir,
        interactive=True
    )
    
    # Export results to CSV
    export_path = analyzer.export(
        results,
        format="csv",
        filename=os.path.join(output_dir, f"{SUBREDDIT}_analysis")
    )
    
    # Print file paths
    if viz_files:
        print(f"\nCreated {len(viz_files)} visualization files in {output_dir}")
    
    if export_path:
        print(f"Results exported to: {export_path}")
    
    # Custom analysis: Post time vs. Score
    custom_analysis(posts_df, output_dir)
    
    print("\nAnalysis complete!")
    return 0

def custom_analysis(posts_df, output_dir):
    """Perform a custom analysis of posting time vs. score."""
    if 'created_utc' not in posts_df.columns or posts_df.empty:
        return
    
    print("\nPerforming custom analysis of posting time vs. score...")
    
    # Extract hour of day
    posts_df['hour'] = posts_df['created_utc'].dt.hour
    
    # Analyze hour vs. score
    hour_stats = posts_df.groupby('hour')['score'].mean().reset_index()
    
    # Find the best hour to post
    best_hour = hour_stats.loc[hour_stats['score'].idxmax()]
    
    print(f"Best hour to post: {best_hour['hour']}:00 UTC")
    print(f"Average score at this hour: {best_hour['score']:.1f}")
    
    # Create a visualization
    plt.figure(figsize=(12, 6))
    sns.barplot(x='hour', y='score', data=hour_stats, color='royalblue')
    plt.title(f'Average Score by Hour of Day - r/{SUBREDDIT}', fontsize=16)
    plt.xlabel('Hour (UTC)', fontsize=14)
    plt.ylabel('Average Score', fontsize=14)
    plt.xticks(range(0, 24))
    plt.grid(axis='y', alpha=0.3)
    
    # Save the figure
    hour_analysis_path = os.path.join(output_dir, 'posting_hour_analysis.png')
    plt.savefig(hour_analysis_path)
    plt.close()
    
    print(f"Custom analysis saved to: {hour_analysis_path}")

if __name__ == "__main__":
    sys.exit(main())