########################################################################################################################

# This file contains functions related to the function of the Webtoons Announcer discord bot.
# Relevant functions are described, modification of functions shouldn't be necessary.
# I'm currently publicly reworking it for general use and upgrading it to be a bit cleaner and use sqlite.
# Additionally, the bot has been upgraded to use slash commands to better align with Discord's developer direction.
# A new README is under construction as well and will be added with the setup.py file

# tselky#9999 @discord

########################################################################################################################


import os
import disnake
from disnake import ChannelType
from disnake.ext import commands, tasks
import commands_config
from RSS import *
import sqlite3

con = sqlite3.connect('test.db')
cur = con.cursor()
status = 'with new episodes'  # can set to anything you want.
discord = disnake
ccfg = commands_config
cfg = config
client = commands.Bot(command_prefix=cfg.BOT_PREFIX, test_guilds=[cfg.server_id], activity=disnake.Game(status),
                      status=discord.Status.online)
servers = []


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'you forgot this one very important part!!! do `{cfg.BOT_PREFIX}help` for more detail')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission to execute this command")


# Displays in terminal that bot is now running
@client.event
async def on_ready():
    server = retrieve_settings()
    print(client.user.name, 'is online')
    await webtoon_loop.start()


@client.slash_command()
async def series(ctx: disnake.ApplicationCommandInteraction,
                 link: str,
                 ):
    """
    Parameters
    ----------
    link: The RSS link

    """
    ...

    set_series(link, ctx.guild_id)
    await ctx.send(link)
    # await ctx.send("This series has been set!")
    # "This is not a valid link"


# Set announcement channel, uses function from RSS.py
@client.slash_command()
async def announce(ctx):
    set_announce(ctx.channel.id, ctx.guild_id)
    await ctx.send("This channel has been set as the announcement channel!")


# set thread channel, uses function from RSS.py
@client.slash_command()
async def thread(ctx):
    set_discussion(ctx.channel.id, ctx.guild_id)
    await ctx.send("This channel has been set as the discussion channel!")


# ping
@client.slash_command()
async def ping(ctx):
    ping = int(round(client.latency, 3) * 1000)
    embed = discord.Embed(title="Bot's Ping", description=(f"{ctx.author.display_name} the bot's ping is {ping}ms"))
    await ctx.send(embed=embed)


# Ping command
@client.command()
async def ping(ctx):
    ping = int(round(client.latency, 3) * 1000)
    await ctx.send(f'{ctx.author.mention} {ping} ms.')


@client.slash_command()
async def search(ctx):
    await ctx.send(discord.utils.get(ctx.guild.roles, name="Ping").mention)


# Main Webtoon loop. Runs every 3 minutes to announce and generate threads.
# Uses data and functions from RSS.py
@tasks.loop(seconds=180)
async def webtoon_loop():
    print('WEBTOON LOOP START')

    settings = retrieve_settings()
    details = rss_post()
    embed = disnake.Embed(
        # description=  "<@&ROLEID>", #Role id goes here

        color=0x9C84EF
    )
    embed.set_author(
        name=("EPISODE " + details[5] + " RELEASED!")
    )
    embed.add_field(
        name="Title:",
        value=details[0],
        inline=True
    )
    embed.add_field(
        name="Date:",
        value=details[1],
        inline=True
    )
    embed.add_field(
        name="Link",
        value=(details[2]),
        inline=False
    )
    embed.set_footer(
        # text=

    )

    ann_channel = client.get_channel(settings[2])
    thr_channel = client.get_channel(settings[3])

    # if or match
    await ann_channel.send(embed=embed)

    # if or match
    await thr_channel.create_thread(
        name="EPISODE " + details[5] + " DISCUSSION THREAD",
        type=ChannelType.public_thread
    )


@client.event
async def on_message(message):
    if client.user.id != message.author.id:
        if "reaction" in message.content:
            pass


@webtoon_loop.before_loop
async def before_some_task():
    await client.wait_until_ready()


# Makes the bot run
client.run(os.environ['token'])
