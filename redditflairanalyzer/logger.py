"""
Logging configuration for the Reddit Flair Analyzer.

This module sets up a professional logging system with colored console output
and optional file logging.
"""

import os
import logging
import sys
from datetime import datetime
import colorlog

def setup_logger(name="redditflairanalyzer", level=logging.INFO, log_file=None):
    """
    Set up and configure a logger with colored console output and optional file logging.
    
    Args:
        name (str, optional): Logger name. Defaults to "redditflairanalyzer".
        level (int, optional): Logging level. Defaults to logging.INFO.
        log_file (str, optional): Path to log file. If None, file logging is disabled.
            Defaults to None.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create console handler with colored formatter
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(level)
    
    # Define color scheme
    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    
    # Create formatters
    colored_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors=log_colors
    )
    
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Set formatter for console handler
    console_handler.setFormatter(colored_formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(file_formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    
    # Prevent logging from propagating to the root logger
    logger.propagate = False
    
    return logger

def get_logger(name=None):
    """
    Get the package logger or create a child logger.
    
    Args:
        name (str, optional): Child logger name. If None, returns the main package logger.
        
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        return logging.getLogger("redditflairanalyzer")
    return logging.getLogger(f"redditflairanalyzer.{name}")

def enable_file_logging(log_file=None):
    """
    Enable logging to a file.
    
    Args:
        log_file (str, optional): Path to log file. If None, a default path is generated.
        
    Returns:
        str: Path to the log file
    """
    logger = logging.getLogger("redditflairanalyzer")
    
    # Generate default log file path if not provided
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join(os.path.expanduser("~"), ".redditflairanalyzer", "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, f"redditflair_{timestamp}.log")
    
    # Check if file handler already exists
    has_file_handler = False
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            has_file_handler = True
            break
    
    # Add file handler if not already present
    if not has_file_handler:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s:%(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logger.level)
        logger.addHandler(file_handler)
    
    logger.info(f"File logging enabled: {log_file}")
    return log_file