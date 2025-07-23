import os
import asyncio
from dotenv import load_dotenv
from interactions import listen, slash_command, SlashContext, Client, Intents
import interactions
from openai import OpenAI


load_dotenv()
discord_token = os.getenv("DISCORD_TOKEN")
chatgpt_token = os.getenv('CHATGPT_TOKEN')

intents = interactions.Intents.new(guilds=True, message_content=True, guild_voice_states=True, guild_members=True)
bot = interactions.Client(intents=intents,command_prefix="/")

openai_client = OpenAI(api_key=chatgpt_token)

banned_words = {}
transcribe_channel = {}


async def check_values(guild_id):
    if not guild_id in banned_words:
        banned_words[guild_id] = []
    if not guild_id in transcribe_channel:
        transcribe_channel[guild_id] = None


async def transcribe_and_kick(ctx, user_id, file):
    await check_values(ctx.guild_id)

    member = await ctx.guild.fetch_member(user_id)
    loop = asyncio.get_event_loop()
    def sync_transcribe():
        with open(file, "rb") as audio_file:
            transcription = openai_client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file
            )
            return transcription

    transcription = await loop.run_in_executor(None, sync_transcribe)

    if transcription.text is None:
        return

    if transcribe_channel[ctx.guild_id] is not None:
        if member:
            await transcribe_channel[ctx.guild_id].send(f"{member.display_name}: {transcription.text}")

    if any(text in transcription.text.lower() for text in banned_words[ctx.guild_id]):
        if member and member.voice:
            await member.move(None)
            await ctx.send(f"{member.display_name} said a banned word and was kicked (Message: {transcription.text})")

    os.remove(file)


@listen()
async def on_startup():
    print("Live Transcription Bot created by @kubes05")
    print("Bot successfully started")


@slash_command(name="listen",description="Joins your call and transcribes")
async def listen(ctx: SlashContext):
    await check_values(ctx.guild_id)

    if not ctx.author.voice:
        await ctx.send("You are not in a voice channel")
        return
    
    if ctx.voice_state is not None:
        await ctx.send("Already in a voice channel")
        return
    
    channel = ctx.author.voice.channel
    voice_state = await channel.connect()
    await ctx.send(f"Joined {channel.name}")

    while voice_state is not None:
        await voice_state.start_recording(output_dir="audioRecordings")
        await asyncio.sleep(6)
        await voice_state.stop_recording()
        
        for user_id, file in voice_state.recorder.output.items():
            asyncio.create_task(transcribe_and_kick(ctx, user_id, file))


@slash_command(name="leave",description="Leaves the call")
async def leave(ctx: SlashContext):
    await check_values(ctx.guild_id)

    if ctx.voice_state is None:
        await ctx.send("Not in a voice channel")
        return
    else:
        channel_name = ctx.voice_state.channel.name
        await ctx.voice_state.disconnect()
        await ctx.send(f"Left {channel_name}")


@slash_command(name="banword",description="Add a word to the banned words list")
@interactions.slash_option(
    name="word",
    description="Word to ban",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def banword(ctx: SlashContext, word: str):
    await check_values(ctx.guild_id)

    if not word.lower() in banned_words[ctx.guild_id]:
        banned_words[ctx.guild_id].append(word.lower())
        await ctx.send(f'Added "{word.lower()}" to banned words list ({", ".join(banned_words[ctx.guild_id])})')
    else:
        await ctx.send(f'"{word.lower()}" is already banned') 


@slash_command(name="unbanword",description="Remove a word from the banned words list")
@interactions.slash_option(
    name="word",
    description="Word to unban",
    required=True,
    opt_type=interactions.OptionType.STRING
)
async def unbanword(ctx: SlashContext, word: str):
    await check_values(ctx.guild_id)
    
    if word.lower() in banned_words[ctx.guild_id]:
        banned_words[ctx.guild_id].remove(word.lower())
        await ctx.send(f'Removed "{word.lower()}" from banned words list ({", ".join(banned_words[ctx.guild_id])})')
    else:
        await ctx.send(f'"{word.lower()}" could not be found in the banned word list') 


@slash_command(name="starttranscribing",description="Start transcribing to a channel")
@interactions.slash_option(
    name="channel",
    description="Channel to transcribe to",
    required=True,
    opt_type=interactions.OptionType.CHANNEL
)
async def starttranscribing(ctx: SlashContext, channel: interactions.BaseChannel):
    global transcribe_channel
    await check_values(ctx.guild_id)

    if transcribe_channel[ctx.guild_id] is not None:
        await ctx.send("Already transcribing to a channel")
        return
    
    transcribe_channel[ctx.guild_id] = channel
    await ctx.send(f"Now transcribing to {channel.mention}")
    

@slash_command(name="stoptranscribing",description="Stop transcribing to any channels")
async def stoptranscribing(ctx: SlashContext):
    global transcribe_channel
    await check_values(ctx.guild_id)

    if transcribe_channel[ctx.guild_id] is None:
        await ctx.send("Not currently transcribing to any channels")
        return
    
    transcribe_channel[ctx.guild_id] = None
    await ctx.send(f"No longer transcribing to any channels")

bot.start(discord_token)