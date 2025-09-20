import arcade

#CONSTANTs
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Golf Game"


class GameView(arcade.Window):
    '''
    Main application class
    '''

    def __init__(self):
        #Call to set up window:
        super().__init__(WINDOW_WIDTH,WINDOW_HEIGHT,WINDOW_TITLE)

        self.background_color = arcade.csscolor.DARK_GREEN


    def setup(self):
        """
        Set up the core game here.  Call to restart game.
        """

    def on_draw(self):
        
        self.clear()




def main():
    window = GameView()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()