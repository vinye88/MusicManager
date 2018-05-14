import itertools

class Song(dict):
    def __str__(self):
        ret =  '[' + self['artist'] + '],'
        ret += '[' + self['album'] + '],'
        ret += '[' + str(self['track_number']) + '],'
        ret += '[' + self['name'] + '],'
        ret += '[' + str(self['duration_ms']) + ']'
        return ret

    def __hash__(self):
        return hash(self['name']) + hash(self['album']) + hash(self['artist'])
    
    def __init__(self, name, album, artist, track_number=0, duration_ms=0):
        super(Song, self).__setitem__('name', name)
        super(Song, self).__setitem__('album', album)
        super(Song, self).__setitem__('artist', artist)
        super(Song, self).__setitem__('track_number', track_number)
        super(Song, self).__setitem__('duration_ms', duration_ms)
    
    def __eq__(self,other):
        return self['name'] == other['name'] and self['album'] == other['album'] and self['artist'] == other['artist']
    
    def __ne__(self,other):
        return not self.__eq__(other)

class Album(dict):
    def __setitem__(self, key, value):
        #if super(Album, self).__contains__(key):
        #    print('\tFound song duplicity: ' + str(value))
        super(Album, self).__setitem__(key, value)

    def len(self):
        return len(self)

    def __str__(self):
        ret = '\t' + self.name + '(' + str(self.len()) + '):'
        for song in self.values():
            ret += '\n\t\t' + str(song)
        return ret

    def __init__(self, name, songs = []):
        self.name = name
        for song in songs:
            self.__setitem__(song['name'], song)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Album):
            return self.name == other.name and super(Album, self).__eq__(other)
        else:
            return super(Album, self).__eq__(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __copy__(self):
        newone = self.copy()
        newone.name = self.name
        return newone

    def getsongs(self):
        return list([x for x in self.values()])

class Artist(dict):
    def song_len(self):
        return sum([x.len() for x in self.values()])
    
    def album_len(self):
        return len(self)

    def __setitem__(self, key, value):
        if not super(Artist, self).__contains__(key):
            super(Artist, self).__setitem__(key, value)
        else:
            #print('\tFound album duplicity: ' + str(value))
            self[key].update(value)

    def __init__(self, name, albums=[]):
        self.name = name
        for album in albums:
            super(Artist, self).__setitem__(album.name, album)

    def __eq__(self,other):
        if isinstance(other, str):
            return self.name == other
        elif isinstance(other, Artist):
            return self.name == other.name and super(Artist, self).__eq__(other)
        else:
            return super(Artist, self).__eq__(other)

    def __ne__(self,other):
        return not self.__eq__(other)

    def __str__(self):
        ret = self.name + '(' + str(self.album_len()) + ',' + str(self.song_len()) + '):'
        for albuns in self.values():
            ret += '\n' + str(albuns)
        return ret

    def getsongs(self):
        return list(itertools.chain(*[x.getsongs() for x in self.values()]))

class MusicLibrary(dict):
    def artist_len(self):
        return len(self)
    
    def album_len(self):
        return sum([a.album_len() for a in self.values()])

    def song_len(self):
        return sum([a.song_len() for a in self.values()])

    def __setitem__(self, key, value):
        if not self.__contains__(key):
            super(MusicLibrary, self).__setitem__(key, value)
        else:
            self[key].update(value)

    def __init__(self, name='', artists = []):
        self.name = name
        for artist in artists:
            super(MusicLibrary, self).__setitem__(artist.name, artist)

    def __str__(self):
        ret =  'Artists: ' + str(self.artist_len())
        ret += '\nAlbums: ' + str(self.album_len())
        ret += '\nSongs: ' + str(self.song_len())
        return ret

    def add(self,item):
        if isinstance(item, Song):
            self.__addsong__(item)
        elif isinstance(item, Artist):
            self.__addartist__(item)
        elif isinstance(item,list):
            for x in item:
                self.add(x)
    
    def __addartist__(self, artist):
        addthis = None
        if isinstance(artist, str):
            if not self.__contains__(artist):
                addthis = Artist(artist)
        elif isinstance(artist, Artist):
            addthis = artist

        if addthis is not None:
            super(MusicLibrary, self).__setitem__(addthis.name, addthis)

    def __addsong__(self, song):
        if not self.__contains__(song['artist']):
            super(MusicLibrary, self).__setitem__(song['artist'], Artist(song['artist']))

        if not self[song['artist']].__contains__(song['album']):
            self[song['artist']][song['album']] = Album(song['album'])
        
        if not self[song['artist']][song['album']].__contains__(song['name']):
            self[song['artist']][song['album']][song['name']] = song
    def getsongs(self):
        songs = list()
        for artist in self.values():
            for album in artist.values():
                for song in album.values():
                    songs.append(song)
        return list(itertools.chain(*[x.getsongs() for x in self.values()]))
        #return songs