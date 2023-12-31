import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import json

client = commands.Bot(command_prefix="?", intents=discord.Intents.all())
client.remove_command( 'help' )

@client.event
async def on_guild_join(guild):
    with open("mute_id.json", "r") as f:
            muteid = json.load(f)
    role = await guild.create_role(name="mute", colour=discord.Colour.red())
    muteid[str(guild.id)] = role.id
    with open("mute_id.json", "w") as f:
        json.dump(muteid, f, indent=4)

@client.event
async def on_ready():
    activity = discord.Game(name=f"?help - список команд", type=3)
    await client.change_presence(activity=activity, status=discord.Status.idle)
    print("BOT IS READY")

@client.command(aliases = ['info','Info'])
async def __info(ctx):
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(title=f"{ctx.guild.name} Информация", description="Информация об этом сервере", color=discord.Colour.blue())
    embed.add_field(name='🆔Сервер ID', value=f"{ctx.guild.id}", inline=True)
    embed.add_field(name='📆Создан', value=ctx.guild.created_at.strftime("%d.%m.%Y"), inline=False)
    embed.add_field(name='👑Владелец', value=f"{ctx.guild.owner.mention}", inline=True)
    embed.add_field(name='👥Участников', value=f'**:heavy_minus_sign: {ctx.guild.member_count}**', inline=False)
    embed.add_field(name='💬Каналы', value=f'{len(ctx.guild.text_channels)} Текстовых | {len(ctx.guild.voice_channels)} Голосовых', inline=True)
    embed.set_thumbnail(url=ctx.guild.icon)
    embed.set_footer(text="⭐ • Bot prefix: ?")
    embed.set_author(name=f'{ctx.author.name}', icon_url=ctx.message.author.avatar)
    await ctx.send(embed=embed, delete_after=15)

@client.command(aliases = ['help'])
async def __help(ctx):
    await ctx.channel.purge(limit=1)
    admin_role = ctx.author.guild.get_role(1123014212667584574)
    if admin_role in ctx.author.roles:
        admin = discord.Embed(title="Список команд для админов", color=discord.Color.dark_red())
        admin.add_field(
            name="Mute",
            value="Замутить игрока\nПример: `?mute [игрок] [время в минутах] [причина]`\n\n**Ban**\nЗабанить игрока\nПример: `?ban [игрок] [время в минутах] [причина]`"
        )
        admin.add_field(
            name="Unmute",
            value="Размутить игрока\nПример: `?unmute [игрок]`\n\n**Kick**\nВыгнать игрока\nПример: `?kick [игрок] [причина]`"
        )
        await ctx.send(embed=admin, delete_after=10)
    else:
        user = discord.Embed(title="Список команд для админов", color=discord.Color.dark_green())
        user.add_field(
            name="Navigation",
            value="Открыть навигацию\nПример: `?navigation`\n\n**Say**\nОтправить сообщение игроку\nПример: `?say [игрок] [сообщение]`"
        )
        user.add_field(
            name="Report",
            value="Отправить жалобу на игрока\nПример: `?report [игрок] [причина]`\n\n**Info**\nУзнать инфу о боте\nПример: `?info`"
        )
        await ctx.send(embed=user, delete_after=10)

@client.command(aliases = ['clear'])
@commands.is_owner()
async def __clear(ctx, amount: int = None):
    if amount is None:
        await ctx.channel.purge(limit=1)
        emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, укажите кол-во слов для очистки")
        await ctx.send(embed=emb, delete_after=5)
    else:
        await ctx.channel.purge(limit=amount+1)
        await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), description=f':white_check_mark: Удалено **{amount}** сообщений(я)'),
                       delete_after=5)


