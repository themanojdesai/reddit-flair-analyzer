"""
Reddit data scraping module for the Reddit Flair Analyzer.

This module handles all interaction with the Reddit API through PRAW,
collecting posts and their metadata from specified subreddits.
"""

import praw
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm
import concurrent.futures
import math
from .logger import get_logger

# Get module logger
logger = get_logger("scraper")

class RedditScraper:
    """
    Handles collection of Reddit post data through the Reddit API.
    
    Supports efficient batch scraping with rate limiting awareness
    and multi-threaded processing for faster data collection.
    
    Args:
        client_id (str): Reddit API client ID
        client_secret (str): Reddit API client secret
        user_agent (str): Reddit API user agent
        batch_size (int, optional): Number of posts to process in each batch. Defaults to 100.
        max_workers (int, optional): Maximum number of worker threads. Defaults to 4.
    """
    
    def __init__(self, client_id, client_secret, user_agent, batch_size=100, max_workers=4):
        """Initialize the Reddit Scraper with API credentials."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.batch_size = batch_size
        self.max_workers = max_workers
        
        # Create Reddit instance
        self.reddit = self._create_reddit_instance()
        
        logger.info("RedditScraper initialized")
    
    def _create_reddit_instance(self):
        """Create and return a PRAW Reddit instance."""
        try:
            reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            logger.debug(f"Created Reddit instance (read-only: {reddit.read_only})")
            return reddit
        except Exception as e:
            logger.error(f"Failed to create Reddit instance: {e}")
            raise
    
    def scrape_subreddit(self, subreddit_name, limit=1000, time_filter="all", use_multithreading=True):
        """
        Scrape posts from a specific subreddit.
        
        Args:
            subreddit_name (str): Name of the subreddit to scrape (without r/ prefix)
            limit (int, optional): Maximum number of posts to retrieve. Defaults to 1000.
            time_filter (str, optional): Time filter for posts ('all', 'day', 'week', 'month', 'year').
                Defaults to "all".
            use_multithreading (bool, optional): Whether to use multiple threads for faster scraping.
                Defaults to True.
        
        Returns:
            pandas.DataFrame: DataFrame containing post data
        """
        logger.info(f"Starting to scrape r/{subreddit_name} (limit: {limit}, time filter: {time_filter})")
        
        try:
            # Get subreddit
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get subreddit info for logging
            try:
                subscribers = subreddit.subscribers
                logger.info(f"r/{subreddit_name} has {subscribers:,} subscribers")
            except:
                logger.warning(f"Could not retrieve subscriber count for r/{subreddit_name}")
            
            # Get posts
            if use_multithreading and limit > self.batch_size:
                posts_data = self._scrape_with_multithreading(subreddit, limit, time_filter)
            else:
                posts_data = self._scrape_sequentially(subreddit, limit, time_filter)
            
            # Convert to DataFrame
            df = pd.DataFrame(posts_data)
            
            # Process and clean the data
            df = self._process_dataframe(df)
            
            logger.info(f"Successfully scraped {len(df)} posts from r/{subreddit_name}")
            
            return df
        
        except Exception as e:
            logger.error(f"Error scraping r/{subreddit_name}: {e}")
            raise
    
    def _scrape_sequentially(self, subreddit, limit, time_filter):
        """Scrape posts sequentially with a progress bar."""
        posts_data = []
        
        # Create progress bar
        pbar = tqdm(total=min(limit, 1000), desc=f"Scraping r/{subreddit.display_name}", unit="posts")
        
        # Collect posts
        for post in subreddit.top(time_filter=time_filter, limit=limit):
            post_data = self._extract_post_data(post)
            posts_data.append(post_data)
            pbar.update(1)
            
            # Check if we've reached the limit
            if len(posts_data) >= limit:
                break
        
        pbar.close()
        return posts_data
    
    def _scrape_with_multithreading(self, subreddit, limit, time_filter):
        """Scrape posts using multiple threads for faster processing."""
        # Calculate number of batches
        num_batches = math.ceil(limit / self.batch_size)
        posts_data = []
        
        logger.info(f"Using multithreading with {self.max_workers} workers, {num_batches} batches")
        
        # Create batches of post IDs first (to avoid rate limiting issues)
        post_ids = []
        logger.debug("Collecting post IDs")
        
        # Use a progress bar for the initial collection
        with tqdm(total=min(limit, 1000), desc=f"Collecting post IDs from r/{subreddit.display_name}", unit="posts") as pbar:
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                post_ids.append(post.id)
                pbar.update(1)
                
                # Check if we've reached the limit
                if len(post_ids) >= limit:
                    break
        
        logger.debug(f"Collected {len(post_ids)} post IDs")
        
        # Now process the posts in parallel
        with tqdm(total=len(post_ids), desc=f"Processing posts from r/{subreddit.display_name}", unit="posts") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit tasks to process each batch
                future_to_batch = {}
                for i in range(0, len(post_ids), self.batch_size):
                    batch = post_ids[i:i + self.batch_size]
                    future = executor.submit(self._process_post_batch, batch, pbar)
                    future_to_batch[future] = i
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_batch):
                    batch_posts = future.result()
                    posts_data.extend(batch_posts)
        
        logger.debug(f"Processed {len(posts_data)} posts with multithreading")
        return posts_data
    
    def _process_post_batch(self, post_ids, pbar):
        """Process a batch of posts by IDs."""
        batch_data = []
        
        for post_id in post_ids:
            try:
                # Get full post data
                post = self.reddit.submission(id=post_id)
                post_data = self._extract_post_data(post)
                batch_data.append(post_data)
                
                # Update progress bar
                pbar.update(1)
                
            except Exception as e:
                logger.warning(f"Error processing post {post_id}: {e}")
                pbar.update(1)
                continue
        
        return batch_data
    
    def _extract_post_data(self, post):
        """Extract relevant data from a Reddit post."""
        return {
            'id': post.id,
            'title': post.title,
            'score': post.score,
            'upvote_ratio': post.upvote_ratio,
            'num_comments': post.num_comments,
            'created_utc': datetime.fromtimestamp(post.created_utc),
            'flair': post.link_flair_text,
            'author': str(post.author) if post.author else '[deleted]',
            'is_original_content': post.is_original_content,
            'is_self': post.is_self,
            'over_18': post.over_18,
            'spoiler': post.spoiler if hasattr(post, 'spoiler') else False,
            'permalink': post.permalink,
            'url': post.url,
            'selftext_length': len(post.selftext) if hasattr(post, 'selftext') else 0,
            'domain': post.domain if hasattr(post, 'domain') else None,
            'gilded': post.gilded if hasattr(post, 'gilded') else 0,
            'stickied': post.stickied if hasattr(post, 'stickied') else False
        }
    
    def _process_dataframe(self, df):
        """Process and clean the DataFrame of posts."""
        # Handle missing/null values
        df['flair'] = df['flair'].fillna('No Flair')
        
        # Add derived columns
        if 'created_utc' in df.columns:
            df['post_date'] = df['created_utc'].dt.date
            df['post_hour'] = df['created_utc'].dt.hour
            df['post_day'] = df['created_utc'].dt.day_name()
            
        # Add engagement ratio (comments per score)
        if 'score' in df.columns and 'num_comments' in df.columns:
            df['comment_ratio'] = df['num_comments'] / df['score'].apply(lambda x: max(x, 1))
        
        return df
    
    def get_subreddit_info(self, subreddit_name):
        """
        Get general information about a subreddit.
        
        Args:
            subreddit_name (str): Name of the subreddit (without r/ prefix)
            
        Returns:
            dict: Dictionary containing subreddit information
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            info = {
                'display_name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.public_description,
                'subscribers': subreddit.subscribers,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc),
                'over18': subreddit.over18,
                'url': subreddit.url,
                'active_user_count': subreddit.active_user_count if hasattr(subreddit, 'active_user_count') else None,
            }
            
            # Get available flairs if possible
            try:
                available_flairs = [flair['text'] for flair in subreddit.flair.link_templates]
                info['available_flairs'] = available_flairs
            except:
                info['available_flairs'] = []
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting info for r/{subreddit_name}: {e}")
            raise