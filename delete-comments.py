from yaml import safe_load
from deletion_bot import Deletion_Bot


try:
    with open('config.yaml') as y:
        config = safe_load(y)
except FileNotFoundError:
    raise Exception(f'config.yaml file wasnt found.')


d = Deletion_Bot(config)

for channel in config['CHANNEL_IDS']:
    d.delete_all_comments_in_channel(channel)
