# Examples

This document provides practical examples of using the Reddit Flair Analyzer for various use cases.

## Basic Analysis Example

### Command-line Interface

```bash
# Analyze which flairs perform best in r/datascience
reddit-analyze --subreddit datascience --posts 500 --timeframe month
```

This command will:
1. Analyze the last 500 posts from the past month in r/datascience
2. Calculate which flairs have the highest viral potential
3. Generate visualizations and a dashboard
4. Open the dashboard in your default web browser

### Python API

```python
from redditflairanalyzer import RedditAnalyzer

# Initialize the analyzer with your credentials
analyzer = RedditAnalyzer(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Example Script v1.0"
)

# Analyze r/datascience
results = analyzer.analyze_subreddit(
    subreddit="datascience",
    post_limit=500,
    time_filter="month",
    viral_threshold=90
)

# Generate visualizations
viz_files = analyzer.visualize(
    results,
    output_dir="./results/datascience",
    interactive=True
)

# Print the top 5 flairs by viral rate
top_flairs = results["flair_stats"].head(5)
print("\nTop 5 flairs by viral rate:")
for i, (_, flair) in enumerate(top_flairs.iterrows(), 1):
    print(f"{i}. {flair['flair']}: {flair['viral_rate']:.1%} viral rate, {flair['total_posts']} posts")
```

## Marketing Strategy Example

This example shows how to analyze a subreddit to develop an optimal posting strategy.

```python
import pandas as pd
import matplotlib.pyplot as plt
from redditflairanalyzer import RedditAnalyzer

# Initialize the analyzer
analyzer = RedditAnalyzer(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Marketing Strategy Analysis v1.0"
)

# Analyze a subreddit relevant to your product/service
results = analyzer.analyze_subreddit(
    subreddit="marketing",
    post_limit=1000,
    time_filter="year"
)

# Get the data
posts_df = results["posts_df"]
flair_stats = results["flair_stats"]

# 1. Find the best flairs to use
best_flairs = flair_stats.head(3)
print("Best flairs to use:")
for i, row in best_flairs.iterrows():
    print(f"- {row['flair']}: {row['viral_rate']:.1%} viral rate")

# 2. Find the best time to post
# Extract hour and day from timestamps
posts_df["hour"] = posts_df["created_utc"].dt.hour
posts_df["day"] = posts_df["created_utc"].dt.day_name()

# Calculate average score by hour
hour_performance = posts_df.groupby("hour")["score"].mean().reset_index()
best_hour = hour_performance.loc[hour_performance["score"].idxmax()]

# Calculate average score by day
day_performance = posts_df.groupby("day")["score"].mean().reset_index()
# Sort days of week properly
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_performance["day"] = pd.Categorical(day_performance["day"], categories=day_order, ordered=True)
day_performance = day_performance.sort_values("day")
best_day = day_performance.loc[day_performance["score"].idxmax()]

print(f"\nBest time to post: {best_day['day']} at {best_hour['hour']}:00 UTC")

# 3. Analysis of title characteristics
posts_df["title_length"] = posts_df["title"].str.len()
posts_df["has_question"] = posts_df["title"].str.contains(r'\?').astype(int)

# Compare viral posts with non-viral
viral_posts = posts_df[posts_df["is_viral"] == True]
non_viral_posts = posts_df[posts_df["is_viral"] == False]

viral_avg_length = viral_posts["title_length"].mean()
non_viral_avg_length = non_viral_posts["title_length"].mean()

viral_question_pct = viral_posts["has_question"].mean() * 100
non_viral_question_pct = non_viral_posts["has_question"].mean() * 100

print("\nTitle characteristics analysis:")
print(f"- Viral posts average title length: {viral_avg_length:.1f} characters")
print(f"- Non-viral posts average title length: {non_viral_avg_length:.1f} characters")
print(f"- Viral posts with questions: {viral_question_pct:.1f}%")
print(f"- Non-viral posts with questions: {non_viral_question_pct:.1f}%")

# 4. Create an optimal posting strategy
print("\n=== RECOMMENDED POSTING STRATEGY ===")
print(f"1. Use the '{best_flairs.iloc[0]['flair']}' flair")
print(f"2. Post on {best_day['day']} around {best_hour['hour']}:00 UTC")
if viral_avg_length > non_viral_avg_length:
    print(f"3. Use longer titles (aim for {viral_avg_length:.0f}+ characters)")
else:
    print(f"3. Use concise titles (aim for {viral_avg_length:.0f} characters)")
if viral_question_pct > non_viral_question_pct:
    print("4. Include a question in your title")
else:
    print("4. Make a statement rather than asking a question")
```

## Comparative Analysis Example

