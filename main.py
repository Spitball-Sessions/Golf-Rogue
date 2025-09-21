import arcade, logging, random, math
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
            self.vx = 0
            self.vy = 0
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
            """applies change vectors to the ball position.  
                
                Args:
                    * Change_x = x-axis velocity * delta_time 
                    * Change_y = y-axis velocity * delta_time
                """
            self.cx += self.vx * change_x
            self.cy += self.vy * change_y
            log.debug(f"circle_x = {self.cx}, circle_y = {self.cy}")

        def locate_ball(self, left, bottom, width, height):
            """
            Checks for collision with the sides of the course.  
            Checks left + bottom, then right (left + width) and top (bottom + height)

            Args:
                match to dimensions from Room (for now)
            """
            self.position.text = f"Position: ({self.cx},{self.cy})"

            self.near_sides = (self.cx - self.radius) < left or (self.cx + self.radius) > (left+width)
            self.near_top_bottom = (self.cy - self.radius) < bottom or (self.cy + self.radius) > (bottom+height)

        def ball_bounce(self):
            """
            If collision detected, this inverts the velocity for the direction collision is detected on.
            Dual if's allow for handling corners.
            """
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

    def set_aim(self, x, y):
        '''
        Calculates angle of shot based on mouse location relative to the ball.  (Tangent of (mouse.y - ball),(mouse.x - ball))
        Args:
        * x = mouse x
        * y = mouse y
        '''
        self.aim_position = (x,y)
        dx = x - self.center_x
        dy = y - self.center_y
        radians = math.atan2(dy, dx)
        self.aim_degrees = math.degrees(radians)
        self.aim_meter.text = f"Aim: {self.aim_degrees}"
 
    def change_shot_meter(self,delta_time):
        """
        Handles the Power and Accuracy meters.  Currently 5 stages - start, set power, start accuracy, set accuracy, reset. Will condense to 3 after debugging.
        """
        #When mouse is clicked, starts power bar.  Bar goes up till it hits 100, then goes back down.
        if self.shot_meter_stage == 1:
            if self.shot_meter_direction == "Up":
                self.shot_meter +=.75+(1*delta_time)
                if self.shot_meter > 100:
                    self.shot_meter_direction = "Down"
            if self.shot_meter_direction == "Down":
                self.shot_meter -=.75 + (1*delta_time)
                if self.shot_meter < 0:
                    self.shot_meter_direction = "Up"
            self.shot_meter_display.text = f"{self.shot_meter:.1f}"

        #Second click freezes shot meter and displays power.
        elif self.shot_meter_stage == 2:
            self.shot_meter = self.shot_meter
            self.shot_meter_display.text = f"{self.shot_meter:.1f}"

        #Third click starts accuracy bar.  -50 = Hard Left, +50 = Hard Right
        elif self.shot_meter_stage == 3:
            if self.accuracy_meter_direction == "Up":
                self.accuracy_meter +=.75+(1*delta_time)
                if self.accuracy_meter > 50:
                    self.accuracy_meter_direction = "Down"
            elif self.accuracy_meter_direction == "Down":
                self.accuracy_meter -=.75+(1*delta_time)
                if self.accuracy_meter < -50:
                    self.accuracy_meter_direction = "Up"
            self.accuracy_meter_display.text = f"{self.accuracy_meter:.1f}"

        
            #Need to do math

            
        elif self.shot_meter_stage == 0:
            #Resets meters
            self.shot_meter = 0
            self.accuracy_meter = 0
            self.shot_meter_display.text = f"{self.shot_meter:.1f}"
            self.accuracy_meter_display.text = f"{self.accuracy_meter:.1f}"


    def create_meters(self):
        """
        Initializes shot, accuracy and aim meters. 
        """
        #Shot Meter Stage affects swing meter.
        self.shot_meter_stage = 0
        #Shot Meter is Power
        self.shot_meter = 0
        self.shot_meter_direction = "Up"
        self.shot_meter_display = arcade.Text(f"{self.shot_meter:.1f}",x = 1220, y = 40)

        #accuracy meter is curve
        self.accuracy_meter = -50
        self.accuracy_meter_direction = "Up"
        self.accuracy_meter_display = arcade.Text(f"{self.accuracy_meter:.1f}", x=1220, y = 20)
    
        #aim is positional
        self.aim_position = (0,0)
        self.aim_degrees = 0
        self.aim_meter = arcade.Text(f"Aim: {self.aim_degrees}", x = 20, y = 20)

    def draw_meters(self):
        self.golf_ball.position.draw()
        self.shot_meter_display.draw()
        self.accuracy_meter_display.draw()
        self.aim_meter.draw()


    def setup(self):
        """
        Set up the core game here.  Call to restart game.
        """
        self.level = Level()
        gbx = self.level.rooms[0].left + 40
        gby = self.level.rooms[0].bottom + 40
        
        self.golf_ball = GolfBall(gbx,gby)    
 
        self.create_meters()


    def on_update(self, delta_time) -> None:
        self.golf_ball.move_ball(delta_time,delta_time)
        
        for room in self.level.rooms:
            self.golf_ball.locate_ball(*room)
        self.golf_ball.ball_bounce()

        self.change_shot_meter(delta_time)


    def on_draw(self):
        self.clear()
        self.level.draw_room()
        self.golf_ball.draw()
        self.draw_meters()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.setup()

    def on_mouse_motion(self, x, y, dx, dy):
        pass
    
    def on_mouse_press(self, x, y, button, modifiers):

        if self.shot_meter_stage == 0:
            self.shot_meter_stage = 1
            self.set_aim(x,y)
        elif self.shot_meter_stage == 1:
            self.shot_meter_stage = 2
        elif self.shot_meter_stage == 2:
            self.shot_meter_stage = 3
        elif self.shot_meter_stage == 3:
            self.shot_meter_stage = 4
        elif self.shot_meter_stage == 4:
            self.shot_meter_stage = 0







def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    log = start_logging()
    main()