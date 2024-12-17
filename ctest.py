from modules import adapter, agent
import environ
import asyncio

env = environ.Env()
environ.Env.read_env()

ad = adapter.Adapter(env)
ag = agent.Agents(env)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
print(loop.run_until_complete(ag.invoke_agent("tell me about scp-5000", "Smith")))

# print(ad.chat("tell me about yourself", "Smith"))