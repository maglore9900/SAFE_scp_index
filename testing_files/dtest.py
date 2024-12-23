from modules import adapter
import environ

env = environ.Env()
environ.Env.read_env()

ad = adapter.Adapter(env)

result = ad.query_datastore("tell me about scp-002 and scp-010")

print(result)