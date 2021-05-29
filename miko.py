import os
import discord
import datetime
from discord.ext import commands, timers
import requests
import json
import random
import asyncio
from decouple import config
from database import add_time, return_time

GUILD_ID = 785024897863647282
CAFE_LOUNGE_ID = 801100961313194004

intents = discord.Intents.default()
intents.members = True
intents.presences = True
emojisOn = False

client = commands.Bot(command_prefix='m.', case_insensitive=True, intents=intents)
client.remove_command("help")
client.timer_manager = timers.TimerManager(client)
GUILD = client.get_guild(GUILD_ID)
LOUNGE = client.get_channel(CAFE_LOUNGE_ID)

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('With Ashish'))
  print('Bot is Online.')

@client.command()
async def inspire(ctx):
  def get_quote():
      response = requests.get("https://zenquotes.io/api/random")
      json_data = json.loads(response.text)
      quote = json_data[0]['q'] + " -" + json_data[0]['a']
      return quote
  quote = get_quote()
  await ctx.send(quote)  


@client.command()
async def help(ctx):
  try:
    h = discord.Embed(
      title="NEED HELP?",
      description="Bot Creator: **ASHISH**\nCommands Suggestion: **SENSEI**",
      color=0xe81741,
    )
    h.add_field(
      name="__ABOUT__", 
      value=f"\nPrefix : `m.`\nMiko Chan is a Discord Bot created for people who find it hard to focus while working. She can start a focus timer for you, send you inspirational quotes, motivate you if you are sad and love you if you love her❤️.", 
      inline=False
    )
    h.add_field(
      name="__COMMANDS__",
      value=f"`start (time)` Starts the focus timer.\n`stop` Stops the focus timer.\n`total` Shows the total time you have focused.\n`inspire` Miko chan sends an inspirational quote for you.\n`padhle (user)` Just a normal study reminder for fun",
      inline=False
    )
    h.add_field(
      name="__WARNING__", value="If you are using focus timer, the time focused will be added only after you complete your focus time. Using `m.stop` will not owrk, So no cheating now, grind hard!", inline=False
    )
    h.add_field(
      name="__MISC__", value="Miko Chan also replies to you when you say `I love you miko chan` or `I hate you miko chan`", inline=False
    )

    await ctx.send(embed=h)
  except Exception as e:
    print(e)

  @client.command()
  async def source(self, ctx):
    await ctx.send("To be updated soon!")

#global variables 

user_list = []

@client.command()
async def start(ctx, time: int):
  if ctx.author.id not in user_list:
    if ctx.channel.id == CAFE_LOUNGE_ID:
      global pomodoro_timer
      pomodoro_timer = True
      global showTimer
      showTimer = False
      global specialBreakTime
      specialBreakTime = False


      t = time*60 + 1 #pomodoro time in seconds
      hour = int(time/60)
      minute = time%60

      while(t):
          mins, secs = divmod(t, 60) 
          timer = "**{:02d}:{:02d}**".format(mins, secs) 
          await asyncio.sleep(1) 
          t -= 1

          #displays time remaining
          if(showTimer):
            emb = discord.Embed(
            title="", description=f"{timer}", color=0xe81741)
            await ctx.send(embed=emb, delete_after=20) 
            showTimer = False

          #stops clock
          if(pomodoro_timer == False):
              break


          #start of clock
          if(t == time*60):
            emb = discord.Embed(
          title="", description=f"**⏱ Your focus time is set to {hour} hour and {minute} minutes ⏱\n\n😀 Good Luck! 😀**", color=0xe81741)
            await ctx.send(ctx.author.mention)
            await ctx.send(embed=emb)
            user_list.append(ctx.author.id)


          #break time
          elif(t == 0):
            emb = discord.Embed(
            title="", description=f"**⏱ Your focus time has ended ⏱\n\n😀 Take a break 😀**", color=0xe81741)
            await ctx.send(ctx.author.mention)
            await ctx.send(embed=emb)
            add_time(ctx.author.id, time)
            user_list.remove(ctx.author.id)
    else:
      return
  else:
     emb = discord.Embed(
      title="", description=f"**You are already working!.**", color=0xe81741)
     await ctx.send(ctx.author.mention)
     await ctx.send(embed=emb) 
    
    
@client.command()
async def total(ctx):
  hour, minutes = return_time(ctx.author.id)
  emb = discord.Embed(
    title="", description=f"**You have focused for {hour} hour and {minutes} minutes till now.**", color=0xe81741)
  await ctx.send(ctx.author.mention)
  await ctx.send(embed=emb)
  
