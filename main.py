import arcade, logging, random, math
from collections import namedtuple as nt

#CONSTANTs
SCREEN_WIDTH = 1280 #right edge
SCREEN_HEIGHT = 720 #top edge
#(0,0) is bottom left.  (1280,720) is top right
WINDOW_TITLE = "Golf Game"
LOG_LEVEL = "INFO"
FRICTION = .98


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
        self.create_meters()
        self.cx = cx
        self.cy = cy
        self.vx = self.vy = 0
        self.dx = self.dy = 0
        self.radians = 0
        self.radius = 10
        self.apply_friction = False
        self.circumference = 2*math.pi*self.radius
        self.area = math.pi*(self.radius*self.radius)
        self.position = arcade.Text(f"Position: ({self.cx},{self.cy})", x = 20, y = SCREEN_HEIGHT - 20)

        log.info(f"Golf ball created. " + ", ".join(f"{k} = {v}" for k,v in vars(self).items() if isinstance(v,( int,float))))
   
    def create_meters(self):
        """
        Initializes shot, accuracy and aim meters. 
        """
        #Shot Meter Stage affects swing meter.
        self.shot_meter_stage = 0
        #Shot Meter is Power
        self.power_meter = 0
        self.power_meter_direction = "Up"
        self.power_meter_display = arcade.Text(f"{self.power_meter:.1f}",x = 1220, y = 40)

        #accuracy meter is curve
        self.accuracy_meter = -50
        self.accuracy_meter_direction = "Up"
        self.accuracy_meter_display = arcade.Text(f"{self.accuracy_meter:.1f}", x=1220, y = 20)

        #aim is positional
        self.aim_position = (0,0)
        self.aim_meter = 0
        self.aim_meter_display = arcade.Text(f"Aim: {self.aim_meter}", x = 20, y = 20)

    def update_shot_meter(self,delta_time):
        """
        Handles the Power and Accuracy meters.  Currently 5 stages - start, set power, start accuracy, set accuracy, reset. Will condense to 3 after debugging.
        """
        #When mouse is clicked, starts power bar.  Bar goes up till it hits 100, then goes back down.
        if self.shot_meter_stage == 2:
            if self.power_meter_direction == "Up":
                self.power_meter +=.75+(1*delta_time)
                if self.power_meter > 100:
                    self.power_meter_direction = "Down"
            if self.power_meter_direction == "Down":
                self.power_meter -=.75 + (1*delta_time)
                if self.power_meter < 0:
                    self.power_meter_direction = "Up"
            self.power_meter_display.text = f"{self.power_meter:.1f}"

        #Second click freezes shot meter and displays power.

        #Third click starts accuracy bar.  -50 = Hard Left, +50 = Hard Right
        elif self.shot_meter_stage == 3:
            self.power_meter = self.power_meter
            self.power_meter_display.text = f"{self.power_meter:.1f}"
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
            self.power_meter = 0
            self.accuracy_meter = 0
            self.power_meter_display.text = f"{self.power_meter:.1f}"
            self.accuracy_meter_display.text = f"{self.accuracy_meter:.1f}"

    def calculate_aim(self, x, y):
        '''
        Calculates angle of shot based on mouse location relative to the ball.  (Tangent of (mouse.y - ball),(mouse.x - ball))
        Args:
        * x = mouse x
        * y = mouse y
        '''
        self.aim_position = (x,y)
        self.dx = x - self.cx
        self.dy = y - self.cy
        self.radians = math.atan2(self.dy, self.dx)
        self.aim_meter_display.text = f"Aim: {math.degrees(self.radians)}"

    def calculate_trajectory(self):
        '''
        The formulas to convert the golf swing to actually move the ball.
        Takes offset, applies to angle (self.radians), then multiplies by power to get vector.  Vector is then applied during updates.
        '''
        max_offset_degrees = 15
        offset_degrees = (self.accuracy_meter / 50) * max_offset_degrees
        adjusted_angle = self.radians + math.radians(offset_degrees)
        log.debug(f'Angle = {math.degrees(self.radians)}, Speed = {self.power_meter}, Accuracy = {self.accuracy_meter}, Adjusted angle = {math.degrees(adjusted_angle)}.')

        self.vx = math.cos(adjusted_angle) * self.power_meter * 5
        self.vy = math.sin(adjusted_angle) * self.power_meter * 5

        self.shot_meter_stage = 0

    def draw_meters(self):
        self.position.draw()
        self.power_meter_display.draw()
        self.accuracy_meter_display.draw()
        self.aim_meter_display.draw()

    def draw_ball(self):
        arcade.draw_circle_filled(self.cx, self.cy,self.radius,arcade.color.WHITE)
        arcade.draw_circle_outline(self.cx,self.cy,self.radius,arcade.color.ORANGE,border_width=2)
        log.debug(f"Ball positioned at {self.cx, self.cy}")

    def move_ball(self, delta_time):
        """applies change vectors to the ball position.  
            
            Args:
                * Change_x = x-axis velocity * delta_time 
                * Change_y = y-axis velocity * delta_time
            """

        self.cx += self.vx * delta_time 
        self.cy += self.vy * delta_time

        #Slows ball by Friction constant.  self.apply_friction = true after 2.25 seconds
        if self.apply_friction:
            self.vy = self.vy * FRICTION
            self.vx = self.vx * FRICTION

        #Stops ball once it slows below a certain speed.  If I go higher than 3, it seems to break the collision logic.
        if abs(self.vy) < 1 and abs(self.vx) < 1:
            self.cx += 0
            self.cy += 0
            self.vy = self.vx = 0
            self.apply_friction = False
        
        log.debug(f"vx = {self.vx}, vy = {self.vy}")

    def handle_collisions(self, left, bottom, width, height):
            """
            If collision detected, this inverts the velocity for the direction collision is detected on.
            Dual if's allow for handling corners.
            """
            self.position.text = f"Position: ({self.cx},{self.cy})"

            self.near_sides = (self.cx - self.radius) < left or (self.cx + self.radius) > (left+width)
            self.near_top_bottom = (self.cy - self.radius) < bottom or (self.cy + self.radius) > (bottom+height)

            if self.near_sides and not self.last_near_sides:
                log.debug("near sides")
                self.vx = -1.1 * self.vx
                log.debug(f"new vx = {self.vx}")
            if self.near_top_bottom and not self.last_near_top_bottom:
                log.debug("near top/bottom")
                self.vy = -1.1 * self.vy
                log.debug(f"new_vy = {self.vy}")

            self.last_near_sides = self.near_sides
            self.last_near_top_bottom = self.near_top_bottom


