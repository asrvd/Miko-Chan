import discord
import os
import datetime
from discord.ext import commands, timers
import requests
import json
import random
from keep_alive import keep_alive
from googlesearch import search
import asyncio
from decouple import config


token = os.environ['token']
intents = discord.Intents.default()
intents.members = True
intents.presences = True
emojisOn = False


client = commands.Bot(command_prefix='m.', case_insensitive=True, intents=intents)
client.remove_command("help")
client.timer_manager = timers.TimerManager(client)

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('With Ashish'))
  print('Bot is Online.')

#Inspirational quotes  
@client.command()
async def inspire(ctx):
  def get_quote():
      response = requests.get("https://zenquotes.io/api/random")
      json_data = json.loads(response.text)
      quote = json_data[0]['q'] + " -" + json_data[0]['a']
      return quote
  quote = get_quote()
  await ctx.send(quote)  

#help
@client.command()
async def help(ctx):
  try:
    h = discord.Embed(
      title="NEED HELP?",
      description="Bot Creator: **ASHISH**\nHelper: **Ankoosh Kun**\nCommands Suggestion: **SENSEI**",
      color=0xe81741,
    )
    h.add_field(
      name="__ABOUT__", 
      value=f"\nPrefix : `m.`\nMiko Chan is a Discord Bot created for people who find it hard to focus while working. She can start a focus timer for you, send you inspirational quotes, motivate you if you are sad and love you if you love her❤️. You can also ask her to search things on google related to studies. Good luck!", 
      inline=False
    )
    h.add_field(
      name="__COMMANDS__",
      value=f"`start (time)` Starts the focus timer.\n`stop` Stops the focus timer.\n`showtimer` Shows your remaining focus time.\n`inspire` Miko chan sends an inspirational quote for you.\n`padhle (user)` Just a normal study reminder for fun",
      inline=False
    )
    h.add_field(
      name="__MISC__", value="`source` source code for the bot", inline=False
    )

    await ctx.send(embed=h)
  except Exception as e:
    print(e)

  @client.command()
  async def source(self, ctx):
    await ctx.send("To be updated soon!")

#global variables 

user_list = []

#Start timer
@client.command()
async def start(ctx, time: int):
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
            await ctx.send(timer) 
            showTimer = False

        #stops clock
        if(pomodoro_timer == False):
            break


        #start of clock
        if(t == time*60):
          await ctx.send(f'{ctx.author.mention}\nYour focus time is set to {hour} hour and {minute} minutes. Good Luck!', delete_after=20)
          user_list.append(ctx.author.id)


        #break time
        elif(t == 0):
          await ctx.send(f'{ctx.author.mention}\nYour focus time has ended! Take a break :)', delete_after=20)
          user_list.remove(ctx.author.id)

#stop timer                              
@client.command()
async def stop(ctx):
    if ctx.author.id in user_list:
      global pomodoro_timer 
      pomodoro_timer = False
      await ctx.send(f'{ctx.author.mention}\nYour timer has been stopped!', delete_after=20)
      user_list.remove(ctx.author.id)
    else:
      await ctx.send(f'{ctx.author.mention}\nYou are not currently working! Use m.start [time] to start a timer', delete_after=20)  

#Show remaining time      
@client.command() 
async def showtimer(ctx):
  if ctx.author.id in user_list:
    global showTimer
    showTimer = True
    await ctx.send(f"{ctx.author.mention}\n**Here is the time remaining on the Pomodoro Clock:**")
  else:
    await ctx.send(f'{ctx.author.mention}\nYou are not currently working! Use m.start [time] to start a timer', delete_after=20)

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
      if message.content.startswith('m.'):
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
    if 'failed' in message.content:
        response = random.choice(fail_quote)
        await message.channel.send(f'{message.author.mention}\n{response}')
    
    if 'tired' in message.content:
        response = random.choice(tired_quote)
        await message.channel.send(f'{message.author.mention}\n{response}')
    
    if 'die' in message.content:
        response = random.choice(die_quote)
        await message.channel.send(f'{message.author.mention}\n{response}')       

token = config("Token")
client.run(token)        
