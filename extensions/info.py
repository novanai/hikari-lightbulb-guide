from datetime import datetime
from typing import Optional

import hikari
import lightbulb

info_plugin = lightbulb.Plugin("Info")


@info_plugin.command
@lightbulb.option(
    "user", "The user to get information about.", hikari.User, required=False
)
@lightbulb.command("userinfo", "Get info on a server member.", pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def userinfo(ctx: lightbulb.Context, user: Optional[hikari.User] = None) -> None:
    if not (guild := ctx.get_guild()):
        await ctx.respond("This command may only be used in servers.")
        return

    user = user or ctx.author
    user = ctx.bot.cache.get_member(guild, user)

    if not user:
        await ctx.respond("That user is not in the server.")
        return

    created_at = int(user.created_at.timestamp())
    joined_at = int(user.joined_at.timestamp())

    roles = (await user.fetch_roles())[1:]  # All but @everyone
    roles = sorted(
        roles, key=lambda role: role.position, reverse=True
    )  # sort them by position, then reverse the order to go from top role down

    embed = (
        hikari.Embed(
            title=f"User Info - {user.display_name}",
            description=f"ID: `{user.id}`",
            colour=0x3B9DFF,
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.author.username}",
            icon=ctx.author.display_avatar_url,
        )
        .set_thumbnail(user.avatar_url)
        .add_field(
            "Bot?",
            "Yes" if user.is_bot else "No",
            inline=True,
        )
        .add_field(
            "Created account on",
            f"<t:{created_at}:d>\n(<t:{created_at}:R>)",
            inline=True,
        )
        .add_field(
            "Joined server on",
            f"<t:{joined_at}:d>\n(<t:{joined_at}:R>)",
            inline=True,
        )
        .add_field(
            "Roles",
            ", ".join(r.mention for r in roles),
            inline=False,
        )
    )

    await ctx.respond(embed)


@info_plugin.command
@lightbulb.command("serverinfo", "Get info on the server.")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def serverinfo(ctx: lightbulb.Context) -> None:
    if not (guild := ctx.get_guild()) or not (guild_id := ctx.guild_id):
        await ctx.respond("This command may only be used in servers.")
        return

    created_at = int(guild.created_at.timestamp())
    owner = await guild.fetch_owner()

    mem_cache = ctx.bot.cache.get_members_view_for_guild(guild_id)

    members = await mem_cache.iterator().count()
    humans = await mem_cache.iterator().filter(lambda user: not user.is_bot).count()
    bots = await mem_cache.iterator().filter(lambda user: user.is_bot).count()

    chan_cache = ctx.bot.cache.get_guild_channels_view_for_guild(guild_id)

    channels = (
        await chan_cache.iterator()
        .filter(lambda chan: not isinstance(chan, hikari.GuildCategory))
        .count()
    )
    text = (
        await chan_cache.iterator()
        .filter(lambda chan: isinstance(chan, hikari.GuildTextChannel))
        .count()
    )
    voice = (
        await chan_cache.iterator()
        .filter(
            lambda chan: isinstance(
                chan, (hikari.GuildVoiceChannel, hikari.GuildStageChannel)
            )
        )
        .count()
    )

    embed = (
        hikari.Embed(
            title=f"Server Info - {guild.name}",
            description=f"ID: `{guild.id}`",
            colour=0x3B9DFF,
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.author.username}",
            icon=ctx.author.display_avatar_url,
        )
        .set_thumbnail(guild.icon_url)
        .set_image(guild.banner_url)
        .add_field(
            "Created on",
            f"<t:{created_at}:d>\n(<t:{created_at}:R>)",
            inline=True,
        )
        .add_field(
            "Member count",
            f"Total: {members}\nHumans: {humans}\nBots: {bots}",
            inline=True,
        )
        .add_field(
            "Channels",
            f"Total: {channels}\nText: {text}\nVoice: {voice}",
            inline=True,
        )
        .add_field(
            "Owner",
            f"{owner}\nID: `{owner.id}`",
            inline=False,
        )
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(info_plugin)
