from discord.ext import commands
from datetime import datetime, timedelta
from time import sleep
import discord, threading, os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

SONG_PATH = "freebird.mp3"
playing: list[tuple[datetime]] = {}

APPLICATION_ID = 1104484489553510611 # Free Bird#4900
TEST_GUILD = discord.Object(id=666331295852396583) # Red Penguin's Living Room
AUTO_JOIN_USER = 666323445453291561 # ren.penguin
OWNERS = [666323445453291561] # ren.penguin

def get_playing_seconds(guild: discord.Guild):
	time_playing: timedelta = datetime.now() - playing[guild.id]
	return round(time_playing.total_seconds())

def play(guild: discord.Guild, vc: discord.VoiceClient):
	while playing[guild.id] is not None:
		print(f"Playing free bird in guild {guild.id}")
		free_bird = discord.FFmpegPCMAudio(source=SONG_PATH)
		vc.play(free_bird)
		while vc.is_playing() and vc.is_connected():
			sleep(1)
			if playing[guild.id] is None:
				break

		vc.stop()
		sleep(1)

async def join_voice_channel(guild: discord.Guild, user_id: discord.User):
	member = guild.get_member(user_id)
	if member is None:
		return 2
	voice_state = member.voice
	if voice_state != None:
		if playing[guild.id] is None:
			voice_channel = voice_state.channel
			vc = await voice_channel.connect(timeout=2**32)
			playing[guild.id] = datetime.now()

			t = threading.Thread(target=play, args=(guild, vc))
			t.start()

			return 0
		else:
			return 3

	else:
		return 1

class MyBot(commands.Bot):
	def __init__(self):
		intents = discord.Intents.default()
		intents.message_content = True

		super().__init__(
			command_prefix = "$",
			owner_ids = OWNERS,
			help_command = None,
			intents = intents,
			activity = discord.Activity(type=discord.ActivityType.listening, name="Free Bird"),
			application_id = APPLICATION_ID
		)

	async def setup_hook(self):
		await self.tree.sync()
		self.tree.copy_global_to(guild=TEST_GUILD)

bot = MyBot()

@bot.event
async def on_ready():
	for guild in bot.guilds:
		playing[guild.id] = None
	print(f"Logged in as {bot.user.name} | {len(bot.guilds)} servers")

	if AUTO_JOIN_USER:
		for guild in bot.guilds:
			error = await join_voice_channel(guild, AUTO_JOIN_USER)
			if error == 0:
				break

@bot.tree.command(description="Begin the free bird loop")
async def begin(ctx: discord.Interaction):
	error = await join_voice_channel(ctx.guild, ctx.user.id)

	match error:
		case 0:
			await ctx.response.send_message("The free bird is here :O")
		case 1:
			await ctx.response.send_message("The free bird has nowhere to go :/")
		case 2:
			raise "Member not found"
		case 3:
			await ctx.response.send_message("Free bird is already in another channel, run `$stop` to move it")

@bot.tree.command(description="Stop the free bird loop")
async def stop(ctx: commands.Context):
	time_playing = get_playing_seconds(ctx.guild)
	playing[ctx.guild.id] = None

	for vc in bot.voice_clients:
		if vc.guild.id == ctx.guild.id:
			await vc.disconnect()

			return await ctx.response.send_message(f"The free bird is gone :( Final time stat: {time_playing}s")

	await ctx.response.send_message("No free bird found in this server >:O")

@bot.tree.command(description="Show how long the bot has been running for")
async def stats(ctx: commands.Context):
	await ctx.response.send_message(f"The bird has been free for {get_playing_seconds(ctx.guild)} seconds")

@bot.tree.command(description="Displays the bot's latency")
async def ping(ctx: commands.Context):
	await ctx.response.send_message(f"{round(bot.latency*1000, -2)}ms")

if __name__ == "__main__":
	bot.run(TOKEN, reconnect=True)