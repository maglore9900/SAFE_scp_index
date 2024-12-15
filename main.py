import discord
import environ
from modules import agent
import asyncio
from datetime import datetime

env = environ.Env()
environ.Env.read_env()
TOKEN = env('DISCORD_TOKEN')
ag = agent.Agents(env)

# Initialize the client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)



async def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M")

# Define a command prefix, for example, '!'
command_prefix = '!'

prompt = """
Today: {date}, {username} said: {query}
"""

async def send_long_message(channel, content):
    """
    Sends a long message in intelligently sized chunks, avoiding breaking in the middle of sentences.

    :param channel: The channel where the message should be sent.
    :param content: The full message string to be split and sent.
    """
    while len(content) > 1900:
        # Find the nearest sentence-ending character within the first 1900 characters
        chunk = content[:1900]
        last_sentence_end = max(chunk.rfind('. '), chunk.rfind('! '), chunk.rfind('? '), chunk.rfind('\n'))

        if last_sentence_end == -1:  # If no sentence-ending character is found, break at 1900
            split_index = 1900
        else:
            split_index = last_sentence_end + 1  # Include the sentence-ending character in the chunk

        # Send the chunk and move to the next part
        await channel.send(content[:split_index].strip())
        content = content[split_index:].strip()

    # Send the remaining content
    if content:
        await channel.send(content.strip())

async def get_username(user_id: int):
    username = None  # Initialize the variable to store the username
    # First, try to get the user from the cache
    user = client.get_user(user_id)
    if user:
        username = user.name  # Set the username if found in cache
        return username
    # If not in cache, try fetching the user from Discord's servers
    try:
        user = await client.fetch_user(user_id)
        username = user.name  # Set the username if fetched from API
        return username
    except discord.NotFound:
        return None
    except discord.HTTPException:
        return None


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignore messages from the bot itself
    is_in_thread = isinstance(message.channel, discord.Thread)

    if message.content.startswith(command_prefix):  # Check if the message starts with the command prefix
        # Remove the prefix from the message content and process the command
        command = message.content[len(command_prefix):].strip().split(" ")[0].lower()

        if command == 'get_username':
            try:
                # Get the user ID from the message (assuming it's the second word after the command)
                user_id = int(message.content.split(" ")[1])
                username = await get_username(user_id)
                if username:
                    await message.channel.send(f"Username: {username}")
                else:
                    await message.channel.send("User not found.")
            except (IndexError, ValueError):
                await message.channel.send("Please provide a valid user ID.")
        else:
            await message.channel.send(f"Unknown command: {command}")
    
    # Additional logic for handling mentions and attachments (as in the original code)
    attachments = []
    if client.user in message.mentions or any(role in message.role_mentions for role in message.guild.get_member(client.user.id).roles):
        print("heard")
        if not is_in_thread:
            thread = await message.create_thread(name="Max's Response")
        else:
            thread = message.channel
        if len(message.attachments) > 0:
            print("found attachment")
            for attachment in message.attachments:
                await attachment.save(fp=f"./tmp/{attachment.filename}")
                attachments.append(f"{attachment.filename}")
        received_message = message.content.replace(f'<@{client.user.id}>', '').strip()
        username = await get_username(message.author.id)  # Await the username function
        date = await get_current_datetime()
        custom_query = prompt.format(date=date, username=username, query=received_message)
        print(custom_query)
        try:
            output = await ag.invoke_agent(custom_query, attachments)
            output = output.content
        except Exception as e:
            output = f"Error: {e}"

        # await message.channel.send(f'{output}')
        # await send_long_message(message.channel, output)
        await send_long_message(thread, output)


async def main():
    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Shutting down...")
    finally:
        await client.close()
        print("Bot has been disconnected.")


# Run the asyncio event loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Program terminated by user.")
