import random
import time
import board
import displayio
import terminalio
import framebufferio
import rgbmatrix
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import adafruit_display_text.label

displayio.release_displays()

# set up the button input
button = DigitalInOut(board.D7)
button.direction = Direction.INPUT
button.pull = Pull.UP

# set up the potentiometer
pot = AnalogIn(board.A5)

#set up the LED display
panel = rgbmatrix.RGBMatrix(
    width=32, bit_depth=4,
    rgb_pins=[board.D8, board.D9, board.D10, board.D11, board.D12, board.D13],
    addr_pins=[board.D4, board.D5, board.D6],
    clock_pin=board.D1, latch_pin=board.D3, output_enable_pin=board.D2)
display = framebufferio.FramebufferDisplay(panel, auto_refresh=False)
SCALE = 1
matrix = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 10)
pixelColor = displayio.Palette(10)
tg1 = displayio.TileGrid(matrix, pixel_shader=pixelColor)
g1 = displayio.Group(scale=SCALE)
g1.append(tg1)
display.root_group = g1

# pallette color index numbers
BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, WHITE, LIME, AQUA = range(10)

# set pallette colors
pixelColor[BLACK] = 0x000000
pixelColor[RED] = 0xff0000
pixelColor[ORANGE] = 0xffa500
pixelColor[YELLOW] = 0xffff00
pixelColor[GREEN] = 0x008000
pixelColor[BLUE] = 0x0000ff
pixelColor[PURPLE] = 0xa020f0
pixelColor[WHITE] = 0xffffff
pixelColor[LIME] = 0x00ff00
pixelColor[AQUA] = 0x00ffff

# ---------------- Utility display functions ----------------

def print_text(inputText: str, value: str | int | None = None) -> None:
    '''
    # call this function with one or two arguments
    # the first argument will print on the top half of the display
    # the second argument (if provided) will print on the bottom half
    '''
    # first line
    topline = adafruit_display_text.label.Label(
        terminalio.FONT,
        color=0xffffff,
        text=inputText
    )
    topline.x = 0
    topline.y = 4

    textGroup = displayio.Group()
    textGroup.append(topline)

    # optional second line
    if value is not None:
        bottomline = adafruit_display_text.label.Label(
            terminalio.FONT,
            color=0xffffff,
            text=str(value)
        )
        bottomline.x = 0
        bottomline.y = 12
        textGroup.append(bottomline)

    display.root_group = textGroup

    display.refresh()

    display.root_group = g1

def fill_screen(color) -> None:
    # sets each pixel on the display to color
    for i in range(matrix.height * matrix.width):
        matrix[i] = color
    display.refresh()  

NUM_ENEMIES = 16

# ---------------- Invader ----------------
class Invader:
    def __init__(self, x_arg: int = 0, y_arg: int = 0, strength_arg: int = 0) -> None:
        self.x = x_arg
        self.y = y_arg
        self.strength = strength_arg

    def initialize(self, x_arg: int, y_arg: int, strength_arg: int) -> None:
        # initialize instance variables
        self.x = x_arg
        self.y = y_arg
        self.strength = strength_arg
    
    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_strength(self) -> int:
        return self.strength

    # Moves the Invader down the screen by one row
    # Modifies: y
    def move(self) -> None:
        self.y += 1

    def get_body_color(self):
        if self.strength == 1:
            return RED
        elif self.strength == 2:
            return ORANGE
        elif self.strength == 3:
            return YELLOW
        elif self.strength == 4:
            return GREEN
        elif self.strength == 5:
            return BLUE
        elif self.strength == 6:
            return PURPLE
        else:
            return WHITE
        
    # draws the Invader if its strength is greater than 0
    # use self.draw_with_rgb
    def draw(self) -> None:
        if self.strength > 0:
            body_color = self.get_body_color()
            self.draw_with_rgb(body_color, BLUE)

    # draws black where the Invader used to be
    # use self.draw_with_rgb
    def erase(self) -> None:
        if self.strength > 0:
            body_color = self.get_body_color()
            self.draw_with_rgb(BLACK, BLACK)

    # Invader is hit by a Cannonball.
    # Modifies: strength
    # calls: draw, erase
    def hit(self) -> None:
        self.strength -= 1
        self.erase()
        self.draw()

    # draws the Invader
    def draw_with_rgb(self, body_color: int, eye_color: int) -> None:
        left = self.x
        top = self.y
        matrix[left + 1, top] = body_color
        matrix[left + 2, top] = body_color
        matrix[left, top + 1] = body_color
        matrix[left + 1, top + 1] = eye_color
        matrix[left + 2, top + 1] = eye_color
        matrix[left + 3, top + 1] = body_color
        matrix[left, top + 2] = body_color
        matrix[left + 1, top + 2] = body_color
        matrix[left + 2, top + 2] = body_color
        matrix[left + 3, top + 2] = body_color
        matrix[left, top + 3] = body_color
        matrix[left + 3, top + 3] = body_color


