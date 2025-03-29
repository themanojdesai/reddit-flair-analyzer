# Installation Guide

This guide will walk you through the process of installing the Reddit Flair Analyzer on your system.

## Prerequisites

Before installing the Reddit Flair Analyzer, ensure you have the following:

- Python 3.7 or higher
- pip (Python package installer)
- A Reddit account and API credentials

## Installation Options

### 1. Install from PyPI (Recommended)

The easiest way to install the Reddit Flair Analyzer is directly from PyPI:

```bash
pip install reddit-flair-analyzer
```

This will install the package and all its dependencies.

### 2. Install from Source

If you want the latest development version or plan to contribute to the project:

```bash
# Clone the repository
git clone https://github.com/themanojdesai/reddit-flair-analyzer.git

# Navigate to the project directory
cd reddit-flair-analyzer

# Install in development mode
pip install -e .
```

## Verifying the Installation

To verify that the installation was successful, run:

```bash
reddit-analyze --version
```

You should see the current version of the Reddit Flair Analyzer displayed.

## Getting Reddit API Credentials

To use the Reddit Flair Analyzer, you need to create a Reddit application to get API credentials:

1. Visit https://www.reddit.com/prefs/apps
2. Click "create app" at the bottom
3. Fill in the following:
   - Name: Reddit Flair Analyzer (or any name you prefer)
   - App type: Select "script"
   - Description: Optional
   - About URL: http://localhost:8080
   - Redirect URI: http://localhost:8080
4. Click "create app"
5. Note your:
   - Client ID: The string under the app name (e.g., "YourAppID")
   - Client Secret: Listed as "secret"

These credentials will be used to authenticate your requests to the Reddit API.

## Dependencies

The Reddit Flair Analyzer has the following main dependencies, which will be automatically installed:

- praw (Python Reddit API Wrapper)
- pandas (Data manipulation)
- matplotlib, seaborn, plotly (Visualization)
- numpy (Numerical computing)
- tqdm (Progress bars)
- colorlog (Colored logging)

## Troubleshooting

### Common Installation Issues

1. **Permission Error**: If you encounter permission errors, try using:
   ```bash
   pip install --user reddit-flair-analyzer
   ```

2. **Dependency Conflicts**: If you experience dependency conflicts, consider using a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install reddit-flair-analyzer
   ```

3. **Outdated pip**: Make sure your pip is up to date:
   ```bash
   pip install --upgrade pip
   ```

For more help, please open an issue on the [GitHub repository](https://github.com/themanojdesai/reddit-flair-analyzer).