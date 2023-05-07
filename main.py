from discord.ext import commands
from datetime import datetime, timedelta
from time import sleep
import discord, threading, os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

SONG_PATH = "freebird.mp3"
playing: list[tuple[datetime]] = {}

def get_playing_seconds(guild: discord.Guild):
	time_playing: timedelta = datetime.now() - playing[guild.id]
	return round(time_playing.total_seconds())

def play(ctx: commands.Context, vc: discord.VoiceClient):
	while playing[ctx.guild.id] is not None:
		print(f"Playing free bird in guild {ctx.guild.id}")
		free_bird = discord.FFmpegPCMAudio(source=SONG_PATH)
		vc.play(free_bird)
		while vc.is_playing() and vc.is_connected():
			sleep(1)
			if playing[ctx.guild.id] is None:
				break

		vc.stop()
		sleep(1)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="$",
	intents=intents,
	owner_ids=[666323445453291561],
	activity = discord.Activity(type=discord.ActivityType.listening, name="Free Bird")
)

@bot.event
async def on_ready():
	for guild in bot.guilds:
		playing[guild.id] = None
	print(f"Logged in as {bot.user.name} | {len(bot.guilds)} servers")

@bot.command(help="Begin the free bird loop")
async def begin(ctx: commands.Context):
	voice_state = ctx.author.voice
	if voice_state != None and playing[ctx.guild.id] is None:
		voice_channel = voice_state.channel
		vc = await voice_channel.connect(timeout=2**32)
		playing[ctx.guild.id] = datetime.now()

		await ctx.reply("The free bird is here :O")

		t = threading.Thread(target=play, args=(ctx, vc))
		t.start()

	else:
		await ctx.reply("The free bird has nowhere to go :/")

@bot.command(help="Stop the free bird loop")
async def stop(ctx: commands.Context):
	time_playing = get_playing_seconds(ctx.guild)
	playing[ctx.guild.id] = None

	for vc in bot.voice_clients:
		if vc.guild.id == ctx.guild.id:
			await vc.disconnect()

	await ctx.reply(f"The free bird is gone :( Final time stat: {time_playing}s")

@bot.command(help="Show how long the bot has been running for")
async def stats(ctx: commands.Context):
	await ctx.reply(f"The bird has been free for {get_playing_seconds(ctx.guild)} seconds")

@bot.command(help="Displays the bot's latency")
async def ping(ctx: commands.Context):
	await ctx.reply(f"{round(bot.latency*1000, -2)}ms")

if __name__ == "__main__":
	bot.run(TOKEN, reconnect=True)