This example compares multiple technology subreddits to find which ones have the highest engagement.

```python
from redditflairanalyzer import RedditAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize the analyzer
analyzer = RedditAnalyzer(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Subreddit Comparison v1.0"
)

# List of subreddits to compare
tech_subreddits = ["python", "javascript", "webdev", "programming", "datascience"]

# Store results
comparison_data = []

# Analyze each subreddit
for subreddit in tech_subreddits:
    print(f"Analyzing r/{subreddit}...")
    results = analyzer.analyze_subreddit(
        subreddit=subreddit,
        post_limit=200,  # Lower limit for quicker analysis
        time_filter="month"
    )
    
    # Get metrics
    posts_df = results["posts_df"]
    metrics = results["metrics"]
    viral_threshold = results["viral_threshold"]
    
    # Calculate averages
    avg_score = posts_df["score"].mean()
    avg_comments = posts_df["num_comments"].mean() if "num_comments" in posts_df.columns else 0
    engagement_ratio = avg_comments / avg_score if avg_score > 0 else 0
    
    # Store data
    comparison_data.append({
        "subreddit": subreddit,
        "subscribers": metrics.get("subscribers", 0),
        "posts_analyzed": len(posts_df),
        "viral_threshold": viral_threshold,
        "avg_score": avg_score,
        "avg_comments": avg_comments,
        "engagement_ratio": engagement_ratio,
        "viral_post_pct": metrics.get("viral_post_percentage", 0)
    })

# Create comparison dataframe
comparison_df = pd.DataFrame(comparison_data)

# Print comparison table
print("\n=== SUBREDDIT COMPARISON ===")
print(comparison_df[["subreddit", "avg_score", "avg_comments", "engagement_ratio", "viral_post_pct"]])

# Create visualization
plt.figure(figsize=(12, 8))
sns.barplot(x="subreddit", y="avg_score", data=comparison_df)
plt.title("Average Post Score by Subreddit")
plt.ylabel("Average Score")
plt.xlabel("Subreddit")
plt.savefig("subreddit_comparison.png")

# Find best subreddit for engagement
best_engagement = comparison_df.loc[comparison_df["engagement_ratio"].idxmax()]
print(f"\nSubreddit with highest engagement: r/{best_engagement['subreddit']}")
print(f"Engagement ratio: {best_engagement['engagement_ratio']:.2f} comments per score point")

# Find best subreddit for visibility (highest average score)
best_visibility = comparison_df.loc[comparison_df["avg_score"].idxmax()]
print(f"\nSubreddit with highest visibility: r/{best_visibility['subreddit']}")
print(f"Average score: {best_visibility['avg_score']:.1f}")
```

## Historical Trend Analysis Example

This example analyzes how flair performance changes over time.

```python
from redditflairanalyzer import RedditAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Initialize the analyzer
analyzer = RedditAnalyzer(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Trend Analysis v1.0"
)

# Analyze a subreddit with a large time frame
subreddit_name = "wallstreetbets"
results = analyzer.analyze_subreddit(
    subreddit=subreddit_name,
    post_limit=2000,  # Higher limit for better trend analysis
    time_filter="year"
)

posts_df = results["posts_df"]
flair_stats = results["flair_stats"]

# Get top 5 flairs by post count
top_flairs = flair_stats.sort_values("total_posts", ascending=False).head(5)["flair"].tolist()

# Filter posts to only include top flairs
filtered_posts = posts_df[posts_df["flair"].isin(top_flairs)]

# Extract month from timestamp
filtered_posts["month"] = filtered_posts["created_utc"].dt.strftime("%Y-%m")

# Group by month and flair, calculate average score
monthly_performance = filtered_posts.groupby(["month", "flair"])["score"].mean().reset_index()

# Pivot for easier plotting
pivot_data = monthly_performance.pivot(index="month", columns="flair", values="score")

# Sort by month
pivot_data = pivot_data.sort_index()

# Plot trends
plt.figure(figsize=(14, 8))
pivot_data.plot(marker='o', linestyle='-', ax=plt.gca())

plt.title(f"Flair Performance Trends in r/{subreddit_name}")
plt.xlabel("Month")
plt.ylabel("Average Score")
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{subreddit_name}_flair_trends.png")

# Identify trending flairs
first_month = pivot_data.index[0]
last_month = pivot_data.index[-1]

trend_data = []
for flair in pivot_data.columns:
    if first_month in pivot_data.index and last_month in pivot_data.index:
        first_score = pivot_data.loc[first_month, flair]
        last_score = pivot_data.loc[last_month, flair]
        
        if pd.notna(first_score) and pd.notna(last_score) and first_score > 0:
            percent_change = ((last_score - first_score) / first_score) * 100
            trend_data.append({
                "flair": flair,
                "first_score": first_score,
                "last_score": last_score,
                "percent_change": percent_change
            })

trend_df = pd.DataFrame(trend_data)
trend_df = trend_df.sort_values("percent_change", ascending=False)

print("\n=== FLAIR TREND ANALYSIS ===")
print(f"Time period: {first_month} to {last_month}")
print("\nFlairs with increasing performance:")
for i, row in trend_df[trend_df["percent_change"] > 0].iterrows():
    print(f"- {row['flair']}: {row['percent_change']:.1f}% increase")

print("\nFlairs with decreasing performance:")
for i, row in trend_df[trend_df["percent_change"] < 0].iterrows():
    print(f"- {row['flair']}: {row['percent_change']:.1f}% decrease")

# Recommendation based on trends
print("\n=== TREND-BASED RECOMMENDATIONS ===")
if not trend_df.empty:
    trending_flair = trend_df.iloc[0]["flair"]
    print(f"Consider using the '{trending_flair}' flair, which has shown a {trend_df.iloc[0]['percent_change']:.1f}% increase in performance")
```

