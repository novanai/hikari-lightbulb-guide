import hikari
import lightbulb

mod_plugin = lightbulb.Plugin("Mod")


@mod_plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)  # 1 use every 5 seconds per user
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES),
    lightbulb.bot_has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES),
)
@lightbulb.option(
    "messages", "The number of messages to purge.", type=int, required=True
)
@lightbulb.command("purge", "Purge messages.", aliases=["clear"])
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def purge_messages(ctx: lightbulb.Context) -> None:
    num_msgs = ctx.options.messages
    channel = ctx.channel_id

    # If the command was invoked using the PrefixCommand, it will create a message
    # before we purge the messages, so we want to delete this message first
    if isinstance(ctx, lightbulb.PrefixContext):
        await ctx.event.message.delete()

    msgs = await ctx.bot.rest.fetch_messages(channel).limit(num_msgs)
    await ctx.bot.rest.delete_messages(channel, msgs)

    await ctx.respond(f"{len(msgs)} messages deleted", delete_after=5)


@purge_messages.set_error_handler
async def on_purge_error(event: lightbulb.CommandErrorEvent) -> bool:
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.MissingRequiredPermission):
        await event.context.respond("You do not have permission to use this command.")
        return True

    elif isinstance(exception, lightbulb.BotMissingRequiredPermission):
        await event.context.respond("I do not have permission to delete messages.")
        return True

    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(
            f"This command is on cooldown! You can use it again in {int(exception.retry_after)} seconds."
        )
        return True

    return False


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(mod_plugin)
