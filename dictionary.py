import aiohttp

url = 'https://api.dictionaryapi.dev/api/v2/entries/en/'

async def _get_definition(word):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{url}{word}') as r:
            if r.status == 200:
                js = await r.json()
                return js
            else:
                return None

async def lookup(word):
    isWord = True
    definition = ''

    data = await _get_definition(word)

    if data is not None:
        meanings = data[0]["meanings"]

        for m in meanings:
            definition += f'{m["partOfSpeech"]}\n\t'
            first_def = m["definitions"][0]
            definition += f'{first_def["definition"]}\n'

    else:
        isWord = False
        definition = f"Sorry, we couldn't find any definitions for {word}"

    return {
        "isWord": isWord,
        "definition": definition
    }

async def pronounce(word):
    data = await _get_definition(word)
    print(data)
    
    if data is None or len(data) == 0:
        return None

    phonetics = data[0].get('phonetics')
    if phonetics is None:
        return None

    audio = next((p['audio'] for p in phonetics if 'audio' in p and p['audio'] != ''), None)
    if audio is None:
        return None

    return audio