@client.command(aliases = ['mute', 'Mute'])
async def __mute(ctx, member: discord.Member = None, time: int = None, *, reason="причина не указана"):
    await ctx.channel.purge(limit=1)
    with open("mute_id.json", "r") as f:
        muteid = json.load(f)
    mutid = muteid[str(ctx.guild.id)]
    role = member.guild.get_role(mutid)
    if ctx.author.guild.get_role(1123014212667584574) in ctx.author.roles:
        if member is None:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, укажите игрока, которого хотите замутить!")
            await ctx.send(embed=emb, delete_after=5)
        elif time is None:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, укажите время мута")
            await ctx.send(embed=emb, delete_after=5)
        elif member.name is ctx.author.name:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, вы не можете замутить самого себя")
            await ctx.send(embed=emb, delete_after=5)
        else:
            if not role in member.roles:
                await member.add_roles(role)
                emb = discord.Embed(title="Система", color=discord.Color.green(),
                            description=f"**{ctx.author.mention}**, замутил **{member.mention}** на **{time} мин** по причине: **{reason}**")
                await ctx.send(embed=emb, delete_after=5)
                mem = discord.Embed(title="Система", color=discord.Color.green(),
                            description=f"**{ctx.author.mention}**, замутил **вас** на **{time} мин** по причине: **{reason}**")
                await member.send(embed=mem, delete_after=5)
                await asyncio.sleep(time*60)
                await member.remove_roles(role)
                mem = discord.Embed(title="Система", color=discord.Color.green(),
                            description=f"Время мута окончено!!")
                await member.send(embed=mem, delete_after=5)
            else:
                emb = discord.Embed(title="Система", color=discord.Color.red(),
                                    description=f"**{ctx.author.mention}**, игрок уже в муте")
                await ctx.send(embed=emb, delete_after=5)
    else:
        emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, у вас нет прав на эту команду")
        await ctx.send(embed=emb, delete_after=5)

@client.command(aliases = ['unmute', 'Unmute'])
async def __unmute(ctx, member: discord.Member = None):
    await ctx.channel.purge(limit=1)
    with open("mute_id.json", "r") as f:
        muteid = json.load(f)
    mutid = muteid[str(ctx.guild.id)]
    role = member.guild.get_role(mutid)
    if ctx.author.guild.get_role(1123014212667584574) in ctx.author.roles:
        if member is None:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                                description=f"**{ctx.author.mention}**, укажите игрока, которого хотите размутить!")
            await ctx.send(embed=emb, delete_after=5)
        elif member.name is ctx.author.name:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, вы не можете размутить самого себя")
            await ctx.send(embed=emb, delete_after=5)
        else:
            if role in member.roles:
                await member.remove_roles(role)
                emb = discord.Embed(title="Система", color=discord.Color.green(),
                                description=f"**{ctx.author.mention}**, размутил **{member.mention}**")
                await ctx.send(embed=emb, delete_after=5)
                mem = discord.Embed(title="Система", color=discord.Color.green(),
                                description=f"**{ctx.author.mention}**, размутил **вас**")
                await member.send(embed=mem, delete_after=5)
            else:
                emb = discord.Embed(title="Система", color=discord.Color.red(),
                                    description=f"**{ctx.author.mention}**, игрок не в муте")
                await ctx.send(embed=emb, delete_after=5)
    else:
        emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, у вас нет прав на эту команду")
        await ctx.send(embed=emb, delete_after=5)

