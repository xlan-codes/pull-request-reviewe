"""
Multi-agent orchestration using CrewAI for code review.
"""
from typing import Dict, Any, Optional
import logging
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from src.config.settings import settings
from src.config.prompts import (
    ANALYZER_AGENT_PROMPT,
    RETRIEVER_AGENT_PROMPT,
    CRITIC_AGENT_PROMPT,
    SYNTHESIZER_AGENT_PROMPT,
    SYSTEM_MESSAGE
)
from src.data_preparation.base_adapter import PullRequest
from src.data_preparation.github_adapter import GitHubAdapter
from src.data_preparation.gitlab_adapter import GitLabAdapter
from src.data_preparation.bitbucket_adapter import BitbucketAdapter
from src.data_preparation.diff_parser import DiffParser
from src.rag.retriever import Retriever
from src.tools.code_analyzer import CodeAnalyzer

logger = logging.getLogger(__name__)


class ReviewCrew:
    """Orchestrates multiple agents for PR review."""

    def __init__(self):
        """Initialize the review crew."""
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key
        )

        # Initialize components
        self.retriever = Retriever()
        self.diff_parser = DiffParser()
        self.code_analyzer = CodeAnalyzer()

        # Initialize platform adapters
        self.adapters = {
            'github': GitHubAdapter(),
            'gitlab': GitLabAdapter(),
            'bitbucket': BitbucketAdapter()
        }

        logger.info("ReviewCrew initialized")

    def _detect_platform(self, url: str) -> str:
        """Detect platform from URL."""
        if 'github.com' in url:
            return 'github'
        elif 'gitlab.com' in url:
            return 'gitlab'
        elif 'bitbucket.org' in url:
            return 'bitbucket'
        else:
            raise ValueError(f"Unsupported platform URL: {url}")

    def _create_analyzer_agent(self) -> Agent:
        """Create the code analyzer agent."""
        return Agent(
            role='Code Analyzer',
            goal='Identify potential issues, bugs, and improvements in code changes',
            backstory=ANALYZER_AGENT_PROMPT,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def _create_retriever_agent(self) -> Agent:
        """Create the knowledge retriever agent."""
        return Agent(
            role='Knowledge Retriever',
            goal='Find relevant best practices, patterns, and guidelines from the knowledge base',
            backstory=RETRIEVER_AGENT_PROMPT,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def _create_critic_agent(self) -> Agent:
        """Create the self-reflection critic agent."""
        return Agent(
            role='Review Critic',
            goal='Evaluate and validate review suggestions for quality and accuracy',
            backstory=CRITIC_AGENT_PROMPT,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def _create_synthesizer_agent(self) -> Agent:
        """Create the synthesis agent."""
        return Agent(
            role='Review Synthesizer',
            goal='Create comprehensive, actionable code review feedback',
            backstory=SYNTHESIZER_AGENT_PROMPT,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def _prepare_pr_context(self, pr: PullRequest) -> Dict[str, Any]:
        """Prepare PR context for agents."""
        # Parse diffs
        all_hunks = []
        for file_change in pr.files_changed:
            if file_change.patch:
                hunks = self.diff_parser.parse_patch(file_change.patch)
                all_hunks.extend(hunks)

        # Get change summary
        change_summary = self.diff_parser.get_change_summary(all_hunks)

        # Prepare code context
        code_changes = []
        for hunk in all_hunks[:10]:  # Limit to first 10 hunks for context
            code_changes.append({
                'file': hunk.file_path,
                'added': len(hunk.added_lines),
                'removed': len(hunk.removed_lines),
                'sample_changes': hunk.added_lines[:5]  # First 5 added lines
            })

        context = {
            'pr_info': {
                'title': pr.title,
                'description': pr.description,
                'author': pr.author,
                'platform': pr.platform,
                'language': pr.language,
                'files_changed': pr.changed_files,
                'additions': pr.additions,
                'deletions': pr.deletions
            },
            'change_summary': change_summary,
            'code_changes': code_changes,
            'all_files': [f.filename for f in pr.files_changed]
        }

        return context

    def review_pull_request(self, pr_url: str, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Review a pull request using the agent crew.

        Args:
            pr_url: URL of the PR/MR
            platform: Platform name (auto-detected if not provided)

        Returns:
            Review results
        """
        try:
            # Detect platform
            if not platform:
                platform = self._detect_platform(pr_url)

            logger.info(f"Reviewing PR from {platform}: {pr_url}")

            # Fetch PR data
            adapter = self.adapters.get(platform)
            if not adapter:
                raise ValueError(f"Unsupported platform: {platform}")

            pr = adapter.fetch_pull_request(pr_url)
            logger.info(f"Fetched PR: {pr.title}")

            # Prepare context
            context = self._prepare_pr_context(pr)

            # Create agents
            analyzer = self._create_analyzer_agent()
            retriever = self._create_retriever_agent()
            critic = self._create_critic_agent()
            synthesizer = self._create_synthesizer_agent()

            # Create tasks
            analysis_task = Task(
                description=f"""Analyze the following code changes and identify potential issues:
                
PR Title: {pr.title}
Description: {pr.description}
Language: {pr.language}
Files Changed: {pr.changed_files}
Additions: {pr.additions} / Deletions: {pr.deletions}

Files:
{chr(10).join(f"- {f}" for f in context['all_files'][:20])}

Focus on:
1. Security vulnerabilities
2. Performance issues
3. Potential bugs
4. Code quality concerns
5. Best practice violations

Provide specific file and line references where possible.
""",
                agent=analyzer,
                expected_output="List of identified issues with severity, location, and explanation"
            )

            retrieval_task = Task(
                description=f"""Based on the code changes in this {pr.language or 'unknown language'} PR, 
retrieve relevant best practices and patterns from the knowledge base.

Focus areas based on the analysis:
- Security guidelines
- Performance optimization
- Code quality standards
- Language-specific best practices

Return the most relevant guidelines that apply to this review.
""",
                agent=retriever,
                expected_output="Relevant best practices and patterns from knowledge base",
                context=[analysis_task]
            )

            critic_task = Task(
                description="""Review the identified issues from the analyzer and evaluate each one:

For each issue, assess:
1. Is this a real issue or false positive?
2. Is the severity level appropriate?
3. Is the suggestion actionable and specific?
4. Is it directly related to the changes?

Assign a quality score (0.0-1.0) to each suggestion.
Filter out suggestions with score < 0.6.
Provide reasoning for your evaluations.
""",
                agent=critic,
                expected_output="Validated and scored list of issues with quality assessment",
                context=[analysis_task]
            )

            synthesis_task = Task(
                description=f"""Create a comprehensive code review report for this PR.

PR: {pr.title}

Combine:
1. Validated issues from the critic
2. Relevant best practices from the retriever
3. Original analysis insights

Create a structured review with:
- Executive summary
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (nice to have)
- Positive feedback

Make it actionable, specific, and developer-friendly.
""",
                agent=synthesizer,
                expected_output="Complete, structured code review report",
                context=[analysis_task, retrieval_task, critic_task]
            )

            # Create crew
            crew = Crew(
                agents=[analyzer, retriever, critic, synthesizer],
                tasks=[analysis_task, retrieval_task, critic_task, synthesis_task],
                process=Process.sequential,
                verbose=True
            )

            # Execute review
            logger.info("Starting crew execution...")
            result = crew.kickoff()

            logger.info("Review complete!")

            return {
                'success': True,
                'pr_info': context['pr_info'],
                'review': str(result),
                'platform': platform,
                'url': pr_url
            }

        except Exception as e:
            logger.error(f"Error during review: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'url': pr_url
            }

