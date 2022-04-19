import discord
import os
from bad_insp import bad_list
from random import shuffle

client = discord.Client()
inds = list(range(0, 17))

@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('$badquote'):
    shuffle(bad_list)
    shuffle(inds)
    await message.channel.send(bad_list[inds[1]])

  if message.content.startswith('$meme'):
    with open("birb.jpg", "rb") as f:
      pic = discord.File(f)
      await message.channel.send(file=pic)

client.run(os.getenv("TOKEN"))
