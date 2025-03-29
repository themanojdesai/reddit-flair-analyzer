"""
Reddit Flair Analyzer - A professional tool for analyzing viral potential of Reddit post flairs.

This package helps content creators, marketers, and researchers understand which flairs
perform best in specific subreddits, with comprehensive analytics and visualizations.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

import logging
from .logger import setup_logger

# Set up default logger
logger = setup_logger()

# Import main components
from .scraper import RedditScraper
from .analyzer import FlairAnalyzer
from .visualizer import Visualizer

# Create main class for easy access to functionality
class RedditAnalyzer:
    """
    Main entry point for the Reddit Flair Analyzer package.
    
    Combines scraping, analysis, and visualization functionality into a simple interface.
    
    Args:
        client_id (str): Reddit API client ID
        client_secret (str): Reddit API client secret
        user_agent (str): Reddit API user agent
        log_level (int, optional): Logging level. Defaults to logging.INFO.
    """
    
    def __init__(self, client_id, client_secret, user_agent, log_level=logging.INFO):
        """Initialize the Reddit Analyzer with API credentials."""
        # Set logging level
        logger.setLevel(log_level)
        
        # Initialize components
        self.scraper = RedditScraper(client_id, client_secret, user_agent)
        self.analyzer = FlairAnalyzer()
        self.visualizer = Visualizer()
        
        logger.info("RedditAnalyzer initialized successfully")
    
    def analyze_subreddit(self, subreddit, post_limit=1000, time_filter="all", viral_threshold=90):
        """
        Analyze a subreddit to find which flairs have the highest viral potential.
        
        Args:
            subreddit (str): Name of the subreddit to analyze
            post_limit (int, optional): Maximum number of posts to scrape. Defaults to 1000.
            time_filter (str, optional): Time filter for posts. Defaults to "all".
            viral_threshold (int, optional): Percentile to consider viral. Defaults to 90.
            
        Returns:
            dict: Analysis results containing dataframes and statistics
        """
        logger.info(f"Starting analysis of r/{subreddit}")
        
        # Scrape posts
        posts_df = self.scraper.scrape_subreddit(subreddit, post_limit, time_filter)
        
        # Analyze flair performance
        analysis_results = self.analyzer.analyze_flair_performance(
            posts_df, 
            viral_threshold=viral_threshold
        )
        
        logger.info(f"Completed analysis of r/{subreddit}")
        
        return {
            "posts_df": posts_df,
            "flair_stats": analysis_results["flair_stats"],
            "viral_threshold": analysis_results["viral_threshold"],
            "subreddit": subreddit,
            "metrics": analysis_results["metrics"]
        }
    
    def visualize(self, results, output_dir="./", plot_types=None, interactive=False):
        """
        Generate visualizations from analysis results.
        
        Args:
            results (dict): Analysis results from analyze_subreddit()
            output_dir (str, optional): Directory to save visualizations. Defaults to "./".
            plot_types (list, optional): Types of plots to generate. Defaults to all.
            interactive (bool, optional): Whether to create interactive visualizations. Defaults to False.
            
        Returns:
            dict: Paths to generated visualization files
        """
        logger.info(f"Generating visualizations for r/{results['subreddit']}")
        
        return self.visualizer.create_visualizations(
            results,
            output_dir=output_dir,
            plot_types=plot_types,
            interactive=interactive
        )
    
    def export(self, results, format="csv", filename=None):
        """
        Export analysis results to file.
        
        Args:
            results (dict): Analysis results from analyze_subreddit()
            format (str, optional): Export format (csv, excel, json). Defaults to "csv".
            filename (str, optional): Custom filename. Defaults to auto-generated.
            
        Returns:
            str: Path to exported file
        """
        from .utils import export_results
        
        if filename is None:
            subreddit = results["subreddit"]
            filename = f"{subreddit}_flair_analysis"
        
        logger.info(f"Exporting results for r/{results['subreddit']} to {format} format")
        
        return export_results(results, format=format, filename=filename)

# Define what's available when using from redditflairanalyzer import *
__all__ = ["RedditAnalyzer", "RedditScraper", "FlairAnalyzer", "Visualizer", "logger"]