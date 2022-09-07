from typing import Tuple
import pygame, os, json
from dotenv import load_dotenv

class Picker():
    '''
    The jubepicker class.
    '''
    def __init__(self):
        # First, we want to init everything
        self.run = True
        self.framerate = 90
        self.clock = pygame.time.Clock()
        self.resolution = (576, 1024)#(768, 1360)
        self.screen = None
        self.pygame_flags = 0 #pygame.FULLSCREEN|pygame.NOFRAME :: for testing.
        self.caption = 'soon...'
        self.timer = 25
        self.boot = None

        # Create some data vars
        self.rectangles = [None]*16
        self.buttons = [None]*16
        self.files = [None]*16
        self.buttons[15] = 'START!'

        # Read games.json to add buttons.
        i = 0
        games = json.loads(open('./games.json', 'r').read())
        for game in games:
            if i > 14:
                continue
            self.buttons[i] = game['title']
            self.boot = (game['title'], game['filepath'])
            self.files[i] = game['filepath']
            i+=1

        # Now we just light the fuse!
        self.startMenu()


    def startMenu(self):
        '''
        Used to setup the pygame window, and init pygame.
        '''
        # Wake up pygame
        pygame.init()

        # Set up the screen
        self.startWindow()

        # enter a loop.... FOREVERRRRRR (not true)
        self.theLoop()

    def launchProgram(self):
        '''
        GTFO, launch the game.
        '''
        clean_title = self.boot[0].replace('\n', ' ')
        self.screen.fill(pygame.Color("black"))
        print(self.boot)

        if os.path.exists(self.boot[1]):
            print(f'Starting {clean_title}, goodbye!')
            os.startfile(self.boot[1])
            exit()
        else:
            raise Exception(f"Can't load {self.boot[1]} for {clean_title}!\nPlease check your games.json file!")

    def eventHandler(self):
        '''
        Handles game events.
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                print('thank you for playing!')
                pygame.display.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # will be used for rebinding.
                    print('rebind comin soon :tm:')

            if event.type == pygame.MOUSEBUTTONDOWN:
                '''
                Handle mouse/touch.
                '''
                mouse_pos = pygame.mouse.get_pos()
                for i in range(16):
                    if self.buttons[i] == None:
                        continue
                    mouse_diff = (self.rectangles[i]['x']-mouse_pos[0], self.rectangles[i]['y']-mouse_pos[1])
                    if mouse_diff[0] <= 3 and mouse_diff[1] <= 1:
                        if i == 15:
                            # Special stuff for start button
                            self.launchProgram()
                        self.boot = (self.buttons[i], self.files[i])
     
    def startWindow(self):
        '''
        Inits the PyGame window, sets all details.
        '''
        # Start display
        pygame.display.init()

        # We should init the caption and icon before the screen runs.
        pygame.display.set_caption(f'JubePicker V0.1 ({self.caption})')
        pygame.display.set_icon(pygame.image.load('./assets/tex/icon.png'))

        # Start the screen
        self.screen = pygame.display.set_mode(self.resolution, self.pygame_flags, display=0, vsync=1)
        print('Welcome to JubePicker!')

    def drawTexture(self, texture: pygame.Surface, coordinates: Tuple[int, int], size: Tuple[int, int] = None):
        # let's throw this on the screen.
        original_res = texture.get_size()
        textrect = texture.get_rect()
        textrect.center = coordinates
        if size != None:
            texture = pygame.transform.smoothscale(texture, (
                int(size[0]*original_res[0]/self.resolution[0]),
                int(size[1]*original_res[1]/self.resolution[1])
            ))
        self.screen.blit(texture, coordinates)

    def drawText(self, text: str, color: tuple, x: int, y: int, size: int, align: int):
        font = pygame.font.Font(self.system_font, int(size*self.resolution[1]/768))
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()

        if align == 0:
            textrect.topleft = (x, y)
        elif align == 1:
            textrect.center = (x, y)
        elif align == 2:
            textrect.topright = (x, y)
        else: raise Exception('Unknown font position! Please use 0, 1, 2!')

        self.screen.blit(textobj, textrect)

    def theLoop(self):
        '''
        The menu loop.
        '''
        # Before we loop, let's draw core screen things.
        background = pygame.image.load('./assets/tex/background.png')
        title = pygame.image.load('./assets/tex/title.png')
        subtitle = pygame.image.load('./assets/tex/subtitle.png')
        button_frame = pygame.image.load('./assets/tex/button_frame.png')
        button = pygame.image.load('./assets/tex/button.png')

        # Now, we should load the system font path into a var. We'll do a simple check on it to be safe.
        font_path = './assets/fonts/copious-sans-medium.ttf'
        if os.path.exists(font_path):
            self.system_font = font_path
        else: raise Exception(f"Can't load the font! Please check that {font_path} exists!")

        # We made it!
        self.caption = 'pick a game!'

        # here we go!
        while self.run:
            # First things first, we refresh events.
            self.eventHandler()

            # Tick the clock for good luck!
            self.clock.tick(self.framerate)

            # Update menu status bar
            pygame.display.set_caption(f'JubePicker V0.1 ({self.caption})')

            # Headers
            self.drawTexture(background, (0, 0))
            self.drawTexture(title, (self.resolution[0]/5, 1), (55, 100))
            self.drawTexture(subtitle, (self.resolution[0]/8, 150), (77, 130))

            # Auto start message
            clock = self.clock
            dt = clock.tick(15) / 1000
            self.timer -= dt
            no_newline = self.boot[0].replace('\n', ' ')
            secs = str(self.timer).replace('-','').replace('.',' ')[:2]
            message = f'{no_newline} will boot automatically\nin {secs} secs.'
            if len(message.split('\n')) == 2:
                txtoffset = -20
            else:
                txtoffset = 0

            if self.timer <= 0:
                self.run = False

            for e in message.split('\n'):
                self.drawText(e, (255, 100, 100), 280, 320+txtoffset, 14, 1)
                txtoffset = 20

            # Let's draw the button frames.
            x_offset = 150
            y_offset = 150
            x_stock = self.resolution[0]/180
            frame_x = self.resolution[0]/180
            frame_y = 450

            i = 0
            for a in range(4):
                for b in range(4):
                    self.drawTexture(button_frame, (frame_x, frame_y), (90, 155))
                    self.rectangles[i] = {
                        'name': f'rect_{i}',
                        'x': (frame_x),
                        'y': (frame_y)
                    }
                    frame_x += x_offset
                    i+=1
                frame_y += y_offset
                frame_x = x_stock

            # Now, we add the real buttons.
            i = 0
            for rectangle in self.rectangles:
                if self.buttons[i] == None:
                    i+=1
                    continue
                self.drawTexture(button, (rectangle['x'], rectangle['y']), (90, 150))
                if len(self.buttons[i].split('\n')) == 2:
                    txtoffset = -20
                else:
                    txtoffset = 0

                for e in self.buttons[i].split('\n'):
                    self.drawText(e, (255, 255, 255), rectangle['x']+60, rectangle['y']+59+txtoffset, 21, 1)
                    txtoffset = 20
                i+=1

            # End the tick!
            pygame.display.update()
            self.screen.fill(pygame.Color("black"))
        self.launchProgram()


# Start the FEVER!
if __name__ == "__main__":
    # load the .env
    env_state = load_dotenv()
    if not env_state:
        raise Exception('Failed to load the .env file! Please reload your repo.')

    Picker()