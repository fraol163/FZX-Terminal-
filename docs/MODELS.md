# Model Selection Guide

## Quick Recommendations

| Task | Best Free Model | Best Paid Model | Reason |
|------|----------------|-----------------|--------|
| React apps | DeepSeek-Coder-V2 | GPT-4 | Strong component generation |
| Python APIs | Qwen3-Coder | Claude-3-Sonnet | Accurate FastAPI syntax |
| CLI tools | CodeLlama-70B | GPT-4-Turbo | Excellent argparse usage |
| Documentation | Gemini-2.0-Flash | Claude-3-Opus | Clear technical writing |
| Bug fixes | DeepSeek-V3 | GPT-4 | Strong debugging ability |

## Model Categories

### Free Models (0 cost)
- **DeepSeek-Coder-V2**: Best free coding model
- **Gemini 2.0 Flash**: Fast, 1M context, good for large projects
- **Qwen3-Coder**: Strong Python generation
- **CodeLlama-70B**: Good for basic CRUD apps

### Low Cost (< $0.001/1k tokens)
- Use these for experimentation and testing
- Most OpenRouter models fall in this category

### Premium Models ($0.01+/1k tokens)
- **GPT-4**: Most reliable, best for complex projects
- **Claude-3-Opus**: Excellent code quality, fewer hallucinations
- Use these for production-quality code

## Model Performance by Project Type

### Web Applications
1. GPT-4 (98% success rate in tests)
2. Claude-3-Sonnet (95% success rate)
3. DeepSeek-Coder-V2 (85% success rate, free)

### API Servers
1. Claude-3-Sonnet (Best FastAPI generation)
2. GPT-4 (Best error handling)
3. Qwen3-Coder (Good, free alternative)

### CLI Tools
1. GPT-4-Turbo (Best argparse generation)
2. DeepSeek-V3 (Good structure, free)

## Context Length Guide

| Context Needed | Minimum Model | Recommended |
|----------------|---------------|-------------|
| Simple app (< 5 files) | 8k tokens | 32k tokens |
| Medium app (5-15 files) | 32k tokens | 128k tokens |
| Large app (15+ files) | 128k tokens | 1M tokens |

Use Gemini 2.0 Flash (1M context) for large projects.

## Cost Estimation

### Example Costs
- Generate React todo app: ~2k tokens = $0.02 with GPT-4, FREE with DeepSeek
- Generate FastAPI server: ~3k tokens = $0.03 with GPT-4, FREE with Qwen3
- Generate complex e-commerce: ~10k tokens = $0.10 with GPT-4

### Daily Limits (OpenRouter Free Tier)
- Requests: 200/day
- Tokens: 200k/day
- Enough for ~50 project generations

## Model Limitations

### What Models Cannot Do
- Generate working payment integrations (Stripe, PayPal) - they hallucinate API keys
- Create production-ready authentication - always review security code
- Generate deployment configs for your specific infrastructure
- Write database migrations - they do not know your schema
- Generate API keys or credentials

### What Models Excel At
- Boilerplate code (routes, models, controllers)
- UI components (React, Vue)
- Project structure and organization
- Test file generation
- Documentation