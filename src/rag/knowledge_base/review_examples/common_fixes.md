# Code Review Examples
**Category:** Security
**Severity:** Critical → Fixed

- ⚠️ **Action Required**: Update .env.example and documentation
- ✅ **Best Practice**: Follows 12-factor app principles
- ✅ **Security**: Now uses environment variables
- ✅ **Critical Fix**: Removed hardcoded credentials
**Review Comments:**

```
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
API_KEY = os.getenv("API_KEY")
load_dotenv()

from dotenv import load_dotenv
import os
# After

DATABASE_PASSWORD = "mypassword123"
API_KEY = "sk-abc123xyz789"
# Before - INSECURE!
```python
**Code Change:**

## Example 4: Hardcoded Credentials


**Category:** Error Handling
**Severity:** Warning → Fixed

- ✅ **Logging**: Errors are now logged for debugging
- ✅ **Timeout**: Prevents hanging requests
- ✅ **Robustness**: Added proper error handling
**Review Comments:**

```
        raise
        logger.error(f"API request failed: {e}")
    except requests.RequestException as e:
        return response.json()
        response.raise_for_status()
        response = requests.get(url, timeout=10)
    try:
def fetch_api_data(url):
# After

    return response.json()
    response = requests.get(url)
def fetch_api_data(url):
# Before
```python
**Code Change:**

## Example 3: Missing Error Handling


**Category:** Performance
**Severity:** Warning → Fixed

- ℹ️ **Note**: Consider using generators for very large datasets
- ✅ **Readability**: Cleaner, more functional approach
- ✅ **Performance**: More memory-efficient using map
**Review Comments:**

```
}
    return data.map(item => processItem(item));
function processLargeDataset(data) {
// After

}
    return results;
    }
        results.push(processItem(data[i]));
    for (let i = 0; i < data.length; i++) {
    const results = [];
function processLargeDataset(data) {
// Before
```javascript
**Code Change:**

## Example 2: Memory Leak in Loop


**Category:** Security
**Severity:** Critical → Fixed

- ✅ **Best Practice**: Follows secure coding guidelines
- ✅ **Security**: Now uses parameterized queries
- ✅ **Critical Fix**: Properly addressed SQL injection vulnerability
**Review Comments:**

```
    return db.execute(query, (user_id,))
    query = "SELECT * FROM users WHERE id = ?"
def get_user(user_id):
# After  

    return db.execute(query)
    query = f"SELECT * FROM users WHERE id = {user_id}"
def get_user(user_id):
# Before
```python
**Code Change:**

## Example 1: SQL Injection Vulnerability


