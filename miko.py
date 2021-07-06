import os
import discord
import datetime
from discord.audit_logs import _transform_verification_level
from discord.ext import commands, tasks
import requests
import json
import random
import asyncio
from decouple import config
import pyrebase

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

firebase = pyrebase.initialize_app(json.loads(config("firebaseConfig")))
db = firebase.database()

firebase2 = pyrebase.initialize_app(json.loads(config("firebaseConfig2")))
db2 = firebase2.database()

def acreate(user: int, message: str):
  db2.child("AFK_USER").child(user).set(
    {"MESSAGE": message, "TIME": 0, "PINGS": 0}
  )

def update_ping(user: int):
  ping = db2.child("AFK_USER").child(user).child("PINGS").get().val()
  ping = ping + 1
  db2.child("USER_TIME").child(user).child("PINGS").update(ping)

def update_time(user: int):
  time = db2.child("AFK_USER").child(user).child("TIME").get().val()
  time = time + 1
  db2.child("USER_TIME").child(user).child("PINGS").update(time)

def afk_time(user: int):
  time = db2.child("AFK_USER").child(user).child("TIME").get().val()
  return time

def acheck(user: int):
  auth = db2.child("AFK_USER").child(user).get().val()
  if auth == None:
    return False
  else:
    return True

def aremove(user: int):
  db2.child("AFK_USER").child(user).remove()    

def return_message(user: int):
  note = db2.child("AFK_USER").child(user).child("MESSAGE").get().val()
  return note

def create(user: int, time: int):
    db.child("USER_TIME").child(user).set(
        {"TOTAL": time}
    )

def check(user: int):
  auth = db.child("USER_TIME").child(user).get().val()
  if auth == None:
    return False
  else:
    return True  

def add_time(user: int, time: int):
  users = db.child("USER_TIME").child(user).get().val()
  if users==None:
    create(user, time)
  else:
    auth = db.child("USER_TIME").child(user).child("TOTAL").get()
    t = auth.val()
    t = t + time
    db.child("USER_TIME").child(user).update({"TOTAL": t})
    
def return_time(user: int):
  auth = db.child("USER_TIME").child(user).child("TOTAL").get()
  t = auth.val()
  hour = int(t/60)
  min = t%60
  return hour, min

def min_hour(time: int):
  hour = int(time/60)
  min = time%60
  return hour, min
    
@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('With Ashish'))
  print('Bot is Online.')
  time_update.start()

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
      value=f"`start (time)` Starts the focus timer.\n`stop` Stops the focus timer.\n`total` Shows the total time you have focused.\n`lb` Shows leaderboard of total focused time.\n`inspire` Miko chan sends an inspirational quote for you.\n`padhle (user)` Just a normal study reminder for fun.",
      inline=False
    )
    h.add_field(
      name="__WARNING__", value="If you are using focus timer, the time focused will be added only after you complete your focus time. Using `m.stop` will not work, So no cheating now, grind hard!", inline=False
    )
    h.add_field(
      name="__SOURCE__", value="`m.source`", inline=False
    )
    await ctx.send(embed=h)
  except Exception as e:
    print(e)

@client.command()
async def source(ctx):
  await ctx.send("https://github.com/AsheeshhSenpai/Miko-Chan")

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
            title="Timer Started!", description=f"⏱ Your focus time is set to {hour} hour and {minute} minutes ⏱\n\n😀 Good Luck! 😀", color=0xe81741)
            await ctx.send(ctx.author.mention, embed=emb)
            user_list.append(ctx.author.id)
            if check(ctx.author.id) == False:
              create(ctx.suthor.id, 0)

          #break time
          elif(t == 0):
            emb = discord.Embed(
            title="Timer Ended!", description=f"⏱ Your focus time has ended ⏱\n\n😀 Take a break 😀", color=0xe81741)
            await ctx.send(ctx.author.mention, embed=emb)
            user_list.remove(ctx.author.id)
            add_time(ctx.author.id, time)        
    else:
      return
  else:
    emb = discord.Embed(
      title="", description=f"**You are already working!.**", color=0xe81741)
    await ctx.send(ctx.author.mention, embed=emb)

@client.command()
async def lb(ctx):
  lb_dict={}
  desc = f""
  guild = client.get_guild(GUILD_ID)
  users_list=[]
  all_users = db.child("USER_TIME").get()
  for user in all_users.each():
    user_id = user.key()
    users_list.append(user_id)
  for member in users_list:
    time = db.child("USER_TIME").child(member).child("TOTAL").get().val()
    lb_dict[member] = time
  sort_lb = dict(sorted(lb_dict.items(), key=lambda x: x[1], reverse=True))
  for mem_id in sort_lb:
    try:
      member = await guild.fetch_member(mem_id)
    except Exception:
      member = "UNKNOWN MEMBER"
    position = list(sort_lb.keys()).index(mem_id) + 1
    hrs, mins = min_hour(sort_lb[mem_id])
    if position > 10:
      break
    else:
      if position == 1:
        desc += f"👑-> {member} | {hrs} Hrs {mins} Mins\n"
      elif position == 10:  # ONE SPACE LESSER
        desc += f"#{position}-> {member} | {hrs} Hrs {mins} Mins\n"
      else:
        desc += f"#{position} -> {member} | {hrs} Hrs {mins} Mins\n"

  mem_id = str(ctx.author.id)
  try:
    member = await guild.fetch_member(mem_id)
  except Exception:
    member = "UNKNOWN MEMBER"
  hrs, mins = min_hour(sort_lb[mem_id])
  position = list(sort_lb.keys()).index(mem_id) + 1

  emb = discord.Embed(
    title=f"**TOTAL FOCUSED TIME LEADERBOARD**",
    description=f"```\n{desc}\n```",
    color=0xe81741,
  )
  emb.set_footer(text=f"#{position} -> {member} | {hrs} Hrs {mins} Mins")
  await ctx.send(embed=emb)

