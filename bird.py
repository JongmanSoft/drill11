# 이것은 각 상태들을 객체로 구현한 것임.

from pico2d import get_time, load_image, load_font, clamp,  SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT
from ball import Ball, BigBall
import game_world
import game_framework

# state event check
# ( state event type, event value )

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def time_out(e):
    return e[0] == 'TIME_OUT'

# time_out = lambda e : e[0] == 'TIME_OUT'




# Boy Run Speed
PIXEL_PER_METER = (183.0 / 1.0)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)


# Boy Action Speed
TIME_PER_ACTION = 0.25
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 5

class Idle:

    @staticmethod
    def enter(boy, e):
        if boy.face_dir == -1:
            boy.action = 2
        elif boy.face_dir == 1:
            boy.action = 3
        boy.dir = 0
        boy.frame = 0
        boy.wait_time = get_time() # pico2d import 필요
        pass

    @staticmethod
    def exit(boy, e):
        if space_down(e):
            boy.fire_ball()
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 5
        if get_time() - boy.wait_time > 2:
            boy.state_machine.handle_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        if boy.face_dir == -1:
            boy.image.clip_composite_draw(int(boy.frame) * 183, 338, 183, 168,
                                          0, 'h', boy.x + 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(int(boy.frame) * 183, 338, 183, 168,
                                          0, '', boy.x - 25, boy.y - 25, 100, 100)



class Run:

    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e): # 오른쪽으로 RUN
            boy.dir, boy.action, boy.face_dir = 1, 1, 1
        elif left_down(e) or right_up(e): # 왼쪽으로 RUN
            boy.dir, boy.action, boy.face_dir = -1, 0, -1

    @staticmethod
    def exit(boy, e):
        if space_down(e):
            boy.fire_ball()

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 5
        boy.x += boy.dir * RUN_SPEED_PPS * game_framework.frame_time
        boy.x = clamp(25, boy.x, 1600 - 25)

    @staticmethod
    def draw(boy):
        if boy.face_dir == -1:
            boy.image.clip_composite_draw(int(boy.frame) * 183, 338, 183, 168,
                                          0, 'h', boy.x + 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(int(boy.frame) * 183, 338, 183, 168,
                                          0, '', boy.x - 25, boy.y - 25, 100, 100)



class Sleep:
    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == -1:
            boy.image.clip_composite_draw(int(boy.frame) * 183, 338, 183, 168,
                                              0, 'h', boy.x + 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(int(boy.frame) * 183, 338, 183, 168,
                                              0, '', boy.x - 25, boy.y - 25, 100, 100)


class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle
        self.transitions = {
            Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run},
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle},
            Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run}
        }

    def start(self):
        self.cur_state.enter(self.boy, ('NONE', 0))

    def update(self):

        self.cur_state.do(self.boy)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True
        return False

    def draw(self):
        self.cur_state.draw(self.boy)





class Boy:
    def __init__(self,x,y):
        self.x, self.y = x, y
        self.frame = 0
        self.action = 3
        self.face_dir = 1
        self.dir = 1
        self.image = load_image('bird_animation.png')
        self.item = 'Ball'


    def fire_ball(self):

        if self.item ==   'Ball':
            ball = Ball(self.x, self.y, self.face_dir*10)
            game_world.add_object(ball)
        elif self.item == 'BigBall':
            ball = BigBall(self.x, self.y, self.face_dir*10)
            game_world.add_object(ball)
        # if self.face_dir == -1:
        #     print('FIRE BALL LEFT')
        #
        # elif self.face_dir == 1:
        #     print('FIRE BALL RIGHT')

        pass

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 5
        self.x += self.dir * RUN_SPEED_PPS * game_framework.frame_time
        self.x = clamp(25, self.x, 1600 - 25)
        if (self.x > 1500): self.dir = -1
        if (self.x < 100):self.dir = 1
        pass
        #self.state_machine.update()

    def handle_event(self, event):
        pass

    def draw(self):
        if self.dir == -1:
            self.image.clip_composite_draw(int(self.frame) * 183, 338, 183, 168,
                                          0, 'h', self.x + 25, self.y - 25, 100, 100)
        else:
            self.image.clip_composite_draw(int(self.frame) * 183, 338, 183, 168,
                                          0, '', self.x - 25, self.y - 25, 100, 100)
