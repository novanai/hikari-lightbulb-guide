import asyncio

import hikari
import lightbulb
import miru

fun_plugin = lightbulb.Plugin("Fun")


@fun_plugin.command
@lightbulb.command("fun", "All the entertainment commands you'll ever need!")
@lightbulb.implements(lightbulb.PrefixCommandGroup, lightbulb.SlashCommandGroup)
async def fun_group(ctx: lightbulb.Context) -> None:
    pass  # as slash commands cannot have their top-level command ran, we simply pass here


@fun_group.child
@lightbulb.command("meme", "Get a meme!")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def meme_subcommand(ctx: lightbulb.Context) -> None:
    async with ctx.bot.d.aio_session.get(
        "https://meme-api.herokuapp.com/gimme"
    ) as response:
        res = await response.json()
        if response.ok and res["nsfw"] != True:
            link = res["postLink"]
            title = res["title"]
            img_url = res["url"]

            embed = hikari.Embed(colour=0x3B9DFF)
            embed.set_author(name=title, url=link)
            embed.set_image(img_url)

            await ctx.respond(embed)

        else:
            await ctx.respond(
                "Could not fetch a meme :c", flags=hikari.MessageFlag.EPHEMERAL
            )


ANIMALS = {
    "Dog": "🐶",
    "Cat": "🐱",
    "Panda": "🐼",
    "Fox": "🦊",
    "Red Panda": "🐼",
    "Koala": "🐨",
    "Bird": "🐦",
    "Racoon": "🦝",
    "Kangaroo": "🦘",
}


@fun_group.child
@lightbulb.command("animal", "Get a fact + picture of a cute animal :3")
@lightbulb.implements(lightbulb.PrefixSubCommand, lightbulb.SlashSubCommand)
async def animal_subcommand(ctx: lightbulb.Context) -> None:
    select_menu = (
        ctx.bot.rest.build_action_row()
        .add_select_menu("animal_select")
        .set_placeholder("Pick an animal")
    )

    for name, emoji in ANIMALS.items():
        select_menu.add_option(
            name,  # the label, which users see
            name.lower().replace(" ", "_"),  # the value, which is used by us later
        ).set_emoji(emoji).add_to_menu()

    resp = await ctx.respond(
        "Pick an animal from the dropdown :3",
        component=select_menu.add_to_container(),
    )
    msg = await resp.message()

    try:
        event = await ctx.bot.wait_for(
            hikari.InteractionCreateEvent,
            timeout=60,
            predicate=lambda e: isinstance(e.interaction, hikari.ComponentInteraction)
            and e.interaction.user.id == ctx.author.id
            and e.interaction.message.id == msg.id
            and e.interaction.component_type == hikari.ComponentType.SELECT_MENU,
        )
    except asyncio.TimeoutError:
        await msg.edit("The menu timed out :c", components=[])
    else:
        animal = event.interaction.values[0]
        async with ctx.bot.d.aio_session.get(
            f"https://some-random-api.ml/animal/{animal}"
        ) as res:
            if res.ok:
                res = await res.json()
                embed = hikari.Embed(description=res["fact"], colour=0x3B9DFF)
                embed.set_image(res["image"])

                animal = animal.replace("_", " ")

                await msg.edit(
                    f"Here's a {animal} for you! :3", embed=embed, components=[]
                )
            else:
                await msg.edit(f"API returned a {res.status} status :c", components=[])


class AnimalView(miru.View):
    def __init__(self, author: hikari.User) -> None:
        self.author = author
        super().__init__(timeout=60)

    @miru.select(
        custom_id="animal_select",
        placeholder="Pick an animal",
        options=[
            miru.SelectOption("Dog", "dog", emoji="🐶"),
            miru.SelectOption("Cat", "cat", emoji="🐱"),
            miru.SelectOption("Panda", "panda", emoji="🐼"),
            miru.SelectOption("Fox", "fox", emoji="🦊"),
            miru.SelectOption("Red Panda", "red_panda", emoji="🐼"),
            miru.SelectOption("Koala", "koala", emoji="🐨"),
            miru.SelectOption("Bird", "bird", emoji="🐦"),
            miru.SelectOption("Racoon", "racoon", emoji="🦝"),
            miru.SelectOption("Kangaroo", "kangaroo", emoji="🦘"),
        ],
    )
    async def select_menu(self, select: miru.Select, ctx: miru.Context) -> None:
        animal = select.values[0]
        async with ctx.app.d.aio_session.get(
            f"https://some-random-api.ml/animal/{animal}"
        ) as res:
            if res.ok:
                res = await res.json()
                embed = hikari.Embed(description=res["fact"], colour=0x3B9DFF)
                embed.set_image(res["image"])

                animal = animal.replace("_", " ")

                await ctx.edit_response(
                    f"Here's a {animal} for you! :3", embed=embed, components=[]
                )
            else:
                await ctx.edit_response(
                    f"API returned a {res.status} status :c", components=[]
                )

    async def on_timeout(self) -> None:
        await self.message.edit("The menu timed out :c", components=[])

    async def view_check(self, ctx: miru.Context) -> bool:
        return ctx.user.id == self.author.id


@fun_group.child
@lightbulb.command("animal2", "Get a fact + picture of a cute animal :3")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashSubCommand)
async def animal_subcommand_2(ctx: lightbulb.Context) -> None:
    view = AnimalView(ctx.author)
    resp = await ctx.respond(
        "Pick an animal from the dropdown :3", components=view.build()
    )
    msg = await resp.message()

    view.start(msg)
    await view.wait()


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(fun_plugin)
