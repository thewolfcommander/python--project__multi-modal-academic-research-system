# multi_modal_rag/logging_config.py
import logging
import os
from datetime import datetime

def setup_logging():
    """
    Configure comprehensive logging for the multi-modal research system
    Creates both file and console handlers with appropriate formatting
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"research_system_{timestamp}.log")

    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create file handler for detailed logging (unbuffered)
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    # Force immediate flush
    file_handler.flush = lambda: None  # Will use stream.flush() instead

    # Make the underlying stream unbuffered
    original_emit = file_handler.emit
    def emit_and_flush(record):
        original_emit(record)
        if file_handler.stream is not None:
            file_handler.stream.flush()
    file_handler.emit = emit_and_flush

    # Create console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create detailed formatter for file
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create simpler formatter for console
    console_formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(message)s'
    )

    # Set formatters
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Log the start of logging session
    logger.info("="*80)
    logger.info(f"Logging initialized - Log file: {log_file}")
    logger.info("="*80)

    return logger, log_file

def get_logger(name):
    """
    Get a logger instance for a specific module

    Args:
        name: Usually __name__ from the calling module

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
