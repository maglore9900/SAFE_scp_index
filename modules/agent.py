from phi.agent import Agent
from phi.tools.searxng import Searxng
from modules import adapter, tools, prompts, active_mem
import random
from datetime import datetime

class Agents():
    def __init__(self, env):
        self.env = env
        self.ad = adapter.Adapter(env)
        self.model = self.ad.model
        self.model2 = self.ad.model2
        self.filename = None
        self.active_mem = active_mem.TokenLimitedString(2000)
        self.searxng = Searxng(
            host="http://10.0.0.141:8080",
            engines=[],
            fixed_max_results=5,
            news=True,
            science=True,
            images=True,
            it=True,
            map=True,
            videos=True
        )
        self.prompt = prompts.prompt
        self.response = prompts.response
        self.gate = prompts.gate
        self.websearch_agent = Agent(
            name="Web Agent",
            role="A web search agent that uses a search engine to find information.",
            model=self.model,
            tools=[self.searxng],
            instructions=["Always include sources"],
            show_tool_calls=True,
            markdown=False,
        ) 
        self.data_store_agent = Agent(
            name="Data Store Agent",
            role="Your job manage all data related to SCPs. You can save data to a data store or query data stores.",
            model=self.model,
            instructions=["Support user actions with saving files or querying data stores", "You have a number of tools, use them"],
            tools=[tools.DataSaveToolkit(self.ad), tools.DataQueryToolkit(self.ad)],
            show_tool_calls=True,
            markdown=True,
            allow_dangerous_deserialization=True,
        )
        self.agent_team = Agent (
            team=[self.websearch_agent, self.data_store_agent],
            model=self.model,
            instructions=["When a user asks a question pertaining to SCP of any kind, pass that to the Data Store Agent. This agent will tell you if that information or file exists.", "if the Data Store Agent tells you the information isnt found, you may use the Web Agent."],
            show_tool_calls=True,
            markdown=True,   
        )
        
    async def invoke_agent(self, query, user, filename=None): 
        #! gate-keeper protocol
        gate_start = datetime.now()
        gate = self.ad.llm_chat.invoke(self.gate.format(query=query))
        if "no" in gate.content.lower():
            return prompts.deny.format(user=user, deny_type=random.choice(prompts.deny_type))
        gate_finish = datetime.now()
        print(f"gate-keeper protocol took: {gate_finish - gate_start}")
        if filename:
            query = query + " these files: " + ", ".join(filename)
        #! memory
        self.active_mem.add_data(query)
        print(f"current active mem length: {len(self.active_mem.value)}")
        #! agent manager
        manager_start = datetime.now()
        manager = self.prompt.format(query=query, chat_history=self.active_mem.value)
        result = await self.agent_team.arun(manager)
        manager_finish = datetime.now()
        print(f"agent manager took: {manager_finish - manager_start}")
        #! character response
        respone_start = datetime.now()
        safe_response = await self.ad.llm_chat.ainvoke(prompts.safe.format(query=query, context=result.content))
        response_finish = datetime.now()
        print(f"response agent took: {response_finish - respone_start}")
        self.active_mem.add_data(safe_response.content)
        result = safe_response.content
        response = prompts.response.format(user=user, query=query, context=result)
        return response