## Exporting Data for Further Analysis

This example shows how to export data for use in other tools like Excel or Google Sheets.

```python
from redditflairanalyzer import RedditAnalyzer

# Initialize the analyzer
analyzer = RedditAnalyzer(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Data Export Example v1.0"
)

# Analyze a subreddit
subreddit_name = "marketing"
results = analyzer.analyze_subreddit(
    subreddit=subreddit_name,
    post_limit=1000,
    time_filter="year"
)

# Export in different formats
export_dir = "./exports"

# 1. Export to CSV
csv_path = analyzer.export(
    results,
    format="csv",
    filename=f"{export_dir}/{subreddit_name}_analysis"
)
print(f"CSV data exported to: {csv_path}")

# 2. Export to Excel with multiple sheets
excel_path = analyzer.export(
    results,
    format="excel",
    filename=f"{export_dir}/{subreddit_name}_analysis"
)
print(f"Excel data exported to: {excel_path}")

# 3. Export to JSON
# 3. Export to JSON
json_path = analyzer.export(
    results,
    format="json",
    filename=f"{export_dir}/{subreddit_name}_analysis"
)
print(f"JSON data exported to: {json_path}")

print("\nYou can now import this data into other tools for further analysis!")
```

## Custom Dashboard Creation

This example shows how to create a custom dashboard with specific visualizations.

```python
from redditflairanalyzer import RedditAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os

# Initialize the analyzer
analyzer = RedditAnalyzer(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="Custom Dashboard Example v1.0"
)

# Analyze a subreddit
subreddit_name = "datascience"
results = analyzer.analyze_subreddit(
    subreddit=subreddit_name,
    post_limit=500,
    time_filter="month"
)

# Extract data from results
flair_stats = results["flair_stats"]
posts_df = results["posts_df"]
viral_threshold = results["viral_threshold"]

# Get top 10 flairs for visualization
top_flairs = flair_stats.head(10)

# Create a custom dashboard using plotly
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Viral Rate by Flair",
        "Average Score vs. Comments",
        "Score Distribution",
        "Post Volume by Day of Week"
    ),
    specs=[
        [{"type": "bar"}, {"type": "scatter"}],
        [{"type": "histogram"}, {"type": "bar"}]
    ],
    vertical_spacing=0.1,
    horizontal_spacing=0.1
)

# 1. Viral rate by flair
fig.add_trace(
    go.Bar(
        x=top_flairs["viral_rate"],
        y=top_flairs["flair"],
        orientation="h",
        marker_color=top_flairs["viral_rate"],
        name="Viral Rate"
    ),
    row=1, col=1
)

# 2. Scatter plot of avg score vs comments
fig.add_trace(
    go.Scatter(
        x=flair_stats["avg_score"],
        y=flair_stats["avg_comments"],
        mode="markers",
        marker=dict(
            size=flair_stats["total_posts"],
            sizemode="area",
            sizeref=2.*max(flair_stats["total_posts"])/(40.**2),
            sizemin=4,
            color=flair_stats["viral_rate"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Viral Rate")
        ),
        text=flair_stats["flair"],
        hovertemplate="<b>%{text}</b><br>Avg Score: %{x:.1f}<br>Avg Comments: %{y:.1f}<br>Posts: %{marker.size}<extra></extra>"
    ),
    row=1, col=2
)

# 3. Score distribution
fig.add_trace(
    go.Histogram(
        x=posts_df["score"],
        nbinsx=50,
        marker_color="royalblue",
        name="Score Distribution"
    ),
    row=2, col=1
)

# Add vertical line for viral threshold
fig.add_vline(
    x=viral_threshold,
    line_dash="dash",
    line_color="red",
    row=2, col=1
)

# 4. Post volume by day of week
if "created_utc" in posts_df.columns:
    posts_df["day_of_week"] = posts_df["created_utc"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    post_counts = posts_df["day_of_week"].value_counts().reindex(day_order)
    
    fig.add_trace(
        go.Bar(
            x=post_counts.index,
            y=post_counts.values,
            marker_color="teal",
            name="Post Volume"
        ),
        row=2, col=2
    )

# Update layout
fig.update_layout(
    title_text=f"Custom Dashboard for r/{subreddit_name}",
    height=900,
    width=1200,
    showlegend=False,
    template="plotly_white"
)

# Update axes
fig.update_xaxes(title_text="Viral Rate", tickformat=".0%", row=1, col=1)
fig.update_xaxes(title_text="Average Score", row=1, col=2)
fig.update_yaxes(title_text="Average Comments", row=1, col=2)
fig.update_xaxes(title_text="Post Score", row=2, col=1)
fig.update_yaxes(title_text="Frequency", row=2, col=1)
fig.update_xaxes(title_text="Day of Week", row=2, col=2)
fig.update_yaxes(title_text="Number of Posts", row=2, col=2)

# Save the custom dashboard
os.makedirs("./custom_dashboards", exist_ok=True)
dashboard_path = f"./custom_dashboards/{subreddit_name}_custom_dashboard.html"
fig.write_html(dashboard_path)

print(f"Custom dashboard created: {dashboard_path}")
```

