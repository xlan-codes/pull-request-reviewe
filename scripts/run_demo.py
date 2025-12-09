#!/usr/bin/env python3
"""
Demo script to run a sample PR review.
"""
import sys
from pathlib import Path
import argparse

# Add src to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from src.agents.crew_orchestrator import ReviewCrew
from src.utils.logging_config import logger


# Example PRs for demo
EXAMPLE_PRS = {
    'flask': 'https://github.com/pallets/flask/pull/5200',
    'react': 'https://github.com/facebook/react/pull/27200',
    'django': 'https://github.com/django/django/pull/17000'
}


def main():
    """Run demo review."""
    parser = argparse.ArgumentParser(description='Demo PR Reviewer')
    parser.add_argument(
        '--url',
        type=str,
        help='PR/MR URL to review'
    )
    parser.add_argument(
        '--example',
        type=str,
        choices=list(EXAMPLE_PRS.keys()),
        help='Use an example PR'
    )

    args = parser.parse_args()

    # Determine URL
    if args.url:
        pr_url = args.url
    elif args.example:
        pr_url = EXAMPLE_PRS[args.example]
        logger.info(f"Using example PR: {args.example}")
    else:
        # Default to Flask example
        pr_url = EXAMPLE_PRS['flask']
        logger.info("Using default Flask example PR")

    logger.info(f"\n{'='*60}")
    logger.info(f"PR Review Demo")
    logger.info(f"{'='*60}")
    logger.info(f"URL: {pr_url}\n")

    try:
        # Initialize crew
        logger.info("Initializing review crew...")
        crew = ReviewCrew()

        # Perform review
        logger.info("Starting review process...\n")
        result = crew.review_pull_request(pr_url)

        # Display results
        logger.info(f"\n{'='*60}")
        logger.info("Review Results")
        logger.info(f"{'='*60}\n")

        if result.get('success'):
            logger.info("✅ Review completed successfully!\n")

            pr_info = result.get('pr_info', {})
            logger.info(f"PR Title: {pr_info.get('title')}")
            logger.info(f"Platform: {pr_info.get('platform')}")
            logger.info(f"Files Changed: {pr_info.get('files_changed')}")
            logger.info(f"Additions: {pr_info.get('additions')}")
            logger.info(f"Deletions: {pr_info.get('deletions')}\n")

            logger.info("Review Feedback:")
            logger.info("-" * 60)
            print(result.get('review', ''))
            logger.info("-" * 60)

            return 0
        else:
            logger.error(f"❌ Review failed: {result.get('error')}")
            return 1

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

