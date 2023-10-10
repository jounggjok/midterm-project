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

        self.score = 0

        self.running = False
        self.tick_speed_ms = 1000 // 60

        self.current_level = None
        self.current_level_id = 0

        self.load_level(self.current_level_id)

        self.pressed_keys = dict()

        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<KeyRelease>', self._on_key_release)
        self.last_time = None

    def reset(self):
        self.current_level_id = 0
        self.score = 0


        self.load_level(self.current_level_id)



    def _on_key_press(self, event):
        self.pressed_keys[event.keysym] = True

    def _on_key_release(self, event):
        self.pressed_keys[event.keysym] = False

    def is_key_pressed(self, key):
        return key in self.pressed_keys and self.pressed_keys[key]
    
    def get_keys_pressed(self):
        return self.pressed_keys

    def load_level(self, level_id:int, seed:int=1337, score=0) -> None:
        
        self.score = score

        # delete turtle objects
        if self.current_level is not None:
            for child in self.current_level.children:
                if isinstance(child, AnimatedTurtle):
                    child.turtle.clear()
                    child.turtle.hideturtle()
                    child.turtle._tracer(1, 0)
                    del child.turtle

        self.last_time = time.time()
        self.current_level = Level(self, level_id, seed)
        self.current_level.score = self.score

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


class GOIterator:
    def __init__(self, obj):
        self.obj = obj
        self.index = 0
        self.i = 0

    def _get_go(self, go):
        for child in go.children:
            if self.i > self.index:
                raise StopIteration
            if self.i == self.index:
                return child
            self.i += 1

            result = self._get_go(child)
            if result is not None:
                return result
        raise StopIteration

            
        

        

    def __next__(self):
        self.i = 0
        e = self._get_go(self.obj)
        self.index += 1
        return e

    def __iter__(self):
        return self

