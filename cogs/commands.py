import logging
import os
import sqlite3

import discord
from discord.ext import commands

from modbot import DB_PATH

logger = logging.getLogger("modbot-errors")

class Commands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

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

	def mod_check(self, user):
    if user.id == int(os.getenv('USER_ID')):
        return True
    for role in user.roles:
        if not role:
            continue
        if role.name.lower() in ('mods', 'moderators'):
            return True
    return False

	@discord.commands.application_command(
		name = "pings",
		description = "Add a role ping to monitoring"
	)
	@discord.commands.option(name = "ping", description = "Messages will be monitored for pinging this role")
	async def pings(self, ctx: discord.ApplicationContext, ping: discord.SlashCommandOptionType.role):
		await ctx.defer(ephemeral = True)
		if not mod_check(ctx.user):
			await ctx.respond("Only moderators may use this command.")
			return
		monitored_pings = self.get_monitored_pings(ctx.guild)
		if monitored_pings:
			monitored_pings = [x[0] for x in monitored_pings]
		if monitored_pings and ping.id in monitored_pings:
			await ctx.respond(f"Pinging the role <@&{ping.id}> is already being monitored.")
			return
		with sqlite3.connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute("INSERT INTO pings (guild_id, role_id) VALUES (?, ?)", (ctx.guild.id, ping.id))
			conn.commit()
		await ctx.respond(f"Pinging the role <@&{ping.id}> will now be monitored.")


	@discord.commands.application_command(
		name = "roles",
		description = "Add a user role to monitoring"
	)
	@discord.commands.option(name = "role", description = "Users with this role will be monitored")
	async def roles(self, ctx: discord.ApplicationContext, role: discord.SlashCommandOptionType.role):
		await ctx.defer(ephemeral = True)
		if not mod_check(ctx.user):
			await ctx.respond("Only moderators may use this command.")
			return
		monitored_roles = self.get_monitored_roles(ctx.guild)
		if monitored_roles:
			monitored_roles = [x[0] for x in monitored_roles]
		if monitored_roles and role.id in monitored_roles:
			await ctx.respond(f"Users with the role <@&{role.id}> are already being monitored.")
			return
		with sqlite3.connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute("INSERT INTO roles (guild_id, role_id) VALUES (?, ?)", (ctx.guild.id, role.id))
			conn.commit()
		await ctx.respond(f"Users with the role <@&{role.id}> will now be monitored.")

	@discord.commands.application_command(
		name = "rules",
		description = "Check current monitoring rules for this server"
	)
	async def rules(self, ctx:discord.ApplicationContext):
		await ctx.defer(ephemeral = True)
		if not mod_check(ctx.user):
			await ctx.respond("Only moderators may use this command.")
			return
		monitored_pings = self.get_monitored_pings(ctx.guild)
		monitored_roles = self.get_monitored_roles(ctx.guild)
		if not monitored_roles and not monitored_pings:
			await ctx.respond(f"There are no monitoring rules in this server.")
			return
		response = "**Monitoring rules:**\n*Pings:*"
		if monitored_pings:
			for ping in monitored_pings:
				response += f"\n<@&{ping[0]}>"
		else:
			response += "\nNone"
		response += "\n\n*Roles:*"
		if monitored_roles:
			for role in monitored_roles:
				response += f"\n<@&{role[0]}>"
		else:
			response += "\nAll"
		await ctx.respond(response)

	@discord.commands.application_command(
		name = "logs",
		description = "Setup a log channel for the bot's ban actions"
	)
	@discord.commands.option(name = "channel", description = "Channel to send log messages in (make sure the bot's role has access)")
	async def logs(self, ctx:discord.ApplicationContext, channel: discord.SlashCommandOptionType.channel):
		await ctx.defer(ephemeral = True)
		if not mod_check(ctx.user):
			await ctx.respond("Only moderators may use this command.")
			return
		with sqlite3.connect(DB_PATH) as conn:
			cur = conn.cursor()
			try:
				cur.execute("INSERT INTO settings (guild_id, log_channel) VALUES (?, ?)", (ctx.guild.id, channel.id))
			except sqlite3.IntegrityError:
				cur.execute("UPDATE settings SET log_channel = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
			conn.commit()
		try:
			await channel.send(f"<@{self.bot.user.id}> will now log actions in this channel.")
			await ctx.respond(f"<@{self.bot.user.id}> will now log actions in <#{channel.id}>.")
		except:
			await ctx.respond(f"<@{self.bot.user.id}> does not have access to <#{channel.id}>.")

	@discord.commands.application_command(
		name = "clear",
		description = "Clear all monitoring rules"
	)
	async def logs(self, ctx:discord.ApplicationContext):
		await ctx.defer(ephemeral = True)
		if not mod_check(ctx.user):
			await ctx.respond("Only moderators may use this command.")
			return
		with sqlite3.connect(DB_PATH) as conn:
			cur = conn.cursor()
			cur.execute("DELETE FROM pings WHERE guild_id = ?", (ctx.guild.id, ))
			cur.execute("DELETE FROM roles WHERE guild_id = ?", (ctx.guild.id, ))
			conn.commit()
		await ctx.respond("All rules have been cleared.")

def setup(bot):
	bot.add_cog(Commands(bot))
