from pico2d import load_image, get_time, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_a
from transitions import Machine
import math


class Idle:
    @staticmethod
    def enter(boy):
        boy.wait_start_time = get_time()

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.wait_start_time > 5.0:
            boy.time_out()

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 300, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 200, 100, 100, boy.x, boy.y)


class Sleep:
    @staticmethod
    def enter(boy):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100
            )
        else:
            boy.image.clip_composite_draw(
                boy.frame * 100, 200, 100, 100,
                -math.pi / 2, '', boy.x + 25, boy.y - 25, 100, 100
            )


class Run:
    @staticmethod
    def enter(boy):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        boy.x = max(25, min(800 - 25, boy.x))

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, boy.y)
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, boy.y)


class AutoRun:
    @staticmethod
    def enter(boy):
        boy.autorun_start_time = get_time()
        if boy.dir == 0:
            boy.dir = boy.face_dir

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 15
        if boy.x <= 50:
            boy.x = 50
            boy.dir = 1
            boy.face_dir = 1
        elif boy.x >= 800 - 50:
            boy.x = 800 - 50
            boy.dir = -1
            boy.face_dir = -1

        if get_time() - boy.autorun_start_time > 5.0:
            boy.dir = 0
            boy.time_out()

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * 100, 100, 100, 100, boy.x, boy.y + 30, 200, 200)
        else:
            boy.image.clip_draw(boy.frame * 100, 0, 100, 100, boy.x, boy.y + 30, 200, 200)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.wait_start_time = get_time()
        self.autorun_start_time = 0.0

        self.state_classes = {
            'IDLE': Idle,
            'SLEEP': Sleep,
            'RUN': Run,
            'AUTORUN': AutoRun,
        }

        # IDLE, SLEEP, RUN, AUTORUN 상태를 정의한다.
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN', 'AUTORUN'],
            initial='IDLE',
            auto_transitions=False,
        )

        # 상태 전이 규칙 설정
        self.machine.add_transition(
            trigger='time_out',
            source='IDLE',
            dest='SLEEP',
        )
        self.machine.add_transition(
            trigger='key_down',
            source='SLEEP',
            dest='IDLE',
        )
        self.machine.add_transition(
            trigger='start_run',
            source='IDLE',
            dest='RUN',
        )
        self.machine.add_transition(
            trigger='stop_run',
            source='RUN',
            dest='IDLE',
        )
        self.machine.add_transition(
            trigger='start_autorun',
            source='IDLE',
            dest='AUTORUN',
        )
        self.machine.add_transition(
            trigger='time_out',
            source='AUTORUN',
            dest='IDLE',
        )
        self.machine.add_transition(
            trigger='start_run',
            source='AUTORUN',
            dest='RUN',
        )

    def on_enter_IDLE(self):
        Idle.enter(self)

    def on_enter_SLEEP(self):
        Sleep.enter(self)

    def on_enter_RUN(self):
        Run.enter(self)

    def on_enter_AUTORUN(self):
        AutoRun.enter(self)

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                if self.state == 'AUTORUN':
                    self.dir = 1
                    self.face_dir = 1
                    self.start_run()
                    return
                self.dir += 1
            elif event.key == SDLK_LEFT:
                if self.state == 'AUTORUN':
                    self.dir = -1
                    self.face_dir = -1
                    self.start_run()
                    return
                self.dir -= 1
            elif event.key == SDLK_a:
                if self.state == 'IDLE':
                    self.start_autorun()
                    return

            if self.state == 'SLEEP':
                self.key_down()

            if self.state == 'IDLE' and self.dir != 0:
                self.face_dir = self.dir
                self.start_run()
            elif self.state == 'RUN':
                if self.dir == 0:
                    self.stop_run()
                else:
                    self.face_dir = self.dir

        elif event.type == SDL_KEYUP:
            if event.key in (SDLK_RIGHT, SDLK_LEFT):
                if self.state == 'AUTORUN':
                    return
                if event.key == SDLK_RIGHT:
                    self.dir -= 1
                elif event.key == SDLK_LEFT:
                    self.dir += 1

                if self.state == 'RUN':
                    if self.dir == 0:
                        self.stop_run()
                    else:
                        self.face_dir = self.dir
                elif self.state == 'IDLE' and self.dir != 0:
                    self.face_dir = self.dir
                    self.start_run()

    def update(self):
        self.state_classes[self.state].do(self)

    def draw(self):
        self.state_classes[self.state].draw(self)
