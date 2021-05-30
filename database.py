db = {
  747477050335690752: 300,
  534384083925598218: 300,
  744854846506532885: 300,
  443844596586250240: 300,
  784363251940458516: 240
}

def add_time(user, time):
  if user in db:
    t = db[user]
    t = t + time
    db[user] = t
  else:
    db[user] = time
    
def return_time(user):
  time = db[user]
  hour = int(time/60)
  minute = time%60
  return hour, minute
    
