from modules import adapter
import environ

env = environ.Env()
environ.Env.read_env()

ad = adapter.Adapter(env)

print(ad.chat("tell me about yourself"))