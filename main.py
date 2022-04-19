import discord
import os
import sqlite3
import logging
import math
from hangman import Hangman
from dictionary import lookup, pronounce

logging.basicConfig(level=logging.INFO)
client = discord.Client()
conn = None
game = Hangman()

@client.event
async def on_connect():
  global conn

  conn = sqlite3.connect('wordbot.db')
  conn.row_factory = sqlite3.Row
  with conn:
    conn.execute('CREATE TABLE IF NOT EXISTS lookups (user TEXT, word TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS typescore (user INTEGER PRIMARY KEY, real INTEGER, fake INTEGER)')

@client.event
async def on_disconnect():
  global conn
  if conn:
    conn.close()
    conn = None

@client.event
async def on_ready():
  print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
  global conn
  args = message.content.split(' ')
  user = message.author.id

  if message.author == client.user:
    return

  if message.content.startswith('$hello'):
    await message.channel.send('Hello!')

  if not message.content.startswith('$'):
    real = 0
    fake = 0

    cursor = conn.cursor()
    row = cursor.execute('SELECT * FROM typescore WHERE user = ?', (user,)).fetchone()
    if row is not None:
      real = row["real"]
      fake = row["fake"]

    for word in args:
      if (lookup(word)["isWord"]):
        real += 1
      else:
        fake += 1

    conn.execute('INSERT OR REPLACE INTO typescore (user, real, fake) VALUES (?, ?, ?)', (user, real, fake))
  
  if message.content.startswith('$score'):
    score = None
    rows = cursor.execute('SELECT * FROM typescore')
    scores = []

    for r in rows:
      u = r["user"]
      real = r["real"]
      fake = r["fake"]
      s = (real / (real + fake)) * math.log(real + fake + 1, 2)
      scores.append({"user": u, "score": s})
      if u == user:
        score = s

    def sf(val):
      return val["score"]
    
    scores.sort(key=sf, reverse=True)
    msg = f'Your score is {score}\n========================\n'
    idx = 1
    for s in scores:
      msg += f'{idx}. {s["user"]} - {s["score"]}\n'
      idx += 1
    await message.channel.send(msg)

  if message.content.startswith('$lookup'):
    query = message.content.replace('$lookup', '').split()[0]
    print(f'Inserting {message.author}, {query}')
    with conn:
      conn.execute('INSERT INTO lookups (user, word) VALUES (?, ?)', (str(message.author), query))
    response = await lookup(query)
    await message.channel.send(response["definition"])

  if message.content.startswith('$pronounce'):
    query = message.content.replace('$pronounce', '').split()[0]
    response = await pronounce(query)

    if response is not None:
      # play the audio if the user is in a voice channel
      if message.author.voice is not None:
        channel = message.author.voice.channel
        voice = discord.utils.get(message.guild.voice_channels, name=channel.name)
        voice_client = discord.utils.get(client.voice_clients, guild=message.guild)

        if voice_client is None:
          voice_client = await voice.connect()
        else:
          await voice_client.move_to(channel)

        source = discord.FFmpegPCMAudio(response)
        voice_client.play(source, after=None)
      else:
        # no voice channel, post a file
        print(response)
        await message.channel.send(response)
    else:
      await message.channel.send(f"I'm sorry, {message.author.name}. I'm afraid I can't do that.")

  if message.content.startswith('$stats'):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(word) AS num_words FROM lookups WHERE user = ?', (str(message.author),))
    row = cursor.fetchone()
    
    stats = f'You have looked up {row["num_words"] if row is not None else 0} words.\n\n'
    stats += 'MOST SEARCHED WORDS\n===================\n'

    for row in conn.execute('SELECT word, COUNT(word) as num_lookups FROM lookups GROUP BY word ORDER BY num_lookups DESC LIMIT 5'):
      stats += f'{row["word"]}: {row["num_lookups"]}\n'

    await message.channel.send(stats)

  elif message.content.startswith('!hangman'):
    game_message = ""
    if len(args) > 1:
      if args[1] == 'start':
        game.start_game()
        game_message = "A word has been randomly selected (all lowercase). \nGuess letters by using `!hangman x` (x being the guessed letter)."

      else:
        game.guess(message.content)
    await message.channel.send(game_message + game.get_game_status())
    
client.run(os.environ["TOKEN"])
