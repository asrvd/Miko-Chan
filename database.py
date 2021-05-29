db = {}

def add_time(user, time):
  if user in db:
    t = db[user]
    t = t + time
    db[user] = time
  else:
    db[user] = time
    
def return_time(user):
  time = db[user]
  hour = int(time/60)
  minute = time%60
  return hour, minute
    
