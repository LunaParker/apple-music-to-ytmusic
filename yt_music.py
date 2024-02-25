import json
import os

import time
from typing import Optional, Any, Tuple

from ytmusicapi import YTMusic

from main import AppleMusicApi


class YouTubeMusicApi:
    ytmusicapi_instance: YTMusic = None
    credential_filename: str = 'oauth.json'
    time_between_requests: int = 1



    def add_song_to_library(self, feedback_tokens: tuple[str, str]):
        self.ytmusicapi_instance.edit_song_library_status([feedback_tokens[0]])

    def get_all_songs_by_artist(self, artist_channel_id: str):
        channel_artist = self.ytmusicapi_instance.get_artist(artist_channel_id)
        channel_artist_browse_id: str = channel_artist['songs']['browseId']

        try:
            playlist_results = self.ytmusicapi_instance.get_playlist(channel_artist_browse_id, limit=999)
        except:
            return None

        return playlist_results['tracks']

    def get_feedback_tokens_for_song(self, videoId: str, artist_channel_id: str) -> tuple[str, str]:
        songs_by_artist = self.get_all_songs_by_artist(artist_channel_id)

        if not songs_by_artist or len(songs_by_artist) < 1:
            return '', ''

        for song in songs_by_artist:
            if videoId == song['videoId']:
                if 'feedbackTokens' in song:
                    return song['feedbackTokens']['add'], song['feedbackTokens']['remove']

        return '', ''

    def get_song_feedback_tokens(self, videoId: str, artist_channel_id: str) -> tuple[str, str]:
        song_feedback_tokens: tuple[str, str] = self.get_feedback_tokens_for_song(videoId, artist_channel_id)

        if not song_feedback_tokens[0] or song_feedback_tokens[0] == '' or not song_feedback_tokens[1] or \
                song_feedback_tokens[1] == '':
            return '', ''

        return song_feedback_tokens

    def search_for_song(self, song_name: str, artist_name: str, album_name: Optional[str] = None) -> tuple[str, str]:
        search_query: str = song_name + " " + artist_name

        if album_name is not None:
            search_query = search_query + " " + album_name

        song_results = self.ytmusicapi_instance.search(search_query, filter='songs', limit=10, ignore_spelling=True)

        current_song_videoId: Optional[str] = None
        current_song_artist_id: Optional[str] = None

        for result in song_results:
            if result.get('videoType') != 'MUSIC_VIDEO_TYPE_ATV' or not result.get('artists') or len(
                    result.get('artists')) < 1:
                continue

            current_song_videoId: str = result.get('videoId')
            current_song_artist_id = result['artists'][0]['id']

            break

        if current_song_videoId is None or current_song_artist_id is None:
            return '', ''

        return current_song_videoId, current_song_artist_id

    def __init__(self):
        if not os.path.isfile(self.credential_filename):
            raise Exception(
                "The required credential file for YouTube Music (" + self.credential_filename + ") does not exist")

        try:
            self.ytmusicapi_instance = YTMusic(auth=('./' + self.credential_filename))
        except:
            raise Exception("Unable to establish YTMusic instance with given credential file")


def import_apple_songs():
    start_index: int = 0
    apple_music_api: AppleMusicApi = AppleMusicApi()
    apple_songs: list[dict] = apple_music_api.get_song_list()
    youtube_music_api: YouTubeMusicApi = YouTubeMusicApi()

    for current_index, song in enumerate(apple_songs):
        if current_index <= start_index:
            continue

        current_song: dict = apple_songs[current_index]
        current_attributes: dict = current_song.get('attributes')

        if current_attributes is None:
            continue

        song_name: str = current_attributes.get('name')
        artist_name: str = current_attributes.get('artistName')
        album_name: str = current_attributes.get('albumName')

        videoId, artist_channel_id = youtube_music_api.search_for_song(song_name, artist_name, album_name)

        if not videoId or videoId == '' or not artist_channel_id or artist_channel_id == '':
            continue

        feedback_tokens: tuple[str, str] = youtube_music_api.get_song_feedback_tokens(videoId, artist_channel_id)

        if not feedback_tokens[0] or feedback_tokens[0] == '' or not feedback_tokens[1] or feedback_tokens[1] == '':
            continue

        youtube_music_api.add_song_to_library(feedback_tokens)

        print(
            '[Index #' + str(current_index) + '] Found song: ' + song_name + ' by ' + artist_name + '. Waiting ' + str(
                YouTubeMusicApi.time_between_requests) + ' seconds before continuing...')

        time.sleep(YouTubeMusicApi.time_between_requests)


def import_apple_playlists():
    start_index: int = 0
    apple_music_api: AppleMusicApi = AppleMusicApi()
    apple_playlists: list[dict] = apple_music_api.get_library_playlists()
    youtube_music_api: YouTubeMusicApi = YouTubeMusicApi()

    for current_index, playlist in enumerate(apple_playlists):
        if current_index <= start_index:
            continue

        current_playlist = apple_playlists[current_index]
        current_playlist_data = current_playlist.get('data')
        current_playlist_data_object = current_playlist_data[0]
        current_playlist_attributes = current_playlist_data_object.get('attributes')

        playlist_name: str = current_playlist_attributes.get('name', 'Untitled Playlist')
        playlist_songs: list[dict] = current_playlist.get('songs')

        playlist_video_ids: list[str] = []

        print('[Index #' + str(current_index) + '] Starting to find songs for playlist ' + playlist_name + '...')

        for current_index, song in enumerate(playlist_songs):
            current_yt_song = youtube_music_api.search_for_song(song.get('name'), song.get('artist_name'),
                                                                song.get('album_name'))

            if not current_yt_song[0] or current_yt_song[0] == '':
                continue

            print('[Index #' + str(current_index) + '] Found song ' + song.get('name') + ' by ' + song.get('artist_name'))

            playlist_video_ids.append(current_yt_song[0])

        try:
            print('[Index #' + str(current_index) + '] Creating playlist ' + playlist_name + '...')
            youtube_music_api.ytmusicapi_instance.create_playlist(title=playlist_name, description='', video_ids=playlist_video_ids)
        except:
            print('Error creating the playlist ' + playlist_name)

        print('[Index #' + str(current_index) + '] Processed playlist ' + playlist_name + '. Waiting ' + str(
            YouTubeMusicApi.time_between_requests) + ' seconds before continuing...')

        time.sleep(YouTubeMusicApi.time_between_requests)


if __name__ == '__main__':
    import_apple_songs()
    import_apple_playlists()
