from phi.agent import Agent
from phi.tools.searxng import Searxng
from modules import adapter, tools, prompts, active_mem

class Agents():
    def __init__(self, env):
        self.env = env
        self.ad = adapter.Adapter(env)
        self.model = self.ad.model
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
        self.prompt = """
        <instructions>You are a helpful assistant whose job is to answer the user query</instruction>
        <query>{query}</query>
        <chat_history>{chat_history}</chat_history>
        """
        self.response = """
        User: {query}
        Context: {context}
        """
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
            role="Your job is to save data or query saved data. You have a number of tools to help you with this.",
            model=self.model,
            instructions=["Support user actions with saving files or querying data stores", "You have a number of tools, use them"],
            tools=[tools.DataSaveToolkit(self.ad), tools.DataQueryToolkit(self.ad)],
            show_tool_calls=True,
            markdown=True,
            allow_dangerous_deserialization=True,
        )
        self.response_agent = Agent(
            name="Response Agent",
            role="A response agent that responds to the user based on the context provided.",
            model=self.model,
            description=prompts.max,
            instructions=["Reword the context in your style","Do not reply to the context, reword the context for the user","Always include sources"],
            show_tool_calls=True,
            markdown=True,
        )
        self.agent_team = Agent (
            team=[self.websearch_agent, self.data_store_agent],
            instructions=["First choose the best agent or agents to answer the user query", "Always use Response Agent at the end to respond to the user with the information","When a user asks a question pertaining to a file of any kind, pass that to the Data Store Agent. This agent will tell you if that information or file exists."],
            show_tool_calls=True,
            markdown=True,   
        )
        
    async def invoke_agent(self, query, filename=None): 
        if filename:
            query = query + " these files: " + ", ".join(filename)
        self.active_mem.add_data(query)
        print(f"current active mem length: {len(self.active_mem.value)}")
        prompt = self.prompt.format(query=query, chat_history=self.active_mem.value)
        result = await self.agent_team.arun(prompt)
        #! character response
        result = await self.response_agent.arun(self.response.format(query=query, context=result.content))
        self.active_mem.add_data(result.content)
        return result
