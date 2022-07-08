import os
import discord
import disnake
from disnake import ChannelType, SelectOption
from disnake.ext import commands, tasks
import commands_config
import config
from RSS import check_rss, announce, checkToggle
import sqlite3
import pandas as pd

con = sqlite3.connect('test.db')
cur = con.cursor()

status = 'with new episodes'

discord = disnake
ccfg = commands_config
cfg = config
client = commands.Bot(command_prefix=cfg.BOT_PREFIX, test_guilds=[cfg.server_id], activity=disnake.Game(status),
                      status=discord.Status.online)



@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'you forgot this one very important part!!! do `{cfg.BOT_PREFIX}help` for more detail')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission to execute this command")


@client.event
async def on_ready():
    print(client.user.name, 'is online')
    await webtoon_loop.start()


@client.slash_command()
async def ping(ctx):
    ping = int(round(client.latency, 3) * 1000)
    embed = discord.Embed(title="Bot's Ping", description=(f"{ctx.author.display_name} the bot's ping is {ping}ms"))
    await ctx.send(embed=embed)


ping = None


# Ping command
@client.command()
async def ping(ctx):
    ping = int(round(client.latency, 3) * 1000)
    await ctx.send(f'{ctx.author.mention} {ping} ms.')
    print(config.updateList)


# Embed command
@client.command()
async def embed(ctx):
    e = discord.Embed(title=ccfg.Example_Embed_Title, description=ccfg.Example_Embed_Title,
                      color=0x5865f2)  # blurple hex code
    e.add_field(name=ccfg.Embed_Name_1, value=(ccfg.Embed_Text_1))
    e.add_field(name=ccfg.Embed_Name_2, value=(ccfg.Embed_Text_2))
    await ctx.send(e=embed)


@client.slash_command()
async def search(ctx):
    await ctx.send(discord.utils.get(ctx.guild.roles, name="Ping").mention)


@tasks.loop(seconds=180)
async def webtoon_loop():
    print('WEBTOON LOOP START')
    check_rss()
    announce()
    for tuple in config.updateList:
        """
                Get some useful (or not) information about the bot.
                """
        embed = disnake.Embed(
            # description=  "<@&ROLEID>", #Role id goes here

            color=0x9C84EF
        )
        embed.set_author(
            name=(tuple[1] + " RELEASED!")
        )
        embed.add_field(
            name="Title:",
            value=tuple[0],
            inline=True
        )
        embed.add_field(
            name="Date:",
            value=tuple[2],
            inline=True
        )
        embed.add_field(
            name="Link",
            value=(tuple[3]),
            inline=False
        )
        embed.set_footer(
            # text=

        )

        ann_channel = client.get_channel(835060643958358039)
        thr_channel = client.get_channel(835062639767978014)
        await ann_channel.send(embed=embed)

        channel = ann_channel

        await thr_channel.create_thread(
            name=tuple[1] + " DISCUSSION THREAD",
            type=ChannelType.public_thread
        )
        str = ''.join(tuple[3])
        print(str)
        checkToggle(str)


@client.event
# We create an on message event
async def on_message(message):
    # We check if the the message that has been sent equals react
    if client.user.id != message.author.id:
        if "reaction" in message.content:
            pass



@webtoon_loop.before_loop
async def before_some_task():
    await client.wait_until_ready()


# Makes the bot run
client.run(os.environ['token'])
