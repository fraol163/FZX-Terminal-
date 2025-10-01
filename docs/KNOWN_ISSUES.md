# Known Issues and Limitations

## Generation Failures

### Issue 1: Complex Authentication
**Problem:** Models generate incomplete JWT authentication
**Description:** `build describe 'FastAPI with JWT auth'`
**Symptom:** Generated code missing token refresh logic
**Workaround:** 
1. Generate basic structure first
2. Manually add token refresh logic
3. Or use simpler prompt: 'FastAPI with basic auth middleware'

### Issue 2: Database Relationships
**Problem:** Models struggle with complex foreign keys
**Description:** "Create blog with users, posts, comments, tags"
**Symptom:** SQLAlchemy relationships have errors
**Workaround:** Generate schema separately, then add relationships

### Issue 3: Payment Integration
**Problem:** Models hallucinate API endpoints
**Description:** Any project requesting Stripe/PayPal integration
**Symptom:** Code references non-existent API methods
**Solution:** Never trust generated payment code. Use official SDK docs.

## API Issues

### Issue 4: Rate Limiting
**Symptom:** Error: "Rate limit exceeded"
**When:** After ~50 generations in one hour
**Solution:** 
- Wait 1 hour, or
- Switch to different model, or
- Use Gemini (higher free tier limit)

### Issue 5: Model Timeout
**Symptom:** Request hangs for 30+ seconds
**When:** Using large context or complex descriptions
**Solution:**
- Simplify description
- Break into smaller prompts
- Use faster model (DeepSeek-V3 instead of GPT-4)

## Installation Issues

### Issue 6: Module Import Errors
**Symptom:** `ModuleNotFoundError: No module named 'aiohttp'`
**Solution:** 
```bash
pip install -r requirements.txt
python test_imports.py
```

### Issue 7: Python Version
**Symptom:** Syntax errors on startup
**Cause:** Python version < 3.8
**Solution:** Upgrade to Python 3.8+

## Common User Mistakes

### Issue 8: Vague Descriptions
**Problem:** "Build me an app"
**Result:** Generic, unusable output
**Solution:** Be specific: "Create a React todo app with dark mode, local storage, and drag-and-drop"

### Issue 9: Unrealistic Expectations
**Problem:** Expecting production-ready e-commerce in one generation
**Reality:** Generated code is a starting point, not final product
**Solution:** Use for scaffolding, then customize and secure

### Issue 10: Not Testing Generated Code
**Problem:** Using generated code without verification
**Risk:** Security vulnerabilities, broken functionality
**Solution:** Always test and review generated code before deployment

## Performance Issues

### Issue 11: Slow Generation
**Symptom:** Takes 30+ seconds to generate simple projects
**Causes:**
- Using high-latency models
- Complex descriptions
- Network connectivity issues
**Solutions:**
- Use faster models like DeepSeek-V3
- Simplify project description
- Check internet connection

### Issue 12: Large Memory Usage
**Symptom:** FZX-Terminal uses excessive RAM
**Cause:** Large model cache or many concurrent operations
**Solution:**
- Clear model cache: `build clear-cache`
- Restart FZX-Terminal
- Reduce concurrent operations