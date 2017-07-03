import ahocorasick, configparser, glob, re

data = configparser.ConfigParser(allow_no_value=True)
data.read('/home/mihai/bin/bot/config.ini')

general = data['DISCORD']
musicbot = data['MUSIC']
memeifiers = data['MEMEIFY']

## GENERAL PARAMETERS
BOT_NAME        = general['bot_name']
LOGIN_TOKEN     = general['login_token']
BOT_CHANNEL_ID  = general['bot_channel']
MAIN_CHANNEL_ID = general['main_channel']
MEME_THRESHOLD  = float(general['meme_chance'])
MEME_FOLDER     = general['meme_folder']

## MUSIC BOT
BANNED_TAGS     = re.compile(musicbot['music_tag_filters'])
PLAYLIST_MAX_SIZE = int(musicbot['playlist_max_size'])
DEFAULT_VOLUME = int(musicbot['default_volume'])

CMD_MARKER_TEXT = re.compile('[!\\\\`]|bot |ds |sudo ')
CMD_MARKER      = 'cmd_'
PROTECTED_IDS = frozenset(data.options('PROTECTED_NICKNAMES'))

def collect_memes(MEMES, meme_folder):
  for file in glob.iglob(meme_folder + '**', recursive = True):
    tkn = file.split('/')[-1].split('.')
    if len(tkn) > 1 and tkn[-1] != 'txt':
      MEMES.add_word(tkn[0].replace('_', ' '), file)
  for line in open(meme_folder + 'react.txt'):
    line = line.split(':', maxsplit=1)
    file = line[0]
    if file[0] != '/':
      file = meme_folder + file
    if len(line) == 1:
      continue
    for react in line[1].split(','):
      react = react.strip()
      if react:
        MEMES.add_word(react, file)

def getGoogleMeme(query):
  return None,None

def read_all_memes():
  global MEMES
  MEMES = ahocorasick.Automaton()
  for folder in memeifiers.values():
    collect_memes(MEMES, MEME_FOLDER + folder + '/')
  MEMES.make_automaton()
read_all_memes()

def getMemes(query):
  return list(MEMES.iter(query.strip().lower()))
