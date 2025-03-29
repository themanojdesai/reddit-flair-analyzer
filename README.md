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

```bash
# Basic analysis
reddit-analyze --subreddit wallstreetbets --posts 500

# Export results
reddit-analyze --subreddit AskReddit --posts 1000 --export excel

# Advanced visualization
reddit-analyze --subreddit movies --posts 1000
```

### Using the Python API

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