import discord
import os
from hangman import Hangman

client = discord.Client()
game = Hangman()

@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
  args = message.content.split(' ')
  if message.author == client.user:
    return

  if message.content.startswith('$'):
    await message.channel.send("hello")

  elif message.content.startswith('!hangman'):
    game_message = ""
    if len(args) > 1:
      if args[1] == 'start':
        game.start_game()
        game_message = "A word has been randomly selected (all lowercase). \nGuess letters by using `!hangman x` (x being the guessed letter)."

      else:
        game.guess(message.content)
    await message.channel.send(game_message + game.get_game_status())
    
client.run("OTY1OTY0MzcwMDA3OTUzNDkw.Yl62bA.UcY5K-jFTyuLhiqo4U9JB35w76I")
