# Reddit Flair Analyzer

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.0.0-orange)
[![GitHub stars](https://img.shields.io/github/stars/themanojdesai/reddit-flair-analyzer?style=social)](https://github.com/themanojdesai/reddit-flair-analyzer/stargazers)
[![PyPI version](https://img.shields.io/pypi/v/reddit-flair-analyzer.svg)](https://pypi.org/project/reddit-flair-analyzer/)
[![Downloads](https://img.shields.io/pypi/dm/reddit-flair-analyzer.svg)](https://pypi.org/project/reddit-flair-analyzer/)

A professional tool for analyzing which post flairs have the highest chance of going viral on Reddit subreddits. This package helps content creators, marketers, and researchers understand flair performance to optimize content strategy.

## 🚀 Features

- **Comprehensive Scraping**: Collect thousands of posts from any public subreddit
- **Advanced Analytics**: Calculate viral rates, engagement metrics, and performance statistics
- **Beautiful Visualizations**: Generate publication-ready charts and interactive dashboards
- **Flexible Export**: Save results in multiple formats (CSV, JSON, Excel)
- **Detailed Logging**: Track progress with configurable logging levels
- **Command-line Interface**: Run analyses without writing code
- **Optimized Performance**: Multi-threaded scraping for faster data collection

## 🔧 Installation

```bash
# Install from PyPI
pip install reddit-flair-analyzer

# Or install from the repository
git clone https://github.com/themanojdesai/reddit-flair-analyzer.git
cd reddit-flair-analyzer
pip install -e .
```

The package is available on PyPI: [https://pypi.org/project/reddit-flair-analyzer/](https://pypi.org/project/reddit-flair-analyzer/)

## 📖 Quick Start

### Using the CLI

The CLI provides a user-friendly way to analyze Reddit flairs without writing code. You'll need to provide your Reddit API credentials (either as arguments or environment variables).

```bash
# Basic analysis with credentials
reddit-analyze --subreddit AskReddit --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET

# Using environment variables for credentials
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
reddit-analyze --subreddit datascience

# Specify number of posts and time frame
reddit-analyze --subreddit wallstreetbets --posts 500 --timeframe month

# Set viral threshold (percentile)
reddit-analyze --subreddit science --threshold 95  # Top 5% are considered viral

# Export results to different formats
reddit-analyze --subreddit movies --export excel
reddit-analyze --subreddit gaming --export json

# Save results to custom directory
reddit-analyze --subreddit programming --output ./my_analysis

# Disable auto-opening dashboard in browser
reddit-analyze --subreddit python --auto-open false

# Get verbose output for debugging
reddit-analyze --subreddit learnpython --verbose --log-file

# Show version information
reddit-analyze --version

# Get help with all available options
reddit-analyze --help
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--subreddit`, `-s` | Subreddit to analyze (required) | |
| `--client-id`, `-c` | Reddit API client ID | (Environment variable) |
| `--client-secret`, `-cs` | Reddit API client secret | (Environment variable) |
| `--user-agent`, `-u` | Reddit API user agent | "Reddit Flair Analyzer CLI v1.0" |
| `--posts`, `-p` | Maximum posts to retrieve | 500 |
| `--timeframe`, `-t` | Time filter (all, day, week, month, year) | all |
| `--threshold`, `-th` | Viral threshold percentile (50-99) | 90 |
| `--output`, `-o` | Output directory for results | ./results |
| `--export`, `-e` | Export format (csv, excel, json) | csv |
| `--interactive`, `-i` | Generate interactive visualizations | True |
| `--auto-open`, `-a` | Open dashboard in browser | True |
| `--verbose`, `-v` | Enable verbose output | False |
| `--log-file` | Enable logging to file | False |
| `--version` | Show version information | |
| `--help` | Show help message | |

### Using the Python API

The Python API gives you programmatic access to all analysis features with more flexibility:

```python
from redditflairanalyzer import RedditAnalyzer
import os

# Initialize the analyzer with your Reddit API credentials
analyzer = RedditAnalyzer(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="MyApp/1.0 (by /u/YourUsername)"
)

# Analyze a subreddit
results = analyzer.analyze_subreddit(
    subreddit="datascience",    # Subreddit name (without r/ prefix)
    post_limit=1000,            # Number of posts to analyze
    time_filter="year",         # Time filter (all, day, week, month, year)
    viral_threshold=90          # Percentile to consider viral (top 10%)
)

# Generate visualizations
visualization_files = analyzer.visualize(
    results,
    output_dir="./results/datascience",
    plot_types=["bar", "heatmap", "scatter", "dashboard"],  # Specific plots to generate
    interactive=True            # Create interactive HTML visualizations
)

# Export results to different formats
analyzer.export(results, format="excel", filename="datascience_analysis.xlsx")
analyzer.export(results, format="csv", filename="datascience_analysis.csv")
analyzer.export(results, format="json", filename="datascience_analysis.json")

# Access analysis results directly
flair_stats = results["flair_stats"]
posts_df = results["posts_df"]
viral_threshold = results["viral_threshold"]
metrics = results["metrics"]

# Print top 5 flairs by viral rate
top_flairs = flair_stats.head(5)
print("\nTop flairs by viral rate:")
for i, (_, row) in enumerate(top_flairs.iterrows(), 1):
    print(f"{i}. {row['flair']}: {row['viral_rate']:.1%} viral rate ({row['total_posts']} posts)")

# Find optimal posting time
if "created_utc" in posts_df.columns:
    posts_df["hour"] = posts_df["created_utc"].dt.hour
    hour_stats = posts_df.groupby("hour")["score"].mean()
    best_hour = hour_stats.idxmax()
    print(f"\nBest hour to post: {best_hour}:00 UTC (Avg score: {hour_stats.max():.1f})")
```

### Main API Components

#### `RedditAnalyzer` Class

The main entry point for the package:

```python
analyzer = RedditAnalyzer(
    client_id,              # Reddit API client ID
    client_secret,          # Reddit API client secret
    user_agent,             # Reddit API user agent
    log_level=logging.INFO  # Optional logging level
)
```

#### `analyze_subreddit()` Method

Analyzes a subreddit to find which flairs have the highest viral potential:

```python
results = analyzer.analyze_subreddit(
    subreddit,              # Name of the subreddit
    post_limit=1000,        # Maximum posts to retrieve
    time_filter="all",      # Time filter (all, day, week, month, year)
    viral_threshold=90      # Percentile to consider viral
)
```

#### `visualize()` Method

Generates visualizations from analysis results:

```python
files = analyzer.visualize(
    results,                # Results from analyze_subreddit()
    output_dir="./results", # Directory to save visualizations
    plot_types=None,        # Types of plots (None = all)
    interactive=True        # Whether to create interactive visualizations
)
```

Available plot types: `'bar'`, `'heatmap'`, `'scatter'`, `'bubble'`, `'time'`, `'distribution'`, `'dashboard'`

#### `export()` Method

Exports analysis results to file:

```python
path = analyzer.export(
    results,                # Results from analyze_subreddit()
    format="csv",           # Export format (csv, excel, json)
    filename=None           # Custom filename (None = auto-generated)
)
```

## 📝 Documentation

For detailed documentation, see:

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Examples](docs/examples.md)

## 🔒 Authentication

You need to create a Reddit application to get API credentials:

1. Visit https://www.reddit.com/prefs/apps
2. Click "create app" at the bottom
3. Fill in the name, select "script", and enter "http://localhost:8080" as the redirect URI
4. Note your client ID and client secret

## ⭐ Star This Repository

If you find this tool useful, please consider giving it a star on GitHub! It helps others discover the project and motivates further development.

[![GitHub Repo stars](https://img.shields.io/github/stars/themanojdesai/reddit-flair-analyzer?style=social)](https://github.com/themanojdesai/reddit-flair-analyzer/stargazers)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

Questions? Issues? Please open an issue on the GitHub repository.

Connect with the author:
- [LinkedIn](https://www.linkedin.com/in/themanojdesai/)
- [Twitter](https://x.com/themanojdesai)

---

Made with ❤️ by [Manoj Desai](https://github.com/themanojdesai)