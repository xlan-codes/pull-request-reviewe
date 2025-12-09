# Performance Patterns

## Database Query Optimization
**Good Pattern:**
```python
# Use select_related/prefetch_related to avoid N+1 queries
users = User.objects.select_related('profile').all()
```

**Anti-pattern:**
```python
# N+1 query problem
users = User.objects.all()
for user in users:
    profile = user.profile  # Additional query for each user!
```

## Caching
**Good Pattern:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(n):
    # Cached result
    return sum(i**2 for i in range(n))
```

**Anti-pattern:**
```python
# Recomputing same values repeatedly
def expensive_computation(n):
    return sum(i**2 for i in range(n))
```

## Lazy Loading
**Good Pattern:**
```python
# Generator for large datasets
def read_large_file(filepath):
    with open(filepath) as f:
        for line in f:
            yield line.strip()
```

**Anti-pattern:**
```python
# Loading entire file into memory
def read_large_file(filepath):
    with open(filepath) as f:
        return f.readlines()  # Memory intensive!
```

## Async Operations
**Good Pattern:**
```python
import asyncio

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

**Anti-pattern:**
```python
# Synchronous sequential requests - SLOW!
def fetch_all(urls):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.json())
    return results
```

