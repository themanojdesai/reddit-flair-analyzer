"""
Command-line interface for the Reddit Flair Analyzer.

This module provides a user-friendly command-line interface
for analyzing Reddit flair performance without writing code.
"""

import argparse
import sys
import os
import textwrap
import webbrowser
from datetime import datetime
import logging
from getpass import getpass
from .logger import setup_logger, enable_file_logging
from . import RedditAnalyzer, __version__
from .utils import format_table_for_console

# Set up logger
logger = setup_logger("cli", level=logging.INFO)

def parse_arguments():
    """Parse command-line arguments."""
    # Create parser
    parser = argparse.ArgumentParser(
        description="Reddit Flair Analyzer - Analyze which flairs have the highest chance of going viral",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          # Basic analysis
          reddit-analyze --subreddit wallstreetbets --posts 500
          
          # Analysis with specific time filter and viral threshold
          reddit-analyze --subreddit AskReddit --posts 1000 --timeframe month --threshold 95
          
          # Interactive dashboard
          reddit-analyze --subreddit datascience --interactive
          
          # Export results to Excel
          reddit-analyze --subreddit politics --export excel
        """)
    )
    
    # Add arguments
    parser.add_argument(
        "--subreddit", "-s",
        help="Name of the subreddit to analyze (without r/ prefix)",
        required=True
    )
    
    parser.add_argument(
        "--posts", "-p",
        help="Maximum number of posts to retrieve (default: 500)",
        type=int,
        default=500
    )
    
    parser.add_argument(
        "--timeframe", "-t",
        help="Time filter for posts (default: all)",
        choices=["all", "day", "week", "month", "year"],
        default="all"
    )
    
    parser.add_argument(
        "--threshold", "-th",
        help="Percentile threshold to consider a post viral (default: 90)",
        type=int,
        default=90,
        choices=range(50, 100)
    )
    
    parser.add_argument(
        "--client-id", "-c",
        help="Reddit API client ID (will prompt if not provided)",
        default=os.getenv("REDDIT_CLIENT_ID")
    )
    
    parser.add_argument(
        "--client-secret", "-cs",
        help="Reddit API client secret (will prompt if not provided)",
        default=os.getenv("REDDIT_CLIENT_SECRET")
    )
    
    parser.add_argument(
        "--user-agent", "-u",
        help="Reddit API user agent (will default to standard if not provided)",
        default=os.getenv("REDDIT_USER_AGENT") or "Reddit Flair Analyzer CLI v1.0"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output directory for results (default: ./results)",
        default="./results"
    )
    
    parser.add_argument(
        "--export", "-e",
        help="Export results format (default: csv)",
        choices=["csv", "excel", "json"],
        default="csv"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        help="Enable verbose output",
        action="store_true"
    )
    
    parser.add_argument(
        "--log-file",
        help="Enable logging to file",
        action="store_true"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        help="Generate interactive visualizations",
        action="store_true",
        default=True  # Changed to True by default
    )
    
    parser.add_argument(
        "--auto-open", "-a",
        help="Automatically open dashboard in browser",
        action="store_true",
        default=True  # Open dashboard by default
    )
    
    parser.add_argument(
        "--version",
        help="Show version information",
        action="store_true"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle version flag
    if args.version:
        print(f"Reddit Flair Analyzer v{__version__}")
        sys.exit(0)
    
    return args

def prompt_for_credentials(args):
    """Prompt for Reddit API credentials if not provided."""
    client_id = args.client_id
    client_secret = args.client_secret
    
    if not client_id:
        client_id = input("Enter Reddit API client ID: ")
    
    if not client_secret:
        client_secret = getpass("Enter Reddit API client secret: ")
    
    return client_id, client_secret, args.user_agent

def main():
    """Main entry point for the CLI."""
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    if args.log_file:
        log_file = enable_file_logging()
        logger.info(f"Logging to file: {log_file}")
    
    logger.info(f"Reddit Flair Analyzer v{__version__}")
    logger.info(f"Starting analysis of r/{args.subreddit}")
    
    try:
        # Get credentials
        client_id, client_secret, user_agent = prompt_for_credentials(args)
        
        if not client_id or not client_secret:
            logger.error("Reddit API credentials are required")
            print("\nERROR: Reddit API credentials are required.")
            print("You can provide them using the --client-id and --client-secret arguments,")
            print("or by setting the REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.")
            print("\nTo get API credentials:")
            print("1. Visit https://www.reddit.com/prefs/apps")
            print("2. Click 'create app' at the bottom")
            print("3. Fill in the name, select 'script', and enter 'http://localhost:8080' as the redirect URI")
            print("4. Note your client ID and client secret")
            sys.exit(1)
        
        # Create output directory
        os.makedirs(args.output, exist_ok=True)
        
        # Create subreddit-specific output directory
        subreddit_output_dir = os.path.join(args.output, args.subreddit)
        os.makedirs(subreddit_output_dir, exist_ok=True)
        
        # Initialize analyzer
        log_level = logging.DEBUG if args.verbose else logging.INFO
        analyzer = RedditAnalyzer(client_id, client_secret, user_agent, log_level=log_level)
        
        # Start analysis with progress info
        print(f"Analyzing r/{args.subreddit}...")
        print(f"- Retrieving up to {args.posts} posts ({args.timeframe} timeframe)")
        print(f"- Viral threshold set to top {100-args.threshold}% of posts")
        
        # Run analysis
        results = analyzer.analyze_subreddit(
            subreddit=args.subreddit,
            post_limit=args.posts,
            time_filter=args.timeframe,
            viral_threshold=args.threshold
        )
        
        # Get results
        flair_stats = results.get('flair_stats')
        metrics = results.get('metrics', {})
        
        # Print results
        print("\n" + "="*80)
        print(f"ANALYSIS RESULTS FOR r/{args.subreddit}")
        print("="*80)
        print(f"Total posts analyzed: {metrics.get('total_posts', 0):,}")
        print(f"Unique flairs found: {metrics.get('total_flairs', 0):,}")
        print(f"Viral threshold score: {results.get('viral_threshold', 0):,.0f}")
        print(f"Most viral flair: {metrics.get('most_viral_flair', 'N/A')} ({metrics.get('most_viral_rate', 0):.1%} viral rate)")
        print("-"*80)
        
        # Display top flairs
        print("\nTOP FLAIRS BY VIRAL RATE:")
        if not flair_stats.empty:
            table = format_table_for_console(
                flair_stats[['flair', 'viral_rate', 'total_posts', 'avg_score', 'num_viral_posts']].head(10)
            )
            print(table)
        else:
            print("No flair statistics available")
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        visualization_files = analyzer.visualize(
            results,
            output_dir=subreddit_output_dir,
            interactive=args.interactive
        )
        
        # Always generate dashboard even if 'dashboard' not in visualization_files
        dashboard_path = None
        if args.interactive and 'dashboard' not in visualization_files:
            try:
                print("Creating interactive dashboard...")
                dashboard_path = analyzer.visualizer._create_interactive_dashboard(results, subreddit_output_dir)
                visualization_files['dashboard'] = dashboard_path
            except Exception as e:
                logger.error(f"Error creating dashboard: {e}")
                print(f"Could not create dashboard: {e}")
        
        # Print visualization files
        if visualization_files:
            print(f"\nCreated {len(visualization_files)} visualization files in {subreddit_output_dir}:")
            for viz_type, file_path in visualization_files.items():
                print(f"- {viz_type}: {os.path.basename(file_path)}")
        
        # Export results
        print(f"\nExporting results to {args.export.upper()} format...")
        export_path = analyzer.export(
            results,
            format=args.export,
            filename=os.path.join(subreddit_output_dir, f"{args.subreddit}_flair_analysis")
        )
        
        if export_path:
            print(f"Results exported to: {export_path}")
        
        # Print and potentially open dashboard
        if args.interactive and 'dashboard' in visualization_files:
            dashboard_path = visualization_files['dashboard']
            dashboard_abs_path = os.path.abspath(dashboard_path)
            
            print("\n" + "="*80)
            print(f"INTERACTIVE DASHBOARD CREATED:")
            print(f"{dashboard_abs_path}")
            print("="*80)
            
            # Automatically open dashboard if requested
            if args.auto_open:
                dashboard_url = f"file://{dashboard_abs_path}"
                print("\nOpening dashboard in your default web browser...")
                webbrowser.open(dashboard_url)
            else:
                print("\nTo view the dashboard, open this file in your web browser:")
                print(f"  {dashboard_abs_path}")
        
        # Print summary
        print("\n" + "="*80)
        print(f"Analysis completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"All results saved to: {os.path.abspath(subreddit_output_dir)}")
        print("="*80)
        
        return 0
    
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        return 1
    
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        print("\nFor more details, run with --verbose and --log-file flags")
        return 1


if __name__ == "__main__":
    sys.exit(main())