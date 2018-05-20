import spotipy, json
import spotipy.util as util
import requests, base64
import webbrowser
from enum import Enum, auto
from music_framework import Song, MusicLibrary

class MusicExportFormat(Enum):
    JSON = auto()
    TXT = auto()

class MusicProvider():
    def __init__(self, username, scope, client_id, client_secret, redirect_uri):
        self.username = username
        self.scope = 'user-library-read'
        self.saved_tracks = MusicLibrary(username)
        self.token = None
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = redirect_uri

    def __export_txt__(self, location):
        f = None
        songlist = self.saved_tracks.getsongs()
        try:
            f = open(location + '\\' + self.username + '_saved_tracks.txt','w', encoding='utf8')
            for song in songlist:
                s = '\t'.join([
                    song['artist'],
                    song['album'],
                    str(song['track_number']),
                    song['name'],
                    song['track_id'],
                    str(song['duration_ms'])
                ])
                f.write(s + '\n')
            f.close()
            return True
        except Exception:
            if f is not None:
                f.close()
            return False

    def __export_json__(self, location):
        f = None
        try:
            f = open(location + '\\' + self.username + '_saved_tracks.json','w')
            f.write(json.dumps(self.saved_tracks))
            f.close()
            return True
        except Exception:
            if f is not None:
                f.close()
            return False

    def export(self, format=MusicExportFormat.TXT, location='.\\'):
        if format is MusicExportFormat.TXT:
            return self.__export_txt__(location)
        elif format is MusicExportFormat.JSON:
            return self.__export_json__(location)
        else:
            return False

    def connect(self):
        raise NotImplementedError("Please Implement connect")

    def reconnect(self):
        raise NotImplementedError("Please Implement reconnect")

    def get_saved_tracks(self):
        raise NotImplementedError("Please Implement get_saved_tracks")

    def _ask_for_permission(self,url):
        print('''

            User authentication requires interaction with your
            web browser. Once you enter your credentials and
            give authorization, you will be redirected to
            a url.  Paste that url you were directed to to
            complete the authorization.

        ''')
        auth_url = url
        try:
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except:
            print("Please navigate here: %s" % auth_url)

        print()
        print()
        try:
            response = raw_input("Enter the URL you were redirected to: ")
        except NameError:
            response = input("Enter the URL you were redirected to: ")

        print()
        print() 

        try:
            return response.split("?code=")[1].split("&")[0]
        except IndexError:
            return None


class Spotify(MusicProvider):
    def __init__(self, username):
        try:
            f = open('.\\.cache-spotify','r')
            info = json.loads(''.join(f.readlines()))
            f.close()
            CLIENT_ID=info['SPOTIPY_CLIENT_ID']
            CLIENT_SECRET=info['SPOTIPY_CLIENT_SECRET']
        except Exception:
            CLIENT_ID=input('Please enter Spotify Client ID: ')
            CLIENT_SECRET=input('Please enter Spotify Client Secret: ')
            txt = {
                'SPOTIPY_CLIENT_ID':    CLIENT_ID,
                'SPOTIPY_CLIENT_SECRET': CLIENT_SECRET
            }
            f = open('.\\.cache-spotify','w')
            f.write(json.dumps(txt))
            f.close()
        REDIRECT_URI='http://localhost/?a=x'
        scope = 'user-library-read'
        super(Spotify,self).__init__(username, scope, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    def connect(self):
        if self.token is not None: return True
        #client_credentials_manager = SpotifyClientCredentials(client_id=self.SPOTIPY_CLIENT_ID, client_secret=self.SPOTIPY_CLIENT_SECRET)
        #sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.token = util.prompt_for_user_token(
            self.username,
            self.scope,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            redirect_uri=self.REDIRECT_URI)

        if self.token:return True
        else: return False

    def reconnect(self):
        if self.token: self.token = None
        return self.connect()

    def get_saved_tracks(self):
        successfull_op = False
        if self.token:
            sp = spotipy.Spotify(auth=self.token)
            offset=0
            limit=20
            results = sp.current_user_saved_tracks(offset=offset, limit=limit)
            while results['next'] != None:
                for item in results['items']:
                    track = item['track']
                    song = Song(
                        name=track['name'],
                        album=track['album']['name'],
                        artist=track['artists'][0]['name'],
                        track_number=track['track_number'],
                        track_id=track['id'],
                        duration_ms=track['duration_ms'])
                    self.saved_tracks.add(song)
                offset += limit
                results = sp.current_user_saved_tracks(offset=offset, limit=limit)
            successfull_op = True
        return successfull_op
    
class Deezer(MusicProvider):
    def __init__(self, username):
        try:
            f = open('.\\.cache-deezer','r')
            info = json.loads(''.join(f.readlines()))
            f.close()
            CLIENT_ID=info['CLIENT_ID']
            CLIENT_SECRET=info['CLIENT_SECRET']
        except Exception:
            CLIENT_ID=input('Please enter Deezer Client ID: ')
            CLIENT_SECRET=input('Please enter Deezer Client Secret: ')
            txt = {
                'CLIENT_ID':    CLIENT_ID,
                'CLIENT_SECRET': CLIENT_SECRET
            }
            self._save_persistent_info('.\\.cache-deezer', json.dumps(txt))
        REDIRECT_URI='http://localhost/'
        scope = 'user-library-read'
        self.OAUTH_TOKEN_URL = 'https://connect.deezer.com/oauth/auth.php'
        self.OAUTH_ACCESS_TOKEN_URL = 'https://connect.deezer.com/oauth/access_token.php'
        self.proxies = None

        super(Deezer,self).__init__(username, scope, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    def _save_persistent_info(self, file, content):
        f = open(file,'w')
        f.write(content)
        f.close()

    def connect(self):
        url = self.OAUTH_TOKEN_URL + '?'
        url += 'app_id=' + self.CLIENT_ID
        url += '&redirect_uri=' + self.REDIRECT_URI
        url += '&perms=' + self.scope
        try:
            f = open('.\\.cache-deezer-' + self.username,'r')
            self.token = json.loads(''.join(f.readlines()))
            f.close()
        except Exception:
            code = self._ask_for_permission(url)

            url = self.OAUTH_ACCESS_TOKEN_URL + '?'
            url += 'app_id=' + self.CLIENT_ID
            url += '&secret=' + self.CLIENT_SECRET
            url += '&code=' + code
            url += '&output=json'
            
            response = requests.get(url, verify=True, proxies=self.proxies)
            if response.status_code is not 200:
                raise Exception(response.reason)
            self.token = response.json()
            self._save_persistent_info('.\\.cache-deezer-' + self.username, str(response.text))
        
        '''url = 'https://api.deezer.com/user/me?'
        url += 'access_token=' + self.token['access_token']
        response = requests.get(url, verify=True, proxies=self.proxies)'''

        return True

    def get_saved_tracks(self):
        successfull_op = True
        url = 'https://api.deezer.com/user/me/tracks?'
        url += 'access_token=' + self.token['access_token']
        response = requests.get(url, verify=True, proxies=self.proxies).json()
        keep_search = True
        while keep_search:
            tracks = response['data']
            for track in tracks:
                song = Song(
                        name=track['title'],
                        album=track['album']['title'],
                        artist=track['artist']['name'],
                        track_number='0',
                        track_id=track['id'],
                        duration_ms=str(int(track['duration'])*1000))
                self.saved_tracks.add(song)
            if 'next' in response:
                url = response['next']
                response = requests.get(url, verify=True, proxies=self.proxies).json()
            else: keep_search = False
        return successfull_op