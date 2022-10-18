import datetime as dt
import os
from typing import Union, List

import aiohttp
import discord
import emoji as emoji_
import pytz
from discord.ext import commands

from cache import cache

TWEMOJI_CDN_URL = "https://twemoji.maxcdn.com/v/latest/72x72/{}.png"

STARBOARD_CHANNEL_ID = 692594515638222935
STARBOARD_GUILD_ID = 692593519302279229

if __name__ == "__main__":
    # Initialize bot
    intent: discord.Intents = discord.Intents.none()
    intent.guilds = True
    intent.messages = True
    intent.message_content = True
    intent.emojis = True
    intent.reactions = True

    bot = commands.Bot(
        command_prefix=["p!"],
        case_insensitive=True,
        description="PinIt - Pin messages just by reacting!",
        intents=intent,
    )

    starred_messages = set()

    @bot.event
    async def on_ready():
        print("Ready!")
        print("Logged in as:")
        print(bot.user.name)
        print(bot.user.id)
        # Change discord activity
        await bot.change_presence(
            activity=discord.Activity(type=3, name="your every move")
        )

    @bot.event
    async def on_reaction_add(reaction: discord.Reaction, user):
        if reaction.emoji == "\N{PUSHPIN}" and reaction.count >= 3:
            try:
                await reaction.message.pin()
            except discord.HTTPException:
                await reaction.message.channel.send(
                    "**Pinning the message failed.** Are there more than 50 pinned messages already?"
                )
        elif (
            reaction.emoji == "\N{WHITE MEDIUM STAR}"
            and reaction.count >= 3
            and reaction.message.id not in starred_messages
            and reaction.message.guild.id == STARBOARD_GUILD_ID
        ):
            starred_messages.add(reaction.message.id)

            channel = bot.get_channel(STARBOARD_CHANNEL_ID)

            embed: discord.Embed = discord.Embed(
                type="rich",
                description=reaction.message.content,
                color=discord.Color.gold(),
            )
            embed.add_field(
                name="Original Message:",
                value=f"By {reaction.message.author.mention}\n\n[Jump to message!]({reaction.message.jump_url})",
            )
            embed.set_author(
                name=str(reaction.message.author),
                icon_url=str(reaction.message.author.avatar_url),
            )

            pacific = pytz.timezone("US/Pacific")
            message_date = pytz.utc.localize(reaction.message.created_at).astimezone(
                pacific
            )
            embed.set_footer(
                text=message_date.strftime("%a. %b. %d, %Y at %I:%M:%S %p %Z")
            )
            await channel.send(embed=embed)

    @bot.event
    async def on_reaction_remove(reaction, user):
        if reaction.emoji == "\N{PUSHPIN}" and reaction.count <= 1:
            try:
                await reaction.message.unpin()
            except discord.HTTPException:
                await reaction.message.channel.send("**Unpinning the message failed.**")

    @bot.command(help="- React multiple times with the same emoji!", aliases=["r"])
    @commands.guild_only()
    async def react(
        ctx, num: int, emoji: Union[discord.PartialEmoji, str], message: discord.Message
    ):
        print("command: react")
        if num > 10 or num < 1:
            print("invalid num")
            await ctx.send(
                "**The number of reactions is invalid!**\n*Please use a number between 1 and 10 inclusive.*"
            )
            return
        if isinstance(emoji, discord.PartialEmoji) and emoji.is_custom_emoji():
            print("custom emoji")
            emoji_content: bytes = await emoji.url.read()
            emoji_name = emoji.name if emoji.name else "PinItCustomEmote"
        if isinstance(emoji, str):
            print("unicode emoji")
            emoji_content = await get_emoji(emoji)
            emoji_name = (
                emoji_.demojize(emoji, language="alias")
                .replace(":", "")
                .replace("-", "_")
            )
        print("emoji_name:", emoji_name)
        print("len emoji_content:", len(emoji_content))

        for i in range(num):
            print(f"reacting {i+1} of {num}")
            new_emoji = await ctx.guild.create_custom_emoji(
                name=emoji_name, image=emoji_content
            )
            print("created emoji")
            await message.add_reaction(new_emoji)
            print("adding reaction")
            await new_emoji.delete()
            print("deleted emoji")
        await ctx.message.add_reaction("\N{THUMBS UP SIGN}")

    @bot.command(help="- React with words!", aliases=["m"])
    @commands.guild_only()
    async def message(ctx, string: str, message: discord.Message):
        print("command: message")
        if len(string) < 1 or len(string) > 10:
            print("invalid num")
            await ctx.send(
                "**The string is invalid!**\n*Please use a word between 1 and 10 letters inclusive.*"
            )
            return
        print("string:", string)
        for letter in string:
            letter = letter.lower()[0]
            print("letter: ", letter)

            emoji_name = chr(ord(letter) - 97 + 127462)
            emoji_content = await get_emoji(emoji_name)
            print("len emoji_content:", len(emoji_content))
            new_emoji = await ctx.guild.create_custom_emoji(
                name=f"letter_{letter}", image=emoji_content
            )
            print("created emoji")
            await message.add_reaction(new_emoji)
            print("adding reaction")
            await new_emoji.delete()
            print("deleted emoji")
        await ctx.message.add_reaction("\N{THUMBS UP SIGN}")

    @bot.command(help="- React with an emoji sequence!", aliases=["s"])
    @commands.guild_only()
    async def sequence(
        ctx, *sequence: Union[discord.Message, discord.PartialEmoji, str]
    ):
        print("command: sequence")
        if not isinstance(sequence[-1], discord.Message):
            print("no message")
            await ctx.send(
                "**Invalid message!** Please ensure the last argument is the message to react to!"
            )
            return
        message = sequence[-1]
        sequence = sequence[:-1]
        if len(sequence) < 1 or len(sequence) > 10:
            print("invalid num")
            await ctx.send(
                "**The sequence is invalid!**\n*Please enter between 1 and 10 emojis inclusive.*"
            )
            return
        print("sequence:", sequence)
        for emoji in sequence:
            print("emoji: ", emoji)
            if isinstance(emoji, discord.PartialEmoji) and emoji.is_custom_emoji():
                print("custom emoji")
                emoji_content: bytes = await emoji.url.read()
                emoji_name = emoji.name if emoji.name else "PinItCustomEmote"
            if isinstance(emoji, str):
                print("unicode emoji")
                emoji_content = await get_emoji(emoji)
                emoji_name = (
                    emoji_.demojize(emoji, language="alias")
                    .replace(":", "")
                    .replace("-", "_")
                )
            print("emoji_name:", emoji_name)
            print("len emoji_content:", len(emoji_content))
            new_emoji = await ctx.guild.create_custom_emoji(
                name=emoji_name, image=emoji_content
            )
            print("created emoji")
            await message.add_reaction(new_emoji)
            print("adding reaction")
            await new_emoji.delete()
            print("deleted emoji")
        await ctx.message.add_reaction("\N{THUMBS UP SIGN}")

    @cache()
    async def get_emoji(emoji: str) -> bytes:
        if int("0x200d", base=16) not in map(ord, emoji):
            emoji = emoji.replace("\ufe0f", "")
        url = TWEMOJI_CDN_URL.format("-".join([f"{ord(char):x}" for char in emoji]))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                emoji_content = await resp.read()
        return emoji_content

    # Send command - for testing purposes only
    @bot.command(help="- send command", hidden=True, aliases=["sendas"])
    @commands.is_owner()
    async def send_as_bot(ctx, *, args):
        channel_id = int(args.split(" ")[0])
        message = args.strip(str(channel_id))
        channel = bot.get_channel(channel_id)
        await channel.send(message)
        await ctx.send("Ok, sent!")

    ## Error handling
    @bot.event
    async def on_command_error(ctx, error):
        """Handles errors for all commands without local error handlers."""
        print("Error: " + str(error))

        if isinstance(error, commands.CommandOnCooldown):  # send cooldown
            await ctx.send(
                "**Cooldown.** Try again after "
                + str(round(error.retry_after))
                + " s.",
                delete_after=5.0,
            )

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("Sorry, the command was not found.")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("This command requires an argument!")

        elif isinstance(error, commands.BadArgument):
            await ctx.send("The argument passed was invalid. Please try again.")

        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send("An invalid character was detected. Please try again.")

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("**This command is unavaliable in DMs!**")

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                "**The bot does not have enough permissions to fully function.**\n"
                + f"**Permissions Missing:** `{', '.join(map(str, error.missing_perms))}`\n"
                + "*Please try again once the correct permissions are set.*"
            )

        elif isinstance(error, discord.Forbidden):
            await ctx.send(
                "**The bot does not have enough permissions to fully function.**\n"
                + "*Please try again once the correct permissions are set.*"
            )

        elif isinstance(error, discord.NotFound):
            await ctx.send("**The message was not found or deleted.**\n")

        else:
            await ctx.send(
                "**An uncaught error has occurred.**\n" + "**Error:** " + str(error)
            )
            raise error

    # Actually run the bot
    token = os.environ["DISCORD_BOT_TOKEN"]
    bot.run(token)
