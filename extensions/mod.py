import datetime

import hikari
import lightbulb

mod_plugin = lightbulb.Plugin("Mod")


@mod_plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)  # 1 use every 5 seconds per user
@lightbulb.app_command_permissions(hikari.Permissions.MANAGE_MESSAGES, dm_enabled=False)
@lightbulb.add_checks(
    lightbulb.bot_has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES),
)
@lightbulb.option(
    "sent_by",
    "Only purge messages sent by this user.",
    type=hikari.User,
    required=False,
)
@lightbulb.option(
    "messages",
    "The number of messages to purge.",
    type=int,
    required=True,
    min_value=2,
    max_value=200,
)
@lightbulb.command("purge", "Purge messages.", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def purge_messages(ctx: lightbulb.SlashContext) -> None:
    num_msgs = ctx.options.messages
    sent_by = ctx.options.sent_by
    channel = ctx.channel_id

    bulk_delete_limit = datetime.datetime.now(
        datetime.timezone.utc
    ) - datetime.timedelta(days=14)

    iterator = (
        ctx.bot.rest.fetch_messages(channel)
        .take_while(lambda msg: msg.created_at > bulk_delete_limit)
        .filter(lambda msg: not (msg.flags & hikari.MessageFlag.LOADING))
    )
    if sent_by:
        iterator = iterator.filter(lambda msg: msg.author.id == sent_by.id)

    iterator = iterator.limit(num_msgs)

    count = 0

    async for messages in iterator.chunk(100):
        count += len(messages)
        await ctx.bot.rest.delete_messages(channel, messages)

    await ctx.respond(f"{count} messages deleted.", delete_after=5)


@purge_messages.set_error_handler
async def on_purge_error(event: lightbulb.CommandErrorEvent) -> bool:
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.BotMissingRequiredPermission):
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
