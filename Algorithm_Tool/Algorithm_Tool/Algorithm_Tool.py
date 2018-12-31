#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, os.path
import math
import numpy
#import basic pygame modules
import pygame
from pygame.locals import *

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


#game constants
main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard


class Temp(pygame.sprite.Sprite):
    speed = 2
    def __init__(self,color,initial_position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([30,30])
        self.image.fill(color)

        self.rect=self.image.get_rect()
        
        self.rect.topleft=initial_position
        self.speed =Temp.speed
        self.right = 1
        self.left = -1
        self.direction = self.left
    def update(self,speed=None,scope=None):
        self.speed = speed
        
        #if not scope.contains(self.rect):
        #    self.speed = -self.speed;
        #    self.rect = self.rect.clamp(scope)
        #print(self.rect)
        if self.rect.right > scope.right:
            self.direction = self.left
        if self.rect.left < scope.left:
            self.direction = self.right
        self.rect.move_ip(self.speed*self.direction, 0)

    def move_retangle(self,axis=None):
        self.rect.move_ip(axis[0],axis[1])

    def update_size(self,color,new_size):
        current_position = self.rect.topleft
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(new_size)
        self.image.fill(color)
        self.rect=self.image.get_rect()
        self.rect.topleft=current_position

    def auto_update_size(self):

        self.rect=self.rect.inflate(100,100)

class MouseInfo(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = Color('black')
        self.update()
        self.rect = self.image.get_rect().move(0, 0)

    def update(self,x=0,y=0):

        msg = "pos: %s,%s" % (x,y)
        self.image = self.font.render(msg, 0, self.color)

class TrajectoryInfo(object):
    """用于记录轨迹的信息"""
    def __init__(self):
        pass
    def retangle_trajectory(self,target,speed):
        """记录矩形轨迹信息，speed为步进，从top left开始，顺时针记录，如需反向，则逆向使用序列"""
        line = []
        for i in range(target.left,target.right,speed):
            line.append([speed,0])
        for i in range(target.top,target.bottom,speed):
            line.append([0,speed])
        for i in range(target.left,target.right,speed):
            line.append([-speed,0])
        for i in range(target.top,target.bottom,speed):
            line.append([0,-speed])

        return line


    def circle_trajectory(self,target,speed):
        """记录圆形轨迹信息，speed为步进，从top left开始，顺时针记录，如需反向，则逆向使用序列"""
        radius = (target.right - target.left) / 2
        delta_axis = []
        for i in range(int(2*math.pi*radius/speed)):
            target_speed_angle = float(360 * speed * i/ (2 * math.pi * radius))
            #转为弧度
            target_speed_x_radian =math.radians(target_speed_angle)
            #计算x坐标相对顶点坐标的差
            delta_x = radius*math.sin(target_speed_x_radian)
            #计算y坐标相对顶点坐标的差
            delta_y = radius-radius*math.cos(target_speed_x_radian)
        #    delta_axis.append([delta_x,delta_y])
        #line = []
        #for i in range(1,len(delta_axis)):

        #    x = delta_axis[i][0]-delta_axis[i-1][0]
        #    y = delta_axis[i][1]-delta_axis[i-1][1]
        #    line.append([math.ceil(x),math.ceil(y)])

        #return line
            delta_axis.append([math.ceil(delta_x+target.centerx),math.ceil(delta_y+target.top)])
        return delta_axis

class TransformTarget(object):
    """用于改变物体的大小"""
    def __init__(self):
        pass

    def transform_size(self,target,grow_rate):
        """用于改变物体的大小，输入image对象，然后变形"""
        if grow_rate>1:
            target = pygame.transform.smoothscale(target, (math.ceil(target.get_width()*grow_rate), math.ceil(target.get_height()*grow_rate)))
        else:
            target = pygame.transform.smoothscale(target, (math.floor(target.get_width()*grow_rate), math.floor(target.get_height()*grow_rate)))
        return target



def main(winstyle = 0):
    # Initialize pygame
    

    pygame.init()
    box_num = 4

    # Set the display mode
    #winstyle = 0  # |FULLSCREEN
    winstyle = pygame.RESIZABLE
    screen = pygame.display.set_mode((0,0), winstyle)#这个函数将创建一个 Surface 对象的显示界面。传入的参数用于指定显示类型。最终创建出来的显示界面将是最大可能地匹配当前操作系统。resolution 参数是一个二元组，表示宽和高。flags 参数是附件选项的集合。depth 参数表示使用的颜色深度。
    SCREENRECT     = Rect(0, 0, screen.get_width(), screen.get_height())

    #Load images, assign to sprite classes
    #(do this before the classes are used, after screen setup)


    icon = load_image('algorithm.icon.jpg').convert_alpha() #convert_alpha()方法会使用透明的方法绘制前景对象，因此在加载一个有alpha通道的素材时（比如PNG TGA），需要使用convert_alpha()方法，不用貌似就只有一片相同颜色像素

    #decorate the game window
    icon = pygame.transform.smoothscale(icon, (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('Algorithm Tool')
    pygame.mouse.set_visible(0)
    

    #create the background, tile the bgd image
    #bgdtile = load_image('background.gif')
    background = pygame.Surface((screen.get_width(), screen.get_height()))
    #for x in range(0, SCREENRECT.width, bgdtile.get_width()):
    #    background.blit(bgdtile, (x, 0))
    
    screen.fill((255,255,255))
    #screen.blit(background, (0,0))

    pygame.display.flip()

    
    # Initialize Game Groups

    temp = pygame.sprite.Group()
    boxs = pygame.sprite.Group()
    text = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastalien = pygame.sprite.GroupSingle()

    #assign default groups to each sprite class

    Temp.containers = temp
    MouseInfo.containers = text

    clock = pygame.time.Clock()

    #initialize our starting sprites

    tf = TransformTarget()
    traj_info = TrajectoryInfo()
    text.add(MouseInfo())

    speed = 10
    b=Temp([255,0,0],[0,0])

    #生成矩形组



    #生成矩形轨迹组
    my_rect_list =[]
    box_list = []
    for i in range(box_num):
        w =int( screen.get_width()/(i+1))
        h =int( screen.get_height()/(i+1))
        left = int((screen.get_width()-w)/2)
        top = int((screen.get_height()-h)/2)
        box =Temp([255,0,0],[left-15,top-15])
        box_list.append(box)
        my_rect_list.append(pygame.Rect(left,top,w,h))
    traj_info_list = []
    for each in my_rect_list:
        traj_info_list.append(traj_info.retangle_trajectory(each,speed))

    #生成圆形轨迹组
    my_rect_list_circle =[]
    box_list_circle = []
    for i in range(box_num):
        w =int( screen.get_width()/(i+1))
        h =int( screen.get_height()/(i+1))
        left = int((screen.get_width()-w)/2)
        top = int((screen.get_height()-h)/2)

        current_circle = pygame.draw.circle(screen,[255,0,0],[left+int(w/2),top+int(h/2)],int(h/2),1)
        box =Temp([0,255,0],[left+int(w/2)-15,current_circle.top-15])
        box_list_circle.append(box)
        my_rect_list_circle.append(current_circle)
    traj_info_list_circle = []
    for each in my_rect_list_circle:
        traj_info_list_circle.append(traj_info.circle_trajectory(each,speed))

    speed_count = 0
    while True:
        for event in pygame.event.get():
            if event.type == VIDEORESIZE:
                SCREEN_SIZE = event.size
                screen == pygame.display.set_mode(SCREEN_SIZE, RESIZABLE, 32)
                #pygame.display.set_caption("Window resized to " + str(event.size))
    
                screen_width, screen_height = SCREEN_SIZE
                SCREENRECT     = Rect(0, 0, screen_width, screen_height)


        screen.fill((255,255,255))
        # 这里需要重新填充满窗口
        #for y in range(0, screen_height, background.get_height()):
        #    for x in range(0, screen_width, background.get_width()):
        #        screen.blit(background, (x, y))

        #get input
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return

        keystate = pygame.key.get_pressed()
        stop = keystate[K_SPACE]
        action = keystate[K_UP]
        grow = keystate[K_DOWN]
        bigger = keystate[K_LEFT]
        sizec = keystate[K_RIGHT]
        for i in temp:
            if stop:
                speed = 0
            if action:
                speed = 1
            if grow:
                i.update_size([255,0,0],[100,100])

            if bigger:

                i.image = pygame.transform.smoothscale(i.image, (100, 100))

            #i.image = tf.transform_size(i.image,1.01)
            #i.update(speed,SCREENRECT)
            #screen.blit(i.image,i.rect)


        #for i in text:
        #    for k in temp:
        #        i.update(k.rect.left,k.rect.top)
        #        screen.blit(i.image,i.rect)

        #按矩形轨迹移动矩形框
        for i in range(box_num):
            current_step = traj_info_list[i][speed_count % len(traj_info_list[i])]
            box_list[i].move_retangle(current_step)
            screen.blit(box_list[i].image,box_list[i].rect)

        #绘制矩形轨迹
        for each in my_rect_list:
            print(each)
            pygame.draw.rect(screen,[255,0,0],each,1)


        #绘制圆形轨迹
        circles = []
        for i in range(box_num):


            w =int( screen.get_width()/(i+1))
            h =int( screen.get_height()/(i+1))

            left = int((screen.get_width()-w)/2)
            top = int((screen.get_height()-h)/2)

            circles.append(pygame.draw.circle(screen,[0,255,0],[left+int(w/2),top+int(h/2)],int(h/2),1))
        #按圆形轨迹移动矩形框
        for i in range(box_num):
            current_step = traj_info_list_circle[i][speed_count % len(traj_info_list_circle[i])]
            x = current_step[0]-box_list_circle[i].rect.left
            y = current_step[1]-box_list_circle[i].rect.top
            box_list_circle[i].move_retangle([x,y])

            box_list_circle[i].rect.clamp_ip(circles[i])#周期性调整，令其始终在圆内
            screen.blit(box_list_circle[i].image,box_list_circle[i].rect)

        #pygame.draw.aaline(screen, (0, 0, 255), (100, 250), (540, 300), 1)
        #current_circle = pygame.draw.circle(screen,[255,0,0],[100,100],100,1)
        pygame.display.update()
        pygame.display.flip()
        #cap the framerate 
        clock.tick(50) #50 frames per second.
        speed_count+=1

    pygame.time.wait(1)
    pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()



