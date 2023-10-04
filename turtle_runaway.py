# This example is not working in Spyder directly (F5 or Run)
# Please type '!python turtle_runaway.py' on IPython console in your Spyder.
import tkinter as tk
import turtle, random
import math
from enum import Enum
from dataclasses import dataclass, field

class RunawayGame:
    def __init__(self, screen : turtle.TurtleScreen):
        self.screen = screen

        # Instantiate an another turtle for drawing
        self.drawer = turtle.RawTurtle(screen)
        self.drawer.hideturtle()
        self.drawer.penup()

        self.sprites = {}

        self.running = False
        self.tick_speed_ms = 1000 // 60

    def load_sprite(self, filename:str, scale=1, size=None) -> str:
        if filename in self.sprites:
            return self.sprites[filename]

        self.screen.register_shape(filename)
        self.sprites[filename] = filename
        return filename
        
    def loop(self):
        if not self.running:
            return
        
        self.screen.ontimer(self.loop, self.tick_speed_ms)


    def start(self):

        if self.running:
            return
        
        self.running = True

        self.screen.ontimer(self.loop, self.tick_speed_ms)



# direction enum
class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
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
    


class Level(GameObject):
    def __init__(self, game: RunawayGame, id:int, seed:int=1234, **kwargs):
        super().__init__(game, **kwargs)
        self.id : int = id
        self.seed : int = seed

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
        self.turtle.speed(0.5)

    def left(self) -> None:
        self.direction = Direction.LEFT
        self.turtle.setheading(self.direction.value * 90)
        self.x -= self.step_size
        
        self.turtle.setpos(self.x, self.y)

    def right(self) -> None:
        self.direction = Direction.RIGHT
        self.turtle.setheading(self.direction.value * 90)
        self.x += self.step_size
        self.turtle.setpos(self.x, self.y)

    def up(self) -> None:
        self.direction = Direction.UP
        self.turtle.setheading(self.direction.value * 90)
        self.y += self.step_size
        self.turtle.setpos(self.x, self.y)

    def down(self) -> None:
        self.direction = Direction.DOWN
        self.turtle.setheading(self.direction.value * 90)
        self.y -= self.step_size
        self.turtle.setpos(self.x, self.y)

    def draw(self, _: turtle.RawTurtle) -> None:
        # set position just in case
        self.turtle.setpos(self.x, self.y)
        return super().draw(_) # type: ignore
    

class Player(MovingTurtle):
    def __init__(self, game: RunawayGame, **kwargs):
        super().__init__(game, **kwargs, step_size=10)
        #self.turtle.shape(game.load_sprite('player.gif'))
        self.last_key = None

        self._register_controls(game.screen)

    def tick(self, dt: float) -> None:
        """
        Called every frame, moves the player"""
        if self.last_key is None:
            return
        
        match self.last_key:
            case Direction.LEFT:
                self.left()
            case Direction.RIGHT:
                self.right()
            case Direction.UP:
                self.up()
            case Direction.DOWN:
                self.down()
            case _:
                pass

        # remove this to make the player move continuously
        self.last_key = None

    def _set_last_key(self, direction: Direction) -> None:
        self.last_key = direction

    def _register_controls(self, canvas: tk.Canvas) -> None:
        canvas.onkeypress(lambda: self._set_last_key(Direction.UP), 'Up')
        canvas.onkeypress(lambda: self._set_last_key(Direction.DOWN), 'Down')
        canvas.onkeypress(lambda: self._set_last_key(Direction.LEFT), 'Left')
        canvas.onkeypress(lambda: self._set_last_key(Direction.RIGHT), 'Right')
        canvas.listen()



class ManualMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn

        # Register event handlers
        canvas.onkeypress(lambda: self.forward(self.step_move), 'Up')
        canvas.onkeypress(lambda: self.backward(self.step_move), 'Down')
        canvas.onkeypress(lambda: self.left(self.step_turn), 'Left')
        canvas.onkeypress(lambda: self.right(self.step_turn), 'Right')
        canvas.listen()

    def run_ai(self, opp_pos, opp_heading):
        pass

class RandomMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn

    def run_ai(self, opp_pos, opp_heading):
        mode = random.randint(0, 2)
        if mode == 0:
            self.forward(self.step_move)
        elif mode == 1:
            self.left(self.step_turn)
        elif mode == 2:
            self.right(self.step_turn)

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Turtle Runaway')

        self.canvas = tk.Canvas(self.root, width=800, height=800)
        self.canvas.pack()

        self.screen = turtle.TurtleScreen(self.canvas)

        self.game = RunawayGame(self.screen)

    def start(self):
        self.game.start()
        self.screen.mainloop()

def main():
    app = App()
    app.start()

if __name__ == '__main__':
    main()
