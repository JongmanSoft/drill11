from pico2d import *

import bird
import game_framework

import game_world
from grass import Grass
from boy import Boy
from bird import Boy

# boy = None

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)

def init():
    global grass
    global boy

    running = True
    for i in range (0,10):
        boy = bird.Boy(200+i*100,70 +i*50)
        game_world.add_object(boy, 1)



def finish():
    game_world.clear()
    pass


def update():
    game_world.update()
    #delay(1.0)


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause():
    pass

def resume():
    pass

