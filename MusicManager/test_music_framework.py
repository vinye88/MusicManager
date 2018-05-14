import unittest
from music_framework import Song, Album, Artist, MusicLibrary

class TestCaseHelperForMusicFramework(unittest.TestCase):
    songs = [
        Song('A','A','A'),
        Song('A','A','A', 2, 32768),
        Song('A','A','a'),
        Song('A','a','A'),
        Song('a','A','A')
    ]

    albuns = [
        Album('A'),
        Album('A', songs[-2::]),
        Album('B'),
        Album('C', songs[-2::])
    ]

    artists = [
        Artist('A'),
        Artist('A', [x for i,x in enumerate(albuns) if i%2 == 1]),
        Artist('B'),
        Artist('C', [x for i,x in enumerate(albuns) if i%2 == 1])
    ]

class TestSong(TestCaseHelperForMusicFramework):
    def test_constructor(self):
        self.assertEqual(self.songs[0]['name'], 'A')
        self.assertEqual(self.songs[0]['album'], 'A')
        self.assertEqual(self.songs[0]['artist'], 'A')
        self.assertEqual(self.songs[0]['track_number'], 0)
        self.assertEqual(self.songs[0]['duration_ms'], 0)
        self.assertEqual(self.songs[1]['track_number'], 2)
        self.assertEqual(self.songs[1]['duration_ms'], 32768)
    
    def test_eq_ne(self):
        for x in range(0,len(self.songs)):
            errorstr = 's[0] and s[' + str(x) + ']'
            if x < 2:
                self.assertEqual(self.songs[0], self.songs[x], errorstr)
            else:
                self.assertNotEqual(self.songs[0], self.songs[x], errorstr)
    
    def test_hash(self):
        for x in range(0,len(self.songs)):
            errorstr = 's[0] and s[' + str(x) + ']'
            if x < 2:
                self.assertEqual(hash(self.songs[0]), hash(self.songs[x]), errorstr)
            else:
                self.assertNotEqual(hash(self.songs[0]), hash(self.songs[x]), errorstr)

    def test_str(self):
        for song in self.songs:
            strtocheck =  '[' + song['artist'] + '],'
            strtocheck += '[' + song['album'] + '],'
            strtocheck += '[' + str(song['track_number']) + '],'
            strtocheck += '[' + song['name'] + '],'
            strtocheck += '[' + str(song['duration_ms']) + ']'
            self.assertEqual(str(song), strtocheck)

class TestAlbum(TestCaseHelperForMusicFramework):
    def test_setitem(self):
        self.assertEqual(len(Album("X", self.songs)), 2)

    def test_constructor(self):
        self.assertEqual(self.albuns[-2].name, 'B')
        self.assertEqual(self.albuns[1], Album(self.albuns[1].name, self.albuns[1].values()))
        self.assertEqual(self.albuns[0], Album(self.albuns[0].name))
        
    def test_copy(self):
        self.assertDictEqual(self.albuns[1], self.albuns[1].copy())
    
    def test_len(self):
        self.assertEqual(len(self.albuns[-1]),2)

    def test_eq_ne(self):
        self.assertEqual(self.albuns[0], self.albuns[0].name)
        self.assertEqual(self.albuns[0], self.albuns[0].copy())
        self.assertNotEqual(self.albuns[0], self.albuns[1])
        self.assertNotEqual(self.albuns[1], self.albuns[-1])

    def test_str(self):
        self.assertEqual(str(self.albuns[0]),"\t" + self.albuns[0].name + '(0):')
        strtest = "\t" + self.albuns[1].name + '(2):'
        for song in self.songs[-2::]:
            strtest +='\n\t\t' + str(song)
        self.assertEqual(str(self.albuns[1]),strtest)

    def test_getsongs(self):
        self.assertEqual(len(self.albuns[-1].getsongs()), 2)
        self.assertEqual(len(self.albuns[0].getsongs()), 0)
        
