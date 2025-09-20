import arcade
import logging

#CONSTANTs
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
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
        def __init__(self, circle_x = 200,circle_y = 200):
            self.circle_x = circle_x
            self.circle_y = circle_y
            self.speed_x = 200
            self.speed_y = 200
            self.radius = 15
            log.info(f"Golf ball created. " + ", ".join(f"{k} = {v}" for k,v in vars(self).items()))

        def draw_ball(self):
            arcade.draw_circle_filled(self.circle_x,self.circle_y,self.radius,arcade.color.WHITE)
            log.debug(f"Ball positioned at {self.circle_x,self.circle_y}")

        def move_ball(self, change_x, change_y):
            self.circle_x += self.speed_x * change_x
            self.circle_y += self.speed_y * change_y
            log.debug(f"circle_x = {self.circle_x}, circle_y = {self.circle_y}")


class GameView(arcade.Window):
    '''
    Main application class
    '''

    def __init__(self):
        #Call to set up window:
        super().__init__(WINDOW_WIDTH,WINDOW_HEIGHT,WINDOW_TITLE)
        self.background_color = arcade.csscolor.BLACK
           

    def setup(self):
        """
        Set up the core game here.  Call to restart game.
        """
        self.golf_ball = GolfBall(200,200)    

    def on_update(self, delta_time) -> None:
        self.golf_ball.move_ball(delta_time,delta_time)
        pass

    def on_draw(self):
        self.clear()
        self.golf_ball.draw_ball()
        self.position = (self.golf_ball.circle_x,self.golf_ball.circle_y)
        #print(self.position)


def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    log = start_logging()
    main()