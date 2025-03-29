# Usage Guide

This guide explains how to use the Reddit Flair Analyzer effectively, covering both the command-line interface (CLI) and the Python API.

## Command-line Interface (CLI)

The Reddit Flair Analyzer provides a powerful CLI that lets you analyze subreddits without writing any code.

### Basic Usage

```bash
reddit-analyze --subreddit AskReddit --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

This will:
1. Analyze the r/AskReddit subreddit
2. Generate visualizations and a dashboard
3. Automatically open the dashboard in your default web browser

### Command-line Options

Here are the main options available:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--subreddit` | `-s` | Name of the subreddit to analyze (without r/ prefix) | (Required) |
| `--posts` | `-p` | Maximum number of posts to retrieve | 500 |
| `--timeframe` | `-t` | Time filter for posts (all, day, week, month, year) | all |
| `--threshold` | `-th` | Percentile threshold to consider a post viral (50-99) | 90 |
| `--client-id` | `-c` | Reddit API client ID | (Will prompt if not provided) |
| `--client-secret` | `-cs` | Reddit API client secret | (Will prompt if not provided) |
| `--user-agent` | `-u` | Reddit API user agent | "Reddit Flair Analyzer CLI v1.0" |
| `--output` | `-o` | Output directory for results | ./results |
| `--export` | `-e` | Export results format (csv, excel, json) | csv |
| `--interactive` | `-i` | Generate interactive visualizations | True |
| `--auto-open` | `-a` | Automatically open dashboard in browser | True |
| `--verbose` | `-v` | Enable verbose output | False |
| `--log-file` | | Enable logging to file | False |
| `--version` | | Show version information | |

### Examples

```bash
# Basic analysis with 1000 posts
reddit-analyze --subreddit wallstreetbets --posts 1000

# Analysis with a specific time frame
reddit-analyze --subreddit datascience --timeframe month

# Export to Excel
reddit-analyze --subreddit movies --export excel

# Don't open the dashboard automatically
reddit-analyze --subreddit programming --auto-open false

# Save credentials in environment variables to avoid typing them each time
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
reddit-analyze --subreddit python
```

## Python API

You can also use the Reddit Flair Analyzer programmatically in your Python scripts.

### Basic Usage

```python
from redditflairanalyzer import RedditAnalyzer

# Initialize the analyzer
analyzer = RedditAnalyzer(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="YOUR_USER_AGENT"
)

# Analyze a subreddit
results = analyzer.analyze_subreddit(
    subreddit="datascience",
    post_limit=1000,
    time_filter="year",
    viral_threshold=90
)

# Generate visualizations
analyzer.visualize(
    results,
    output_dir="./results",
    interactive=True
)

# Export results
analyzer.export(results, format="excel", filename="datascience_analysis.xlsx")
```

### Main Classes and Methods

#### `RedditAnalyzer`

The main entry point for the package.

```python
analyzer = RedditAnalyzer(
    client_id,              # Reddit API client ID
    client_secret,          # Reddit API client secret
    user_agent,             # Reddit API user agent
    log_level=logging.INFO  # Logging level
)
```

#### `analyze_subreddit()`

Analyzes a subreddit to find which flairs have the highest viral potential.

```python
results = analyzer.analyze_subreddit(
    subreddit,                  # Name of the subreddit to analyze
    post_limit=1000,            # Maximum number of posts to retrieve
    time_filter="all",          # Time filter (all, day, week, month, year)
    viral_threshold=90          # Percentile to consider viral
)
```

#### `visualize()`

Generates visualizations from analysis results.

```python
viz_files = analyzer.visualize(
    results,                    # Results from analyze_subreddit()
    output_dir="./results",     # Directory to save visualizations
    plot_types=None,            # Types of plots to generate (None = all)
    interactive=True            # Whether to create interactive visualizations
)
```

Available plot types: 'bar', 'heatmap', 'scatter', 'bubble', 'time', 'distribution', 'dashboard'

#### `export()`

Exports analysis results to file.

```python
file_path = analyzer.export(
    results,                    # Results from analyze_subreddit()
    format="csv",               # Export format (csv, excel, json)
    filename=None               # Custom filename (None = auto-generated)
)
```

## Working with Results

The `analyze_subreddit()` method returns a dictionary with the following keys:

- `posts_df`: DataFrame of all posts analyzed
- `flair_stats`: DataFrame of flair statistics
- `viral_threshold`: Score threshold used to determine viral posts
- `subreddit`: Name of the analyzed subreddit
- `metrics`: Dictionary of overall analysis metrics

### Example: Accessing Flair Statistics

```python
results = analyzer.analyze_subreddit("python")
flair_stats = results["flair_stats"]

# Get the top 5 flairs by viral rate
top_flairs = flair_stats.head(5)
print(top_flairs[["flair", "viral_rate", "total_posts", "avg_score"]])
```

### Example: Finding Optimal Posting Time

```python
results = analyzer.analyze_subreddit("AskReddit")
posts_df = results["posts_df"]

# Group by hour and calculate average score
hour_stats = posts_df.groupby(posts_df['created_utc'].dt.hour)['score'].mean()

# Find the best hour to post
best_hour = hour_stats.idxmax()
print(f"Best hour to post: {best_hour}:00 UTC (Avg score: {hour_stats.max():.1f})")
```

## Advanced Usage

### Custom Analysis

You can perform custom analysis on the results:

```python
from redditflairanalyzer import RedditAnalyzer
import pandas as pd
import matplotlib.pyplot as plt

# Initialize and run analysis
analyzer = RedditAnalyzer(client_id, client_secret, user_agent)
results = analyzer.analyze_subreddit("datascience")

# Custom analysis: Compare post length vs. score
posts_df = results["posts_df"]
posts_df["title_length"] = posts_df["title"].apply(len)

# Create correlation plot
plt.figure(figsize=(10, 6))
plt.scatter(posts_df["title_length"], posts_df["score"], alpha=0.5)
plt.title("Title Length vs. Post Score")
plt.xlabel("Title Length (characters)")
plt.ylabel("Post Score")
plt.savefig("title_length_analysis.png")
```

### Analyzing Multiple Subreddits

```python
subreddits = ["python", "javascript", "golang"]
comparison = {}

for subreddit in subreddits:
    print(f"Analyzing r/{subreddit}...")
    results = analyzer.analyze_subreddit(subreddit, post_limit=500)
    
    # Store the most viral flair and its rate
    top_flair = results["flair_stats"].iloc[0]
    comparison[subreddit] = {
        "most_viral_flair": top_flair["flair"],
        "viral_rate": top_flair["viral_rate"],
        "avg_score": top_flair["avg_score"]
    }

# Create comparison table
comparison_df = pd.DataFrame.from_dict(comparison, orient='index')
print(comparison_df)
```

## Best Practices

1. **Start with a small number of posts** (100-200) to test your analysis before scaling up
2. **Be mindful of API rate limits** - Reddit limits how many requests you can make
3. **Use environment variables** for your API credentials for better security
4. **Save your analysis results** to avoid repeating the same API calls
5. **Analyze across different time frames** to account for seasonal trends