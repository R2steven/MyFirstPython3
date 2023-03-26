from vpython import *

#ball = sphere(color=color.red)
circle = shapes.circle(radius=10)
circle_path = [vector(0,0,0),vector(0,0,1)]
disk = extrusion(path = circle_path, shape = circle)

sleep(5)
#ball.color=color.blue
while True:
    pass