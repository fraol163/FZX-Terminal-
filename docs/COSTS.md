# Costs and Rate Limits

## OpenRouter Free Tier

Daily Limits:
- 200 requests per day
- 200,000 tokens per day
- Enough for approximately 50 project generations

What counts as a request:
- Each `build describe` command = 1 request
- Each `build browse-models` = 1 request
- Each `build analyze` = 1 request

When you hit limits:
- Error: "Rate limit exceeded"
- Resets at midnight UTC
- Workaround: Use Gemini (separate limits)

## OpenRouter Paid Models

Cost Examples:
| Model | Cost per 1M tokens | Typical project cost |
|-------|-------------------|---------------------|
| GPT-4 | $30 input / $60 output | $0.05 - $0.15 |
| Claude-3-Sonnet | $3 input / $15 output | $0.01 - $0.05 |
| GPT-3.5-Turbo | $0.50 input / $1.50 output | $0.001 - $0.003 |

Monthly estimate:
- 10 projects/day with GPT-4: ~$30-50/month
- 10 projects/day with Claude-3: ~$10-15/month
- 10 projects/day with free models: $0/month

## Gemini Free Tier
Daily Limits:
- 1,500 requests per day
- Higher than OpenRouter
- 1M token context (best for large projects)

Rate limits:
- 60 requests per minute
- Better for rapid iteration

## Cost Optimization Tips

1. **Start with free models** - Test descriptions with DeepSeek before using GPT-4
2. **Refine prompts** - Clear descriptions reduce retries
3. **Use caching** - `build browse-models` caches for 24 hours
4. **Batch similar projects** - Generate 5 similar apps in one session
5. **Mix providers** - Use Gemini for large projects, OpenRouter for speed

## Monitoring Usage

```bash
# View your usage
build ai-status

# Output shows:
# - Requests today: 23/200
# - Tokens used: 45,000/200,000
# - Estimated cost: $0.00 (free tier)
```

## Billing

OpenRouter billing:
- Add credit at https://openrouter.ai/account
- Minimum $5
- Unused credit never expires
- Get usage alerts at 50%, 80%, 90%

Gemini billing:
- Free tier is sufficient for most users
- Paid tier starts at $0.50/1M tokens