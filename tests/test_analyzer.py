from redditflairanalyzer import RedditAnalyzer

# Replace with your actual Reddit API credentials
CLIENT_ID = 'client_id'
CLIENT_SECRET = 'client_secrete'
USER_AGENT = 'Flair Analysis by /u/yourusername'

def main():
    # Initialize the analyzer
    analyzer = RedditAnalyzer(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    
    # Choose a subreddit with plenty of posts and diverse flairs
    subreddit = 'askreddit'
    
    print(f"Analyzing r/{subreddit}...")
    
    # Run the analysis with a small post count for testing
    results = analyzer.analyze_subreddit(
        subreddit=subreddit,
        post_limit=100,  # Use a small number for testing
        time_filter='month',
        viral_threshold=90
    )
    
    # Generate visualizations
    print("Generating visualizations...")
    viz_files = analyzer.visualize(
        results,
        output_dir="./test_results",
        interactive=True
    )
    
    # Export results
    print("Exporting results...")
    export_path = analyzer.export(
        results,
        format="csv",
        filename="./test_results/test_analysis"
    )
    
    print(f"Test completed. Results saved to: ./test_results")
    print(f"Generated {len(viz_files)} visualizations")

if __name__ == "__main__":
    main()