@client.command()
async def stop(ctx):
  if ctx.channel.id == CAFE_LOUNGE_ID:
    if ctx.author.id in user_list:
      global pomodoro_timer 
      pomodoro_timer = False
      emb = discord.Embed(
      title="", description=f"**⚠ Your timer has been stopped! ⚠**", color=0xe81741)
      await ctx.send(ctx.author.mention)
      await ctx.send(embed=emb)
      user_list.remove(ctx.author.id)
    else:
      emb = discord.Embed(
      title="", description=f"**You are not currently working! Use m.start [time] to start a timer.**", color=0xe81741)
      await ctx.send(ctx.author.mention)
      await ctx.send(embed=emb) 
  else:
    return    

@client.command()
async def padhle(ctx, m1: discord.User = None):
  padhle_list=[
    "**Pyaar vyaar sab dhoka hai, padhle bete mauka hai..**",
    "**Padhlo beta, agar General Category se ho to**",
    "**Chacha vidhayak hai kya tumhare? Nahi he to jao padh lo**",
    "**Padhlo beta mauka he, aakhir kisne tumko roka hai?**"
  ]
  if m1 == None:
    m1 = ctx.author
  emb = discord.Embed(
      title="", description=f"{m1.mention}\n{random.choice(padhle_list)}", color=0xe81741)
  await ctx.send(embed=emb)        

@client.event
async def on_message(message):
    await client.process_commands(message)

    # Animal emoji reactions!
    reactions = ['🐮', '🐷', '🐒', '🐼', '🐥', '🦕', '🐙']
    if(emojisOn):
        #for emoji in reactions: 
        emoji = random.choice(reactions)
        await message.add_reaction(emoji)

    if message.author == client.user:
        return

    #add more quotes!
    fail_quote = [
        "Don't give up!",
        "Failure is only the opportunity to begin again more intelligently.",
        "You can always bounce back!",
        "Failure is an attitude, not an outcome."
    ]

    tired_quote = [
        "You are strong but you are exhausted.",
        "I know you are tired, but you have to keep going!",
        "The more you sweat in practice, the less you bleed in battle.",
        "WAKE UP!!"
    ]

    die_quote = [
        "You can do this!",
        "Your pet would want you alive",
        "Let's eat ice cream instead",
        "You're too hot to die >.<"
    ]
    
    if message.author.id in user_list:
      if message.content.startswith('m.') or message.content.startswith('s.') or message.content.startswith('S.'):
        return
      else:
        if message.author.id == 534384083925598218:
          await message.channel.send(f'{message.author.mention}\n**Onii Chan Baka..** If you talk during your focus time I will kill you🔪..', delete_after=15)
        else:
          await message.channel.send(f'{message.author.mention}\n**Onii Chan Baka..** If you talk during your focus time I will not love you😡..', delete_after=15)


    if 'hate you' in message.content.lower() and 'miko chan' in message.content.lower():
      if message.author.id == 784363251940458516:
        await message.channel.send(f'{message.author.mention}\nBut I will always love you onii chan..❤️', delete_after=10)
      elif message.author.id == 534384083925598218: 
        await message.channel.send(f'{message.author.mention}\nI love ASHISH you baka..😡', delete_after=10) 
      else:
        await message.channel.send(f'{message.author.mention}\nOkay, I belong to only ASHISH❤️', delete_after=10)

    if 'love you' in message.content.lower() and 'miko chan' in message.content.lower():
      if message.author.id == 784363251940458516:
        await message.channel.send(f'{message.author.mention}\nI love you too onii chan❤️', delete_after=10)
      elif message.author.id == 534384083925598218:
        await message.channel.send(f'{message.author.mention}\nI love ASHISH but we can spend some time together SENSEI..❤️', delete_after=10)  
      else:
        await message.channel.send(f'{message.author.mention}\nI belong to only ASHISH❤️ But I can leave him for you if you are worthy enough..❤️', delete_after=10)
    if 'failed' in message.content.lower():
        response = random.choice(fail_quote)
        await message.channel.send(f'{message.author.mention}\n{response}')
    
    if 'tired' in message.content.lower():
        response = random.choice(tired_quote)
        await message.channel.send(f'{message.author.mention}\n{response}')
    
    if 'die' in message.content.lower():
        response = random.choice(die_quote)
        await message.channel.send(f'{message.author.mention}\n{response}')       
 

token = config("TOKEN")
client.run(token)        
