from turtle import *

wind_direction = 130
wind_length    = 10.1

tracer(False)
pixcel = 360
screensize(pixcel,pixcel)
setup(width=pixcel,height=pixcel)
def Skip(step):#表盘不连续地画图
    penup()
    forward(step)
    pendown()

def SetupClock(radius):
    #建立表的外框
    reset()
    right(-90)
    for i in range(360):
        Skip(radius)#跨越中间这段不画
        if i % 10 == 0:
            pensize(2)
            forward(15)

            if i == 0:
                write(i,align="center")

                Skip(-30)
                write("N", align="center")
                Skip(30)

            elif i == 30 or i == 330:
                Skip(3)
                write(i,align="center")
                Skip(-3)
            elif i == 60 or i == 300:
                Skip(6)
                write(i,align="center")
                Skip(-6)
            elif i == 90 or i == 270:
                Skip(9)
                write(i,align="center")
                Skip(-9)
                if i == 90:
                    Skip(-25)
                    write("E", align="center")
                    Skip(25)
                else:
                    Skip(-25)
                    write("W", align="center")
                    Skip(25)
            elif i == 120 or i == 240:
                Skip(15)
                write(i,align="center")
                Skip(-15)
            elif i == 150 or i == 210:
                Skip(15)
                write(i,align="center")
                Skip(-15)
            elif i == 180:
                Skip(15)
                write(i,align="center")
                Skip(-15)

                Skip(-20)
                write("S", align="center")
                Skip(20)

            Skip(-radius-15)
        elif i % 5 == 0:
            pensize(1)
            forward(15)
            Skip(-radius-15)#抬起画笔，回到原处
        else:
            pensize(1)
            forward(10)
            Skip(-radius-10)#抬起画笔，回到圆心
        right(1)#回到圆心，方向旋转6度

SetupClock(130)

pensize(2)
right(wind_direction)
tracer(True)
forward(90)
Skip(10)
write("%.1fm/s"%(wind_length))
Skip(-10)

ts = getscreen()
ts.getcanvas().postscript(file="compass.eps")