@client.command(aliases = ['ban', 'Ban'])
async def __ban(ctx, member: discord.Member = None, time: int = None, *, reason="причина не указана"):
    await ctx.channel.purge(limit=1)
    if ctx.author.guild.get_role(1123014212667584574) in ctx.author.roles:
        if member is None:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                                description=f"**{ctx.author.mention}**, укажите игрока, которого хотите забанить!")
            await ctx.send(embed=emb, delete_after=5)
        elif time is None:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                                description=f"**{ctx.author.mention}**, укажите время бана")
            await ctx.send(embed=emb, delete_after=5)
        elif member.name is ctx.author.name:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                                description=f"**{ctx.author.mention}**, вы не можете забанить самого себя")
            await ctx.send(embed=emb, delete_after=5)
        else:
            await member.ban(reason=reason)
            emb = discord.Embed(title="Система", color=discord.Color.green(),
                                    description=f"**{ctx.author.mention}**, забанил **{member.mention}** на **{time} мин** по причине: **{reason}**")
            await ctx.send(embed=emb, delete_after=5)
            mem = discord.Embed(title="Система", color=discord.Color.green(),
                                    description=f"**{ctx.author.mention}**, забанил **вас** на **{time} мин** по причине: **{reason}**")
            await member.send(embed=mem, delete_after=5)
            await asyncio.sleep(time * 60)
            await member.unban()
            mem = discord.Embed(title="Система", color=discord.Color.green(),
                                    description=f"Время бана окончено!!")
            await member.send(embed=mem, delete_after=5)
    else:
        emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, у вас нет прав на эту команду")
        await ctx.send(embed=emb, delete_after=5)

@client.command(aliases = ['kick', 'Kick'])
async def __kick(ctx, member: discord.Member = None, *, reason="причина не указана"):
    await ctx.channel.purge(limit=1)
    if ctx.author.guild.get_role(1123014212667584574) in ctx.author.roles:
        if member is None:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                                description=f"**{ctx.author.mention}**, укажите игрока, которого хотите выгнать!")
            await ctx.send(embed=emb, delete_after=5)
        elif member.name is ctx.author.name:
            emb = discord.Embed(title="Система", color=discord.Color.red(),
                                description=f"**{ctx.author.mention}**, вы не можете выгнать самого себя")
            await ctx.send(embed=emb, delete_after=5)
        else:
            await member.kick(reason=reason)
            emb = discord.Embed(title="Система", color=discord.Color.green(),
                                    description=f"**{ctx.author.mention}**, выгнал **{member.mention}** по причине: **{reason}**")
            await ctx.send(embed=emb, delete_after=5)
            mem = discord.Embed(title="Система", color=discord.Color.green(),
                                    description=f"**{ctx.author.mention}**, выгнал **вас** по причине: **{reason}**")
            await member.send(embed=mem, delete_after=5)
    else:
        emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, у вас нет прав на эту команду")
        await ctx.send(embed=emb, delete_after=5)

@client.command(aliases = ['report', 'Report'])
async def __report(ctx, member: discord.Member = None, *, reason="причина не указана"):
    await ctx.channel.purge(limit=1)
    if member is None:
        emb = discord.Embed(title="Система", color=discord.Color.red(),
                            description=f"**{ctx.author.mention}**, укажите игрока, на которого хотите отправить жалобу!")
        await ctx.send(embed=emb, delete_after=5)
    else:
        group = client.get_channel(1123641302353977395)
        now_time = datetime.now().strftime('%d.%m.%Y')
        emb = discord.Embed(title="Репорт", color=discord.Color.red())
        emb.add_field(name="Отправитель:", value=f":heavy_minus_sign: {ctx.author.mention}")
        emb.add_field(name="Нарушитель:", value=f":heavy_minus_sign: {member.mention}")
        emb.add_field(name="Причина:", value=f":heavy_minus_sign: {reason}", inline=False)
        emb.set_thumbnail(url=member.avatar)
        emb.set_footer(text=f"Дата: {now_time}")
        await group.send(embed=emb)
        mem = discord.Embed(title="Система", color=discord.Color.green(),
                            description=f"**{ctx.author.mention}**, жалоба успешно отправлена!")
        await ctx.send(embed=mem, delete_after=5)

@client.command(aliases = ['navigation', 'Navigation'])
async def __navigation(ctx):
    pass

if __name__ == '__main__':
    client.run('MTEyMzAwNjk5NTU2NjQyODM3Mw.GbaWF_.VTAFAvlq1mVP2iOrumhm9W98IqE0IndB0CDBRI')


