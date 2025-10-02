import asyncio
from enhanced_ai_provider import EnhancedAIProvider

async def test_config():
    provider = EnhancedAIProvider()
    print("Provider loaded:", provider.is_configured())
    print("Config:", provider.config)
    
    if provider.config:
        result = await provider.validate_api_key(
            provider.config.provider, 
            provider.config.api_key, 
            provider.config.model_id
        )
        print("Validation result:", result)
    else:
        print("No configuration found")

if __name__ == "__main__":
    asyncio.run(test_config())