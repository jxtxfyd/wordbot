import requests

url = 'https://api.dictionaryapi.dev/api/v2/entries/en/'

def lookup(word):
    isWord = True
    definition = ''

    response = requests.get(f'{url}{word}')

    if response.ok:
        data = response.json()
        meanings = data[0].get("meanings")

        for m in meanings:
            definition += f'{m.partOfSpeech}'

    else:
        isWord = False
        definition = f"Sorry, we couldn't find any definitions for {word}"

    return {
        "isWord": isWord,
        "definition": definition
    }