@client.command()
async def afk(ctx, message):
  if acheck(ctx.author.id) == False:
    member = ctx.author
    old_nick = member.display_name
    new_nick = "[AFK]" + old_nick
    await member.edit(nick=new_nick)
    acreate(ctx.author.id, message)
    await ctx.send(f"{member.mention} is AFK: **{message}**")
  else:
    await ctx.send(f"{ctx.author.mention} You are already AFK.")


@client.command()
async def love(ctx):
  lb_dict={}
  users_list=[]
  all_users = db.child("USER_TIME").get()
  for user in all_users.each():
    user_id = user.key()
    users_list.append(user_id)
  for member in users_list:
    time = db.child("USER_TIME").child(member).child("TOTAL").get().val()
    lb_dict[member] = time
  sort_lb = dict(sorted(lb_dict.items(), key=lambda x: x[1], reverse=True))
  lb_list = list(sort_lb.keys())
  pos1 = lb_list[0]
  user = client.get_user(pos1)
  embed=discord.embed(title=f"I love {user} uwu.", color=0xe81741)
  await ctx.send(embed=embed)


@client.command()
async def total(ctx):
  hour, minutes = return_time(ctx.author.id)
  emb = discord.Embed(
    title="Total Focused Time", description=f"You have focused for {hour} hour and {minutes} minutes till now.", color=0xe81741)
  await ctx.send(ctx.author.mention, embed=emb)
    

@client.command()
async def say(ctx, *,message):
    if ctx.author.id == 784363251940458516:
      emb = discord.Embed(title=message, color=0xe81741)
      await ctx.send(embed = emb)
    else:
        await ctx.send(f"{ctx.author.mention} you don't have perms hehehehe")

@tasks.loop(hours=1)
async def time_update():
  all_users = db2.child("AFK_USER").get()
  for user in all_users.each():
    update_time(user.key())

@client.command()
async def stop(ctx):
  if ctx.channel.id == CAFE_LOUNGE_ID:
    if ctx.author.id in user_list:
      global pomodoro_timer 
      pomodoro_timer = False
      emb = discord.Embed(
      title="", description=f"**⚠ Your timer has been stopped! ⚠**", color=0xe81741)
      await ctx.send(ctx.author.mention, embed=emb)
      user_list.remove(ctx.author.id)
    else:
      emb = discord.Embed(
      title="", description=f"**You are not currently working! Use m.start [time] to start a timer.**", color=0xe81741)
      await ctx.send(ctx.author.mention, embed=emb) 
  else:
    return    

@client.command()
async def padhle(ctx, m1: discord.User = None):
  padhle_list=[
    "**Pyaar vyaar sab dhoka hai, padhle bete mauka hai..**",
    "**Padhlo beta, agar General Category se ho to**",
    "**Chacha vidhayak hai kya tumhare? Nahi he to jao padh lo**",
    "**Padhlo beta mauka he, aakhir kisne tumko roka hai?**",
    "**Abbe padhai likhai karo, IITian, doctor bano..**",
    "**Tera bhi katega, fir tu bhi physics padhega/padhegi..**"  
  ]
  if m1 == None:
    m1 = ctx.author
  emb = discord.Embed(
      title="", description=f"{m1.mention}\n{random.choice(padhle_list)}", color=0xe81741)
  await ctx.send(embed=emb)        

@client.event
async def on_message(message):
  await client.process_commands(message)
  if acheck(message.author.id) == True:
    if message.content.startswith('m.afk') or message.content.startswith('?afk') or message.content.startswith('v!afk'):
      return
    else:
      member = message.author
      nick = member.display_name
      new_nick = nick[7:]
      await member.edit(nick=new_nick)
      aremove(message.author.id)
      await message.channel.send(f"{member.mention} your AFK has been removed.")
  elif message.author.id in user_list:
    if message.channel.id == CAFE_LOUNGE_ID:
      if message.content.startswith('m.') or message.content.startswith('s.') or message.content.startswith('S.'):
          return
      else:
        if message.author.id == 534384083925598218:
          await message.channel.send(f'{message.author.mention}\n**Onii Chan Baka..** If you talk during your focus time I will kill you🔪..', delete_after=15)
        else:
          await message.channel.send(f'{message.author.mention}\n**Onii Chan Baka..** If you talk during your focus time I will not love you😡..', delete_after=15)
    else:
      return
  for mention in message.mentions:
    if acheck(mention.id) == True:
      note = return_message(mention.id)
      update_ping(mention.id)
      time = afk_time(mention.id)
      if time < 1:
        time = "few minutes ago."
      await message.channel.send(
        f"{message.author.mention}, **{mention}** is AFK!\nNOTE: **{note}**\n{time}", delete_after=25,)


token = config("TOKEN")
client.run(token)        
