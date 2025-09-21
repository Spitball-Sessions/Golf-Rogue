import arcade
import logging
import random
import math
from collections import namedtuple as nt

#CONSTANTs
SCREEN_WIDTH = 1280 #right edge
SCREEN_HEIGHT = 720 #top edge
#(0,0) is bottom left.  (1280,720) is top right
WINDOW_TITLE = "Golf Game"
LOG_LEVEL = "INFO"


def start_logging():
    log = logging.getLogger(__name__)
    log.setLevel(LOG_LEVEL)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)s:%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log

class GolfBall():
        def __init__(self, cx = 200,cy = 200):
            self.cx = cx
            self.cy = cy
            self.vx = 150
            self.vy = 150
            self.radius = 10
            self.circumference = 2*math.pi*self.radius
            self.area = math.pi*(self.radius*self.radius)
            self.position = arcade.Text(f"Position: ({self.cx},{self.cy})", x = 20, y = SCREEN_HEIGHT - 20)

            log.info(f"Golf ball created. " + ", ".join(f"{k} = {v}" for k,v in vars(self).items() if isinstance(v,( int,float))))

        def draw(self):
            arcade.draw_circle_filled(self.cx, self.cy,self.radius,arcade.color.WHITE)
            arcade.draw_circle_outline(self.cx,self.cy,self.radius,arcade.color.ORANGE,border_width=2)
            log.debug(f"Ball positioned at {self.cx, self.cy}")

        def move_ball(self, change_x, change_y):
            self.cx += self.vx * change_x
            self.cy += self.vy * change_y
            log.debug(f"circle_x = {self.cx}, circle_y = {self.cy}")

        def locate_ball(self, left, bottom, width, height):
            self.position.text = f"Position: ({self.cx},{self.cy})"

            self.near_sides = (self.cx - self.radius) < left or (self.cx + self.radius) > (left+width)
            self.near_top_bottom = (self.cy - self.radius) < bottom or (self.cy + self.radius) > (bottom+height)

        def ball_bounce(self):
            if self.near_sides:
                self.vx = -1 * self.vx
            if self.near_top_bottom:
                self.vy = -1 * self.vy
            else:
                pass


class Level():
    def __init__(self):
        self.rooms = []
        self.create_room()

    def create_room(self):
        Room = nt("Room",["left","bottom", "width", "height"])

        left = random.randrange(50,300)
        bottom = random.randrange(100,300)
        width = random.randrange(200,600)
        height = random.randrange(100,400)
        room =  Room(left, bottom, width, height)
        self.rooms.append(room)
        log.info(f"Created room at: {room.left, room.bottom} that extends to {room.left+room.width, room.bottom + room.height}")

    def draw_room(self):
        for room in self.rooms:
            arcade.draw_lbwh_rectangle_filled(*room,color=arcade.color.GRANNY_SMITH_APPLE)


class GameView(arcade.Window):
    '''
    Main application class
    '''

    def __init__(self):
        #Call to set up window:
        super().__init__(SCREEN_WIDTH,SCREEN_HEIGHT,WINDOW_TITLE)
        self.background_color = arcade.csscolor.BLACK
        self.test_text = arcade.Text("",x = 400, y = 400)
        
           

    def setup(self):
        """
        Set up the core game here.  Call to restart game.
        """
        self.level = Level()
        gbx = self.level.rooms[0].left + 40
        gby = self.level.rooms[0].bottom + 40
        
        self.golf_ball = GolfBall(gbx,gby)    

    def on_update(self, delta_time) -> None:
        self.golf_ball.move_ball(delta_time,delta_time)
        for room in self.level.rooms:
            self.golf_ball.locate_ball(*room)
        self.golf_ball.ball_bounce()
        

    def on_draw(self):
        self.clear()
        self.level.draw_room()
        self.golf_ball.draw()
        self.golf_ball.position.draw()
        self.test_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.setup()

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    
    def on_mouse_press(self, x, y, button, modifiers):
        self.golf_ball.vx = ((x - (SCREEN_WIDTH/2)) /3)
        self.golf_ball.vy = ((y - (SCREEN_HEIGHT/2)) /3)

        self.test_text.text = f"golf ball velocity is {self.golf_ball.vx, self.golf_ball.vy}"
        self.test_text.x = x
        self.test_text.y = y
  
    

        

        


def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    log = start_logging()
    main()