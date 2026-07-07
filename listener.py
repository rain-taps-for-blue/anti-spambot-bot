import logging
import os
import sqlite3

import discord
from discord.ext import commands

from modbot import DB_PATH

logger = logging.getLogger("modbot-errors")

class Listener(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.init_db()

	def init_db(self):
		os.makedirs("data", exist_ok=True)
		with sqlite3.connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute("""
				CREATE TABLE IF NOT EXISTS settings (
					guild_id INTEGER PRIMARY KEY,
					log_channel INTEGER
					)
				""")
			cur.execute("""
				CREATE TABLE IF NOT EXISTS pings (
					guild_id INTEGER,
					role_id INTEGER
					)
				""")
			cur.execute("""
				CREATE TABLE IF NOT EXISTS roles (
					guild_id INTEGER,
					role_id INTEGER
					)
				""")
			conn.commit()

	def get_monitored_pings(self, guild: discord.Guild):
		with sqlite3.connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute(
				"SELECT role_id FROM pings WHERE guild_id = ?",
				(guild.id,)
			)
			row = cur.fetchall()

		if row and row[0]:
			return row
		return None

	def get_monitored_roles(self, guild: discord.Guild):
		with sqlite3.connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute(
				"SELECT role_id FROM roles WHERE guild_id = ?",
				(guild.id,)
			)
			row = cur.fetchall()

		if row and row[0]:
			return row
		return None

	def get_log_channel(self, guild: discord.Guild):
		with sqlite3.connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute(
				"SELECT log_channel FROM settings WHERE guild_id = ?",
				(guild.id,)
			)
			row = cur.fetchone()

		if row and row[0]:
			return guild.get_channel(row[0])
		return None

	async def send_log(self, guild: discord.Guild, embed: discord.Embed):
		channel = self.get_log_channel(guild)
		if channel:
			await channel.send(embed=embed)

	@commands.Cog.listener()
	async def on_message(self, message):
		#message checks
		if message.author == self.bot.user:
			return
		if not message.role_mentions:
			return

		monitored_pings = self.get_monitored_pings(message.guild)
		if monitored_pings:
			monitored_pings = [x[0] for x in monitored_pings]
		mentioned_roles = [x.id for x in message.role_mentions]
		if monitored_pings and set(monitored_pings).isdisjoint(mentioned_roles):
			return
		
		monitored_roles = self.get_monitored_roles(message.guild)
		if monitored_roles:
			monitored_roles = [x[0] for x in monitored_roles]
		author_roles = [x.id for x in message.author.roles]
		if monitored_roles and set(monitored_roles).isdisjoint(author_roles):
			return

		await message.guild.ban(message.author, delete_message_seconds = 300, reason = 'Banned by modbot')

		#bot log
		logger.info('Banned user', extra = {
			"guild": f"{message.guild.name if message.guild else 'DM'} ({message.guild.id if message.guild else 'N/A'})",
			"user": f"{message.author} ({message.author.id})",
			"command": "None"})
		
		#guild log
		embed = discord.Embed(title = 'Banned User')
		embed.add_field(name = 'User', value = f'{message.author.display_name} - <@{message.author.id}>')
		reason = 'Pinged:'
		for item in set(monitored_pings).intersection(mentioned_roles):
			reason += f" <@&{item}>"
		if monitored_roles and set(monitored_roles).intersection(author_roles):
			reason += f'\nWith role:'
			for item in set(monitored_roles).intersection(author_roles):
				reason += f" <@&{item}>"
		embed.add_field(name = 'Reason', value = reason)
		await self.send_log(guild = message.guild, embed = embed)

def setup(bot):
	bot.add_cog(Listener(bot))