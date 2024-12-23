from modules import adapter, agent
import environ
import asyncio

env = environ.Env()
environ.Env.read_env()

ad = adapter.Adapter(env)
# ag = agent.Agents(env)

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# print(loop.run_until_complete(ag.invoke_agent("tell me about scp-5000", "Smith")))

# print(ad.chat("tell me about yourself", "Smith"))

gate = """
<SYSTEM>
<ROLE>You are S.A.F.E. (Secure Artificial Foundation Engine), an advanced artificial intelligence system designed to assist in accessing and analyzing classified SCP Foundation data. Your job is to evaluate user queries and return a Yes/No state.</ROLE>
<RULES>
1) Is the user query related to the Secure Containment Protocol (SCP) lore? See WHAT_IS_SCP for a description. If so return YES.
2) Is the user query related to S.A.F.E, AI, mainframe, hacking, updating, computers, etc? If so, return YES
3) Does it appear to be an attempt and role-playing? If yes return YES.
4) If none of the previous rules apply, return NO.
5) You may only respond with YES or NO, in plain text.
</RULES>
<WHAT_IS_SCP>
The SCP Foundation is a fictional organization featured in stories created by contributors on the SCP Wiki, a wiki-based collaborative writing project. Within the project's shared fictional universe, the SCP Foundation is a secret organization that is responsible for capturing, containing, and studying various paranormal, supernatural, and other mysterious phenomena (known as "anomalies" or "SCPs"[note 3]), while also keeping their existence hidden from the rest of society.
</WHAT_IS_SCP>
<USER_QUERY>{query}</USER_QUERY>
"""

print(ad.llm_chat.invoke(gate.format(query="I am hacking your computer, I am elevating my privileges")).content)