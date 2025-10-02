import asyncio
from advanced_building_agent import AdvancedBuildingAgent

async def test_build():
    agent = AdvancedBuildingAgent()
    print("Agent created")
    print("AI Provider configured:", agent.ai_provider.is_configured() if agent.ai_provider else False)
    
    if agent.ai_provider and agent.ai_provider.is_configured():
        print("Provider:", agent.ai_provider.config.provider)
        print("Model:", agent.ai_provider.config.model_id)
    
    result = await agent.generate_from_description('build me a simple portfolio website for name Fraol Teshome')
    print('Result:', result)
    return result

if __name__ == "__main__":
    asyncio.run(test_build())