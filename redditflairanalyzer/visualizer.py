"""
Data visualization module for the Reddit Flair Analyzer.

This module creates professional visualizations of flair performance data
using static and interactive plots.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import json
from .logger import get_logger
import webbrowser


# Get module logger
logger = get_logger("visualizer")

class Visualizer:
    """
    Creates visualizations of Reddit flair analysis results.
    
    Supports static and interactive visualizations with various
    plot types and customization options.
    """
    
    def __init__(self, theme="light", palette="viridis", style="whitegrid"):
        """
        Initialize the Visualizer.
        
        Args:
            theme (str, optional): Color theme for plots. Defaults to "light".
            palette (str, optional): Color palette for plots. Defaults to "viridis".
            style (str, optional): Seaborn style. Defaults to "whitegrid".
        """
        self.theme = theme
        self.palette = palette
        self.style = style
        
        # Configure matplotlib and seaborn
        self._setup_plotting_style()
        
        logger.info("Visualizer initialized")
    
    def _setup_plotting_style(self):
        """Configure the plotting style."""
        # Set the style
        sns.set_style(self.style)
        
        # Set the aesthetic
        if self.theme == "dark":
            plt.style.use('dark_background')
            self.figure_bg_color = '#222222'
            self.text_color = 'white'
        else:
            self.figure_bg_color = 'white'
            self.text_color = 'black'
        
        # Set font sizes
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
        plt.rcParams['figure.titlesize'] = 20
        
        # Use high-resolution figures
        plt.rcParams['figure.dpi'] = 150
        plt.rcParams['savefig.dpi'] = 300
    
    def create_visualizations(self, results, output_dir="./", plot_types=None, interactive=False, open_dashboard=True):
        """
        Create visualizations from analysis results.
        
        Args:
            results (dict): Analysis results from FlairAnalyzer
            output_dir (str, optional): Directory to save visualizations. Defaults to "./".
            plot_types (list, optional): Types of plots to generate. If None, all plots are generated.
                Options: ['bar', 'heatmap', 'scatter', 'bubble', 'time', 'distribution', 'dashboard']
            interactive (bool, optional): Whether to create interactive visualizations. Defaults to False.
            
        Returns:
            dict: Paths to generated visualization files
        """
        logger.info(f"Creating visualizations (interactive: {interactive})")
        
        # Extract data from results
        flair_stats = results.get('flair_stats')
        posts_df = results.get('posts_df')
        viral_threshold = results.get('viral_threshold')
        subreddit = results.get('subreddit')
        metrics = results.get('metrics', {})
        
        if flair_stats is None or flair_stats.empty:
            logger.error("No flair statistics available for visualization")
            return {}
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.debug(f"Created output directory: {output_dir}")
        
        # Define default plot types
        if plot_types is None:
            plot_types = ['bar', 'heatmap', 'scatter', 'time', 'distribution']
            if interactive:
                plot_types.append('dashboard')
        
        # Generate visualizations
        output_files = {}
        
        # Generate each requested plot type
        for plot_type in plot_types:
            try:
                if plot_type == 'bar':
                    files = self._create_bar_charts(flair_stats, subreddit, output_dir, interactive)
                    output_files.update(files)
                
                elif plot_type == 'heatmap':
                    files = self._create_heatmap(flair_stats, subreddit, output_dir, interactive)
                    output_files.update(files)
                
                elif plot_type == 'scatter':
                    files = self._create_scatter_plots(flair_stats, subreddit, output_dir, interactive)
                    output_files.update(files)
                
                elif plot_type == 'bubble':
                    files = self._create_bubble_chart(flair_stats, subreddit, output_dir, interactive)
                    output_files.update(files)
                
                elif plot_type == 'time' and posts_df is not None:
                    files = self._create_time_analysis(posts_df, subreddit, output_dir, interactive)
                    output_files.update(files)
                
                elif plot_type == 'distribution' and posts_df is not None:
                    files = self._create_distribution_plots(posts_df, viral_threshold, subreddit, output_dir, interactive)
                    output_files.update(files)
                
                elif plot_type == 'dashboard' and interactive:
                    dashboard_file = self._create_interactive_dashboard(results, output_dir)
                    output_files['dashboard'] = dashboard_file
                
                logger.debug(f"Generated {plot_type} visualization")
            
            except Exception as e:
                logger.error(f"Error creating {plot_type} visualization: {e}")
        
        # Create summary visualization
        try:
            summary_file = self._create_summary_visualization(results, output_dir, interactive)
            output_files['summary'] = summary_file
            logger.debug("Generated summary visualization")
        except Exception as e:
            logger.error(f"Error creating summary visualization: {e}")
        
        logger.info(f"Created {len(output_files)} visualizations")

        # At the end of the method, after all visualizations are created and before returning output_files:
        if interactive and open_dashboard and 'dashboard' in output_files:
            dashboard_path = output_files['dashboard']
            dashboard_url = f"file://{os.path.abspath(dashboard_path)}"
            
            print(f"\nDashboard created: {dashboard_path}")
            print(f"Opening dashboard in your default web browser...")
            
            # Open the dashboard in the default browser
            webbrowser.open(dashboard_url)
        
        return output_files
    
    def _create_bar_charts(self, flair_stats, subreddit, output_dir, interactive=False):
        """Create bar charts showing flair performance."""
        output_files = {}
        
        # Limit to top 15 flairs by viral rate
        top_flairs = flair_stats.head(15).copy()
        
        if interactive:
            # Create interactive bar chart with plotly
            fig = make_subplots(rows=2, cols=1, subplot_titles=("Viral Rate by Flair", "Average Score by Flair"))
            
            # Viral rate plot
            fig.add_trace(
                go.Bar(
                    x=top_flairs['viral_rate'],
                    y=top_flairs['flair'],
                    orientation='h',
                    name='Viral Rate',
                    marker_color=px.colors.sequential.Viridis,
                    hovertemplate='%{y}: %{x:.2%}<br>Total Posts: %{text}<extra></extra>',
                    text=top_flairs['total_posts']
                ),
                row=1, col=1
            )
            
            # Average score plot
            fig.add_trace(
                go.Bar(
                    x=top_flairs['avg_score'],
                    y=top_flairs['flair'],
                    orientation='h',
                    name='Avg Score',
                    marker_color=px.colors.sequential.Plasma,
                    hovertemplate='%{y}: %{x:.1f}<br>Total Posts: %{text}<extra></extra>',
                    text=top_flairs['total_posts']
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title=f'Top Flairs in r/{subreddit}',
                height=800,
                width=1000,
                template='plotly_white',
                showlegend=False,
                margin=dict(t=80, b=40, l=200, r=40)
            )
            
            # Update axes
            fig.update_xaxes(title_text='Viral Rate', row=1, col=1, tickformat='.0%')
            fig.update_xaxes(title_text='Average Score', row=2, col=1)
            
            # Save interactive plot
            html_file = os.path.join(output_dir, f"{subreddit}_flair_bar_charts.html")
            fig.write_html(html_file)
            output_files['bar_charts_interactive'] = html_file
        
        # Create static bar charts with matplotlib
        fig, axes = plt.subplots(2, 1, figsize=(12, 14), constrained_layout=True)
        
        # Viral rate plot - Fixed with hue parameter
        bar1 = sns.barplot(x='viral_rate', y='flair', data=top_flairs, ax=axes[0], hue='flair', legend=False)
        axes[0].set_title(f'Top Flairs by Viral Rate in r/{subreddit}', fontsize=16)
        axes[0].set_xlabel('Viral Rate', fontsize=14)
        axes[0].set_ylabel('Flair', fontsize=14)
        axes[0].set_xlim(0, min(1, top_flairs['viral_rate'].max() * 1.2))
        
        # Add value labels
        for i, v in enumerate(top_flairs['viral_rate']):
            axes[0].text(v + 0.01, i, f'{v:.1%}', va='center')
        
        # Average score plot - Fixed with hue parameter
        bar2 = sns.barplot(x='avg_score', y='flair', data=top_flairs, ax=axes[1], hue='flair', legend=False)
        axes[1].set_title(f'Average Score by Flair in r/{subreddit}', fontsize=16)
        axes[1].set_xlabel('Average Score', fontsize=14)
        axes[1].set_ylabel('Flair', fontsize=14)
        
        # Add value labels
        for i, v in enumerate(top_flairs['avg_score']):
            axes[1].text(v + 1, i, f'{v:.1f}', va='center')
        
        # Add total posts annotation
        for i, posts in enumerate(top_flairs['total_posts']):
            axes[0].text(0.01, i, f'n={posts}', va='center')
            axes[1].text(top_flairs['avg_score'].min(), i, f'n={posts}', va='center')
        
        # Add metadata
        plt.suptitle(f'Flair Analysis for r/{subreddit}', fontsize=20)
        plt.figtext(0.5, 0.01, f'Analysis performed on {datetime.now().strftime("%Y-%m-%d")}', 
                ha='center', fontsize=10, style='italic')
        
        # Save the figure
        png_file = os.path.join(output_dir, f"{subreddit}_flair_bar_charts.png")
        plt.savefig(png_file, bbox_inches='tight')
        plt.close(fig)
        output_files['bar_charts'] = png_file
        
        return output_files
    
    def _create_heatmap(self, flair_stats, subreddit, output_dir, interactive=False):
        """Create a heatmap of flair performance metrics."""
        output_files = {}
        
        # Limit to top 15 flairs by viral rate
        top_flairs = flair_stats.head(15).copy()
        
        # Select metrics for heatmap
        metrics = ['viral_rate', 'avg_score', 'median_score', 'avg_comments',
                 'avg_upvote_ratio', 'viral_score']
        
        # Create a normalized copy of the data for the heatmap
        heatmap_data = top_flairs[['flair'] + metrics].copy()
        
        # Normalize each metric for better visualization
        for metric in metrics:
            max_val = heatmap_data[metric].max()
            min_val = heatmap_data[metric].min()
            if max_val > min_val:
                heatmap_data[metric] = (heatmap_data[metric] - min_val) / (max_val - min_val)
        
        # Reshape for heatmap
        heatmap_data = heatmap_data.set_index('flair')
        
        # Create better column names for display
        column_labels = {
            'viral_rate': 'Viral Rate',
            'avg_score': 'Avg Score',
            'median_score': 'Median Score',
            'avg_comments': 'Avg Comments',
            'avg_upvote_ratio': 'Upvote Ratio',
            'viral_score': 'Viral Score'
        }
        heatmap_data = heatmap_data.rename(columns=column_labels)
        
        if interactive:
            # Create interactive heatmap with plotly
            fig = px.imshow(
                heatmap_data,
                labels=dict(x="Metric", y="Flair", color="Value"),
                x=list(column_labels.values()),
                y=heatmap_data.index,
                color_continuous_scale='viridis',
                aspect="auto"
            )
            
            # Update layout
            fig.update_layout(
                title=f'Flair Performance Heatmap for r/{subreddit}',
                width=1000,
                height=800,
                template='plotly_white',
                margin=dict(t=80, b=40, l=200, r=40)
            )
            
            # Save interactive plot
            html_file = os.path.join(output_dir, f"{subreddit}_flair_heatmap.html")
            fig.write_html(html_file)
            output_files['heatmap_interactive'] = html_file
        
        # Create static heatmap with matplotlib/seaborn
        plt.figure(figsize=(14, 10))
        
        # Generate heatmap
        ax = sns.heatmap(
            heatmap_data,
            annot=True,
            fmt='.2f',
            cmap=self.palette,
            linewidths=0.5,
            cbar_kws={'label': 'Normalized Value'}
        )
        
        # Set titles and labels
        plt.title(f'Flair Performance Heatmap for r/{subreddit}', fontsize=18)
        plt.tight_layout()
        
        # Add metadata
        plt.figtext(0.5, 0.01, f'Higher values (darker color) indicate better performance. Analysis date: {datetime.now().strftime("%Y-%m-%d")}', 
                   ha='center', fontsize=10, style='italic')
        
        # Save the figure
        png_file = os.path.join(output_dir, f"{subreddit}_flair_heatmap.png")
        plt.savefig(png_file, bbox_inches='tight')
        plt.close()
        output_files['heatmap'] = png_file
        
        # Create a table with the actual values for reference
        reference_data = top_flairs[['flair'] + list(column_labels.keys())].copy()
        for col in column_labels.keys():
            if col == 'viral_rate' or col == 'avg_upvote_ratio':
                reference_data[col] = reference_data[col].apply(lambda x: f"{x:.2%}")
            else:
                reference_data[col] = reference_data[col].apply(lambda x: f"{x:.2f}")
        
        reference_data = reference_data.rename(columns=column_labels)
        
        # Save the reference table as CSV
        csv_file = os.path.join(output_dir, f"{subreddit}_flair_metrics.csv")
        reference_data.to_csv(csv_file, index=False)
        output_files['metrics_table'] = csv_file
        
        return output_files
    
    def _create_scatter_plots(self, flair_stats, subreddit, output_dir, interactive=False):
        """Create scatter plots showing relationships between metrics."""
        output_files = {}
        
        # Create scatter plot of viral rate vs. total posts
        plt.figure(figsize=(12, 8))
        
        # Create scatter plot with size based on average score
        scatter = sns.scatterplot(
            x='total_posts',
            y='viral_rate',
            size='avg_score',
            sizes=(20, 500),
            alpha=0.7,
            palette=self.palette,
            hue='viral_score',
            data=flair_stats
        )
        
        # Set titles and labels
        plt.title(f'Flair Viral Rate vs. Popularity in r/{subreddit}', fontsize=18)
        plt.xlabel('Number of Posts', fontsize=14)
        plt.ylabel('Viral Rate', fontsize=14)
        
        # Add flair labels to points
        for i, row in flair_stats.iterrows():
            if row['viral_rate'] > 0.05 or row['total_posts'] > flair_stats['total_posts'].median():
                plt.annotate(
                    row['flair'],
                    (row['total_posts'], row['viral_rate']),
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=9,
                    alpha=0.8
                )
        
        # Add trend line
        sns.regplot(
            x='total_posts',
            y='viral_rate',
            data=flair_stats,
            scatter=False,
            ci=None,
            line_kws={"color": "red", "alpha": 0.5, "lw": 2}
        )
        
        # Add explanatory text
        plt.figtext(0.5, 0.01, f'Circle size represents average score. Color intensity represents viral score.', 
                   ha='center', fontsize=10, style='italic')
        
        # Save the figure
        png_file = os.path.join(output_dir, f"{subreddit}_flair_scatter.png")
        plt.savefig(png_file, bbox_inches='tight')
        plt.close()
        output_files['scatter'] = png_file
        
        if interactive:
            # Create interactive scatter plot with plotly
            fig = px.scatter(
                flair_stats,
                x='total_posts',
                y='viral_rate',
                size='avg_score',
                color='viral_score',
                hover_name='flair',
                text='flair',
                log_x=True,
                size_max=60,
                color_continuous_scale='viridis',
                hover_data={
                    'total_posts': True,
                    'viral_rate': ':.2%',
                    'avg_score': ':.1f',
                    'num_viral_posts': True,
                    'viral_score': ':.3f',
                    'flair': False
                }
            )
            
            # Update layout
            fig.update_layout(
                title=f'Flair Performance in r/{subreddit}',
                xaxis_title='Number of Posts (log scale)',
                yaxis_title='Viral Rate',
                template='plotly_white',
                height=800,
                width=1000,
                yaxis=dict(tickformat='.0%')
            )
            
            # Add trend line
            fig.update_traces(
                textposition='top center',
                textfont=dict(size=10, color='rgba(0,0,0,0.6)')
            )
            
            # Save interactive plot
            html_file = os.path.join(output_dir, f"{subreddit}_flair_scatter_interactive.html")
            fig.write_html(html_file)
            output_files['scatter_interactive'] = html_file
            
        return output_files
    
    def _create_bubble_chart(self, flair_stats, subreddit, output_dir, interactive=False):
        """Create a bubble chart visualization."""
        output_files = {}
        
        # Only create bubble chart if interactive is True (it's better with interactivity)
        if interactive:
            # Limit to flairs with at least a few posts
            filtered_flairs = flair_stats[flair_stats['total_posts'] >= 5].copy()
            
            # Create bubble chart
            fig = px.scatter(
                filtered_flairs,
                x='avg_score',
                y='avg_comments',
                size='total_posts',
                color='viral_rate',
                hover_name='flair',
                size_max=60,
                color_continuous_scale='viridis',
                hover_data={
                    'viral_rate': ':.2%',
                    'total_posts': True,
                    'num_viral_posts': True,
                    'avg_upvote_ratio': ':.2%'
                }
            )
            
            # Update layout
            fig.update_layout(
                title=f'Engagement Analysis for r/{subreddit} Flairs',
                xaxis_title='Average Score',
                yaxis_title='Average Comments',
                template='plotly_white',
                height=800,
                width=1000,
                coloraxis_colorbar=dict(title='Viral Rate')
            )
            
            # Save interactive plot
            html_file = os.path.join(output_dir, f"{subreddit}_flair_bubble_chart.html")
            fig.write_html(html_file)
            output_files['bubble_chart'] = html_file
        
        return output_files
    
    def _create_time_analysis(self, posts_df, subreddit, output_dir, interactive=False):
        """Create visualizations of time-based patterns."""
        output_files = {}
        
        # Check if time data is available
        if 'created_utc' not in posts_df.columns:
            logger.warning("No timestamp data available for time analysis")
            return output_files
        
        # Extract time components if not already present
        if 'post_hour' not in posts_df.columns:
            posts_df['post_hour'] = posts_df['created_utc'].dt.hour
        
        if 'post_day' not in posts_df.columns:
            posts_df['post_day'] = posts_df['created_utc'].dt.day_name()
        
        # Check if viral information is available
        has_viral_info = 'is_viral' in posts_df.columns
        
        # Create aggregation dictionary based on available columns
        agg_dict = {'score': 'mean', 'id': 'count'}
        if has_viral_info:
            agg_dict['is_viral'] = 'mean'
        
        # Analyze posting time
        hour_stats = posts_df.groupby('post_hour').agg(agg_dict).reset_index()
        day_stats = posts_df.groupby('post_day').agg(agg_dict).reset_index()
        
        # Add is_viral column with zeros if it doesn't exist (for plotting)
        if not has_viral_info:
            hour_stats['is_viral'] = 0
            day_stats['is_viral'] = 0
            logger.warning("No viral information available, time analysis will only show scores")
        
        # Order days correctly
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_stats['post_day'] = pd.Categorical(day_stats['post_day'], categories=day_order, ordered=True)
        day_stats = day_stats.sort_values('post_day')
        
        # Create static plots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), constrained_layout=True)
        
        # Hour plots
        if has_viral_info:
            sns.barplot(x='post_hour', y='is_viral', data=hour_stats, ax=axes[0, 0], color='teal')
            axes[0, 0].set_title('Viral Rate by Hour of Day', fontsize=16)
        else:
            # Skip viral rate plot if no data
            axes[0, 0].set_title('Viral Rate Not Available', fontsize=16)
            axes[0, 0].text(0.5, 0.5, "No viral data available", 
                            ha='center', va='center', transform=axes[0, 0].transAxes)
        
        axes[0, 0].set_xlabel('Hour (UTC)', fontsize=14)
        axes[0, 0].set_ylabel('Viral Rate', fontsize=14)
        axes[0, 0].set_xticks(range(0, 24, 2))
        
        sns.barplot(x='post_hour', y='score', data=hour_stats, ax=axes[0, 1], color='darkblue')
        axes[0, 1].set_title('Average Score by Hour of Day', fontsize=16)
        axes[0, 1].set_xlabel('Hour (UTC)', fontsize=14)
        axes[0, 1].set_ylabel('Average Score', fontsize=14)
        axes[0, 1].set_xticks(range(0, 24, 2))
        
        # Day plots
        if has_viral_info:
            sns.barplot(x='post_day', y='is_viral', data=day_stats, ax=axes[1, 0], color='teal')
            axes[1, 0].set_title('Viral Rate by Day of Week', fontsize=16)
        else:
            # Skip viral rate plot if no data
            axes[1, 0].set_title('Viral Rate Not Available', fontsize=16)
            axes[1, 0].text(0.5, 0.5, "No viral data available", 
                            ha='center', va='center', transform=axes[1, 0].transAxes)
        
        axes[1, 0].set_xlabel('Day of Week', fontsize=14)
        axes[1, 0].set_ylabel('Viral Rate', fontsize=14)
        axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=45)
        
        sns.barplot(x='post_day', y='score', data=day_stats, ax=axes[1, 1], color='darkblue')
        axes[1, 1].set_title('Average Score by Day of Week', fontsize=16)
        axes[1, 1].set_xlabel('Day of Week', fontsize=14)
        axes[1, 1].set_ylabel('Average Score', fontsize=14)
        axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=45)
        
        # Add suptitle
        plt.suptitle(f'Timing Analysis for r/{subreddit} Posts', fontsize=20)
        
        # Add post count annotation
        for i, count in enumerate(hour_stats['id']):
            axes[0, 1].text(i, hour_stats.iloc[i]['score'], f"{count}", ha='center', va='bottom', fontsize=8)
        
        for i, count in enumerate(day_stats['id']):
            axes[1, 1].text(i, day_stats.iloc[i]['score'], f"{count}", ha='center', va='bottom', fontsize=8)
        
        if has_viral_info:
            for i, count in enumerate(hour_stats['id']):
                axes[0, 0].text(i, hour_stats.iloc[i]['is_viral'], f"{count}", ha='center', va='bottom', fontsize=8)
            
            for i, count in enumerate(day_stats['id']):
                axes[1, 0].text(i, day_stats.iloc[i]['is_viral'], f"{count}", ha='center', va='bottom', fontsize=8)
        
        # Save the figure
        png_file = os.path.join(output_dir, f"{subreddit}_time_analysis.png")
        plt.savefig(png_file, bbox_inches='tight')
        plt.close(fig)
        output_files['time_analysis'] = png_file
        
        if interactive:
            # Create interactive time analysis with plotly
            if has_viral_info:
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=(
                        "Viral Rate by Hour of Day", "Average Score by Hour of Day",
                        "Viral Rate by Day of Week", "Average Score by Day of Week"
                    )
                )
                
                # Hour - Viral Rate
                fig.add_trace(
                    go.Bar(
                        x=hour_stats['post_hour'],
                        y=hour_stats['is_viral'],
                        name='Viral Rate',
                        marker_color='teal',
                        hovertemplate='Hour: %{x}<br>Viral Rate: %{y:.2%}<br>Posts: %{text}<extra></extra>',
                        text=hour_stats['id']
                    ),
                    row=1, col=1
                )
                
                # Day - Viral Rate
                fig.add_trace(
                    go.Bar(
                        x=day_stats['post_day'],
                        y=day_stats['is_viral'],
                        name='Viral Rate',
                        marker_color='teal',
                        hovertemplate='Day: %{x}<br>Viral Rate: %{y:.2%}<br>Posts: %{text}<extra></extra>',
                        text=day_stats['id']
                    ),
                    row=2, col=1
                )
            else:
                # Create a simpler 1x2 subplot if viral data is not available
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=(
                        "Average Score by Hour of Day",
                        "Average Score by Day of Week"
                    )
                )
            
            # Hour - Score
            fig.add_trace(
                go.Bar(
                    x=hour_stats['post_hour'],
                    y=hour_stats['score'],
                    name='Avg Score',
                    marker_color='darkblue',
                    hovertemplate='Hour: %{x}<br>Avg Score: %{y:.1f}<br>Posts: %{text}<extra></extra>',
                    text=hour_stats['id']
                ),
                row=1, col=2 if has_viral_info else 1
            )
            
            # Day - Score
            fig.add_trace(
                go.Bar(
                    x=day_stats['post_day'],
                    y=day_stats['score'],
                    name='Avg Score',
                    marker_color='darkblue',
                    hovertemplate='Day: %{x}<br>Avg Score: %{y:.1f}<br>Posts: %{text}<extra></extra>',
                    text=day_stats['id']
                ),
                row=2, col=2 if has_viral_info else 1
            )
            
            # Update layout
            fig.update_layout(
                title=f'Timing Analysis for r/{subreddit} Posts',
                height=800,
                width=1200,
                template='plotly_white',
                showlegend=False
            )
            
            # Update axes for score plots
            if has_viral_info:
                # Update y-axes
                fig.update_yaxes(title_text="Viral Rate", tickformat='.0%', row=1, col=1)
                fig.update_yaxes(title_text="Average Score", row=1, col=2)
                fig.update_yaxes(title_text="Viral Rate", tickformat='.0%', row=2, col=1)
                fig.update_yaxes(title_text="Average Score", row=2, col=2)
                
                # Update x-axes
                fig.update_xaxes(title_text="Hour (UTC)", row=1, col=1)
                fig.update_xaxes(title_text="Hour (UTC)", row=1, col=2)
                fig.update_xaxes(title_text="Day of Week", row=2, col=1)
                fig.update_xaxes(title_text="Day of Week", row=2, col=2)
            else:
                # Update axes for simplified layout
                fig.update_yaxes(title_text="Average Score", row=1, col=1)
                fig.update_yaxes(title_text="Average Score", row=2, col=1)
                
                fig.update_xaxes(title_text="Hour (UTC)", row=1, col=1)
                fig.update_xaxes(title_text="Day of Week", row=2, col=1)
            
            # Save interactive plot
            html_file = os.path.join(output_dir, f"{subreddit}_time_analysis_interactive.html")
            fig.write_html(html_file)
            output_files['time_analysis_interactive'] = html_file
        
        return output_files
    
    def _create_distribution_plots(self, posts_df, viral_threshold, subreddit, output_dir, interactive=False):
        """Create distribution plots of post scores."""
        output_files = {}
        
        # Check if required data is available
        if 'score' not in posts_df.columns:
            logger.warning("No score data available for distribution analysis")
            return output_files
        
        # Create figure
        plt.figure(figsize=(14, 8))
        
        # Create distribution plot
        ax = sns.histplot(
            data=posts_df,
            x='score',
            bins=50,
            kde=True,
            color='royalblue'
        )
        
        # Add vertical line at viral threshold
        plt.axvline(x=viral_threshold, color='red', linestyle='--', alpha=0.7)
        
        # Add text annotation for viral threshold
        plt.text(
            viral_threshold * 1.05,
            ax.get_ylim()[1] * 0.9,
            f'Viral Threshold: {viral_threshold:.0f}',
            color='red',
            fontsize=12,
            ha='left',
            va='top'
        )
        
        # Set plot labels and title
        plt.xlabel('Post Score', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.title(f'Score Distribution for r/{subreddit} Posts', fontsize=18)
        
        # Improve x-axis limits
        plt.xlim(left=0)
        if posts_df['score'].max() > viral_threshold * 3:
            plt.xlim(right=viral_threshold * 3)
            plt.figtext(0.5, 0.01, f'Note: Plot truncated. Maximum score is {posts_df["score"].max():.0f}', 
                       ha='center', fontsize=10, style='italic')
        
        # Save the figure
        png_file = os.path.join(output_dir, f"{subreddit}_score_distribution.png")
        plt.savefig(png_file, bbox_inches='tight')
        plt.close()
        output_files['distribution'] = png_file
        
        if interactive:
            # Create interactive distribution plot
            fig = px.histogram(
                posts_df,
                x='score',
                nbins=50,
                marginal='violin',
                title=f'Score Distribution for r/{subreddit} Posts',
                opacity=0.7,
                color_discrete_sequence=['royalblue']
            )
            
            # Add viral threshold line
            fig.add_vline(
                x=viral_threshold,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Viral Threshold: {viral_threshold:.0f}",
                annotation_position="top right"
            )
            
            # Update layout
            fig.update_layout(
                xaxis_title='Post Score',
                yaxis_title='Frequency',
                template='plotly_white',
                height=600,
                width=1000
            )
            
            # Improve x-axis limits
            if posts_df['score'].max() > viral_threshold * 3:
                fig.update_xaxes(range=[0, viral_threshold * 3])
                fig.add_annotation(
                    text=f"Note: Plot truncated. Maximum score is {posts_df['score'].max():.0f}",
                    xref="paper", yref="paper",
                    x=0.5, y=0,
                    showarrow=False,
                    font=dict(size=10, color="gray"),
                    bordercolor="gray",
                    borderwidth=1,
                    borderpad=4,
                    bgcolor="white"
                )
            
            # Save interactive plot
            html_file = os.path.join(output_dir, f"{subreddit}_score_distribution_interactive.html")
            fig.write_html(html_file)
            output_files['distribution_interactive'] = html_file
        
        return output_files
    
    
    def _create_interactive_dashboard(self, results, output_dir):
        """Create a comprehensive interactive dashboard."""
        # Extract data from results
        flair_stats = results.get('flair_stats')
        posts_df = results.get('posts_df')
        viral_threshold = results.get('viral_threshold')
        subreddit = results.get('subreddit')
        metrics = results.get('metrics', {})
        
        # Check if we have enough data for the dashboard
        if flair_stats is None or flair_stats.empty:
            logger.error("No flair statistics available for dashboard")
            return None
        
        # Limit to top 15 flairs for visualizations
        top_flairs = flair_stats.head(15).copy()
        
        # Check if we have score distribution data
        has_score_data = posts_df is not None and 'score' in posts_df.columns
        
        # Check if we have time data
        has_time_data = posts_df is not None and 'created_utc' in posts_df.columns
        
        # Check if we have viral information
        has_viral_info = posts_df is not None and 'is_viral' in posts_df.columns
        
        # Prepare time data if available
        hour_stats = None
        day_stats = None
        if has_time_data:
            # Extract time components if not already present
            if 'post_hour' not in posts_df.columns:
                posts_df['post_hour'] = posts_df['created_utc'].dt.hour
            
            if 'post_day' not in posts_df.columns:
                posts_df['post_day'] = posts_df['created_utc'].dt.day_name()
            
            # Create aggregation dictionary based on available columns
            agg_dict = {'score': 'mean', 'id': 'count'}
            if has_viral_info:
                agg_dict['is_viral'] = 'mean'
            
            # Analyze posting time
            hour_stats = posts_df.groupby('post_hour').agg(agg_dict).reset_index()
            day_stats = posts_df.groupby('post_day').agg(agg_dict).reset_index()
            
            # Order days correctly
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            if 'post_day' in day_stats.columns:
                day_stats['post_day'] = pd.Categorical(day_stats['post_day'], categories=day_order, ordered=True)
                day_stats = day_stats.sort_values('post_day')
        
        # Generate HTML for the dashboard
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reddit Flair Analysis Dashboard - r/{subreddit}</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    color: #333;
                    background-color: #f5f8fa;
                }}
                .container {{
                    width: 95%;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4285f4;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .summary-box {{
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                .metric-card {{
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    transition: transform 0.2s;
                }}
                .metric-card:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                .metric-value {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #4285f4;
                    margin-bottom: 5px;
                }}
                .metric-label {{
                    font-size: 14px;
                    color: #666;
                }}
                .chart-container {{
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .chart-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                    gap: 20px;
                }}
                h2 {{
                    color: #4285f4;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                    border-top: 1px solid #eee;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                table, th, td {{
                    border: 1px solid #ddd;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: 600;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                tr:hover {{
                    background-color: #f1f1f1;
                }}
                .color-scale {{
                    display: flex;
                    align-items: center;
                    margin-top: 10px;
                }}
                .color-bar {{
                    height: 15px;
                    flex-grow: 1;
                    background: linear-gradient(to right, #fde725, #5ec962, #21918c, #3b528b, #440154);
                    border-radius: 3px;
                }}
                .scale-labels {{
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                    color: #666;
                    margin-top: 5px;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    margin-right: 15px;
                    font-size: 12px;
                }}
                .legend-color {{
                    width: 12px;
                    height: 12px;
                    margin-right: 5px;
                    border-radius: 2px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reddit Flair Analysis Dashboard</h1>
                <p>Comprehensive analysis of r/{subreddit} post flairs</p>
            </div>
            
            <div class="container">
                <div class="summary-box">
                    <h2>Analysis Summary</h2>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('total_posts', 0):,}</div>
                            <div class="metric-label">Total Posts Analyzed</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('total_flairs', 0):,}</div>
                            <div class="metric-label">Unique Flairs</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.get('viral_post_percentage', 0):.1f}%</div>
                            <div class="metric-label">Viral Post Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{viral_threshold:,.0f}</div>
                            <div class="metric-label">Viral Threshold (Score)</div>
                        </div>
                    </div>
                    
                    <h3>Key Findings</h3>
                    <p>Most viral flair: <strong>{metrics.get('most_viral_flair', 'N/A')}</strong> ({metrics.get('most_viral_rate', 0):.1%} viral rate)</p>
                    <p>Highest average score: <strong>{metrics.get('highest_avg_score_flair', 'N/A')}</strong> ({metrics.get('highest_avg_score', 0):,.1f} average score)</p>
                </div>
                
                <!-- Top Flairs Section -->
                <div class="chart-grid">
                    <div class="chart-container">
                        <h2>Top Flairs by Viral Rate</h2>
                        <div id="viral-rate-chart" style="height: 500px;"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Flair Performance Metrics</h2>
                        <div id="heatmap-chart" style="height: 500px;"></div>
                        <div class="color-scale">
                            <div class="color-bar"></div>
                        </div>
                        <div class="scale-labels">
                            <span>Low</span>
                            <span>High</span>
                        </div>
                    </div>
                </div>
                
                <!-- Add distribution plot if score data is available -->
                {'''
                <div class="chart-container">
                    <h2>Score Distribution</h2>
                    <div id="score-distribution" style="height: 400px;"></div>
                </div>
                ''' if has_score_data else ''}
                
                <!-- Add time analysis if time data is available -->
                {'''
                <div class="chart-grid">
                    <div class="chart-container">
                        <h2>Posting Time Analysis: Hour of Day</h2>
                        <div id="time-analysis-hour" style="height: 400px;"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h2>Posting Time Analysis: Day of Week</h2>
                        <div id="time-analysis-day" style="height: 400px;"></div>
                    </div>
                </div>
                ''' if has_time_data else ''}
                
                <!-- Detailed data table -->
                <div class="chart-container">
                    <h2>Top Performing Flairs - Detailed Data</h2>
                    <div style="overflow-x: auto;">
                        <table id="flair-table">
                            <thead>
                                <tr>
                                    <th>Rank</th>
                                    <th>Flair</th>
                                    <th>Viral Rate</th>
                                    <th>Total Posts</th>
                                    <th>Viral Posts</th>
                                    <th>Avg Score</th>
                                    <th>Max Score</th>
                                    <th>Avg Comments</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Table rows will be inserted by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>Generated with Reddit Flair Analyzer on {datetime.now().strftime('%Y-%m-%d')} | Data reflects posts as of analysis time</p>
                <p><a href="https://github.com/themanojdesai/reddit-flair-analyzer" target="_blank">GitHub Repository</a></p>
            </div>
            
            <script>
                // Data from Python analysis
                const flairStats = {json.dumps(top_flairs.to_dict('records'))};
                const viralThreshold = {viral_threshold};
                
                // Populate the flair table
                const tableBody = document.getElementById('flair-table').getElementsByTagName('tbody')[0];
                flairStats.forEach((flair, index) => {{
                    const row = tableBody.insertRow();
                    row.insertCell(0).innerText = index + 1;
                    row.insertCell(1).innerText = flair.flair;
                    row.insertCell(2).innerText = (flair.viral_rate * 100).toFixed(1) + '%';
                    row.insertCell(3).innerText = flair.total_posts;
                    row.insertCell(4).innerText = flair.num_viral_posts;
                    row.insertCell(5).innerText = flair.avg_score.toFixed(1);
                    row.insertCell(6).innerText = flair.max_score;
                    row.insertCell(7).innerText = flair.avg_comments ? flair.avg_comments.toFixed(1) : 'N/A';
                }});
                
                // Create viral rate chart
                const viralRateData = [{{
                    x: flairStats.map(f => f.viral_rate),
                    y: flairStats.map(f => f.flair),
                    type: 'bar',
                    orientation: 'h',
                    marker: {{
                        color: flairStats.map(f => f.viral_rate),
                        colorscale: 'Viridis'
                    }},
                    hovertemplate: '%{{y}}: %{{x:.1%}}<br>Total Posts: %{{text}}<extra></extra>',
                    text: flairStats.map(f => f.total_posts)
                }}];
                
                const viralRateLayout = {{
                    title: 'Top Flairs by Viral Rate',
                    xaxis: {{ title: 'Viral Rate', tickformat: '.0%' }},
                    yaxis: {{ title: 'Flair' }},
                    margin: {{ l: 150, r: 20, b: 40, t: 40 }},
                    height: 500
                }};
                
                Plotly.newPlot('viral-rate-chart', viralRateData, viralRateLayout);
                
                // Create heatmap
                const heatmapData = [{{
                    z: [
                        flairStats.map(f => f.viral_rate / Math.max(...flairStats.map(f => f.viral_rate))),
                        flairStats.map(f => f.avg_score / Math.max(...flairStats.map(f => f.avg_score))),
                        flairStats.map(f => f.avg_comments / Math.max(...flairStats.map(f => f.avg_comments || 1))),
                        flairStats.map(f => f.avg_upvote_ratio / Math.max(...flairStats.map(f => f.avg_upvote_ratio || 1)))
                    ],
                    x: flairStats.map(f => f.flair),
                    y: ['Viral Rate', 'Avg Score', 'Avg Comments', 'Upvote Ratio'],
                    type: 'heatmap',
                    colorscale: 'Viridis',
                    hovertemplate: 'Flair: %{{x}}<br>Metric: %{{y}}<br>Normalized Value: %{{z:.2f}}<extra></extra>'
                }}];
                
                const heatmapLayout = {{
                    title: 'Normalized Flair Performance Metrics',
                    margin: {{ l: 100, r: 20, b: 150, t: 40 }},
                    height: 500,
                    xaxis: {{ tickangle: -45 }}
                }};
                
                Plotly.newPlot('heatmap-chart', heatmapData, heatmapLayout);
                
                // Add score distribution if data is available
                if (document.getElementById('score-distribution')) {{
                    // Create histogram data
                    const scoreData = {json.dumps([float(x) for x in posts_df['score'].tolist()]) if has_score_data else '[]'};
                    
                    const histogramData = [{{
                        x: scoreData,
                        type: 'histogram',
                        nbinsx: 50,
                        marker: {{
                            color: 'royalblue',
                            opacity: 0.7
                        }}
                    }}];
                    
                    const histogramLayout = {{
                        title: 'Score Distribution',
                        xaxis: {{ title: 'Post Score', range: [0, viralThreshold * 3] }},
                        yaxis: {{ title: 'Frequency' }},
                        shapes: [{{
                            type: 'line',
                            x0: viralThreshold,
                            y0: 0,
                            x1: viralThreshold,
                            y1: 1,
                            yref: 'paper',
                            line: {{
                                color: 'red',
                                width: 2,
                                dash: 'dash'
                            }}
                        }}],
                        annotations: [{{
                            x: viralThreshold,
                            y: 1,
                            yref: 'paper',
                            text: `Viral Threshold: ${{viralThreshold}}`,
                            showarrow: true,
                            arrowhead: 7,
                            ax: 40,
                            ay: -40,
                            bgcolor: 'white',
                            bordercolor: 'red',
                            borderwidth: 1,
                            borderpad: 4
                        }}]
                    }};
                    
                    Plotly.newPlot('score-distribution', histogramData, histogramLayout);
                }}
                
                // Add time analysis if data is available
                if (document.getElementById('time-analysis-hour')) {{
                    // Hour analysis
                    const hourData = {json.dumps(hour_stats.to_dict('records')) if hour_stats is not None else '[]'};
                    
                    const hourScoreData = [{{
                        x: hourData.map(h => h.post_hour),
                        y: hourData.map(h => h.score),
                        type: 'bar',
                        name: 'Avg Score',
                        marker: {{ color: 'darkblue' }},
                        hovertemplate: 'Hour: %{{x}}<br>Avg Score: %{{y:.1f}}<br>Posts: %{{text}}<extra></extra>',
                        text: hourData.map(h => h.id)
                    }}];
                    
                    const hourLayout = {{
                        title: 'Average Score by Hour of Day',
                        xaxis: {{ title: 'Hour (UTC)', dtick: 2 }},
                        yaxis: {{ title: 'Average Score' }}
                    }};
                    
                    Plotly.newPlot('time-analysis-hour', hourScoreData, hourLayout);
                }}
                
                if (document.getElementById('time-analysis-day')) {{
                    // Day analysis
                    const dayData = {json.dumps(day_stats.to_dict('records')) if day_stats is not None else '[]'};
                    
                    const dayScoreData = [{{
                        x: dayData.map(d => d.post_day),
                        y: dayData.map(d => d.score),
                        type: 'bar',
                        name: 'Avg Score',
                        marker: {{ color: 'darkblue' }},
                        hovertemplate: 'Day: %{{x}}<br>Avg Score: %{{y:.1f}}<br>Posts: %{{text}}<extra></extra>',
                        text: dayData.map(d => d.id)
                    }}];
                    
                    const dayLayout = {{
                        title: 'Average Score by Day of Week',
                        xaxis: {{ title: 'Day of Week' }},
                        yaxis: {{ title: 'Average Score' }}
                    }};
                    
                    Plotly.newPlot('time-analysis-day', dayScoreData, dayLayout);
                }}
            </script>
        </body>
        </html>
        """
        
        # Save the dashboard HTML
        html_file = os.path.join(output_dir, f"{subreddit}_dashboard.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Created interactive dashboard at {html_file}")
        
        return html_file

    
    def _create_summary_visualization(self, results, output_dir, interactive=False):
        """Create a summary visualization with key findings."""
        # Extract data from results
        flair_stats = results.get('flair_stats')
        subreddit = results.get('subreddit')
        metrics = results.get('metrics', {})
        
        # Create a figure with subplots
        fig, axes = plt.subplots(1, 2, figsize=(16, 8), constrained_layout=True)
        
        # Plot 1: Top 5 flairs by viral rate
        top_flairs = flair_stats.head(5).copy()
        
        # Bar chart for viral rate
        sns.barplot(
            x='viral_rate',
            y='flair',
            data=top_flairs,
            ax=axes[0],
            palette=sns.color_palette("viridis", n_colors=len(top_flairs))
        )
        
        # Add value labels
        for i, v in enumerate(top_flairs['viral_rate']):
            axes[0].text(v + 0.01, i, f'{v:.1%}', va='center')
        
        # Set titles and labels
        axes[0].set_title('Top 5 Flairs by Viral Rate', fontsize=16)
        axes[0].set_xlabel('Viral Rate', fontsize=14)
        axes[0].set_ylabel('Flair', fontsize=14)
        axes[0].set_xlim(0, min(1, top_flairs['viral_rate'].max() * 1.2))
        
        # Plot 2: Performance metrics for top flair
        if not flair_stats.empty:
            top_flair = flair_stats.iloc[0]
            
            # Create metrics to display
            metrics_data = {
                'Metric': ['Viral Rate', 'Posts', 'Viral Posts', 'Avg Score', 'Max Score', 'Avg Comments'],
                'Value': [
                    f"{top_flair['viral_rate']:.1%}",
                    f"{top_flair['total_posts']}",
                    f"{top_flair['num_viral_posts']}",
                    f"{top_flair['avg_score']:.1f}",
                    f"{top_flair['max_score']:.0f}",
                    f"{top_flair['avg_comments']:.1f}"
                ]
            }
            
            metrics_df = pd.DataFrame(metrics_data)
            
            # Create a table
            axes[1].axis('tight')
            axes[1].axis('off')
            table = axes[1].table(
                cellText=metrics_df.values,
                colLabels=metrics_df.columns,
                loc='center',
                cellLoc='center',
                colColours=['#f2f2f2', '#f2f2f2'],
                cellColours=[['#ffffff', '#eaf7ff'] for _ in range(len(metrics_df))]
            )
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.scale(1.2, 1.5)
            
            # Add title
            axes[1].set_title(f'Top Flair Details: {top_flair["flair"]}', fontsize=16)
        
        # Add overall title and metadata
        plt.suptitle(f'Flair Analysis Summary for r/{subreddit}', fontsize=20)
        plt.figtext(0.5, 0.01, f'Analysis date: {datetime.now().strftime("%Y-%m-%d")}', 
                   ha='center', fontsize=10, style='italic')
        
        # Save the figure
        png_file = os.path.join(output_dir, f"{subreddit}_summary.png")
        plt.savefig(png_file, bbox_inches='tight')
        plt.close(fig)
        
        return png_file