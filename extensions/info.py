import datetime

import hikari
import lightbulb

info_plugin = lightbulb.Plugin("Info")


@info_plugin.command
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    "member", "The member to get information about.", hikari.Member, required=False
)
@lightbulb.command("memberinfo", "Get info on a server member.", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def memberinfo(ctx: lightbulb.SlashContext, member: hikari.InteractionMember | hikari.User | None) -> None:
    assert ctx.guild_id is not None and ctx.member is not None

    member = member or ctx.member
    
    if not isinstance(member, hikari.Member):
        await ctx.respond("That member is not in this server.")
        return

    created_at = int(member.created_at.timestamp())
    joined_at = int(member.joined_at.timestamp())

    roles = [f"<@&{role}>" for role in member.role_ids if role != ctx.guild_id]

    embed = (
        hikari.Embed(
            title=f"Member Info - {member}",
            description=f"ID: `{member.id}`",
            colour=0x3B9DFF,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        .set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )
        .set_thumbnail(member.display_avatar_url)
        .add_field(
            "Bot?",
            "Yes" if member.is_bot else "No",
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
            ", ".join(roles) if roles else "No roles",
            inline=False,
        )
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(info_plugin)
