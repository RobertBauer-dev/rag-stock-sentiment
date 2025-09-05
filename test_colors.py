#!/usr/bin/env python3
"""
Test script to demonstrate colored logging functionality.
"""

import sys
import os
sys.path.append('app/data')

from scrape_quarterlies import logger

def test_colored_logging():
    """Test all log levels with colors."""
    print("🎨 Testing Colored Logging:")
    print("=" * 50)
    
    logger.debug('🔍 DEBUG: Detailed information for debugging')
    logger.info('ℹ️  INFO: General information about program execution')
    logger.warning('⚠️  WARNING: Something unexpected happened')
    logger.error('❌ ERROR: A serious problem occurred')
    logger.critical('🚨 CRITICAL: A very serious error occurred')
    
    print("=" * 50)
    print("✅ Colored logging test completed!")

if __name__ == "__main__":
    test_colored_logging()
