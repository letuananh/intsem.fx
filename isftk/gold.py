import logging

from chirptext import TextReport
from chirptext.cli import CLIApp, setup_logging
from chirptext.texttaglib import TaggedDoc

from coolisf.gold_extract import read_gold_mrs

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

UPDATE_QUERY = """
UPDATE sent SET sent = '{ntext}'
WHERE           sent = '{otext}'
                AND sid = '{sid}';"""

setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def fix_gold(cli, args):
    sents = read_gold_mrs()
    doc = TaggedDoc('data', 'gold').read()
    patches = []
    for s in sents:
        tagged = doc.sent_map[str(s.ident)]
        if tagged.text != s.text:
            new_text = s.text.replace("'", "''")
            old_text = tagged.text.replace("'", "''")
            patch = UPDATE_QUERY.format(ntext=new_text, sid=s.ident, otext=old_text)
            patches.append(patch)

    # generate patch
    if patches:
        with TextReport(args.output) as outfile:
            for patch in patches:
                outfile.print(patch)
        print("-- Patch has been written to {}".format(outfile.path))
    else:
        print("Nothing to patch")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' ChirpText Tools main function '''
    app = CLIApp(desc='ISF Toolkit', logger=__name__)
    # add tasks
    task = app.add_task('fix', func=fix_gold)
    task.add_argument('-o', '--output', help='Output file', default=None)
    # run app
    app.run()


if __name__ == "__main__":
    main()
