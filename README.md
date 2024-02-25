# Apple Music to YouTube Music Converter

I quickly wrote this Python script to port over songs and playlists from your Apple Music account to your YouTube Music account. Since I'm using ytmusicapi - which can directly query and determine the difference between music videos and their music-only counterparts - the script will try to match with the equivalent audio YouTube ID.

## Important Caveat
Apple Music provides limited end-user access to their music API without a developer license, and with that consideration, the script emulates you using your web browser.

YouTube Music as of this writing does not have any documented API. Features such as searching for only music-tracks and not music videos, and access to port albums and songs into your library are not supported by the general YouTube API at the time of writing.

Since I prefer the higher audio-quality and lack of sound-effects, intros or outros, I'm using [ytmusicapi](https://github.com/sigma67/ytmusicapi) (which I would like to acknowledge for their excellent work reverse-engineering the obscure API calls YouTube Music makes).

With both of these in mind, this script may fall out of date, specifically on the Apple side of things, where implementation is simply with the requests library and emulating how browsers currently communicate with Apple's API.

Pull requests are welcome if you see any possibility for improvement. Both APIs are temperamental so keeping this script up-to-date would be nice.

## Getting Started
### Git
Clone the repository to somewhere that your user has read and write access (ex. Downloads, Documents, Desktop, etc. depending on your operating system and configuration.)

```
git clone 
```

### Python, Pip and Packages
First, install Python 3.10 or higher using a tool like Homebrew. 3.9 doesn't work (at least on MacOS) due to a bug with the version of the ssl package's compatibility with MacOS.

As an optional step, you can create a virtual environment to avoid installing the packages in the next step globally.

Then, run the pip command to pull in your requirements:

```sh
pip install -r requirements.txt
```

### Authenticating with Apple
This is the hardest step, but in essence, in order to access the Apple Music API as an end-user as opposed to a developer (who requires a paid license) you must copy some headers from your web browser.

First, open DevTools and switch to the Network tab. Change the filtering type from 'All' to 'Fetch/XHR' (depending on your browser). Then, open [music.apple.com](https://music.apple.com). Sign in if needed.

You should now have a number of requests (after you have signed in) to amp-api.music.apple.com. If you click on any one of them, it should have the headers needed for the next step.

Using either your IDE or terminal, set the following environment variables before running main.py.

The below are listed in the format of necessary environment variable, and equivalent header:

- **apple_music_authorization_header**: Authorization
- **apple_music_cookie_header**: Cookie (make sure to copy all of the cookie string)
- **apple_music_media_user_token_header**: media-user-token

### Authenticating with YouTube
In my opinion, the easiest way is to go into your venv in your terminal ([this guide](https://ioflood.com/blog/python-activate-venv/) gives good directions), and type the following command:

```
ytmusicapi oauth
```

Follow the steps and when done, you should see a new oauth.json file at the root of your cloned folder.

### Run the Apple Script
In your virtual environment, run ``main.py``. It should tell you that it's finding songs and playlists from your Apple Music collection. Once the script exits, assuming no errors occurred, you should see 2 new files in your cloned folder: ``playlists.json`` and ``song_metadata.json``.

### Run the YouTube Music Script
Now, in your virtual environment, run ``yt_music.py``. It should pull in everything it needs from song_metadata.json, playlists.json and oauth.json. It will give you updates on the status of matching and porting songs to YouTube Music.

## Acknowledgements
This script was made considerably easier with the help of sigma67's [ytmusicapi](https://github.com/sigma67/ytmusicapi). YouTube Music's API is very obscure and reverse-engineering it no-doubt took a considerable amount of time, so thank you, as it meant only learning the ins-and-outs of a single unofficial API.

## Limitations
- The concept of saving an album is considerably different on Apple Music compared to YouTube Music. On Apple Music, an album in your library isn't actually an "album", but rather a collection of songs within that album. Put another way, on Apple Music, if a single song out of an 8-song album is saved to your library, that album will appear in your library.  
‎   
In comparison, YouTube Music lets you have an album saved to your library without a single track inside that album being saved individually.  
‎  
This discordance between the two platforms means that you can't port over albums with my current implementation. Pull-requests are welcome. One idea I had (but wound up  manually porting albums since I have a lot fewer full albums I want saved on YT Music) is to compare whether all of the songs from a given album are in the user's library on Apple.  
‎
- Similar to albums, artists behave differently. You can't add an artist to **only** your **YouTube Music** library. Instead, you have to subscribe to their YouTube channel (meaning your subscription list will include them, and you will receive community posts and videos from them in the main YouTube app).  
‎  
For me, this is an untenable solution given that YouTube and YouTube Music are separate entities to me. Luckily, if you have at least 1 song by an artist saved on YouTube Music, they will appear under the artists tab, which is actually similar behaviour to Apple Music, prior to them adding the Favourite Artist feature.  
‎  
- I'm not sure whether this script will fully work with non-Premium YouTube accounts. In the past, the YouTube Music app used to primarily serve music videos even if you only wanted audio if you were on the free tier. This may have changed, but is something to keep in mind. In my opinion, the value proposition of YouTube Premium is worth it if you regularly use YouTube and stream music (and if you're on iOS, remember: the regular YouTube Premium price is cheaper, and there's an even cheaper student price if you sign up from [YouTube's website](https://www.youtube.com/premium) instead of the app.) In my country, the student plan makes YouTube Premium pretty economical!

## License
This project is under the [MIT license](https://choosealicense.com/licenses/mit/), found in ``LICENSE.md``.