@dataclass
class GameObject:
    game: RunawayGame
    x: float = 0
    y: float = 0
    direction: Direction = Direction.UP
    x_vel: float = 0
    y_vel: float = 0
    children: list = field(default_factory=list)
    radius: float = 10
    parent = None


    def __init__(self, game: RunawayGame, **kwargs):
        self.game = game
        self.children : list[GameObject] = []
        self.__dict__.update(kwargs)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

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

    def __iter__(self):
        return GOIterator(self)
    
    def get_distance(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def get_distance_squared(self, other):
        return (self.x - other.x)**2 + (self.y - other.y)**2
    
    def get_collision(self, other):
        return self.get_distance_squared(other) < (self.radius + other.radius)**2
    
    def remove(self, child):
        self.children.remove(child)

    def remove_me(self):
        if self.parent is not None:
            self.parent.remove(self)


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


class PowerUp(GameObject):
    """gives the turtle a speedboost"""

    def __init__(self, game: RunawayGame, duration: int, boost: int = 2, score: int = 50, **kwargs):
        super().__init__(game, **kwargs)
        self.duration = duration
        self.boost = boost
        self.score = score

    def tick(self, dt: float):
        # check if level is running
        if not self.game.get_current_level().is_running():
            return
        # check for collision with turtle
        for child in self.game.get_current_level().children:
            if isinstance(child, MovingTurtle):
                if self.get_collision(child):
                    child.boost_timer = self.duration
                    child.boost_multiplier = self.boost if child.boost_multiplier < self.boost else child.boost_multiplier

                    # add score
                    self.game.get_current_level().score += self.score

                    self.remove_me()
                    break

        super().tick(dt)

    def draw(self, pen: turtle.RawTurtle):
        pen.penup()
        pen.goto(self.x, self.y)
        pen.pendown()
        pen.color('gold')
        pen.begin_fill()
        pen.circle(self.radius)
        pen.end_fill()
                



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


        self.generate_level()
        self.caught = False
        self.added_game_over = False
        self.added_level_clear = False

    def is_running(self):
        return self.timer > 0 and not self.caught and self.time > 2

    def generate_level(self):
        """
        Generates the level based on id and seed
        """
        random.seed(self.seed+self.id)
        self.timer = 10 + self.id * 2

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


        # add some random powerups
        for _ in range(3+random.randint(0, 4)):
            powerup = PowerUp(
                self.game,
                random.randint(5, 10),
                random.random()+1,
                x = random.randint(-400, 400),
                y = random.randint(-400, 400)
            )

            self.add_child(powerup)

        
        # add ai turtles
        ai_count = 1 + math.floor(self.id / 1.2 * random.random())
        easy_chance = 1 / (1 + self.id / 2)

        for _ in range(ai_count):
            speed = 1 + random.random() * self.id / 20
            # pos not in player radius
            pos = (random.randint(-400, 400), random.randint(-400, 400))
            while abs(pos[0] - self.player.x) < 100 and abs(pos[1] - self.player.y) < 100:
                pos = (random.randint(-400, 400), random.randint(-400, 400))

            if random.random() < easy_chance:
                ai = AITurtle(
                    self.game,
                    x = pos[0],
                    y = pos[1],
                    speed = speed
                )

            else:
                ai = AI2000Turtle(
                    self.game,
                    x = pos[0],
                    y = pos[1],
                    speed = speed
                )

            self.add_child(ai)



    def tick(self, dt: float):

        # check if out of bounds
        if self.player.x < -400 or self.player.x > 400 or self.player.y < -400 or self.player.y > 400:
            self.caught = True

        if self.caught:

            # check if R is pressed
            if self.game.is_key_pressed('r'):
                self.game.reset()
                return

            if not self.added_game_over:
                self.added_game_over = True

                game_over = TextObject(
                    self.game,
                    lambda: f"Game Over! Score: {math.ceil(self.score):,}\nPress R to restart",
                    position=(-200, 0),
                    font=('Arial', 32, 'normal'),
                    color='red'
                )

                self.add_child(game_over)

            return
        
        if self.timer <= 0:
            # add level clear text
            if not self.added_level_clear:
                self.added_level_clear = True

                level_clear = TextObject(
                    self.game,
                    lambda: f"Level Completed! Score: {math.ceil(self.score):,}\nPress SPACE to continue",
                    position=(-300, 0),
                    font=('Arial', 32, 'normal'),
                    color='red'
                )

                self.add_child(level_clear)

            # check if space is pressed
            if self.game.is_key_pressed('space'):
                self.game.load_level(self.id+1, self.seed, self.score)
                return
            return

        self.time += dt
        self.timer -= dt
        self.score += dt * 10

    def is_completed(self):
        return self.timer <= 0
    
    def get_score(self):
        return self.score
    
    def draw(self, pen: turtle.RawTurtle):
         # draw red border
        pen.penup()
        pen.goto(-400, -400)
        pen.pendown()
        pen.color('red')
        pen.pensize(3)
        pen.goto(-400, 400)
        pen.goto(400, 400)
        pen.goto(400, -400)
        pen.goto(-400, -400)
        pen.pensize(1)

        super().draw(pen)



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
        self.boost_multiplier: float = 1.0
        self.boost_timer: float = 0.0
        self.radius = 13

    def _tick(self, dt: float):
        if not self.game.get_current_level().is_running():
            return
        super()._tick(dt)

    def tick(self, dt: float) -> None:
        """
        Called every frame, moves the turtle"""

        self.boost_timer -= dt
        if self.boost_timer < 0:
            self.boost_timer = 0

        super().tick(dt)

    def move_direction(self, direction: Direction) -> None:
        match direction:
            case Direction.LEFT:
                self.left()
            case Direction.RIGHT:
                self.right()
            case Direction.UP:
                self.up()
            case Direction.DOWN:
                self.down()

    def get_speed(self):
        if self.boost_timer > 0:
            return self.speed * self.boost_multiplier * self.step_size
        else:
            return self.speed * self.step_size

    def left(self) -> None:
        self.direction = Direction.LEFT
        self.turtle.setheading(self.direction.value * 90)
        self.x -= self.get_speed()
        
        self.turtle.setpos(self.x, self.y)

    def right(self) -> None:
        self.direction = Direction.RIGHT
        self.turtle.setheading(self.direction.value * 90)
        self.x += self.get_speed()
        self.turtle.setpos(self.x, self.y)

    def up(self) -> None:
        self.direction = Direction.UP
        self.turtle.setheading(self.direction.value * 90)
        self.y += self.get_speed()
        self.turtle.setpos(self.x, self.y)

    def down(self) -> None:
        self.direction = Direction.DOWN
        self.turtle.setheading(self.direction.value * 90)
        self.y -= self.get_speed()
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
        self.turtle.color('blue')
        self.speed = 1.3

    def tick(self, dt: float) -> None:
        """
        Called every frame, moves the player"""

        super().tick(dt)

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
            pass
            #self.speed = 2.0
        else:
            self.speed = 1.0


class AITurtle(MovingTurtle):
    def __init__(self, game: RunawayGame, **kwargs):
        super().__init__(game, **kwargs, step_size=10)
        self.player = None

    
    def get_player(self):
        if self.player is None:
            for child in self.game.get_current_level().children:
                if isinstance(child, Player):
                    self.player = child
                    break
        return self.player

    def do_movement(self):

        # 90% chance to move forward
        if random.random() < 0.9:
            self.move_direction(self.direction)
            return
        

        # 20% chance to move left or right randomly
        if random.random() < 0.2:
            self.direction = Direction((self.direction.value + random.choice([-1, 1]))%4)
            self.move_direction(self.direction)
            return


        player = self.get_player()
        if player is None:
            return
        
        
        # get direction to player
        dx = player.x*1.2 - player.x*0.4*random.random() - self.x
        dy = player.y- player.y*0.4*random.random() - self.y

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

    
    def tick(self, dt: float) -> None:
        """
        Called every frame, moves the turtle"""

        super().tick(dt)

        player = None
        for child in self.game.get_current_level().children:
            if isinstance(child, Player):
                player = child
                break

        if player is None:
            return
        
        # check if caught
        if self.get_collision(player):
            self.game.get_current_level().caught = True
            return
        
        self.do_movement()

class AI2000Turtle(AITurtle):
    def __init__(self, game: RunawayGame, **kwargs):
        super().__init__(game, **kwargs)
        self.turtle.color('black')
        self.ratio = random.random()
        self.speed = 0.8

    def do_movement(self):
        player = self.get_player()


        # 80% chance to move forward
        if random.random() < 0.8:
            self.move_direction(self.direction)
            return

        if player is None:
            return
        

        powerups = []
        for child in self.game.get_current_level().children:
            if isinstance(child, PowerUp):
                powerups.append((child, self.get_distance(child)))

        powerups.sort(key=lambda x: x[1])
        
        # try to predict player position
        distance = self.get_distance(player)
        time = distance / self.get_speed()
        
        px = player.x
        py = player.y

        match player.direction:
            case Direction.UP:
                py += player.get_speed() * time
            case Direction.DOWN:
                py -= player.get_speed() * time
            case Direction.LEFT:
                px -= player.get_speed() * time
            case Direction.RIGHT:
                px += player.get_speed() * time

        # get direction to player
        dx = px - self.x
        dy = py - self.y

        dpx = player.x - self.x
        dpy = player.y - self.y

        ratio = self.ratio
        dx = dx * ratio + dpx * (1 - ratio)
        dy = dy * ratio + dpy * (1 - ratio)

        # if powerup is closer than player/2, go for it
        if len(powerups) > 0 and powerups[0][1] < distance / 2:
            dx = powerups[0][0].x - self.x
            dy = powerups[0][0].y - self.y

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
