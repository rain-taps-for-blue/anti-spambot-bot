import os
import logging
import traceback
from datetime import datetime, timezone

import discord #this is py-cord[speed]
from dotenv import load_dotenv #this is python-dotenv

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()

bot = discord.Bot(intents=intents)
BOT_START_TIME = datetime.now(timezone.utc)
DB_PATH = "data/modbot.db"

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("modbot-errors")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(
  "logs/log.log",
  encoding="utf-8",
  mode='a'
)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
  "%(asctime)s UTC\n"
  "Guild: %(guild)s\n"
  "User: %(user)s\n"
  "Command: %(command)s\n"
  "Action:\n%(message)s\n"
  "────────────────────────────────────────────\n"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

@bot.event
async def on_ready():
  current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
  print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
  print(f"Timestamp: {current_time}")
  print(f"Servers  : {len(bot.guilds)}")
  print(f"Latency  : {round(bot.latency * 1000)} ms")
  print("Initialization complete")
  print(f"Standing by as {bot.user}")
  print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

@bot.event
async def on_application_command_error(
  ctx: discord.ApplicationContext,
  error: Exception
):
  # Ignore harmless errors
  if isinstance(error, (discord.Forbidden, discord.NotFound)):
    return
  timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
  guild_name = ctx.guild.name if ctx.guild else "DM"
  guild_id = ctx.guild.id if ctx.guild else "N/A"
  # Minimal terminal output
  print(f"[{timestamp}] ERROR in Guild: {guild_name} ({guild_id})")
  # Full traceback
  tb = "".join(
    traceback.format_exception(type(error), error, error.__traceback__)
  )
  logger.error(
    tb,
    extra={
      "guild": f"{guild_name} ({guild_id})",
      "user": f"{ctx.author} ({ctx.author.id})",
      "command": ctx.command.name if ctx.command else "Unknown"
    }
  )
  # Safe user-facing message
  try:
    await ctx.respond(
      "❌ An unexpected error occurred while executing this command.\n"
      "The issue has been logged and will be reviewed.",
      ephemeral=True
    )
  except discord.InteractionResponded:
    pass

###make new rule command
###make view rules command

for file in os.listdir("./cogs"):
  if file.endswith(".py") and not file.startswith("_"):
    bot.load_extension(f"cogs.{file[:-3]}")

bot.run(os.getenv('TOKEN'))