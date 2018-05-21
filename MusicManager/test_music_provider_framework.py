import unittest, json
from music_provider_framework import MusicExportFormat, Spotify, Deezer
from music_framework import MusicLibrary, Song

class TestCaseHelperForMusicProviderFramework(unittest.TestCase):
    username = 'vinye_mustaine'

#@unittest.skip
class TestSpotify(TestCaseHelperForMusicProviderFramework):
    def test_constructor(self):
        mp = Spotify(self.username)
        self.assertEqual(mp.username, self.username)
        self.assertEqual(mp.token, None)
        self.assertEqual(len(mp.saved_tracks.getsongs()), 0)

    def test_connect(self):
        self.assertTrue(Spotify(self.username).connect())

    def test_reconnect(self):
        mp = Spotify(self.username)
        self.assertTrue(mp.reconnect())
        self.assertTrue(mp.reconnect())

    def test_empty_export(self):
        mp = Spotify(self.username)
        
        self.assertTrue(mp.export(MusicExportFormat.TXT))
        f = open('.\\' + self.username + '_saved_tracks.txt','r')
        lines = f.readlines()
        f.close()
        self.assertEqual(len(lines), 0)

        self.assertTrue(mp.export(MusicExportFormat.JSON))
        f = open('.\\' + self.username + '_saved_tracks.json','r')
        libmusic = json.loads(''.join(f.readlines()))
        f.close()
        self.assertEqual(len(libmusic), 0)

    def test_get_saved_tracks_export(self):
        mp = Spotify(self.username)

        self.assertTrue(mp.connect(), 'could not connect')
        self.assertTrue(mp.get_saved_tracks(), 'could not get saved tracks')
        self.assertGreater(mp.saved_tracks.artist_len(),0, 'saved tracks length is zero')

        self.assertTrue(mp.export(MusicExportFormat.TXT))
        self.assertTrue(mp.export(MusicExportFormat.JSON))

        f = open('.\\' + self.username + '_saved_tracks.txt','r', encoding='utf8')
        txtsongs = len(f.readlines())
        f.close()

        f = open('.\\' + self.username + '_saved_tracks.json','r')
        libmusic = json.loads(''.join(f.readlines()))
        f.close()
        jsonsongs = 0
        for x,y in libmusic.items():
            for z,w in y.items():
                jsonsongs+= len(w)

        self.assertGreater(jsonsongs, 0, 'json songs is empty')
        self.assertGreater(txtsongs, 0, 'txt songs is empty')
        self.assertEqual(txtsongs, jsonsongs, 'export did not match')
        #check file not empty


class TestDeezer(TestCaseHelperForMusicProviderFramework):
    def test_constructor(self):
        self.assertTrue(Deezer(self.username).connect())

    def test_get_saved_tracks(self):
        mp = Deezer(self.username)
        self.assertTrue(mp.connect(), 'could not connect')
        self.assertTrue(mp.get_saved_tracks(), 'could not get saved tracks')
        self.assertGreater(mp.saved_tracks.artist_len(),0, 'saved tracks length is zero')
    
    def test_synchronize_list(self):
        mp = Deezer(self.username)
        mp.connect()
        f = open('.\\' + self.username + '_saved_tracks.txt','r', encoding='utf8')
        lines = f.readlines()
        f.close()
        music_list = MusicLibrary('vinye_mustaine')
        for line in lines:
            music_list.add(Song(*line.split('\t')))
        print(str(music_list))
        mp.synchronize_list(music_list.getsongs())
        print(str(len(mp.saved_tracks.getsongs())))


if __name__ == '__main__':
    unittest.main()
