from discord.ext import commands
from discord import utils
import discord

class emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def getemote(self, arg):
        emoji = utils.get(self.bot.emojis, name=arg.strip(":"))
        if emoji is not None:
            add = "a" if emoji.animated else ""
            return f"<{add}:{emoji.name}:{emoji.id}>"
        return None

    async def getinstr(self, content):
        if ":" not in content:
            return content

        ret = []
        spc = content.split(" ")

        for item in spc:
            if item.count(":") <= 1:
                ret.append(item)
                continue

            if item.startswith("<") and item.endswith(">"):
                ret.append(item)
                continue

            current = ""
            count = 0
            for char in item:
                if char != ":":
                    current += char
                else:
                    if not current or count == 1:
                        current += " : "
                        count += 1
                    else:
                        ret.append(current.strip())
                        current = ":"
                        count = 1
            ret.append(current.strip())

        return ret

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or ":" not in message.content:
            return

        msg = await self.getinstr(message.content)
        ret = ""
        em = False

        for word in msg:
            if word.startswith(":") and word.endswith(":") and len(word) > 1:
                emoji = await self.getemote(word)
                if emoji:
                    em = True
                    ret += f" {emoji}"
                else:
                    ret += f" {word}"
            else:
                ret += f" {word}"

        if em:
            webhook = utils.get(await message.channel.webhooks(), name="Canopus")
            if webhook is None:
                webhook = await message.channel.create_webhook(name="Canopus")
            
            await webhook.send(
                ret.strip(), 
                username=message.author.display_name, 
                avatar_url=message.author.display_avatar.url
            )
            await message.delete()

async def setup(bot):
    await bot.add_cog(emoji(bot))