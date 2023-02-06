import pygame
import duck_chess

# initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound

# Create sprite class for the various piece
class PieceSprite(pygame.sprite.Sprite):
    def __init__(self, type: str, height: int, width: int, pos: tuple) -> None:
        super().__init__()
        
        self.image = pygame.image.load(f"Sprites\\{type}.png")
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0]*width, pos[1]*height

class DCRenderer():
    # Initialize the renderer and all associated variables
    def __init__(self, WIDTH: int, HEIGHT: int, TITLE: str, board: duck_chess.Board, FPS=30, colors: dict={}) -> None:
        # initialize pygame and create window
        pygame.init()
        pygame.mixer.init()  # For sound
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.width = int(WIDTH/8)
        self.height = int(HEIGHT/8)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()     # For syncing the FPS

        # group all the sprites together for ease of update
        self.pieces = pygame.sprite.Group()
        
        # Set other variables
        self.fps = FPS
        for color in colors.values():
            if type(color) != tuple:
                raise TypeError(message="Invalid color given: " + color)
        self.colors = colors
        self.running = True
        self.board = board
        self.should_update = True
        self.drawn_moves = []
        
    # Process input/events
    def processInputs(self) -> None:
        self.clock.tick(self.fps) # will make the loop run at the same speed all the time
        
        for event in pygame.event.get(): # gets all the events which have occured till now and keeps tab of them.
            # listening for the the X button at the top
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.board.setFEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
                self.addPieces()
                self.update(force=True)
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                x,y = pygame.mouse.get_pos()
                clicked_piece = False
                for piece in self.pieces.sprites():
                    if piece.rect.collidepoint(x, y):
                        if self.board.getTurn() == self.board.getPiece((int(piece.rect.x/self.width), int(piece.rect.y/self.height))).getColor():
                            clicked_piece = True
                            self.drawMoves(piece)
                            break
                
                if not clicked_piece:
                    for move in self.drawn_moves:
                        if move != self.drawn_moves[0] and move.collidepoint(x, y):
                            self.board.movePiece((int(self.drawn_moves[0].x/self.width), int(self.drawn_moves[0].y/self.height)), (int(move.x/self.width), int(move.y/self.height)))
                            self.addPieces()
                            break
                    self.should_update = True    
                
    # Tells the renderer when to update the pieces, so it doesn't draw when nothing changes
    def update(self, force:bool = False) -> None:
        if self.should_update or force:
            self.draw("board", ["White", "Black"])
            self.draw("pieces", [])
            self.drawn_moves = []
            self.should_update = False
    
    # Draw various things
    def draw(self, function, color: list) -> None:
        # Fill the whole screen
        if function == "fill":
            self.screen.fill(self.colors[color[0]])
        
        # Draw a chess board
        elif function == "board":
            square_color = 0
            for row in range(8):
                for column in range(8):
                    pygame.draw.rect(self.screen, self.colors[color[square_color % 2]], (self.width*column, self.height*row, self.width*(column+1), self.height*(row+1)))
                    square_color += 1
                square_color += 1
            
        # Draw the piece sprites
        elif function == "pieces":
            self.pieces.draw(self.screen)
    
    # Displays the available moves for a piece that was clicked on
    def drawMoves(self, piece) -> None:
        self.should_update = True
        self.update()
        self.drawn_moves.append(piece.rect)
        
        # # Draw attacked Squares
        # for space in self.board.attacked_squares:
        #     pygame.draw.circle(self.screen, (222, 84, 84), ((space[0]*self.width) + (self.width/2), (space[1]*self.height) + (self.height/2)), self.width / 3.5)
        
        # Draw the available moves
        for space in self.board.getAvailableMoves((int(piece.rect.x/self.width), int(piece.rect.y/self.height))):
            pygame.draw.circle(self.screen, (84, 222, 139), ((space[0]*self.width) + (self.width/2), (space[1]*self.height) + (self.height/2)), self.width / 4)
            self.drawn_moves.append(pygame.Rect(space[0]*self.width, space[1]*self.height, self.width, self.height))
        
        
    # Returns whether the process is still running
    def isRunning(self) -> bool:
        return self.running
    
    # Translates the current board into sprites
    def addPieces(self) -> None:
        self.pieces.remove(self.pieces)
        for row_indew, row in enumerate(self.board.getBoard()):
            for column_index, piece in enumerate(row):
                if piece.getType() != None:
                    self.pieces.add(PieceSprite(str(piece), self.width, self.height, (column_index, row_indew)))
    