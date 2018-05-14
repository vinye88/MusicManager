import spotipy, json
import spotipy.util as util

from enum import Enum, auto
from music_framework import Song, MusicLibrary

class MusicExportFormat(Enum):
    JSON = auto()
    TXT = auto()

class Spotify():
    def __init__(self, username):
        try:
            f = open('.\\.cache-spotify','r')
            info = json.loads(''.join(f.readlines()))
            f.close()
            self.SPOTIPY_CLIENT_ID=info['SPOTIPY_CLIENT_ID']
            self.SPOTIPY_CLIENT_SECRET=info['SPOTIPY_CLIENT_SECRET']
        except Exception as e:
            self.SPOTIPY_CLIENT_ID=input('Please enter Spotify Client ID: ')
            self.SPOTIPY_CLIENT_SECRET=input('Please enter Spotify Client Secret: ')
            txt = {
                'SPOTIPY_CLIENT_ID':    self.SPOTIPY_CLIENT_ID,
                'SPOTIPY_CLIENT_SECRET': self.SPOTIPY_CLIENT_SECRET
            }
            f = open('.\\.cache-spotify','w')
            f.write(json.dumps(txt))
            f.close()
            
        self.SPOTIPY_REDIRECT_URI='http://localhost/?a=x'
        self.scope = 'user-library-read'
        self.username = username
        self.saved_tracks = MusicLibrary(username)
        self.token = None
    
    def connect(self):
        if self.token is not None: return True
        #client_credentials_manager = SpotifyClientCredentials(client_id=self.SPOTIPY_CLIENT_ID, client_secret=self.SPOTIPY_CLIENT_SECRET)
        #sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.token = util.prompt_for_user_token(
            self.username,
            self.scope,
            client_id=self.SPOTIPY_CLIENT_ID,
            client_secret=self.SPOTIPY_CLIENT_SECRET,
            redirect_uri=self.SPOTIPY_REDIRECT_URI)

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
                        duration_ms=track['duration_ms'])
                    self.saved_tracks.add(song)
                offset += limit
                results = sp.current_user_saved_tracks(offset=offset, limit=limit)
            successfull_op = True
        return successfull_op
    
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
