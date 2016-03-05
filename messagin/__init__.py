'''
messagin: message generation to simulate the feel of natural language.
'''

import random
from xml.dom import minidom


class ReplyCollection():

    def __init__(self):
        self.packs = {
            'default': {}
        }

    def get_reply(self, group, pack='default', fallback=False):
        '''
        Select a random reply from a group.

        :param str group: The group to select the reply from.
        :param str pack: The pack name to select from,
        :param bool fallback: Should the default pack be consulted if a group
          does not exist for the requested pack.
        '''
        if pack not in self.packs:
            raise IndexError('Pack with name "%s" has not been loaded' % pack)
        if group not in self.packs[pack]:
            if self.fallback and pack != 'default':  # Try the default pack
                return self.get_reply(group, pack='default')

    def load_file(self, path):
        '''
        Open an XML file and load its contents into this collection.

        :param str path: The file path to load.
        '''
        with open(path) as fp:
            document = minidom.parse(fp)
            messagefile = document.documentElement
            for messageset in messagefile.getElementsByTagName('messageset'):
                self._add_message_set(messageset)

    def _add_message_set(self, messageset):
        '''
        :param xml.dom.minidom.Element messageset: An XML DOM element
          containing a group of replies.
        :raises ValueError: when a messageset is passed that does not
          specify a group name.
        '''
        if 'group' not in messageset.attributes:
            raise ValueError('message set must have a group')
        group = messageset.attributes['group'].value

        pack = 'default'  # Default pack if none is given
        if 'pack' in messageset.attributes:
            pack = messageset.attributes['pack'].value

        # Check that the storage location exists
        if pack not in self.packs:
            self.packs[pack] = {group: []}
        elif group not in self.modules[pack]:
            self.packs[pack][group] = []

        # Store the replies
        for reply in messageset.getElementsByTagName('reply'):
            self.packs[pack][group].append(Reply(reply))


class Reply():
    def __init__(self, reply):
        self.messages = reply.getElementsByTagName('m')
        self.actions = reply.getElementsByTagName('action')

    def play(self):
        for message in self.messages:
            yield construct_message(message, None)


def construct_message(node, state):
    '''
    :param template: An XML DOM element with the message template.
    :param state: An object representing the state of the person sending
      the message along with variables to use for substitution
    '''

    def parse_text(elm):
        if elm.data.isspace():
            return ''
        else:
            return elm.data

    def parse_element(elm):
        if isinstance(elm, minidom.Text):
            return parse_text(elm)

        if elm.tagName == 'choice':
            c_elms = elm.getElementsByTagName('c')
            return parse_element(random.choice(c_elms))
        elif elm.tagName == 'c':
            return ''.join([parse_element(n) for n in elm.childNodes])
        elif elm.tagName == 'opt':
            chance = 0.5
            if 'chance' in elm.attributes:
                chance = float(elm.attributes['chance'].value)

            if random.random() > chance:
                return ''
            return ''.join([parse_element(n) for n in elm.childNodes])
        elif elm.tagName == 'm':
            return ''.join([parse_element(n) for n in elm.childNodes])
        else:
            print(elm)

    return parse_element(node)
