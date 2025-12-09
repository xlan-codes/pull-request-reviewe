# Python Best Practices
- Remove commented-out code and TODO comments before committing
- Avoid deep nesting (max 3-4 levels)
- Limit function arguments (max 3-4)
- Use type hints to improve code clarity
- Avoid code duplication - extract common logic into functions
## Code Quality

- Mock external dependencies in tests
- Test edge cases and error conditions
- Use descriptive test names that explain what is being tested
- Aim for high test coverage (>80%)
- Write unit tests for all functions
## Testing

- Cache expensive computations when possible
- Profile code before optimizing
- Use generators for large datasets to save memory
- Avoid unnecessary computations in loops
- Use list comprehensions instead of loops where appropriate
## Performance

- Keep dependencies up to date to avoid known vulnerabilities
- Use parameterized queries to prevent SQL injection
- Validate and sanitize all user inputs
- Use environment variables for configuration
- Never hardcode sensitive information like passwords, API keys, or tokens
## Security

- Avoid silent failures - handle or propagate errors explicitly
- Log exceptions with appropriate context
- Always clean up resources using context managers (with statements)
- Use specific exception types rather than bare except clauses
## Error Handling

- Use docstrings to document functions, classes, and modules
- Keep functions small and focused on a single responsibility
- Follow PEP 8 style guidelines for consistent formatting
- Use meaningful variable and function names that clearly describe their purpose
## Code Organization


