import logging
from chirptext.texttaglib import TagInfo
from coolisf.ghub import GrammarHub

# Sample script for benchmarking

ghub = GrammarHub()
sent = ghub.parse('I give a book to him.', 'ERG', tagger=TagInfo.LELESK, ignore_cache=True)
for reading in sent:
    logging.debug(reading.mrs())
