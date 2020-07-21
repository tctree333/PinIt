import os

import discord
from discord.ext import commands

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
                await ctx.send("**Pinning the message failed.** Are there more than 50 pinned messages already?")

    @bot.event
    async def on_reaction_remove(reaction, user):
        if reaction.emoji == "\N{PUSHPIN}" and reaction.count < 3:
            try:
                await reaction.message.unpin()
            except discord.HTTPException:
                await ctx.send("**Unpinning the message failed.**")

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

    # Actually run the bot
    token = os.environ["DISCORD_BOT_TOKEN"]
    bot.run(token)
