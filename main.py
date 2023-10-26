import nextcord
import logging  
import config
import redis
import os
import sys
import json
import pprint
import traceback
import mysql.connector
import re
import time
#from pretty_help import PrettyHelp
from nextcord.ext import commands
from nextcord.ext import application_checks


intents = nextcord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True



## dictionary for donator - REPLACE THIS SOON SKY I BEG
time_units = {
    's': 1,   # seconds
    'm': 60,  # minutes
    'h': 3600,  # hours
    'd': 86400,  # days
    'w': 604800,  # weeks
    'mo': 2592000,  # months (approximately 30 days)
    'y': 31536000,  # years (approximately 365 days)
}

time_pattern = re.compile(r'(\d+)([smhdwMoy]+)')

## import config
token = config.token

DB_CONFIG = {
    'host': config.db_host,
    'user': config.db_user,
    'password': config.db_pass,
    'database': config.db_name,  # Use the specific database name 'nekosu'
}

# Connect to the MySQL database
db_connection = mysql.connector.connect(**DB_CONFIG)
db_cursor = db_connection.cursor()

## redis connection here
r = redis.Redis(host='localhost', port=6379, decode_responses=True)


## logging
logger = logging.getLogger('nextcord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


## other shit the bot needs
bot = commands.Bot(command_prefix=config.prefix, intents=intents)


## py eval shit
with open("whitelist.json", "r") as file:
    whitelist_json = json.load(file)

whitelisted_users = whitelist_json["whitelist"]
py_namespace = globals() | {mod: __import__(mod) for mod in sys.modules}


@bot.event
async def on_ready():
    await bot.change_presence(
        status=nextcord.Status.dnd,  # You can use online, idle, dnd, or offline
        activity=nextcord.Game("on nksu.gg"),  # You can change this to any text or activity you want
    )
    print(f'Authorisation successful\nLogged in as {bot.user}')

        # Get the channel by its ID
    bot_channel_id = 1131373831639023778  # Replace with your desired channel ID
    channel = bot.get_channel(bot_channel_id)

    embed = nextcord.Embed(title=f"NKSUTILS is now online!", description=f"Legacy prefix: !\nSlash commands supported\nFor any enquiries, message <@413283368164261899>", color=0xad1457)
    embed.set_author(name="Nekosu!", url="https://nksu.gg", icon_url="https://a.nksu.gg/999")

    if channel is not None:
        # Send a message to the specified channel
        await channel.send(embed=embed)

## welcome message 
@bot.event
async def on_member_join(member):
    # Create an embed for the welcome message
    embed = nextcord.Embed(title=f"Welcome to the server, {member.display_name}!", description="We're glad to have you here on our server. Please make sure you read the rules before participating! ", color=0xad1457)
    embed.set_author(name="Nekosu!", url="https://nksu.gg", icon_url="https://a.nksu.gg/999")

    avatar_url = member.avatar or member.avatar.url
    embed.set_thumbnail(url=avatar_url)

    # Specify the channel where you want to send the welcome message
    welcome_channel = bot.get_channel(config.welcome_channel)  # Replace with your channel ID

    if welcome_channel is not None:
        await welcome_channel.send(embed=embed)



@bot.slash_command(description="About the server.")
async def about(ctx):

    embed = nextcord.Embed(title="About Nekosu!", description="Nekosu is an osu! private server project run by Sky and her team for the community. We are dedicated to providing a fun, safe and fully free environment for all players to enjoy. We are not affiliated with osu! or ppy in any way.", color=0xad1457)
    embed.set_author(name="Nekosu!", url="https://nksu.gg", icon_url="https://a.nksu.gg/999")
    await ctx.send(embed=embed)

@bot.slash_command(description="In game commands")
async def osuhelp(ctx):

    embed = nextcord.Embed(title="Nekosu! in game commands", description="You can view all ingame commands to use on our server [here](https://nksu.gg/nekobot)", color=0xad1457)
    embed.set_author(name="Nekosu!", url="https://nksu.gg", icon_url="https://a.nksu.gg/999")
    await ctx.send(embed=embed)

@bot.slash_command(description="Connection Guide")
async def connection(ctx):

    embed = nextcord.Embed(title="Nekosu! Connection Guide", description="You can view our connection guide [here](https://www.youtube.com/watch?v=kp2UK6mK2LQ)", color=0xad1457)
    embed.set_author(name="Nekosu!", url="https://nksu.gg", icon_url="https://a.nksu.gg/999")
    await ctx.send(embed=embed)

@bot.slash_command(description="Nekosu! Statistics")
async def stats(ctx):

    total = r.get('ripple:registered_users')
    online = r.get('ripple:online_users')
    total_members = ctx.guild.member_count
    online_members = len([member for member in ctx.guild.members if member.status != nextcord.Status.offline])

    embed = nextcord.Embed(title="Nekosu! statistics", description=f"**osu! Server**\nTotal: {total}\nOnline: {online}\n**Discord Server**\nTotal: {total_members}\nOnline: {online_members}", color=0xad1457)
    embed.set_author(name="Nekosu!", url="https://nksu.gg", icon_url="https://a.nksu.gg/999")
    await ctx.send(embed=embed)

@bot.slash_command(description="The Nekosu liveplay terms.")
async def liveplay(ctx):

    image_url = 'liveplay.png'

    with open('liveplay.txt', 'r') as file:
        text = file.read()

    embed = nextcord.Embed(title="Nekosu! statistics", description=f"{text}", color=0xad1457)
    embed.set_author(name="Nekosu!", url="https://nksu.gg", icon_url="https://a.nksu.gg/999")
    await ctx.send(embed=embed)
    await ctx.send(file=nextcord.File(image_url))

## ADMIN COMMANDS
@bot.slash_command(description="Send an announcement embed to announcements")
@application_checks.has_any_role(config.admin)
async def announce(ctx, *, message):
    embed = nextcord.Embed(title="Announcement", description=message, color=0xad1457)
    embed.set_author(name="Nekosu!", url="https://nksu.gg", icon_url="https://a.nksu.gg/999")
    await bot.get_channel(config.announcements_channel).send(embed=embed)
    await ctx.send("Announcement sent!",ephemeral=True)


## restriction and unrestriction commands
@bot.slash_command(
    name='restrict',
    description='Restrict a user via their user ID'
)
@application_checks.has_any_role(config.admin)
async def restrict(ctx, user_id: int, ban_reason: str):
    """Update the 'privileges' column for a user in the 'nekosu.users' table."""
    try:
        # Execute the specific SQL query to update the 'privileges' column
        update_query = f"UPDATE `nekosu`.`users` SET `privileges` = '2', `ban_reason` = '{ban_reason}' WHERE (`id` = '{user_id}')"
        db_cursor.execute(update_query)
        db_connection.commit()

        # Log the action in the 'rap_logs' table with an auto-incremented ID
        log_query = "INSERT INTO `nekosu`.`rap_logs` (`userid`, `text`, `datetime`, `through`) VALUES (%s, %s, UNIX_TIMESTAMP(), 'NKSUTILS')"
        log_values = (1241, f'has restricted userid {user_id} with reason: {ban_reason}')
        db_cursor.execute(log_query, log_values)
        db_connection.commit()

        await ctx.send(f'Successfully updated privileges for user with ID {user_id}')
    except Exception as e:
        await ctx.send(f'An error occurred while updating privileges in the database: {str(e)}',ephemeral=True)

@bot.slash_command(
    name='unrestrict',
    description='Unrestrict a user via their user ID'
)
@application_checks.has_any_role(config.admin)
async def unrestrict(ctx, user_id: int, ban_reason: str):
    """Update the 'privileges' column for a user in the 'nekosu.users' table."""
    try:
        # Execute the specific SQL query to update the 'privileges' column
        update_query = f"UPDATE `nekosu`.`users` SET `privileges` = '3', `ban_reason` = '{ban_reason}' WHERE (`id` = '{user_id}')"
        db_cursor.execute(update_query)
        db_connection.commit()

        # Log the action in the 'rap_logs' table with an auto-incremented ID
        log_query = "INSERT INTO `nekosu`.`rap_logs` (`userid`, `text`, `datetime`, `through`) VALUES (%s, %s, UNIX_TIMESTAMP(), 'NKSUTILS')"
        log_values = (1241, f'has unrestricted userid {user_id} with reason {ban_reason}')
        db_cursor.execute(log_query, log_values)
        db_connection.commit()

        await ctx.send(f'Successfully updated privileges for user with ID {user_id}')
    except Exception as e:
        await ctx.send(f'An error occurred while updating privileges in the database: {str(e)}',ephemeral=True)

@bot.slash_command(
    name='username',
    description='Change a user\'s username via their user ID'
)
@application_checks.has_any_role(config.admin)
async def username(ctx, username: str, usernamesafe: str, user_id: int):
    """Update the 'username' and 'ban_reason' columns for a user in the 'nekosu.users' table."""
    try:
        # Execute the specific SQL query to update the 'username' and 'ban_reason' columns
        update_query = f"UPDATE `nekosu`.`users` SET `username` = '{username}', `ban_reason` = '{usernamesafe}' WHERE (`id` = '{user_id}')"
        db_cursor.execute(update_query)
        db_connection.commit()

        # Log the action in the 'rap_logs' table with an auto-incremented ID
        log_query = "INSERT INTO `nekosu`.`rap_logs` (`userid`, `text`, `datetime`, `through`) VALUES (%s, %s, UNIX_TIMESTAMP(), 'NKSUTILS')"
        log_values = (1241, f'has changed the username of {username} ({user_id})')
        db_cursor.execute(log_query, log_values)
        db_connection.commit()

        await ctx.send(f'Successfully updated username for user with ID {user_id}')
    except Exception as e:
        await ctx.send(f'An error occurred while updating username in the database: {str(e)}',ephemeral=True)

@bot.slash_command(
    name='badge',
    description='Enable badges for a user via their user ID'
)
@application_checks.has_any_role(config.admin)
async def badge(ctx, user_id: int, enabled: bool):
    """Enable custom badge for a user via their user ID"""
    try:
        # Fetch the current value of `can_custom_badge` from the 'users_stats' table
        fetch_query = f"SELECT `can_custom_badge` FROM `nekosu`.`users_stats` WHERE `id` = '{user_id}';"
        db_cursor.execute(fetch_query)
        current_can_custom_badge = db_cursor.fetchone()[0]

        # Determine the new value of `can_custom_badge` based on the 'enabled' parameter
        new_can_custom_badge = 1 if enabled else 0

        # Update the 'can_custom_badge' column in the 'users_stats' table
        update_query = f"UPDATE `nekosu`.`users_stats` SET `can_custom_badge` = '{new_can_custom_badge}', `show_custom_badge` = '{new_can_custom_badge}' WHERE (`id` = '{user_id}');"
        db_cursor.execute(update_query)
        db_connection.commit()

        # Log the action in the 'rap_logs' table with an auto-incremented ID
        log_query = "INSERT INTO `nekosu`.`rap_logs` (`userid`, `text`, `datetime`, `through`) VALUES (%s, %s, UNIX_TIMESTAMP(), 'NKSUTILS')"
        log_values = (1241, f'has {"enabled" if enabled else "disabled"} custom badge for userid ({user_id})')
        db_cursor.execute(log_query, log_values)
        db_connection.commit()

        await ctx.send(f'Successfully {"enabled" if enabled else "disabled"} custom badge for user with ID {user_id}')
    except Exception as e:
        await ctx.send(f'An error occurred while {"enabling" if enabled else "disabling"} custom badge in the database: {str(e)}',ephemeral=True)

@bot.slash_command(
    name='donator',
    description='Enable donator status for a user via their user ID'
)

@application_checks.has_any_role(config.admin)
async def donator(ctx, time_input: str, user_id: int):
    try:
        # Parse the user input to extract the time and unit
        match = time_pattern.match(time_input)
        if not match:
            await ctx.send('Invalid time format. Please use a valid format like "1mo" for 1 month.')
            return

        quantity, unit = match.groups()
        quantity = int(quantity)
        
        # Calculate the expiration timestamp in seconds
        if unit in time_units:
            seconds = quantity * time_units[unit]
        else:
            await ctx.send('Invalid time unit. Please use one of the following units: s, m, h, d, w, mo, y.')
            return

        # Calculate the expiration timestamp by adding 'seconds' to the current Unix timestamp
        expiration_timestamp = int(time.time()) + seconds

        # Execute the SQL query to update the 'donor_expire' column for the specified user
        update_query = f"UPDATE `nekosu`.`users` SET `donor_expire` = {expiration_timestamp}, `privileges` = `privileges` + 4 WHERE `id` = {user_id}"
        db_cursor.execute(update_query)
        db_connection.commit()

        # Log the action in the 'rap_logs' table
        log_query = "INSERT INTO `nekosu`.`rap_logs` (`userid`, `text`, `datetime`, `through`) VALUES (%s, %s, UNIX_TIMESTAMP(), 'NKSUTILS')"
        log_values = (1241, f'added donator for user with ID {user_id} until {expiration_timestamp}')
        db_cursor.execute(log_query, log_values)
        db_connection.commit()

        await ctx.send(f'Successfully added donator for user with ID {user_id} until <t:{expiration_timestamp}>')
    except Exception as e:
        await ctx.send(f'An error occurred while updating donator expiration timestamp in the database: {str(e)}',ephemeral=True)

## Discord commands or some bullshit who gives a FUCK
@bot.slash_command(
    name='ban',
    description='Ban a user from the Discord server'
)
@application_checks.has_any_role(config.admin)
async def ban(ctx, user: nextcord.Member, reason=str):
    await user.ban(reason=reason)
    await ctx.send(f'{user.name} has been banned from the server.')

@bot.slash_command(
    name='kick',
    description='Kick a user from the Discord server'
)
@application_checks.has_any_role(config.admin)
async def kick(ctx, user: nextcord.Member, reason=str):
    await user.kick(reason=reason)
    await ctx.send(f'{user.name} has been kicked from the server.')


## SKY COMMANDS
def in_whitelist():
    def predicate(ctx):
        return ctx.message.author.id in whitelisted_users
    return commands.check(predicate)

def is_sky():
    def predicate(ctx):
        return ctx.message.author.id == config.owner
    return commands.check(predicate)

@bot.command()
@is_sky()
async def whitelist(ctx):
    for mention in ctx.message.mentions:
        whitelisted_users.append(mention.id)
        with open("whitelist.json", "r+") as file:
            old_json = json.load(file)
            old_json["whitelist"].append(mention.id)
            file.seek(0)
            json.dump(old_json, file, indent=4)

    user_list = ', '.join([u.name for u in ctx.message.mentions])
    await ctx.send(f"Added {user_list} to whitelist!")

@bot.command()
@in_whitelist()
async def py(ctx):
    cmd = ctx.message.content.strip(f'{config.prefix}py\n`') # lawl
    func = '\n'.join(['async def __py():', cmd.replace('\n', '\n ')])
    py_namespace['ctx'] = ctx

    try:
        exec(func, py_namespace)
        command_output = await py_namespace['__py']()
        py_namespace.pop('__py', None)
    except Exception as e:
        await ctx.message.add_reaction('\U0000274C')
        return await ctx.send(f'Error occurred:\n```py{traceback.format_exc()}```')

    if not command_output and not isinstance(command_output, (bool, int)):
        return await ctx.message.add_reaction('\U00002705')

    if not isinstance(command_output, str):
        command_output = pprint.pformat(command_output, compact=True)

    await ctx.send(command_output)
    await ctx.message.add_reaction('\U00002705')

@bot.command()
@in_whitelist()
async def define(ctx):
    split_args = ctx.message.content.split(' ')
    var = split_args[1]
    val = ' '.join(split_args[2:])

    if var in py_namespace:
        new_val = eval(val)
        exec(f'{py_namespace[var]} = {new_val}')
    else:
        new_var = {var: eval(val)}
        exec(f'py_namespace |= {new_var}')

    await ctx.message.add_reaction('\U00002705')
    return await ctx.send(f'Definition {var} set to {val}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.message.add_reaction('\U0000274C')
        await ctx.send('You do not have permission to use this command.')
    elif isinstance(error, commands.errors.CommandNotFound):
        pass
    else:
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


if __name__ == '__main__':
    bot.run(token)
