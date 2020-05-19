from collections import defaultdict

from discord import Embed, TextChannel, Colour
from discord.ext.commands import Cog, Context, command

from bot import constants
from bot.bot import Bot

from bot.cogs.moderation.modlog import ModLog
import textwrap


prefix = constants.Bot.prefix


class Chat(Cog):
    """
    A cog which allows user to send messages using the bot
    """

    def __init__(self, bot: Bot):
        self.bot = bot
        self.embed_mode = defaultdict(bool)
        self.embed = {}

    @property
    def mod_log(self) -> ModLog:
        """Get currently loaded ModLog cog instance."""
        return self.bot.get_cog("ModLog")

    # region: embed mode

    @command(alias=["embed", "embedcreate"])
    async def embedbuild(self, ctx: Context) -> None:
        """Enter embed creation mode"""
        if not self.embed_mode[ctx.author]:
            await ctx.send(f"{ctx.author.mention} You are now in embed creation mode, use `{prefix}help Embed` for more info")
            self.embed_mode[ctx.author] = True
            self.embed[ctx.author] = Embed()
        else:
            await ctx.send(f":x: {ctx.author.mention} You are already in embed creation mode, use `{prefix}help Embed` for more info")

    @command()
    async def embedquit(self, ctx: Context) -> None:
        """Leave embed creation mode"""
        if self.embed_mode[ctx.author]:
            await ctx.send(f"{ctx.author.mention} You are no longer in embed creation mode, your embed was cleared")
            self.embed_mode[ctx.author] = False
            del self.embed[ctx.author]
        else:
            await ctx.send(f":x: {ctx.author.mention} You aren't in embed mode")

    @command()
    async def embedshow(self, ctx: Context) -> None:
        """Take a look at the embed"""
        embed = self.get_embed(ctx)

        if not embed:
            return

        await ctx.send(embed=embed)

    @command()
    async def embedsend(self, ctx: Context, channel: TextChannel) -> None:
        """Send the Embed to specified channel"""
        embed = self.get_embed(ctx)

        if not embed:
            return

        channel_perms = channel.permissions_for(ctx.author)
        if channel_perms.send_messages:
            embed_msg = await channel.send(embed=embed)

            await self.mod_log.send_log_message(
                icon_url=constants.Icons.message_edit,
                colour=Colour.blurple(),
                title="Embed message sent",
                thumbnail=ctx.author.avatar_url_as(static_format="png"),
                text=textwrap.dedent(f"""
                    Actor: {ctx.author.mention} (`{ctx.author.id}`)
                    Channel: {channel.mention}
                    Message jump link: {embed_msg.jump_url}
                """),
            )
            await ctx.send(":white_check_mark: Embed sent")

    # endregion
    # region: embed build
    # endregion

    async def get_embed(self, ctx):
        try:
            embed = self.embed[ctx.author]
        except KeyError:
            await ctx.send(f":x: {ctx.author.mention} No active embed found, are you in embed building mode? (`{prefix}help Embed`)")
            return False
        return embed


def setup(bot: Bot) -> None:
    '''Load the Chat cog.'''
    bot.add_cog(Chat(bot))
