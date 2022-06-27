import requests
from time import sleep
from message import Message


class AuthorizationError(Exception):
    ...

class ChannelNotFound(Exception):
    ...


class Deletion_Bot():
    '''
        Initalized from config.yaml data, then attempts to log in to receive your auth token
    '''
    def __init__(self, config: dict[str, str]) -> None:
        self.USERNAME = config['USERNAME']
        self.PASSWORD = config['PASSWORD']
        self.USER_ID = config['USER_ID']
        self.AUTHORIZATION = self.get_token_and_cookies()

    def get_token_and_cookies(self) -> dict[str]:
        '''
            Attempt login to get token and cookies
        '''
        r = requests.post(f'https://discord.com/api/v9/auth/login', 
                json = {'captcha_key': None,
                'login': self.USERNAME,
                'login_source': None,
                'password': self.PASSWORD,
                })
        try:
            authorization =  {'Authorization': r.json().get('token'), 'Cookies': ';'.join([f'{k}:{v}' for k, v in r.cookies.items()])}
            if not authorization['Authorization']:
                raise AuthorizationError
            print(f'Successful log in.')
        except AuthorizationError:
            print(f'Failed login, couldn\'t obtain token.')
        return authorization

    def delete_request(self, msg: Message) -> bool:
        '''
            Send delete request of a Message object
        '''
        channel_id: str = msg.channel_id
        comment_id: str = msg.comment_id
        content: str = msg.content
        timestamp: str = msg.timestamp

        response = requests.delete(f'https://discord.com/api/v9/channels/{channel_id}/messages/{comment_id}', 
                                    headers=self.AUTHORIZATION)
        if response.status_code not in {400, 401, 404, 429}:
            return True
        print(f'Failed to delete comment with ID: {comment_id}. Response message: {response.json()["message"]}. Code: {response.status_code}')
        return False
        

    def delete_all_comments_in_channel(self, CHANNEL_ID: str) -> bool:

        def find_self_comment_ids(CHANNEL_ID: str, USER_ID: str=self.USER_ID) -> list[dict[any]]:
            '''
                Attempt to find all comments created by USER_ID through search request
                if the comment was left in a private conversation the url includes [...]/channels/[...]
                if the comment was left in a discord server the url includes [...]/guilds/[...]

                Tries one then the other.
            '''
            msgs: list[Message] = []
            try:
                response = requests.get(f'https://discord.com/api/v9/guilds/{CHANNEL_ID}/messages/search?author_id={USER_ID}', headers=self.AUTHORIZATION)
                response_json = response.json()
                if response_json.get('message') and response_json['message'].startswith('Unknown'):            
                    raise ChannelNotFound

                if response_json.get('messages'):
                    msgs = [(Message(
                            channel_id=msg[0].get('channel_id'), 
                            comment_id=msg[0].get('id'), 
                            content=msg[0].get('content'), 
                            timestamp=msg[0].get('timestamp')))

                            for msg in response_json.get('messages')]
            
            except ChannelNotFound:
                try:
                    response = requests.get(f'https://discord.com/api/v9/channels/{CHANNEL_ID}/messages/search?author_id={USER_ID}', headers=self.AUTHORIZATION)
                    response_json = response.json()
                    if response_json.get('message') and response_json['message'].startswith('Unknown'):            
                        raise ChannelNotFound
                    if response_json.get('messages'):
                        msgs = [(Message(
                                channel_id=msg[0].get('channel_id'), 
                                comment_id=msg[0].get('id'), 
                                content=msg[0].get('content'), 
                                timestamp=msg[0].get('timestamp')))
                                
                                for msg in response_json.get('messages')]
                
                except ChannelNotFound:
                    ...

            print(f'{response_json.get("total_results")} Comments left to delete in {CHANNEL_ID}!')
            return msgs

        total_deletions = 0

        comments = find_self_comment_ids(CHANNEL_ID=CHANNEL_ID, USER_ID=self.USER_ID)

        print(f'Beginning Deletion within Channel ID: {CHANNEL_ID}')
        try:
            while comments:
                for comment in comments:
                    result = self.delete_request(comment)
                    total_deletions += 1
                    #Rate limited if you exceed a request every 5 seconds consistently
                    sleep(5)
                comments = find_self_comment_ids(CHANNEL_ID=CHANNEL_ID, USER_ID=self.USER_ID)

        except KeyboardInterrupt:
            print(f'\nDeleted {total_deletions} total comments!')
        except Exception as e:
            print(f'Successfully deleted: {total_deletions} comments so far. Exception: {e}')
        print(f'Successfully deleted: {total_deletions} comments so far.\n')


if __name__ == 'main':
    ...