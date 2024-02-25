import json
import os
import time
from typing import Optional

import requests
from requests import Response

class AppleMusicApi:
    authorization_header: str = None
    cookie_header: str = None
    media_user_token_header: str = None
    user_agent_header: str = None
    apple_music_api_base: str = 'https://amp-api.music.apple.com'
    song_metadata_filename: str = 'song_metadata.json'
    playlists_filename: str = 'playlists.json'
    time_between_requests: int = 2

    def create_get_request(self, url: str) -> Response:
        return requests.get(url, headers=self.get_api_headers())

    def save_api_file(self, file_name: str, contents):
        with open(file_name, 'w') as file:
            json.dump(contents, file, indent=4)

    def get_library_playlist_songs(self, playlist_id: str) -> Optional[list[dict[str, str]]]:
        songs_so_far: list[dict[str, str]] = []
        playlist_url = self.get_api_url('/v1/me/library/playlists/' + playlist_id + '?include=tracks&l=en-CA')
        playlist_api_response: Response = self.create_get_request(playlist_url)

        if playlist_api_response.status_code != 200:
            return None

        playlist_object = playlist_api_response.json()
        playlist_data = playlist_object.get('data')

        if not playlist_data or len(playlist_data) < 1:
            return None

        current_playlist = playlist_data[0]

        playlist_relationships = current_playlist.get('relationships')

        if not playlist_relationships:
            return None

        playlist_track_data = playlist_relationships.get('tracks')

        if not playlist_track_data:
            return None

        playlist_tracks = playlist_track_data.get('data')

        if not playlist_tracks or len(playlist_tracks) < 1:
            return None

        for track in playlist_tracks:
            if 'attributes' not in track:
                continue

            current_track_attributes = track.get('attributes')

            if 'name' not in current_track_attributes or 'artistName' not in current_track_attributes:
                continue

            new_song: dict[str, str] = dict()
            new_song['name'] = current_track_attributes.get('name')
            new_song['artist_name'] = current_track_attributes.get('artistName')
            new_song['album_name'] = current_track_attributes.get('albumName')

            songs_so_far.append(new_song)

        playlist_object['songs'] = songs_so_far

        return playlist_object

    def get_library_playlists(self, use_cached_playlists: bool = True, save_to_cache: bool = True) -> list[dict]:
        if os.path.isfile(self.playlists_filename) and use_cached_playlists:
            with open(self.playlists_filename, 'r') as file:
                data = file.read()
                playlists: list[dict] = json.loads(data)
                return playlists

        playlists_so_far: list = []
        all_playlists_url = self.get_api_url('/v1/me/library/playlists?l=en-CA&limit=100')
        current_response: Response = self.create_get_request(all_playlists_url)

        if current_response.status_code != 200:
            raise Exception("An error occurred when making the playlist list get request")

        current_response_json = current_response.json()
        playlists_list = current_response_json.get('data')

        for playlist_object in playlists_list:
            playlist_data = self.get_library_playlist_songs(playlist_object.get('id'))

            if playlist_data is not None:
                playlists_so_far.append(playlist_data)

        if save_to_cache:
            self.save_api_file(self.playlists_filename, playlists_so_far)

        return playlists_so_far

    def get_song_list(self, use_cached_song_list: bool = True, save_to_cache: bool = True) -> list[dict]:
        if os.path.isfile(self.song_metadata_filename) and use_cached_song_list:
            with open(self.song_metadata_filename, 'r') as file:
                data = file.read()
                song_list: list[dict] = json.loads(data)
                return song_list


        song_list_so_far: list[dict] = []
        current_song_list_url = self.get_api_url('/v1/me/library/songs?l=en-CA')
        current_response: Response = self.create_get_request(current_song_list_url)

        if current_response.status_code != 200:
            raise Exception("An error occurred when making the song list get request. URL: " + current_song_list_url + ", stack trace: " + json.dumps(current_response.text))

        current_response_json = current_response.json()

        for song_object in current_response_json['data']:
            song_list_so_far.append(song_object)

        while current_response_json.get('next'):
            current_song_list_url = self.get_api_url(current_response_json.get('next'))
            current_response = self.create_get_request(current_song_list_url)

            if current_response.status_code != 200:
                raise Exception("Failed fetching song list. URL: " + current_song_list_url + ", stack trace: " + json.dumps(current_response.text))

            current_response_json = current_response.json()

            for song_object in current_response_json['data']:
                song_list_so_far.append(song_object)

            print("Fetched " + str(len(song_list_so_far)) + " songs so far, waiting " + str(self.time_between_requests) + " seconds...")
            time.sleep(self.time_between_requests)

        if save_to_cache:
            self.save_api_file(self.song_metadata_filename, song_list_so_far)

        return song_list_so_far

    def get_api_url(self, relative_api_url: str) -> str:
        return self.apple_music_api_base + relative_api_url

    def get_api_headers(self) -> dict[str, str]:
        api_headers: dict[str, str] = dict()

        api_headers['Accept'] = '*/*'
        api_headers['Accept-Encoding'] = 'gzip, deflate, br'
        api_headers['Accept-Language'] = 'en-CA,en-US;q=0.9,en;q=0.8'
        api_headers['Authorization'] = self.authorization_header
        api_headers['Connection'] = 'keep-alive'
        api_headers['Cookie'] = self.cookie_header
        api_headers['Host'] = 'amp-api.music.apple.com'
        api_headers['media-user-token'] = self.media_user_token_header
        api_headers['Origin'] = 'https://music.apple.com'
        api_headers['Referer'] = 'https://music.apple.com/'
        api_headers['User-Agent'] = self.user_agent_header

        return api_headers

    def __init__(self):
        possible_authorization_header = os.environ.get('apple_music_authorization_header')

        if possible_authorization_header:
            self.authorization_header = possible_authorization_header
        else:
            raise Exception("Missing apple_music_authorization_header environment variable")

        possible_cookie_header = os.environ.get('apple_music_cookie_header')

        if possible_cookie_header:
            self.cookie_header = possible_cookie_header
        else:
            raise Exception("Missing apple_music_cookie_header environment variable")

        possible_media_user_token_header = os.environ.get('apple_music_media_user_token_header')

        if possible_media_user_token_header:
            self.media_user_token_header = possible_media_user_token_header
        else:
            raise Exception("Missing apple_music_media_user_token_header environment variable")

        self.user_agent_header = os.environ.get('apple_music_user_agent_header', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15')


def main_logic():
    apple_music_api: AppleMusicApi = AppleMusicApi()
    apple_music_api.get_song_list()
    apple_music_api.get_library_playlists()


if __name__ == '__main__':
    main_logic()
