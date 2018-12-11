import discord
import asyncio
import os
from discord.ext import commands

Client = discord.Client()
client = commands.Bot(command_prefix="/")

#logs on the discord bot
@client.event
async def on_ready():
	print('I am active')
	await client.change_presence(game=discord.Game(type=3, name='over Raven\'s Nest'))
	
#welcome message
@client.listen()
async def on_member_join(member):
	server = member.server
	count = 0
	for x in server.members:
		count += 1
	welcome_channel = discord.Object(id='484145723198406691')
	w = discord.Embed(description=':inbox_tray: **{}** has `joined` the Raven\'s nest!\n({})'.format(member, member.id), color=discord.Colour.purple())
	w.set_footer(text='User Joined | {} members'.format(count), icon_url=member.avatar_url)
	await client.send_message(welcome_channel, embed=w)
	
#leave message
@client.listen()
async def on_member_remove(member):
	server = member.server
	count = 0
	welcome_channel = discord.Object(id='484145723198406691')
	for x in server.members:
		count += 1
	leave = discord.Embed(description=':outbox_tray: **{}** has `left` the Raven\'s nest.'.format(member), color=discord.Colour.red())
	leave.set_footer(text='User Left | {} members'.format(count), icon_url=member.avatar_url)
	await client.send_message(welcome_channel, embed=leave)

#on message edit
@client.listen()
async def on_message_edit(b, a):
	if b.author == client.user or a.author == client.user:
		return
	logs = discord.Object(id='485951166715396096')
	embed = discord.Embed(color=discord.Colour.orange())
	embed.set_author(name='Message Edit | {}'.format(b.author), icon_url=b.author.avatar_url)
	embed.set_thumbnail(url=b.author.avatar_url)
	embed.add_field(name='Before', value=b.content, inline=False)
	embed.add_field(name='After', value=a.content, inline=False)
	await client.send_message(logs, embed=embed)

#fetches member count
@client.listen()
async def on_message(message):
	count = 0
	channel = client.get_channel('483866400553828354')
	for members in message.author.server.members:
		count += 1
	await client.edit_channel(channel=channel, name='lobby-{}-members'.format(count))

#lol reaction
@client.listen()
async def on_message(cat):
	if cat.content.lower() == "lol":
		await client.add_reaction(cat, emoji="😂")
		
#kick command
@client.command(pass_context=True)
async def kick(ctx, user: discord.Member, *, reason=None):
	author = ctx.message.author
	required_role = [role.name for role in author.roles]
	logs = discord.Object(id='485951166715396096')
	user_role = [role.name for role in user.roles]
	if "Admin" in required_role or "Owner" in required_role:
		if "Admin" in user_role or "Owner" in user_role:
			await client.say('Uhh.. I can\'t ban users that are moderators.')
		else:
			await client.delete_message(ctx.message)
			embed = discord.Embed(description='**{}** was `kicked`.\n({})\n\nModerator: {}\n**Reason**: {}'.format(user, user.id, author.mention, reason), color=discord.Colour.red())
			embed.set_footer(text='User Kicked', icon_url=user.avatar_url)
			if not user.bot:
				await client.send_message(logs, embed=embed)
				await client.send_message(user, 'You were `kicked` from the Raven\'s Nest by: **{}**\n**Reason**: {}'.format(author, reason))
				await client.kick(user)
			else:
				await client.send_message(logs, embed=embed)
				await client.kick(user)
	else:
		await client.say('Hey, {}! You cannot use that command.'.format(author.mention))
		
#clear command
@client.command(pass_context=True)
async def clear(ctx, amount: int):
	required_role = [role.name for role in ctx.message.author.roles]
	logs = client.get_channel('485951166715396096')
	if "Admin" in required_role or "Owner" in required_role:
		await client.purge_from(ctx.message.channel, limit=int(amount + 1))
	else:
		await client.say('Hey, {}! Looks like you cannot use that command.'.format(ctx.message.author.mention))

#announce command
@client.command(pass_context=True)
async def announce(ctx, channel: discord.Channel, t=None, *, d):
	coadmin = [role.name for role in ctx.message.author.roles]
	if "Co-Owner" in coadmin or "Owner" in coadmin:
		await client.delete_message(ctx.message)
		a = discord.Embed(title=t, description=d, color=discord.Colour.gold())
		a.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
		await client.send_message(channel, embed=a)
		
class Modmail:
	def __init__(self, server, user, admin, msg):
		self.server = server
		self.user = user
		self.admin = admin
		self.msg = msg
		
	async def createChannel(self):
		name = self.user.name
		n = name.split(' ')
		nj = '-'.join(n)
		lowerN = nj.lower()
		server = client.get_server(self.server)
		c = discord.utils.get(server.channels, name=lowerN)
		perms = discord.PermissionOverwrite
		cp = discord.ChannelPermissions
		everyone_perms = perms(read_messages=False)
		admin_perms = perms(read_messages=True)
		everyone = cp(target=server.default_role, overwrite=everyone_perms)
		admin = cp(target=self.admin, overwrite=admin_perms)
		
		if not c in server.channels:
			channel = await client.create_channel(server, self.user.name, everyone, admin)
			await client.edit_channel(channel, topic = self.user.id)
			embed = discord.Embed(title="New Mail", description=self.msg.content, color=discord.Color.gold())
			embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
			embed.set_footer(text="ID: {}".format(self.user.id))
			embed.timestamp = self.msg.timestamp
			if self.msg.attachments:
				embed.set_image(url=self.msg.attachments[0]['url'])
				
			await client.send_message(self.user, "**Thank you for your message! Our staff team will reply to you here as soon as possible**.")
			await client.send_message(channel, embed=embed)
		else:
			await Modmail.receiveMsg(self)
			
	
	async def receiveMsg(self):
		name = self.user.name
		n = name.split(' ')
		nj = '-'.join(n)
		lowerN = nj.lower()
		server = client.get_server(self.server)
		c = discord.utils.get(server.channels, name=lowerN)
		embed = discord.Embed(description=self.msg.content, color=discord.Color.blue())
		embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
		embed.set_footer(text="ID: {}".format(self.user.id))
		embed.timestamp = self.msg.timestamp
		if self.msg.attachments:
			embed.set_image(url=self.msg.attachments[0]['url'])
		if c in server.channels:
			await client.send_message(c, embed=embed)
		
@client.listen()
async def on_message(msg):
	if not msg.author.bot and msg.channel.is_private:
		server = client.get_server("483866400553828352")
		admin = discord.utils.get(server.roles, name="Admin")
		alpha = Modmail("483866400553828352", msg.author, admin, msg)
		await alpha.createChannel()
		

@client.command(pass_context=True)
async def reply(ctx, *, msg):
	embed = discord.Embed(description=msg, color=discord.Color.blue())
	embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
	if ctx.message.attachments:
		embed.set_image(url=ctx.message.attachments[0]['url'])
		
	u = ctx.message.channel.topic
	user = discord.utils.get(ctx.message.server.members, id=u)
	await client.send_message(user, embed=embed)
		
		
@client.command(pass_context=True)
async def close(ctx):
	u = ctx.message.channel.topic
	user = discord.utils.get(ctx.message.server.members, id=u)
	await client.send_message(user, "**This thread has been closed. If you need additional help, feel free to ask.**")
	await client.delete_channel(ctx.message.channel)
	
	
client.run(os.getenv('TOKEN'))