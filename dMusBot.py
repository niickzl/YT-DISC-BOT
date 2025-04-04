from typing import Final
import discord
from discord import FFmpegPCMAudio
import yt_dlp as youtube_dl
import os
import queue
'''import psutil'''
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

#Load Token
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
FFMPEG_PATH = r"C:\Users\20051\Desktop\Discord Bot\ffmpeg\ffmpeg-2025-02-17-git-b92577405b-essentials_build\bin\ffmpeg.exe"
DOWNLOAD_PATH = r"C:\Users\20051\Desktop\Discord Bot\Music Files"

#Setup
intents: Intents = Intents.default()
intents.message_content = True
intents.voice_states = True
client: Client = Client(intents=intents)

'''ffmpeg_dict = {}'''
song_queues = queue.Queue()
path_queues = queue.Queue()

#allow private message accessed by ?(context)
async def action(message: Message, user_message: str) -> None:
    if not user_message:
        print("(Message was empty because intents were not enabled probably)")
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    
    try:
        response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

#attempt to clear both queues and dict
async def clear():
    '''ffmpeg_dict.clear()'''
    while not song_queues.empty(): song_queues.get_nowait()
    while not path_queues.empty(): 
        temp = path_queues.get_nowait()
        '''if os.path.exists(temp):
            try:
                # Terminate the specific ffmpeg process for the song
                pc = ffmpeg_dict.get(temp)
                if pc:
                    try:
                        pc.terminate()
                        print(f"Terminated ffmpeg process for {temp}")
                    except Exception as err:
                        print(f"Error terminating ffmpeg process for {temp}: {err}")
                    finally:
                        ffmpeg_dict.pop(temp)
                os.remove(temp)
                print(f"Deleted file: {temp}")
            except Exception as e:
                print(f"Error deleting file: {e}")'''

#function for the bot to join a voice channel
#checks if commander is in a voice channel, if bot is in a voice channel
async def join(message: Message):
    if not message.author.voice or not message.author.voice.channel:
        await message.channel.send("YOU NEED TO JOIN A VOICE CHANNEL FIRST")
        return

    user_channel = message.author.voice.channel
    voice_client = discord.utils.get(client.voice_clients, guild=message.guild)

    if voice_client:
        if voice_client.channel == user_channel:
            await message.channel.send('?')
            await message.channel.send(f"im already in **{user_channel.name}**")
            await message.channel.send('dummy')
        else:
            await voice_client.move_to(user_channel)
            await message.channel.send(f"im gonna follow u to **{user_channel.name}**")
    else:
        await user_channel.connect()
        await message.channel.send(f"welcome your goat zlBot to **{user_channel.name}**!")

#function to disconnect the bot from a voice channel
#checks if the bot is in a voice channel or not
async def leave(message: Message):

    voice_client = discord.utils.get(client.voice_clients, guild=message.guild)

    if voice_client:
        await message.guild.voice_client.disconnect()
        await message.channel.send("boring ahh call, im outta here")
    else:
        await message.channel.send("im not in a call bruh")

    await clear()
    
#function after command "play" is ran
#downloads audio file
async def play(message: Message, url: str):
    """ Plays audio from a YouTube URL """

    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    voice_client = discord.utils.get(client.voice_clients, guild=message.guild)

    # YouTube download
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': f'{DOWNLOAD_PATH}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '128',
        }],
        'ffmpeg_location': FFMPEG_PATH,
    }

    # Extract audio URL
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            file_path = filename.replace("webm", "opus")
            file_path = filename.replace("mp4", "opus")
            title = info.get('title', 'Unknown Title')

        if not os.path.exists(file_path):
            await message.channel.send("Failed to download the audio.")
            return

        if voice_client.is_playing():
            song_queues.put(file_path)
            path_queues.put(file_path)
            await message.channel.send(f"ill sing **{title}** after")
            '''for proc in psutil.process_iter(attrs=['pid', 'name']):
                if 'ffmpeg' in proc.info['name'].lower():
                    ffmpeg_dict[file_path] = proc'''
        else:
            path_queues.put(file_path)
            await play_song(voice_client, file_path)
            '''for proc in psutil.process_iter(attrs=['pid', 'name']):
                if 'ffmpeg' in proc.info['name'].lower():
                    ffmpeg_dict[file_path] = proc'''
        
    except Exception as e:
        await message.channel.send(f"Error downloading or playing the audio for: **{e}**")
        print(f"Error: {e}")

#function comes after play()
#plays the audio file and runs itself to queue next audio
async def play_song(voice_client, file_path):

    def after_playing(e):
        # After the song finishes, check the queue and play the next song
        if not song_queues.empty():
            next_song = song_queues.get_nowait()
            voice_client.play(FFmpegPCMAudio(next_song, executable=FFMPEG_PATH), after=lambda e: after_playing(e))
            print(f"now im gonna sing: **{next_song}** now")
        else:
            print("im done singing")

        # Delete the file after playing
        last_song = path_queues.get_nowait()
        if os.path.exists(last_song):
            try:
                # Terminate the specific ffmpeg process for the song
                '''temp = ffmpeg_dict.get(last_song)
                if temp:
                    try:
                        temp.terminate()
                        print(f"Terminated ffmpeg process for {last_song}")
                    except Exception as err:
                        print(f"Error terminating ffmpeg process for {last_song}: {err}")
                    finally:
                        ffmpeg_dict.pop(last_song)'''

                os.remove(last_song)
                print(f"Deleted file: {last_song}")
            except Exception as e:
                print(f"Error deleting file: {e}")

    voice_client.play(FFmpegPCMAudio(file_path, executable=FFMPEG_PATH), after=lambda e: after_playing(e))

#function to skip audio file to the next in queue
async def skip(message: Message):
    voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
    if not voice_client or not voice_client.is_playing():
        await message.channel.send("i cant skip if im not singing anything")
        return    
    else:
        if not song_queues.empty():
            await message.channel.send("fine ill skip, gonna sing the next song")
            voice_client.stop()
        else:
            await message.channel.send("theres no song in queue bruh")
            voice_client.stop()

#Startup
@client.event
async def on_ready() -> None:
    print(f'{client.user} running')

#incoming message
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    if not client.user in message.mentions and not "!!!" in message.content:
        return
    
    username: str = str(message.author)
    user_message = message.content.replace(f"<@{client.user.id}>", "").replace("!!!", "").strip()
    channel = message.channel

    print(f'[{str(channel)} {username}: {user_message}]')
    
    if "join" in user_message.lower():
        await join(message)
    elif "leave" in user_message.lower():
        await leave(message)
    elif "play" in user_message.lower() or "sing" in user_message.lower():
        voice_client = discord.utils.get(client.voice_clients, guild=message.guild)

        if not message.author.voice or not message.author.voice.channel:
            await join(message)
        if voice_client is None or voice_client.channel != message.author.voice.channel:
            await join(message)

        user_message = user_message.replace("play","").replace("sing","").strip()
        await play(message, user_message)
    elif "skip" in user_message.lower():
        await skip(message)
    else:
        response =  get_response(user_message)
        await channel.send(response)


#main
def main() -> None:
    client.run(TOKEN)

if __name__ == "__main__":
    main()