## Automating Regular Reports

This example shows how to set up automated weekly reports for a subreddit.

```python
import schedule
import time
import os
from datetime import datetime
from redditflairanalyzer import RedditAnalyzer
import pandas as pd

# Set up credentials (in practice, use environment variables)
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
USER_AGENT = "Automated Report Generator v1.0"

# Initialize the analyzer
analyzer = RedditAnalyzer(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def generate_weekly_report(subreddit_name="datascience"):
    """Generate a weekly report for the specified subreddit."""
    print(f"Generating weekly report for r/{subreddit_name}...")
    
    # Create report directory
    today = datetime.now().strftime("%Y-%m-%d")
    report_dir = f"./reports/{subreddit_name}/{today}"
    os.makedirs(report_dir, exist_ok=True)
    
    # Analyze the subreddit
    results = analyzer.analyze_subreddit(
        subreddit=subreddit_name,
        post_limit=500,
        time_filter="week",  # Only analyze the past week
        viral_threshold=90
    )
    
    # Generate visualizations
    viz_files = analyzer.visualize(
        results,
        output_dir=report_dir,
        interactive=True
    )
    
    # Export results
    export_path = analyzer.export(
        results,
        format="excel",
        filename=f"{report_dir}/{subreddit_name}_weekly_report"
    )
    
    # Create a summary report
    flair_stats = results.get('flair_stats')
    metrics = results.get('metrics', {})
    
    with open(f"{report_dir}/summary.txt", "w") as f:
        f.write(f"WEEKLY REPORT FOR r/{subreddit_name}\n")
        f.write(f"Date: {today}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("SUMMARY METRICS:\n")
        f.write(f"Total posts analyzed: {metrics.get('total_posts', 0)}\n")
        f.write(f"Viral threshold: {results.get('viral_threshold', 0):.1f}\n")
        f.write(f"Viral post percentage: {metrics.get('viral_post_percentage', 0):.1f}%\n\n")
        
        f.write("TOP 5 FLAIRS BY VIRAL RATE:\n")
        for i, (_, row) in enumerate(flair_stats.head(5).iterrows(), 1):
            f.write(f"{i}. {row['flair']}: {row['viral_rate']:.1%} viral rate ({row['total_posts']} posts)\n")
    
    print(f"Weekly report generated in {report_dir}")
    return report_dir

# Run once immediately
report_dir = generate_weekly_report()
print(f"Initial report created in {report_dir}")

# Schedule to run every Monday at 8:00 AM
schedule.every().monday.at("08:00").do(generate_weekly_report)
schedule.every().monday.at("08:00").do(generate_weekly_report, "python")  # Also track r/python

print("Scheduler set up. Reports will be generated every Monday at 8:00 AM.")
print("Press Ctrl+C to exit.")

# Keep the script running
try:
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
except KeyboardInterrupt:
    print("Scheduler stopped.")
```

These examples demonstrate various ways to use the Reddit Flair Analyzer for different analytical purposes, from basic analysis to advanced reporting and automation.