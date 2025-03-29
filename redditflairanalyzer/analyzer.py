"""
Statistical analysis module for the Reddit Flair Analyzer.

This module handles all data analysis of Reddit posts, calculating
metrics to determine which flairs have the highest viral potential.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tabulate import tabulate
from .logger import get_logger

# Get module logger
logger = get_logger("analyzer")

class FlairAnalyzer:
    """
    Analyzes flair performance metrics from Reddit post data.
    
    Calculates various statistics to determine which flairs have
    the highest potential for going viral, along with other
    engagement and performance metrics.
    """
    
    def __init__(self):
        """Initialize the FlairAnalyzer."""
        logger.info("FlairAnalyzer initialized")
    
    def analyze_flair_performance(self, df, viral_threshold=90, min_posts=5):
        """
        Analyze which flairs have the highest chance of going viral.
        
        Args:
            df (pandas.DataFrame): DataFrame containing post data
            viral_threshold (int, optional): Percentile threshold to consider a post viral.
                Defaults to 90 (top 10% of posts).
            min_posts (int, optional): Minimum number of posts required for a flair to be included.
                Defaults to 5.
        
        Returns:
            dict: Dictionary containing analysis results
        """
        logger.info(f"Analyzing flair performance (viral threshold: {viral_threshold}th percentile)")
        
        # Make a copy to avoid modifying the original
        analysis_df = df.copy()
        
        # Ensure required columns exist
        required_columns = ['flair', 'score', 'num_comments', 'upvote_ratio']
        for col in required_columns:
            if col not in analysis_df.columns:
                logger.error(f"Required column '{col}' not found in DataFrame")
                raise ValueError(f"Required column '{col}' not found in DataFrame")
        
        # Calculate viral threshold score
        score_threshold = analysis_df['score'].quantile(viral_threshold / 100)
        logger.info(f"Viral threshold score: {score_threshold:.2f}")
        
        # Mark viral posts
        analysis_df['is_viral'] = analysis_df['score'] >= score_threshold
        
        # Add additional metrics
        analysis_df['engagement'] = analysis_df['num_comments'] + analysis_df['score']
        analysis_df['efficiency'] = analysis_df['score'] / analysis_df['num_comments'].apply(lambda x: max(x, 1))
        
        # Group by flair and calculate statistics
        flair_stats = self._calculate_flair_stats(analysis_df, min_posts)
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(analysis_df, flair_stats)
        
        # Print summary to console
        self._print_analysis_summary(flair_stats, score_threshold, overall_metrics)
        
        logger.info("Flair performance analysis completed")
        
        return {
            "flair_stats": flair_stats,
            "viral_threshold": score_threshold,
            "metrics": overall_metrics
        }
    
    def _calculate_flair_stats(self, df, min_posts=5):
        """Calculate statistics for each flair."""
        # Group by flair
        flair_groups = df.groupby('flair')
        
        # Calculate basic statistics
        stats = flair_groups.agg({
            'is_viral': ['mean', 'sum', 'count'],
            'score': ['mean', 'median', 'max', 'std'],
            'num_comments': ['mean', 'median', 'max'],
            'upvote_ratio': ['mean', 'median'],
            'engagement': ['mean', 'max'],
            'efficiency': ['mean', 'median']
        })
        
        # Flatten the column hierarchy
        stats.columns = ['_'.join(col).strip('_') for col in stats.columns.values]
        
        # Reset index to make 'flair' a column
        stats = stats.reset_index()
        
        # Rename columns for clarity
        stats = stats.rename(columns={
            'is_viral_mean': 'viral_rate',
            'is_viral_sum': 'num_viral_posts',
            'is_viral_count': 'total_posts',
            'score_mean': 'avg_score',
            'score_median': 'median_score',
            'score_max': 'max_score',
            'score_std': 'score_std',
            'num_comments_mean': 'avg_comments',
            'num_comments_median': 'median_comments',
            'num_comments_max': 'max_comments',
            'upvote_ratio_mean': 'avg_upvote_ratio',
            'upvote_ratio_median': 'median_upvote_ratio',
            'engagement_mean': 'avg_engagement',
            'engagement_max': 'max_engagement',
            'efficiency_mean': 'avg_efficiency',
            'efficiency_median': 'median_efficiency'
        })
        
        # Calculate confidence metrics
        # We want to be more confident in flairs with more posts
        stats['confidence'] = 1 - (1 / (stats['total_posts'] ** 0.5))
        
        # Calculate adjusted viral rate (weighted by confidence)
        stats['viral_rate_adjusted'] = stats['viral_rate'] * stats['confidence']
        
        # Calculate viralness score (combines multiple factors)
        stats['viral_score'] = (
            stats['viral_rate'] * 0.5 + 
            (stats['avg_score'] / stats['avg_score'].max()) * 0.3 + 
            stats['confidence'] * 0.2
        )
        
        # Filter out flairs with too few posts
        filtered_stats = stats[stats['total_posts'] >= min_posts]
        
        # Sort by viral rate (descending)
        sorted_stats = filtered_stats.sort_values('viral_rate', ascending=False)
        
        return sorted_stats
    
    def _calculate_overall_metrics(self, df, flair_stats):
        """Calculate overall metrics for the analysis."""
        viral_posts = df[df['is_viral'] == True]
        
        metrics = {
            'total_posts': len(df),
            'total_viral_posts': len(viral_posts),
            'viral_post_percentage': len(viral_posts) / len(df) * 100,
            'total_flairs': len(df['flair'].unique()),
            'analyzed_flairs': len(flair_stats),
            'avg_score_all_posts': df['score'].mean(),
            'avg_score_viral_posts': viral_posts['score'].mean(),
            'avg_comments_all_posts': df['num_comments'].mean(),
            'avg_comments_viral_posts': viral_posts['num_comments'].mean(),
            'most_viral_flair': flair_stats.iloc[0]['flair'] if not flair_stats.empty else None,
            'most_viral_rate': flair_stats.iloc[0]['viral_rate'] if not flair_stats.empty else None,
            'highest_avg_score_flair': flair_stats.loc[flair_stats['avg_score'].idxmax()]['flair'] if not flair_stats.empty else None,
            'highest_avg_score': flair_stats['avg_score'].max() if not flair_stats.empty else None,
        }
        
        return metrics
    
    def _print_analysis_summary(self, flair_stats, viral_threshold, metrics):
        """Print a summary of the analysis to the console."""
        # Print overall metrics
        logger.info("=" * 80)
        logger.info("ANALYSIS SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total posts analyzed: {metrics['total_posts']:,}")
        logger.info(f"Viral threshold score: {viral_threshold:.2f}")
        logger.info(f"Total viral posts: {metrics['total_viral_posts']:,} ({metrics['viral_post_percentage']:.2f}%)")
        logger.info(f"Total unique flairs: {metrics['total_flairs']}")
        logger.info(f"Flairs with enough data for analysis: {metrics['analyzed_flairs']}")
        logger.info("-" * 80)
        
        # Print top 10 flairs by viral rate
        top_flairs = flair_stats.head(10)[['flair', 'viral_rate', 'total_posts', 'avg_score', 'viral_score']]
        top_flairs['viral_rate'] = top_flairs['viral_rate'].apply(lambda x: f"{x:.2%}")
        top_flairs['avg_score'] = top_flairs['avg_score'].apply(lambda x: f"{x:.2f}")
        top_flairs['viral_score'] = top_flairs['viral_score'].apply(lambda x: f"{x:.4f}")
        
        logger.info("TOP 10 FLAIRS BY VIRAL RATE:")
        table = tabulate(
            top_flairs, 
            headers=['Flair', 'Viral Rate', 'Total Posts', 'Avg Score', 'Viral Score'],
            tablefmt='pretty'
        )
        for line in table.split('\n'):
            logger.info(line)
        
        logger.info("-" * 80)
        logger.info(f"Most viral flair: {metrics['most_viral_flair']} ({metrics['most_viral_rate']:.2%} viral rate)")
        logger.info(f"Highest avg score flair: {metrics['highest_avg_score_flair']} ({metrics['highest_avg_score']:.2f} avg score)")
        logger.info("=" * 80)
    
    def perform_advanced_analysis(self, df, flair_stats):
        """
        Perform advanced analysis on post data to extract deeper insights.
        
        Args:
            df (pandas.DataFrame): DataFrame containing post data
            flair_stats (pandas.DataFrame): DataFrame containing flair statistics
            
        Returns:
            dict: Dictionary containing advanced analysis results
        """
        logger.info("Performing advanced analysis")
        
        results = {}
        
        # Time-based analysis
        results['time_analysis'] = self._analyze_posting_time(df)
        
        # Post content type analysis
        results['content_analysis'] = self._analyze_content_types(df)
        
        # Correlation analysis
        results['correlations'] = self._analyze_correlations(df)
        
        # Flair combination analysis
        results['flair_combinations'] = self._analyze_flair_combinations(df, flair_stats)
        
        logger.info("Advanced analysis completed")
        
        return results
    
    def _analyze_posting_time(self, df):
        """Analyze how posting time affects virality."""
        if 'created_utc' not in df.columns:
            return None
        
        # Group by hour and day
        hour_stats = df.groupby('post_hour').agg({
            'is_viral': 'mean',
            'score': 'mean',
            'id': 'count'
        }).reset_index()
        
        day_stats = df.groupby('post_day').agg({
            'is_viral': 'mean',
            'score': 'mean',
            'id': 'count'
        }).reset_index()
        
        # Find optimal posting times
        best_hour = hour_stats.loc[hour_stats['is_viral'].idxmax()]
        best_day = day_stats.loc[day_stats['is_viral'].idxmax()]
        
        return {
            'best_hour': int(best_hour['post_hour']),
            'best_hour_viral_rate': float(best_hour['is_viral']),
            'best_day': best_day['post_day'],
            'best_day_viral_rate': float(best_day['is_viral']),
            'hour_stats': hour_stats,
            'day_stats': day_stats
        }
    
    def _analyze_content_types(self, df):
        """Analyze how content type affects virality."""
        if 'is_self' not in df.columns:
            return None
        
        # Define content types
        df['content_type'] = 'link'
        df.loc[df['is_self'], 'content_type'] = 'text'
        df.loc[df['url'].str.contains('i.redd.it|imgur.com', na=False), 'content_type'] = 'image'
        df.loc[df['url'].str.contains('v.redd.it|youtube.com|youtu.be', na=False), 'content_type'] = 'video'
        
        # Group by content type
        content_stats = df.groupby('content_type').agg({
            'is_viral': 'mean',
            'score': 'mean',
            'num_comments': 'mean',
            'id': 'count'
        }).reset_index()
        
        # Find best content type
        best_content = content_stats.loc[content_stats['is_viral'].idxmax()]
        
        return {
            'best_content_type': best_content['content_type'],
            'best_content_viral_rate': float(best_content['is_viral']),
            'content_stats': content_stats
        }
    
    def _analyze_correlations(self, df):
        """Analyze correlations between different metrics."""
        # Select numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        
        # Remove unnecessary columns
        cols_to_drop = ['created_utc', 'post_hour']
        numeric_df = numeric_df.drop(columns=[c for c in cols_to_drop if c in numeric_df.columns])
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()
        
        # Get correlations with virality
        if 'is_viral' in corr_matrix.columns:
            viral_corr = corr_matrix['is_viral'].sort_values(ascending=False).drop('is_viral')
            
            # Top 3 positive correlations
            top_positive = viral_corr.nlargest(3)
            
            # Top 3 negative correlations
            top_negative = viral_corr.nsmallest(3)
            
            return {
                'correlation_matrix': corr_matrix,
                'viral_correlation': viral_corr,
                'top_positive_correlations': top_positive.to_dict(),
                'top_negative_correlations': top_negative.to_dict()
            }
        
        return {'correlation_matrix': corr_matrix}
    
    def _analyze_flair_combinations(self, df, flair_stats):
        """Analyze combinations of flairs with other post attributes."""
        if flair_stats is None or flair_stats.empty:
            return None
        
        # Top 5 viral flairs
        top_flairs = flair_stats.head(5)['flair'].tolist()
        
        # Filter to posts with these flairs
        top_flair_posts = df[df['flair'].isin(top_flairs)]
        
        results = {}
        
        # For each top flair, find best day, hour, content type
        for flair in top_flairs:
            flair_df = df[df['flair'] == flair]
            
            if len(flair_df) < 10:  # Skip if too few posts
                continue
                
            flair_result = {}
            
            # Best time to post
            if 'post_hour' in flair_df.columns and 'post_day' in flair_df.columns:
                hour_stats = flair_df.groupby('post_hour')['is_viral'].mean()
                day_stats = flair_df.groupby('post_day')['is_viral'].mean()
                
                if not hour_stats.empty:
                    flair_result['best_hour'] = int(hour_stats.idxmax())
                    flair_result['best_hour_viral_rate'] = float(hour_stats.max())
                
                if not day_stats.empty:
                    flair_result['best_day'] = day_stats.idxmax()
                    flair_result['best_day_viral_rate'] = float(day_stats.max())
            
            # Best content type
            if 'content_type' in flair_df.columns:
                content_stats = flair_df.groupby('content_type')['is_viral'].mean()
                
                if not content_stats.empty:
                    flair_result['best_content_type'] = content_stats.idxmax()
                    flair_result['best_content_viral_rate'] = float(content_stats.max())
            
            results[flair] = flair_result
        
        return results