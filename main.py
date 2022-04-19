import discord
import os
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

client = discord.Client()
conn = None

@client.event
async def on_connect():
  global conn

  conn = sqlite3.connect('wordbot.db')
  conn.row_factory = sqlite3.Row
  with conn:
    conn.execute('CREATE TABLE IF NOT EXISTS lookups (user TEXT, word TEXT)')

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

  if message.author == client.user:
    return

  if message.content.startswith('$hello'):
    await message.channel.send('Hello!')

  if message.content.startswith('$lookup'):
    query = message.content.replace('$lookup', '').split()[0]
    print(f'Inserting {message.author}, {query}')
    with conn:
      conn.execute('INSERT INTO lookups (user, word) VALUES (?, ?)', (str(message.author), query))

  if message.content.startswith('$stats'):
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(word) AS num_words FROM lookups WHERE user = ?', (str(message.author),))
    row = cursor.fetchone()
    
    stats = f'You have looked up {row["num_words"] if row is not None else 0} words.\n\n'
    stats += 'MOST SEARCHED WORDS\n===================\n'

    for row in conn.execute('SELECT word, COUNT(word) as num_lookups FROM lookups GROUP BY word ORDER BY num_lookups DESC LIMIT 5'):
      stats += f'{row["word"]}: {row["num_lookups"]}\n'

    await message.channel.send(stats)

client.run(os.environ["TOKEN"])