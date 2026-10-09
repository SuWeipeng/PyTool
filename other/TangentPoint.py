import numpy as np
import matplotlib.pyplot as plt

class Vector:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def length(self):
        return np.sqrt(self.x**2 + self.y**2)
    def normalize(self):
        x = self.x / self.length()
        y = self.y / self.length()
        return (x,y)

class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def get_distance(self,p):
        v = Vector(0,0)
        v.x = (p.x - self.x)
        v.y = (p.y - self.y)
        return v

class Circle:
    def __init__(self,center_x,center_y,radius):
        self.cx = center_x
        self.cy = center_y
        self.r = radius
    def cal(self):
        theta = np.linspace(0, 2 * np.pi, 200)
        x = np.cos(theta) + self.cx
        y = np.sin(theta) + self.cy
        return (x,y)

def getPointOfTangency(center, p, radius, direction):
    v = center.get_distance(p)
    l = v.length()
    ret = Point(0, 0)
    if l > radius:
        d1 = radius**2 / l
        nx, ny = v.normalize()
        v1 = Vector(nx * d1, ny * d1)
        l1 = v1.length()
        l2 = np.sqrt(radius**2 - l1**2)
        d = direction / abs(direction)
        # matrix = [[  0, -d],
        #           [  d,  0]]
        n1x = ny * (-d)
        n1y = nx * d
        p1x = center.x + v1.x + n1x * l2
        p1y = center.y + v1.y + n1y * l2
        ret = Point(p1x, p1y)
        return ret
    else:
        return None

# Circle
center = Point(0,0)
r = 1
c = Circle(center.x,center.y,r)
x,y = c.cal()

# Point
p = Point(5,3)

# Vector from center to point
v = center.get_distance(p)

# 计算切点
pt = getPointOfTangency(center, p, r, 1)

if pt != None:
    # 绘图布局
    fig  = plt.figure(figsize=(16, 8), dpi=1920/16)
    ax = plt.subplot2grid((1,1),(0,0))
    ax.grid(ls="--")
    ax.axis('equal')

    # Plot circle
    ax.plot(x, y,
            label="circle",
            marker = '',
            linestyle="-",
            color='g')
    ax.plot(center.x, center.y,
            label="center",
            marker = '.',
            linestyle="-",
            color='r')

    ax.plot(p.x, p.y,
            label="p",
            marker = '.',
            linestyle="-",
            color='r')

    ax.plot(pt.x, pt.y,
            label="pt",
            marker = '.',
            linestyle="-",
            color='r')

    ax.plot((p.x,pt.x), (p.y,pt.y),
            label="",
            marker = '',
            linestyle=":",
            color='c')

    ax.plot((center.x,pt.x), (center.y,pt.y),
            label="",
            marker = '',
            linestyle=":",
            color='c')

    # Plot vector from center to point
    ax.quiver((center.x), (center.y), (v.x), (v.y),
              width = 0.002,
              angles='xy',
              scale_units='xy',
              scale=1,
              color='b')
    dirct = 1
    def on_press(event):
        global dirct
        p = Point(event.xdata, event.ydata)
        v = center.get_distance(p)
        pt = getPointOfTangency(center, p, r, dirct)
        if pt != None:
            ax.plot(p.x, p.y,
                    label="p",
                    marker = '.',
                    linestyle="-",
                    color='r')
            ax.plot(pt.x, pt.y,
                    label="pt",
                    marker = '.',
                    linestyle="-",
                    color='r')
            ax.plot((p.x,pt.x), (p.y,pt.y),
                    label="",
                    marker = '',
                    linestyle=":",
                    color='c')
            ax.plot((center.x,pt.x), (center.y,pt.y),
                    label="",
                    marker = '',
                    linestyle=":",
                    color='c')
            # Plot vector from center to point
            ax.quiver((center.x), (center.y), (v.x), (v.y),
                      width = 0.002,
                      angles='xy',
                      scale_units='xy',
                      scale=1,
                      color='b')
            plt.draw()
        else:
            print("Point inside the circle.")

    def on_key_press(event):
        global dirct
        if event.key == 'd':
            dirct *= -1

    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('key_press_event', on_key_press)
    plt.show()
else:
    print("Point inside the circle.")