# ---------------- Cannonball ----------------
class Cannonball:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # resets private data members to initial values
    def reset(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def has_been_fired(self) -> bool:
        return self.fired

    # sets private data members
    def fire(self, x_arg: int, y_arg: int) -> None:
        self.x = x_arg
        self.y = y_arg

    # moves the Cannonball and detects if it goes off the screen
    # Modifies: y, fired
    def move(self) -> None:
        if self.y >= 0:
            self.y -= 1
        else:
            self.reset()
        

    # resets private data members to initial values
    '''why do we have this as a separate function to reset()--------------------------------''' 
    def hit(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # draws the Cannonball, if it is fired
    def draw(self) -> None:
        left = self.x
        top = self.y
        matrix[left, top] = ORANGE
        matrix[left, top + 1] = ORANGE

    # draws black where the Cannonball used to be
    def erase(self) -> None:
        left = self.x
        top = self.y
        matrix[left, top] = BLACK
        matrix[left, top + 1] = BLACK


# ---------------- Player ----------------
class Player:
    def __init__(self) -> None:
        self.x = 0
        self.y = 14
        self.lives = 3

    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_lives(self) -> int:
        return self.lives

    # setter
    def set_x(self, x_arg: int) -> None:
        self.x = x_arg

    # Modifies: lives
    def die(self) -> None:
        self.lives -= 1

    # draws the Player
    # use self.draw_with_rgb
    def draw(self) -> None:
        self.draw_with_rgb(self, AQUA)

    # draws black where the Player used to be
    # use self.draw_with_rgb
    def erase(self) -> None:
        self.draw_with_rgb(self, BLACK)

    # resets private data members x and y to initial values
    def reset(self, x_arg: int, y_arg: int, lives_arg: int) -> None:
        self.x = x_arg
        self.y = y_arg
        ''' are we resetting the lives? ---------------------------------------- '''
        self.lives = lives_arg

    # draws the player
    def draw_with_rgb(self, color: int) -> None:
        left = self.x
        top = self.y
        matrix[left + 1, top] = color
        matrix[left, top + 1] = color
        matrix[left + 1, top + 1] = color
        matrix[left + 2, top + 1] = color

# ---------------- Game ----------------
class Game:
    def __init__(self) -> None:
        self.level: int = 1
        self.time: float = time.monotonic()
        self.move_time = time.monotonic()
        # suggested: you will want to add more attributes here
        # suggested - float for time for cannonball and invaders to move
        self.last_move: int = 0
        self.player: Player = Player()
        self.ball: Cannonball = Cannonball()
        self.enemies: list[Invader] = [Invader() for _ in range(NUM_ENEMIES)]

    # sets up a new game of Space Invaders
    def setup_game(self) -> None:
        fill_screen(BLACK)
        self.reset_level()

    # main loop (called repeatedly)
    def update(self, potentiometer_value: int, button_pressed: bool) -> None:
        # TODO
        
        matrix[4,7] = RED
        invader1 = Invader(4, 5, 1)
        invader2 = Invader(8, 5, 6)
        invader1.draw()
        invader2.draw()
        display.refresh()
        print(potentiometer_value)

        # suggested steps (check the Game Dynamics section of the specification for more)
        # 1. get the current time - this is a float in seconds
        # since the unit was powered on
        self.time = time.monotonic()

        # 2. check for collision with player
        if self.check_invader_collision():
            player.die()
            if player.get_lives() == 0:
                self.reset_level()

        # 3. update the player if potentiometer moved significantly
        # normalize
        player.setx(potentiometer_value // 1187)

        # 4. detect if should fire
        if button_pressed: 
            cannonball.fire(player.x + 1, player.y - 1)

        # 5. move cannonball if fired
        if self.time > cannonball.time + 0.1:
            cannonball.move()

        # 6. move invaders
        if self.time > invader.time + 0.5:
            '''
            check to make sure invader is within the screen 
            and that its not touching player
            '''
            # if 

            # erase each invader
            for invader in self.enemies:
                invader.erase()
            # move each invader down by 1 
                invader.move()
            # draw each invader
                invader.draw()

        # 7. check for cleared level

        return

    # this function might be useful in loop: check if Player defeated all Invaders
    def level_cleared(self) -> bool:
        # TODO
        pass
    
    # set up/reset a level
    def reset_level(self) -> None:
        # TODO
        # suggested steps:
        # 1. print level and lives

        # 2. reset the cannonball

        # 3. check for game over

        # 4. initialize invaders based on level
        
        # 5. draw enemies

        # 6. draw player

        # 7. reset time so invaders do not move immediately

        return

    # check if cannonball hits an invader
    def check_ball_collision(self) -> None:
        # TODO
        pass

    # check if invaders hit the player or bottom
    def check_invader_collision(self) -> bool:
        # TODO
        pass

# ---------------- Global game instance ----------------
game = Game()


# ---------------- Arduino-style setup and loop ----------------
def setup() -> None:
    game.setup_game()
    loop()

def loop() -> None:
    while True:
        game.update(pot.value, button.value)
