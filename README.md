# anti-spambot-bot
Discord bot for banning role-pinging spam bots.

# setup
After adding the bot to the server (which can be done with [this link](https://discord.com/oauth2/authorize?client_id=1524067132176990228), use /roles to add a role to monitoring (this is usually a "new user" role), then /pings to add a ping to monitoring. Any users that use one of the monitored pings while having one of the monitored roles will be banned by the bot.

You can check the existing rules at any time with /rules. All existing rules can be cleared with /clear.

Optionally, you can set the bot to log all ban actions to a channel with /log (make sure the bot has access to that channel).

All commands are locked behind users having a role that matches 'mods' or 'moderators'. The check is not case sensitive, so roles with the name 'Mods' or 'Moderators' will also grant access.

# images
<img width="309" height="182" alt="image" src="https://github.com/user-attachments/assets/2c840cde-45fc-4bd8-ad1f-6ee1db7b2da0" />

# to-do
~~Mod lock all commands.~~

~~Add command to clear rules.~~
