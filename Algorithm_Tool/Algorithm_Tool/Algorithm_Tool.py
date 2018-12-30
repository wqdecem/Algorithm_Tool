#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, os.path
import math
#import basic pygame modules
import pygame
from pygame.locals import *

#see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


#game constants

ALIEN_ODDS     = 22     #chances a new alien appears

ALIEN_RELOAD   = 12     #frames between new aliens

SCORE          = 0

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


class dummysound:
    def play(self): pass




# each type of game object gets an init and an
# update function. the update function is called
# once per frame, and it is when each object should
# change it's current position and state. the Player
# object actually gets a "move" function instead of
# update, since it is passed extra information about
# the keyboard


class Temp(pygame.sprite.Sprite):
    speed = 10
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

class TransformTarget(object):

    def __init__(self):
        pass

    def transform_size(self,target,grow_rate):
        if grow_rate>1:
            target = pygame.transform.smoothscale(target, (math.ceil(target.get_width()*grow_rate), math.ceil(target.get_height()*grow_rate)))
        else:
            target = pygame.transform.smoothscale(target, (math.floor(target.get_width()*grow_rate), math.floor(target.get_height()*grow_rate)))
        return target

def main(winstyle = 0):
    # Initialize pygame
    

    pygame.init()


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
    text = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastalien = pygame.sprite.GroupSingle()

    #assign default groups to each sprite class

    Temp.containers = temp
    MouseInfo.containers = text

    clock = pygame.time.Clock()

    #initialize our starting sprites

    tf = TransformTarget()

    text.add(MouseInfo())

    speed = 10
    b=Temp([255,0,0],[50,100])
    temp.add(b)

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
            i.update(speed,SCREENRECT)


            screen.blit(i.image,i.rect)


        for i in text:
            for k in temp:
                i.update(k.rect.left,k.rect.top)
                screen.blit(i.image,i.rect)
        pygame.display.update()
        pygame.display.flip()
        #cap the framerate 
        clock.tick(25) #50 frames per second.


    pygame.time.wait(1)
    pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()



