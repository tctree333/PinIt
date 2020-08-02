import os
from typing import Union

import aiohttp
import discord
import emoji as emoji_
from discord.ext import commands

TWEMOJI_CDN_URL = "https://twemoji.maxcdn.com/v/latest/72x72/{}.png"

if __name__ == "__main__":
    bot = commands.Bot(
        command_prefix=["p!"],
        case_insensitive=True,
        description="PinIt - Pin messages just by reacting!",
    )

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
    async def on_reaction_add(reaction, user):
        if reaction.emoji == "\N{PUSHPIN}" and reaction.count >= 3:
            try:
                await reaction.message.pin()
            except discord.HTTPException:
                await ctx.send(
                    "**Pinning the message failed.** Are there more than 50 pinned messages already?"
                )

    @bot.event
    async def on_reaction_remove(reaction, user):
        if reaction.emoji == "\N{PUSHPIN}" and reaction.count <= 1:
            try:
                await reaction.message.unpin()
            except discord.HTTPException:
                await ctx.send("**Unpinning the message failed.**")

    @bot.command(help="React multiple times with the same emoji!", aliases=["r"])
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
            url = TWEMOJI_CDN_URL.format("-".join([f"{ord(char):x}" for char in emoji]))
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    emoji_content = await resp.read()
            emoji_name = emoji_.demojize(emoji).replace(":", "").replace("-", "_")
        print("emoji_name:", emoji_name)
        for i in range(num):
            print(f"reacting {i} of {num}")
            new_emoji = await ctx.guild.create_custom_emoji(
                name=emoji_name, image=emoji_content
            )
            print("created emoji")
            await message.add_reaction(new_emoji)
            print("adding reaction")
            await new_emoji.delete()
            print("deleted emoji")
        await ctx.message.add_reaction("\N{THUMBS UP SIGN}")

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
