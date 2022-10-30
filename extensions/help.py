import itertools

import hikari
import lightbulb

help_plugin = lightbulb.Plugin("Help")


@help_plugin.command
@lightbulb.command("help", "Get help with the bot.", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def help_cmd(ctx: lightbulb.Context) -> None:
    slash = ctx.bot.slash_commands
    cmds_to_plugin = itertools.groupby(
        slash.values(), key=lambda c: c.plugin.name if c.plugin else "No Plugin"
    )
    help_text: dict[str, list[str]] = {}

    gather_help(help_text, cmds_to_plugin)

    embed = hikari.Embed(description="`<>` are required, `[]` are optional")

    for plugin, cmds in help_text.items():
        embed.add_field(
            plugin,
            "\n".join(cmds),
            inline=True,
        )

    await ctx.respond(embed)


def gather_help(
    help_text: dict[str, list[str]], cmds_to_plugin: itertools.groupby
) -> None:
    for plugin, slash_cmds in cmds_to_plugin:
        for cmd in slash_cmds:
            if isinstance(cmd, lightbulb.SlashCommandGroup):
                instance = list(cmd.instances.values())[0]

                for sub_cmd in cmd.subcommands.values():
                    if isinstance(sub_cmd, lightbulb.SlashSubCommand):
                        opt_help = format_option_help(sub_cmd)
                        cmd_help = (
                            f"</{cmd.name} {sub_cmd.name}:{instance.id}> {opt_help}"
                        )
                        if plugin not in help_text:
                            help_text[plugin] = [cmd_help]
                        else:
                            help_text[plugin].append(cmd_help)

            elif isinstance(cmd, lightbulb.SlashCommand):
                opt_help = format_option_help(cmd)
                instance = list(cmd.instances.values())[0]
                cmd_help = f"</{cmd.name}:{instance.id}> {opt_help}"

                if plugin not in help_text:
                    help_text[plugin] = [cmd_help]
                else:
                    help_text[plugin].append(cmd_help)


def format_option_help(cmd: lightbulb.SlashCommand) -> str:
    return " ".join(
        f"`<{opt.name}>`" if opt.required else f"`[{opt.name}]`"
        for opt in cmd.options.values()
    )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(help_plugin)
