# This example is not working in Spyder directly (F5 or Run)
# Please type '!python turtle_runaway.py' on IPython console in your Spyder.
import tkinter as tk
import turtle, random
import math
import time
from enum import Enum
from dataclasses import dataclass, field


class RunawayGame:
    def __init__(self, screen : turtle.TurtleScreen, root: tk.Tk):
        self.screen = screen
        self.root = root

        # Instantiate an another turtle for drawing
        self.drawer = turtle.RawTurtle(screen)
        self.drawer.hideturtle()
        self.drawer.penup()
        self.drawer.speed(0)
        self.drawer._tracer(0, 0)

        self.sprites = {}

        self.running = False
        self.tick_speed_ms = 1000 // 60

        self.current_level = None
        self.current_level_id = 0

        self.load_level(self.current_level_id)

        self.pressed_keys = dict()

        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<KeyRelease>', self._on_key_release)
        self.last_time = None

    def _on_key_press(self, event):
        self.pressed_keys[event.keysym] = True

    def _on_key_release(self, event):
        self.pressed_keys[event.keysym] = False

    def is_key_pressed(self, key):
        return key in self.pressed_keys and self.pressed_keys[key]
    
    def get_keys_pressed(self):
        return self.pressed_keys

    def load_level(self, level_id:int, seed:int=1234) -> None:
        self.last_time = time.time()
        self.current_level = Level(self, level_id, seed)

    def get_current_level(self):
        return self.current_level
    
    def get_level_time(self):
        if self.current_level is None:
            return -1
        
        return self.current_level.time

    def load_sprite(self, filename:str, scale=1, size=None) -> str:
        if filename in self.sprites:
            return self.sprites[filename]

        self.screen.register_shape(filename)
        self.sprites[filename] = filename
        return filename
        
    def loop(self):
        if not self.running:
            return
        
        dt = self.tick_speed_ms / 1000
        if self.last_time is not None:
            dt = time.time() - self.last_time
            self.last_time = time.time()
        
        if self.current_level is not None:
            self.current_level._tick(dt)

            self.drawer.clear()
            self.current_level._draw(self.drawer)

        self.screen.update()
        
        self.screen.ontimer(self.loop, self.tick_speed_ms)


    def start(self):

        if self.running:
            return
        
        self.running = True

        self.screen.ontimer(self.loop, self.tick_speed_ms)



