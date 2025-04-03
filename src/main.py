#!/usr/bin/env python
"""
PokeTogether - Main Game Entry Point
"""

import logging
import logging.config
import sys
import os
from game.core.game import Game

def setup_logging():
    """Richtet das Logging-System ein"""
    if os.path.exists('logging.conf'):
        logging.config.fileConfig('logging.conf')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    return logging.getLogger(__name__)

def main():
    """Main entry point for the game"""
    logger = setup_logging()
    logger.info("Starting PokeTogether")
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        logger.error(f"Error running game: {e}", exc_info=True)
        return 1
    
    logger.info("Game closed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