class TestArtist(TestCaseHelperForMusicFramework):
    def test_len(self):
        self.assertEqual(len(self.albuns[-1]),2)

    def test_setitem(self):
        artists = Artist('A',self.albuns)
        self.assertEqual(list(artists.keys()),['A','B','C'])
        self.assertEqual(len(artists['A'].keys()),2, "both album's songs were not combined")

    def test_constructor(self):
        self.assertEqual(self.artists[-2].name, 'B')
        self.assertEqual(self.artists[1], Artist(self.artists[1].name, self.artists[1].values()))
        self.assertEqual(self.artists[0], Album(self.artists[0].name))

    def test_eq_ne(self):
        self.assertEqual(self.artists[0], self.artists[0].name)
        self.assertEqual(self.artists[0], self.artists[0].copy())
        self.assertNotEqual(self.artists[0], self.artists[1])
        self.assertNotEqual(self.artists[1], self.artists[-1])
    
    def test_str(self):
        self.assertEqual(str(self.artists[0]), self.albuns[0].name + '(0,0):')
        strtest = self.artists[1].name + '(2,4):'
        for album in [x for i,x in enumerate(self.albuns) if i%2 == 1]:
            strtest +='\n' + str(album)
        self.assertEqual(str(self.artists[1]),strtest)

    def test_getsongs(self):
        self.assertEqual(len(self.artists[-1].getsongs()), 4)
        self.assertEqual(len(self.artists[0].getsongs()), 0)

class TestMusicLibrary(TestCaseHelperForMusicFramework):
    def test_setitem(self):
        self.assertEqual(list(MusicLibrary(artists=self.artists).keys()),['A','B','C'])

    def test_constructor(self):
        self.assertEqual(MusicLibrary('A').name, 'A')
        self.assertEqual(len(MusicLibrary(artists=self.artists)),3)

    def test_str(self):
        teststr = 'Artists: 3\nAlbums: 4\nSongs: 8'
        self.assertEqual(str(MusicLibrary(artists=self.artists)),teststr)

    def test_addartist(self):
        lib = MusicLibrary()
        lib.add(self.artists)
        teststr = 'Artists: 3\nAlbums: 4\nSongs: 8'
        self.assertEqual(str(lib), teststr)

    def test_addsong(self):
        lib = MusicLibrary()
        lib.add(self.songs)
        teststr = 'Artists: 2\nAlbums: 3\nSongs: 4'
        self.assertEqual(str(lib), teststr)

    def test_massive_song_add(self):
        l = MusicLibrary()
        ix, iy, iz = 0, 0, 0
        for x in range(65,90):
            ix+=1
            for y in range(65,90):
                iy+=1
                for z in range(65,90):
                    iz+=1
                    l.add(Song(chr(x),chr(y),chr(z)))
        self.assertEqual(ix, l.artist_len(), "wrong artist len")
        self.assertEqual(iy, l.album_len(), "wrong album number")
        self.assertEqual(iz, l.song_len(), "wrong song number")

    @unittest.expectedFailure
    def test_massive_song_add2(self):
        f = open('.\\rawmusiclib.txt','r', encoding='utf8')
        lines = f.readlines()
        f.close()
        l = MusicLibrary()
        i = 0
        for x in range(0, len(lines)-1):
            if len(lines[x]) > 0:
                s = Song(*((lines[x]).replace('\n','').split('\t')))
                l.add(s)
                i+=1
                self.assertEqual(i, l.song_len(), "could not add - " + str(i))
                '''try: self.assertEqual(i, l.song_len(), "could not add - " + str(i))
                except AssertionError:
                    print("could not add line" + str(x+1) + ':' + str(s))
                    i-=1'''
    
    def test_getsongs(self):
        l = MusicLibrary()
        self.assertEqual(len(l.getsongs()), 0)
        for x in range(65,90):
            for y in range(65,90):
                for z in range(65,90):
                    l.add(Song(chr(x),chr(y),chr(z)))
        self.assertEqual(len(l.getsongs()), pow(25,3))

if __name__ == '__main__':
    unittest.main()
