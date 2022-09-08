from typing import Tuple
import pygame, os, json, sys
from dotenv import load_dotenv

class Picker():
    '''
    The jubepicker class.
    '''
    def __init__(self, systemjson: dict):
        # First, we want to init everything
        self.system = systemjson
        self.binding = False
        self.run = True
        self.framerate = 900
        self.clock = pygame.time.Clock()
        self.resolution = (768, 1360) # Do not change! Assets will not scale.
        self.screen = None
        self.pygame_flags = pygame.FULLSCREEN|pygame.NOFRAME
        self.caption = 'soon...'
        self.timer = 25
        self.boot = None

        # We should load the system font path into a var. We'll do a simple check on it to be safe.
        font_path = './assets/fonts/copious-sans-medium.ttf'
        if os.path.exists(font_path):
            self.system_font = font_path
        else: raise Exception(f"Can't load the font! Please check that {font_path} exists!")

        # Joystick data
        self.joysticks = None

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
            self.boot = (game['title'], game['filepath'], i)
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

        # Wake up controller stuff.
        pygame.joystick.init()
        self.initControllers()

        # enter a loop.... FOREVERRRRRR (not true)
        self.theLoop()

    def initWindow(self):
        '''
        Init window name and icon.
        '''
        pygame.display.set_caption(f'JubePicker V1.0 ({self.caption})')
        pygame.display.set_icon(pygame.image.load('./assets/tex/icon.png'))

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
            sys.exit()
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
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Wipe data and trigger controller binding.
                    self.resetSystemData()
                    self.bindControllers()

            if event.type == pygame.MOUSEBUTTONDOWN:
                '''
                Handle mouse/touch.
                '''
                mouse_pos = pygame.mouse.get_pos()
                for i in range(16):
                    if self.buttons[i] == None:
                        continue
                    if self.rectangles[i]['x']+100 > mouse_pos[0] > self.rectangles[i]['x'] and self.rectangles[i]['y']+100 > mouse_pos[1] > self.rectangles[i]['y']:
                        if i == 15:
                            # Special stuff for start button
                            self.launchProgram()
                        self.boot = (self.buttons[i], self.files[i], i)

            elif event.type == pygame.JOYBUTTONDOWN:
                for i in self.system['controller']['bindings']:
                    button = i['button']
                    joystick = self.joysticks[i['controller']]['joystick']
                    bound = i['bound_to']

                    if joystick.get_button(bound) and self.buttons[button] != None:
                        if button == 15:
                            # Special stuff for start button
                            self.launchProgram()
                        self.boot = (self.buttons[button], self.files[button], button)
     
    def startWindow(self):
        '''
        Inits the PyGame window, sets all details.
        '''
        # Start display
        pygame.display.init()

        # We should init the caption and icon before the screen runs.
        self.initWindow()

        # Start the screen
        self.screen = pygame.display.set_mode(self.resolution, self.pygame_flags, display=0, vsync=1)
        print('Welcome to JubePicker!')

    def drawTexture(self, texture: pygame.Surface, coordinates: Tuple[int, int], size: Tuple[int, int] = None, direct: bool = False):
        # let's throw this on the screen.
        original_res = texture.get_size()
        textrect = texture.get_rect()
        textrect.center = coordinates
        if size != None:
            if direct:
                texture = pygame.transform.smoothscale(texture, (
                    int(original_res[0]/size[0]),
                    int(original_res[1]/size[1])
                ))
            else:
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

    def saveSystemData(self):
        '''
        Saves system.json
        '''
        file = open('./system.json', 'w')
        file.write(json.dumps(self.system, indent=4))
        file.close()

    def resetSystemData(self):
        '''
        Resets system.json
        '''
        self.system['firstboot'] = True
        self.system['controller']['used_buttons'] = []
        self.system['controller']['bindings'] = [None]*16
        for i in range(16):
            self.system['controller']['bindings'][i] = {
                "button": i,
                "controller": '',
                "bound_to": ''
            }
        self.saveSystemData()

    def initControllers(self):
        '''
        Init all controllers, get their data, store it.
        '''
        self.joysticks = []
        controllers = pygame.joystick.get_count()
        if controllers <= 0:
            print(f'\nNo plugged in controllers.\nUsing touch input.')
        print(f'\nFound {controllers} controller(s)')

        for controller in range(controllers):
            joystick = pygame.joystick.Joystick(controller)
            joystick.init()

            if joystick.get_numbuttons() >= 16:
                self.joysticks.append({
                    'id': controller,
                    'joystick': joystick,
                    'name': joystick.get_name(),
                    'buttons': joystick.get_numbuttons()
                })

        if len(self.joysticks) <= 0:
            print("\nCan't use any of the plugged in controllers!\nPlease make sure you have at least 16 buttons.\nUsing touch input.\n")
            return

        # Figure out if we need to bind.
        if self.system['firstboot']:
            self.binding = True
            print('\nBinding controllers for firstboot.')
            self.bindControllers()
        else:
            self.binding = False

        return

    def bindEventHandle(self):
        '''
        Handles binding events.
        '''
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                print('thank you for playing!')
                pygame.display.quit()
                sys.exit()

            if event.type == pygame.JOYBUTTONDOWN:
                for joystick in self.joysticks:
                    for button in range(joystick['buttons']):
                        joy = joystick['joystick']
                        if joy.get_button(button):
                            events.append((joystick['id'], button))
        return events

    def bindControllers(self):
        '''
        the controller binding loop.
        '''
        # Before we loop, let's load core screen things.
        background = pygame.image.load('./assets/tex/background.png')
        title = pygame.image.load('./assets/tex/title.png')
        button_frame = pygame.image.load('./assets/tex/button_frame.png')
        button_select = pygame.image.load('./assets/tex/button_select.png')

        print('\nNow binding controllers.\n')

        self.binding = True
        self.caption = 'binding controllers...'
        self.initWindow()

        bound = [False]*16

        while self.binding:
            bindings = self.system['controller']['bindings']
            for binding in bindings:
                while binding['bound_to'] == '':
                    # Headers
                    self.drawTexture(background, (0, 0))
                    self.drawTexture(title, (self.resolution[0]/5, 1), (120, 200))
                    self.drawText('Controller Binding', (100, 200, 200), self.resolution[0]/2, 260, 26, 1)
                    self.drawText('Buttons are in order from top left to bottom right.', (200, 100, 200), self.resolution[0]/2, 310, 15, 1)

                    # Let's draw the button frames. We'll make the ones that are bound glow.
                    x_offset = 200
                    y_offset = 195
                    x_stock = self.resolution[0]/200
                    frame_x = self.resolution[0]/200
                    frame_y = 600

                    i = 0
                    for a in range(4):
                        for b in range(4):
                            if bound[i]:
                                self.drawTexture(button_select, (frame_x, frame_y), (160, 280))
                            else:
                                self.drawTexture(button_frame, (frame_x, frame_y), (160, 280))
                            frame_x += x_offset
                            i+=1
                        frame_y += y_offset
                        frame_x = x_stock

                    events = self.bindEventHandle()
                    button = binding['button']
                    self.drawText(f'Press button {button+1}!', (200, 200, 200), self.resolution[0]/2, 370, 26, 1)

                    if len(events) == 1:
                        event = events[0]
                        if (event[0],event[1]) not in self.system['controller']['used_buttons']:
                            binding['controller'] = event[0]
                            binding['bound_to'] = event[1]
                            bound[button] = True
                            self.system['controller']['used_buttons'].append((event[0],event[1]))

                    pygame.display.update()
                    self.screen.fill(pygame.Color("black"))

            self.bindEventHandle()
            self.drawTexture(background, (0, 0))
            self.drawTexture(title, (self.resolution[0]/5, 1), (55, 100))
            self.drawText('Controller binding complete!', (100, 200, 200), self.resolution[0]/2, 260, 26, 1)

            pygame.display.update()
            self.screen.fill(pygame.Color("black"))
            self.system['firstboot'] = False
            self.saveSystemData()
            self.binding = False

    def theLoop(self):
        '''
        The menu loop.
        '''
        # Before we loop, let's draw core screen things.
        background = pygame.image.load('./assets/tex/background.png')
        title = pygame.image.load('./assets/tex/title.png')
        subtitle = pygame.image.load('./assets/tex/subtitle.png')
        button_frame = pygame.image.load('./assets/tex/button_frame.png')
        button_select = pygame.image.load('./assets/tex/button_select.png')
        button = pygame.image.load('./assets/tex/button.png')

        # We made it!
        self.caption = 'pick a game!'

        # here we go!
        while self.run:
            # First things first, we refresh events.
            self.eventHandler()

            # Tick the clock for good luck!
            self.clock.tick(self.framerate)

            # Update menu status bar
            self.initWindow()

            # Headers
            self.drawTexture(background, (0, 0))
            self.drawTexture(title, (self.resolution[0]/5, 1), (120, 200))
            self.drawTexture(subtitle, (self.resolution[0]/8, 210), (145, 250))

            # Auto start message
            clock = self.clock
            dt = clock.tick(15) / 1000
            self.timer -= dt
            no_newline = self.boot[0].replace('\n', ' ')
            secs = str(self.timer).replace('-','').replace('.',' ')[:2]
            message = f'{no_newline} will boot automatically in {secs} secs.'
            if len(message.split('\n')) == 2:
                txtoffset = -20
            else:
                txtoffset = 0

            if self.timer <= 0:
                self.run = False

            for e in message.split('\n'):
                self.drawText(e, (255, 100, 100), self.resolution[0]/2, 420+txtoffset, 17, 1)
                txtoffset = 20

            # Let's draw the button frames
            x_offset = 200
            y_offset = 195
            x_stock = self.resolution[0]/200
            frame_x = self.resolution[0]/200
            frame_y = 600

            i = 0
            for a in range(4):
                for b in range(4):
                    if i == self.boot[2]:
                        self.drawTexture(button_select, (frame_x, frame_y), (160, 280))
                    else:
                        self.drawTexture(button_frame, (frame_x, frame_y), (160, 280))
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
                self.drawTexture(button, (rectangle['x']+13.5, rectangle['y']+13.5), (4.5, 4.5), direct = True)
                if len(self.buttons[i].split('\n')) == 2:
                    txtoffset = -20
                else:
                    txtoffset = 0

                for e in self.buttons[i].split('\n'):
                    self.drawText(e, (255, 255, 255), rectangle['x']+77, rectangle['y']+79+txtoffset, 21, 1)
                    txtoffset = 20
                i+=1

            # End the tick!
            pygame.display.update()
            self.screen.fill(pygame.Color("black"))
        self.launchProgram()


# Start the FEVER!
if __name__ == "__main__":
    # load the system.json
    if os.path.exists('./system.json'):
        systemjson = open('./system.json', 'r')
        json_read = json.loads(systemjson.read())
        systemjson.close()

    Picker(json_read)