# direction enum
class Direction(Enum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3


@dataclass
class GameObject:
    game: RunawayGame
    x: float = 0
    y: float = 0
    direction: Direction = Direction.UP
    x_vel: float = 0
    y_vel: float = 0
    children: list = field(default_factory=list)


    def __init__(self, game: RunawayGame, **kwargs):
        self.game = game
        self.children : list[GameObject] = []
        self.__dict__.update(kwargs)

    def add_child(self, child):
        self.children.append(child)

    def _tick(self, dt: float):
        self.tick(dt)
        for child in self.children:
            child._tick(dt)

    def tick(self, dt: float):
        pass

    def _draw(self, pen: turtle.RawTurtle):
        self.draw(pen)
        for child in self.children:
            child._draw(pen)

    def draw(self, pen: turtle.RawTurtle):
        pass


class TimedGameObject(GameObject):
    """
    displays children based on time with start and end time
    """

    def __init__(self, game: RunawayGame, start_time: float=0, end_time: float=1.0, duration: float=-1, **kwargs):
        super().__init__(game, **kwargs)

        self.timer = 0.0
        self.start_time = start_time
        self.end_time = end_time

        if duration > 0:
            self.end_time = self.start_time + duration

        self.drawMe = False if self.start_time > 0 else True


    def _draw(self, pen: turtle.RawTurtle):
        if self.drawMe:
            super()._draw(pen)

    def tick(self, dt: float):
        self.timer += dt

        if self.timer > self.start_time and self.timer < self.end_time:
            self.drawMe = True
        else:
            self.drawMe = False

        super().tick(dt)


class TextObject(GameObject):

    def __init__(self, game: RunawayGame, get_text: callable, position: tuple[float, float] = (0, 0), font: tuple[str, int, str] = ('Arial', 12, 'normal'), color: str = 'black', **kwargs):
        super().__init__(game, **kwargs)
        self.get_text = get_text
        self.position = position
        self.font = font
        self.color = color
        self.text = ""

    def draw(self, pen: turtle.RawTurtle):
        pen.penup()
        pen.goto(self.position)
        pen.pendown()
        pen.color(self.color)
        pen.write(self.text, font=self.font)


    def tick(self, dt: float):
        self.text = self.get_text()
        super().tick(dt)

class Level(GameObject):
    def __init__(self, game: RunawayGame, id:int, seed:int=1234, **kwargs):
        super().__init__(game, **kwargs)
        self.id : int = id
        self.seed : int = seed

        self.time : float = 0
        self.timer = 9999
        self.score = 0

        self.player = Player(game, x=0, y=0)
        self.add_child(self.player)

        self.ai = AITurtle(game)
        self.add_child(self.ai)

        self.generate_level()

    def generate_level(self):
        """
        Generates the level based on id and seed
        """
        self.timer = 30 + self.id * 10

        # add timer display
        timer = TextObject(
            self.game,
            lambda: f"Time: {math.ceil(self.timer)}",
            position=(-360, 360),
            font=('Arial', 12, 'normal'),
            color='black'
        )

        self.add_child(timer)

        score = TextObject(
            self.game,
            lambda: f"Score: {math.ceil(self.score):,}",
            position=(360-60, 360),
            font=('Arial', 12, 'normal'),
            color='black'
        )

        self.add_child(score)

        level_name = TextObject(
            self.game,
            lambda: f"Level: {self.id}",
            position=(0, 0),
            font=('Arial', 32, 'normal'),
            color='red'
        )

        level_name_timer = TimedGameObject(
            self.game,
            0,
            2,
            children=[level_name]
        )

        self.add_child(level_name_timer)


    def _tick(self, dt: float):
        if self.timer > 0:
            return super()._tick(dt)

    def tick(self, dt: float):
        self.time += dt
        self.timer -= dt
        self.score += dt * 10

    def is_completed(self):
        return self.timer <= 0
    
    def get_score(self):
        return self.score



class AnimatedTurtle(GameObject):
    """
    Uses a seperate turtle to draw the animation instead of the general drawer
    """

    def __init__(self, game: RunawayGame, **kwargs):
        super().__init__(game, **kwargs)
        self.turtle = turtle.RawTurtle(game.screen)
        #self.turtle.hideturtle()
        self.turtle.shape('turtle')
        self.turtle.color('red')
        self.turtle.penup()
        self.turtle.speed(0)
        
        self.turtle._tracer(0, 0)


    def draw(self, _: turtle.RawTurtle) -> None:
        self.turtle.setpos(self.x, self.y)
        self.turtle.setheading(self.direction.value * 90)
        self.turtle.showturtle()

class MovingTurtle(AnimatedTurtle):
    """
    A turtle that moves
    """

    def __init__(self, game: RunawayGame, step_size: float = 10, **kwargs):
        super().__init__(game, **kwargs)
        self.step_size = step_size
        self.speed: float = 1.0

    def left(self) -> None:
        self.direction = Direction.LEFT
        self.turtle.setheading(self.direction.value * 90)
        self.x -= self.step_size * self.speed
        
        self.turtle.setpos(self.x, self.y)

    def right(self) -> None:
        self.direction = Direction.RIGHT
        self.turtle.setheading(self.direction.value * 90)
        self.x += self.step_size * self.speed
        self.turtle.setpos(self.x, self.y)

    def up(self) -> None:
        self.direction = Direction.UP
        self.turtle.setheading(self.direction.value * 90)
        self.y += self.step_size * self.speed
        self.turtle.setpos(self.x, self.y)

    def down(self) -> None:
        self.direction = Direction.DOWN
        self.turtle.setheading(self.direction.value * 90)
        self.y -= self.step_size * self.speed
        self.turtle.setpos(self.x, self.y)

    def draw(self, _: turtle.RawTurtle) -> None:
        # set position just in case
        self.turtle.setpos(self.x, self.y)
        return super().draw(_) # type: ignore
    

class Player(MovingTurtle):

    DIRECTION_KEYS = [
        "Left",
        "Right",
        "Up",
        "Down",
        "a",
        "d",
        "w",
        "s"
    ]

    def __init__(self, game: RunawayGame, **kwargs):
        super().__init__(game, **kwargs, step_size=10)
        #self.turtle.shape(game.load_sprite('player.gif'))
        self.last_keys = {key: -1 for key in self.DIRECTION_KEYS}

    def tick(self, dt: float) -> None:
        """
        Called every frame, moves the player"""

        # get current keys pressed, prioritise new presses over old ones
        keys = self.game.get_keys_pressed()
        
        key = "None"
        key_time = 2e9

        # check direction keys
        for d_key in self.last_keys:
            if d_key in keys and keys[d_key]:
                if self.last_keys[d_key] < key_time:
                    key = d_key
                    key_time = self.last_keys[d_key]
                self.last_keys[d_key] = self.game.get_level_time()
            else:
                self.last_keys[d_key] = -1


        
        match key:
            case "Left" | "a":
                self.left()
            case "Right" | "d":
                self.right()
            case "Up" | "w":
                self.up()
            case "Down" | "s":
                self.down()
            case _:
                pass


        if "space" in keys and keys["space"]:
            self.speed = 2.0
        else:
            self.speed = 1.0


class AITurtle(MovingTurtle):
    def __init__(self, game: RunawayGame, **kwargs):
        super().__init__(game, **kwargs, step_size=10, x = random.randint(-400, 400), y = random.randint(-400, 400))

    def tick(self, dt: float) -> None:
        """
        Called every frame, moves the turtle"""


        player = None
        for child in self.game.get_current_level().children:
            if isinstance(child, Player):
                player = child
                break

        if player is None:
            return
        
        # get direction to player
        dx = player.x - self.x
        dy = player.y - self.y

        # move towards player, pick the largest component
        if abs(dx) > abs(dy):
            if dx > 0:
                self.right()
            else:
                self.left()
        else:
            if dy > 0:
                self.up()
            else:
                self.down()



class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Turtle Runaway')

        self.canvas = tk.Canvas(self.root, width=800, height=800)
        self.canvas.pack()

        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgcolor('lightblue')
        self.screen.tracer(0, 0)

        self.game = RunawayGame(self.screen, self.root)

    def start(self):
        self.game.start()
        self.screen.mainloop()

def main():
    app = App()
    app.start()

if __name__ == '__main__':
    main()
