"""
Metrics for evaluating review quality.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ReviewMetrics:
    """Metrics for a single review."""
    review_id: str
    timestamp: datetime
    pr_url: str
    platform: str

    # Performance metrics
    total_time_seconds: float
    token_count: int
    api_calls: int

    # Quality metrics
    issues_found: int
    critical_issues: int
    warnings: int
    suggestions: int

    # Reflection metrics
    initial_issues: int
    filtered_issues: int
    false_positives_caught: int

    # RAG metrics
    documents_retrieved: int
    avg_relevance_score: float

    # Cost metrics
    estimated_cost_usd: float


class MetricsTracker:
    """Track and aggregate review metrics."""

    def __init__(self):
        """Initialize metrics tracker."""
        self.metrics: List[ReviewMetrics] = []

    def record_review(self, metrics: ReviewMetrics):
        """Record metrics for a review."""
        self.metrics.append(metrics)
        logger.info(f"Recorded metrics for review: {metrics.review_id}")

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics across all reviews."""
        if not self.metrics:
            return {}

        total_reviews = len(self.metrics)

        return {
            'total_reviews': total_reviews,
            'avg_review_time': sum(m.total_time_seconds for m in self.metrics) / total_reviews,
            'avg_issues_found': sum(m.issues_found for m in self.metrics) / total_reviews,
            'avg_critical_issues': sum(m.critical_issues for m in self.metrics) / total_reviews,
            'total_issues': sum(m.issues_found for m in self.metrics),
            'avg_false_positives_caught': sum(m.false_positives_caught for m in self.metrics) / total_reviews,
            'avg_token_count': sum(m.token_count for m in self.metrics) / total_reviews,
            'total_cost': sum(m.estimated_cost_usd for m in self.metrics),
            'platform_distribution': self._get_platform_distribution()
        }

    def _get_platform_distribution(self) -> Dict[str, int]:
        """Get distribution of reviews by platform."""
        distribution = {}
        for metric in self.metrics:
            distribution[metric.platform] = distribution.get(metric.platform, 0) + 1
        return distribution

    def get_recent_reviews(self, n: int = 10) -> List[ReviewMetrics]:
        """Get N most recent reviews."""
        return sorted(self.metrics, key=lambda m: m.timestamp, reverse=True)[:n]

    def calculate_efficiency_score(self) -> float:
        """
        Calculate overall efficiency score.

        Considers:
        - Time per issue found
        - Cost per issue found
        - False positive rate
        """
        if not self.metrics:
            return 0.0

        total_issues = sum(m.issues_found for m in self.metrics)
        if total_issues == 0:
            return 0.0

        avg_time_per_issue = sum(m.total_time_seconds for m in self.metrics) / total_issues
        avg_cost_per_issue = sum(m.estimated_cost_usd for m in self.metrics) / total_issues

        total_initial = sum(m.initial_issues for m in self.metrics)
        total_filtered = sum(m.filtered_issues for m in self.metrics)

        false_positive_rate = total_filtered / total_initial if total_initial > 0 else 0

        # Normalize and combine (lower is better for time/cost, higher is better for FP detection)
        # This is a simplified scoring mechanism
        efficiency = (
            (1 / (avg_time_per_issue + 1)) * 0.3 +
            (1 / (avg_cost_per_issue * 100 + 1)) * 0.3 +
            (false_positive_rate) * 0.4
        )

        return min(efficiency * 100, 100)  # Scale to 0-100

