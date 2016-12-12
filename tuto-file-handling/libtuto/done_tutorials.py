import json
import os
from os.path import expanduser, isdir, isfile

from libtuto.persistence_dbus import tutorials_todo_update
from libtuto.query_tutorials import peekTutorials

PERSISTENCE_DIR = expanduser("~/.libtuto")
if not isdir(PERSISTENCE_DIR):
    os.makedirs(PERSISTENCE_DIR)

PERSISTENCE_FILE = os.path.join(PERSISTENCE_DIR, "persistence.json")


def _set_persistence_file(persistence_file):
    global PERSISTENCE_FILE
    PERSISTENCE_FILE = persistence_file


def save_tutorials_done(done_tutorials):
    """
    :param done_tutorials: Map of applications desktop filepath and list of
                           tutorial names which have been completed
    :type done_tutorials: dict[str, list[str]]
    """
    with open(PERSISTENCE_FILE, 'w') as f:
        json.dump(done_tutorials, f)
    tutorials_todo_update()


def load_tutorials_done():
    """
    :return: Map of applications desktop filepath and list of tutorial keys
             which have been completed
    :rtype: dict[str, list[str]]
    """
    done_tutorials = {}
    if isfile(PERSISTENCE_FILE):
        with open(PERSISTENCE_FILE) as f:
            try:
                done_tutorials = json.load(f)
            except ValueError:
                # File is probably empty
                pass

    return done_tutorials


def count_tutorials_todo():
    tuto_done = load_tutorials_done()
    all_tuto = peekTutorials()

    count = 0
    for k, tuto_names in all_tuto.items():
        done_tuto_names = tuto_done.get(k[0])
        # Multiline-if to prevent evaluation of both arguments
        if done_tuto_names:
            count += len(set(tuto_names).difference(set(done_tuto_names)))
        else:
            count += len(tuto_names)

    return count