class Room():
    def __init__(self):
        self.left = 0
        self.bottom = 0
        self.width = 0
        self.height = 0
        self.right = self.left + self.width
        self.top = self.bottom + self.height

    def __iter__(self):
        yield self.left
        yield self.bottom
        yield self.width
        yield self.height

    def create_room(self, left, bottom):

        if left == "random":
            self.left = random.randrange(50,300)
        else:
            self.left = left
        if bottom == "random":
            self.bottom = random.randrange(100,300)
        else:
            self.bottom = bottom
        self.width = random.randrange(200, 320)
        self.height = random.randrange(100,140)
        self.right = self.left + self.width
        self.top = self.bottom + self.height
        log.info(f"Created room at: {self.left, self.bottom} that extends to {self.right, self.top}")
        return self



class Level():
    def __init__(self):
        self.rooms = []
        self.level_size = 4
        self.build_level()

    def build_level(self):

  
        while len(self.rooms) < self.level_size:
            if not self.rooms:
                room = Room().create_room("random","random")
                self.rooms.append(room)
            else:
                previous_room = self.rooms[-1]  
                left = random.randrange(previous_room.left,previous_room.right)
                bottom = random.randrange(previous_room.bottom, previous_room.top)
                room = Room().create_room(left, bottom)
                self.rooms.append(room)


        
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
        #allows debugging on screen
        self.test_text = arcade.Text("",x = 400, y = 400)

        self.timer = 0
    
    def setup(self):
        """
        Set up the core game here.  Call to restart game.
        """
        self.level = Level()
        gbx = self.level.rooms[0].left + 40
        gby = self.level.rooms[0].bottom + 40
        
        self.golf_ball = GolfBall(gbx,gby)          

    def on_update(self, delta_time) -> None:

        for room in self.level.rooms:
            self.golf_ball.handle_collisions(*room)

        if self.timer:
            self.timer += 1*delta_time
  
        if self.timer > 2.25:
            self.timer = 0
            self.golf_ball.apply_friction = True
            
        self.golf_ball.move_ball(delta_time)
        self.golf_ball.update_shot_meter(delta_time)


    def on_draw(self):
        self.clear()
        self.level.draw_room()
        self.golf_ball.draw_ball()
        self.golf_ball.draw_meters()
        self.test_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.setup()

    def on_mouse_motion(self, x, y, dx, dy):
        pass
    
    def on_mouse_press(self, x, y, button, modifiers):

        if self.golf_ball.shot_meter_stage == 0:
            self.golf_ball.shot_meter_stage = 1
            self.golf_ball.calculate_aim(x,y)
        elif self.golf_ball.shot_meter_stage == 1:
            self.golf_ball.shot_meter_stage = 2
        elif self.golf_ball.shot_meter_stage == 2:
            self.golf_ball.shot_meter_stage = 3
        elif self.golf_ball.shot_meter_stage == 3:
            self.golf_ball.calculate_trajectory()
            self.timer = 1



def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    log = start_logging()
    main()