from pico2d import load_image, get_time, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT
from transitions import Machine
import math


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.wait_start_time = get_time()

        # IDLE, SLEEP, RUN 상태를 정의한다.
        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN'],
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

    def on_enter_IDLE(self):
        self.wait_start_time = get_time()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT:
                self.dir += 1
            elif event.key == SDLK_LEFT:
                self.dir -= 1

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
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8
            if get_time() - self.wait_start_time > 5.0:
                self.time_out()
        elif self.state == 'SLEEP':
            self.frame = (self.frame + 1) % 8
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 8
            self.x += self.dir * 5
            self.x = max(25, min(800 - 25, self.x))

    def draw(self):
        if self.state == 'IDLE':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 300, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 200, 100, 100, self.x, self.y)
        elif self.state == 'SLEEP':
            if self.face_dir == 1:
                self.image.clip_composite_draw(
                    self.frame * 100, 300, 100, 100,
                    math.pi / 2, '', self.x - 25, self.y - 25, 100, 100
                )
            else:
                self.image.clip_composite_draw(
                    self.frame * 100, 200, 100, 100,
                    -math.pi / 2, '', self.x + 25, self.y - 25, 100, 100
                )
        elif self.state == 'RUN':
            if self.face_dir == 1:
                self.image.clip_draw(self.frame * 100, 100, 100, 100, self.x, self.y)
            else:
                self.image.clip_draw(self.frame * 100, 0, 100, 100, self.x, self.y)
