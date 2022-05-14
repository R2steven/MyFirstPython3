# Ryan Stevens
# restevens52@gmail.com
#
# magic8 implements a magic 8 ball that you can ask for a random answer. Was
# supposed to use if and elif statements, but arrays are just so much nicer than
# a bunch of conditionals.


import random


# the magic 8ball answers
ans = ["Yes - definitely.",
"It is decidedly so.",
"Without a doubt.",
"Reply hazy, try again.",
"Ask again later.",
"Better not tell you now.",
"My sources say no.",
"Outlook not so good.",
"Very doubtful."]

name = input("What's your name?")
question = input("What do you wish to ask the great 8Ball?")
answer = None
random_number = random.randint(0,8)
if name == None or name == "":
  print("Question: "+question)
else:
  print(name+" asks: "+question)
if question == None or question == "":
  print ("Magic 8-ball cannot answer a question not asked")
else:
  print("Magic 8-Ball's answer: ",ans[random_number])

