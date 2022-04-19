import discord
import os
from dictionary import lookup

client = discord.Client()

@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('$hello'):
    await message.channel.send('Hello!')

  if message.content.startswith('-def '):
    word = message.content[5:]
    word = word.strip()
    response = lookup(word)
    await message.channel.send(response)

client.run(os.environ["TOKEN"])
