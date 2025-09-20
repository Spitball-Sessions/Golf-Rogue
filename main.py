import arcade
import logging
import random
import math

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

        def locate_ball(self):
            self.position.text = f"Position: ({self.cx},{self.cy})"

            edge_distance = 30

            near_top_bottom = self.cx < edge_distance or self.cx > SCREEN_WIDTH - edge_distance
            near_sides = self.cy < edge_distance or self.cy > SCREEN_HEIGHT - edge_distance

            bounce_top_bottom = self.cx < (edge_distance - 10)  or self.cx > SCREEN_WIDTH -  (edge_distance - 10)
            bounce_sides = self.cy <  (edge_distance - 10) or self.cy > SCREEN_HEIGHT -  (edge_distance - 10)


            if near_top_bottom or near_sides:
                self.position.color = arcade.color.ORANGE
                if bounce_top_bottom:
                    self.vx = -1 * self.vx
                if bounce_sides:
                    self.vy = -1 * self.vy
                else:
                    pass
            else:
                self.position.color = arcade.color.WHITE


class Level():
    def __init__(self):
        self.room1 = self.create_room()

    def create_room(self):
        left = 100
        bottom = 100
        width = 600
        height = 250
        return (left, bottom, width, height)

    def draw_room(self):
        arcade.draw_lbwh_rectangle_filled(*self.room1,color=arcade.color.GRANNY_SMITH_APPLE)



class GameView(arcade.Window):
    '''
    Main application class
    '''

    def __init__(self):
        #Call to set up window:
        super().__init__(SCREEN_WIDTH,SCREEN_HEIGHT,WINDOW_TITLE)
        self.background_color = arcade.csscolor.BLACK
        self.room = Level()
           

    def setup(self):
        """
        Set up the core game here.  Call to restart game.
        """
        self.golf_ball = GolfBall(200,200)    
        self.room

    def on_update(self, delta_time) -> None:
        self.golf_ball.move_ball(delta_time,delta_time)
        self.golf_ball.locate_ball()

        pass

    def on_draw(self):
        self.clear()
        self.room.draw_room()
        self.golf_ball.draw()
        self.golf_ball.position.draw()
        

        


def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    log = start_logging()
    main()