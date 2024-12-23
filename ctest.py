from modules import adapter, agent
import environ
import asyncio

env = environ.Env()
environ.Env.read_env()

# ad = adapter.Adapter(env)
ag = agent.Agents(env)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# query = "tell me about scp-5000"
query = "tell me about scp-007"


print(loop.run_until_complete(ag.invoke_agent(query, "Smith")))

# print(ad.chat("tell me about yourself", "Smith"))