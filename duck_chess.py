import itertools
DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# DEFAULT_FEN = "8/5ppp/8/8/8/4K3/PPP4/8 w - - 0 1"
FEN_SYMBOLS = {
    "r" : ["Rook", "Black"],
    "n" : ["Knight", "Black"],
    "b" : ["Bishop", "Black"],
    "q" : ["Queen", "Black"],
    "k" : ["King", "Black"],
    "p" : ["Pawn", "Black"],
    "R" : ["Rook", "White"],
    "N" : ["Knight", "White"],
    "B" : ["Bishop", "White"],
    "Q" : ["Queen", "White"],
    "K" : ["King", "White"],
    "P" : ["Pawn", "White"],
    "D" : ["Duck", "Duck"]
}
NOTATION = ["a", "b", "c", "d", "e", "f", "g", "h"]

# Returns two lists, split at a location
def raycastFrom(lst: list, pos) -> list:
    index = lst.index(pos)
    lst1, lst2 = lst[:index], lst[index + 1:]
    lst1.reverse()
    return lst1, lst2

class InvalidFenException(Exception):
    # Raised when an invalid FEN is given.
    def __init__(self, fen, message="Fen notation was not valid: ") -> None:
        self.fen = fen
        self.message = message + f"\'{fen}\'"
        super().__init__(self.message)


class Piece():
    # Initialize the Piece with a set color and type. Both will be None if its an empty space
    def __init__(self, type, color) -> None:
        self.type = type
        self.color = color
        self.available_moves = []
    
    # Return's a piece's type
    def getType(self) -> str:
        return self.type
    
    # Return's a piece's color
    def getColor(self) -> str:
        return self.color
    
    # Resets available moves
    def clearAvailableMoves(self) -> None:
        self.available_moves = []
    
    # Adds a move to list of available moves
    def addMove(self, move: tuple or list) -> None:
        # Add single move
        if type(move) == tuple:
            self.available_moves.append(move)
        # Add multiple moves from list
        elif type(move) == list:
            self.available_moves += move
        else:
            raise(TypeError("Invalid move type: " + type(move)))
    
    def removeMove(self, move: tuple or list) -> None:
        # Delete single move
        if type(move) == tuple:
            self.available_moves.remove((move[1], move[0]))
        # Delete multiple moves from list
        elif type(move) == list:
            for checked_move in move:
                self.available_moves.remove((checked_move[1], checked_move[0]))
        else:
            raise(TypeError("Invalid move type: " + type(move)))
            
    # Represents the Piece object as a string, mostly for debugging
    def __repr__(self) -> str:
        return(f"{self.color} {self.type}")     

class Board():
    # Initialize Board with a List of column number of lists with row length
    def __init__(self, fen:str=DEFAULT_FEN, row=8, column=8) -> None:
        self.board = [[Piece(None, None) for x in range(column)] for y in range(row)]
        self.turn = True
        self.castling = 'KQkq'
        self.passant = '-'
        self.halfmove = 0
        self.fullmove = 1
        self.passant_time = 0
        self.attacked_squares = []
        self.setFEN(DEFAULT_FEN)
    
    # Returns the Board listself.board
    def getBoard(self) -> list:
        return(self.board)
    
    # Returns the piece at a given position, takes a tuple/list as input
    def getPiece(self, pos:tuple) -> Piece:
        return(self.board[pos[1]][pos[0]])
    
    # Returns who's turn it is
    def getTurn(self) -> str:
        return "White" if self.turn else "Black"
    
    # If passed coordinates, returns the standard notation, visa versa
    def getNotation(self, pos) -> str or tuple:
        if type(pos) == tuple:
            return(str(NOTATION[pos[0]]) + str(8 - pos[1]))
        elif type(pos) == str:
            return((NOTATION.index(pos[0]), 8 - int(pos[1])))
    
    # Returns a list of attacked squares
    def getAttackedSquares(self) -> list:
        return self.attacked_squares
    
    def findPiece(self, piece: Piece) -> tuple:
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if (str(self.board[i][j]) == str(piece)):
                    return (i, j)
        return (-1, -1)
    
    def getGameState(self) -> str:
        if self.findPiece(Piece("King", self.getTurn())) == (-1, -1):
            return "win"
    
    # Returns a dictionary of all possible moves, for testing purposes
    def getAllMoves(self, color: str or bool = None) -> dict:
        if type(color) == bool:
            color = "White" if color else "Black"
        elif not type(color) == str:
            raise(TypeError("Invalid color type: " + type(color)))
        moves = {}
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece.getType() != None and (color == None or piece.getColor() == color):
                    moves[(x, y)] = self.getAvailableMoves((x, y))
        return moves
                        
    # Returns a FEN string of the current position
    def getFEN(self) -> str:
        fen = ""
        was_space = False
        for y in range(8):
            spaces = 0
            for x in range(8):
                if self.getPiece((x, y)).getType() != None:
                    index = str(self.getPiece((x, y))).split()
                    index.reverse()
                    if was_space:
                        fen += str(spaces)
                        spaces = 0
                    fen += (list(FEN_SYMBOLS)[list(FEN_SYMBOLS.values()).index(index)])
                    was_space = False
                else:
                    spaces += 1
                    was_space = True
            if spaces != 0:
               fen += str(spaces)
            if y != 7:
                fen += "/"
        fen += " w" if self.turn else " b"
        fen += f" KQkq {self.passant} {self.halfmove} {self.fullmove}"
        return fen
    
    # Returns all legal moves for the piece at a given position
    def getAvailableMoves(self, pos: tuple, attacking:bool = False) -> list:
        piece = self.getPiece(pos)
        color = piece.getColor()
        piece.clearAvailableMoves()
        x, y = pos

        # Pawn Movement
        if piece.getType() == "Pawn":
            # Adds the diagonal options for attack purposes
            if attacking:
                if color == "Black":
                    if x < 7 and y < 7:
                        piece.addMove((x + 1, y + 1))
                    if x > 0 and y < 7:
                        piece.addMove((x - 1, y + 1))
                else:
                    if x < 7 and y > 0:
                        piece.addMove((x + 1, y - 1))
                    if x > 0 and y > 0:
                        piece.addMove((x - 1, y - 1))
            # Normal movement
            else:
                for i in range(-1, 2):
                    checked_move = (x + i, y + 1) if color == "Black" else (x + i, y - 1)
                    if checked_move[0] >= 0 and checked_move[0] < 8 and checked_move[1] >= 0 and checked_move[1] < 8:
                        # Check Diagonal attacks
                        if ((i != 0 and self.getPiece(checked_move).getType() != None) and (self.getPiece(checked_move).getColor() != color)):
                            piece.addMove(checked_move)
                        # Check forward movement
                        elif i == 0 and self.getPiece(checked_move).getType() == None:
                            piece.addMove(checked_move)
                            # Check if its White, one the starting pawn row, and that its moving to an empty space
                            if y == 6 and color == "White" and self.getPiece((x, y - 2)).getType() == None:
                                piece.addMove((x, y - 2))
                            # Same thing but for black
                            elif y == 1 and color == "Black" and self.getPiece((x, y + 2)).getType() == None:
                                piece.addMove((x, y + 2))
                        # Check En Passant
                        elif self.passant == self.getNotation(checked_move):
                            piece.addMove(checked_move)

        # Knight Movement
        if piece.getType() == "Knight":
            # Uses itertools itertools.product to get (x - 1,y - 2),(x - 1,y + 2),(x + 1,y - 2), etc.
            for checked_move in list(itertools.product([x - 1, x + 1],[y - 2, y + 2])) + list(itertools.product([x - 2, x + 2], [y - 1, y + 1])):
                # Checks if move is in bounds
                if checked_move[0] >= 0 and checked_move[0] < 8 and checked_move[1] >= 0 and checked_move[1] < 8:
                    # Checks if area is occupied by a piece of the same color
                    if self.getPiece(checked_move).getColor() != color or attacking:
                        piece.addMove(checked_move)
        
        # Rook Movement
        if piece.getType() == "Rook":
            # Generates moves along the vertical, then horizontal and splits them at the piece's position
            # The left/top movement is reversed, so that it can break when it reaches a piece of the same color
            for raycast in itertools.chain(raycastFrom([(x, i) for i in range(8)], pos), raycastFrom([(i, y) for i in range(8)], pos)):
                for checked_move in raycast:
                    if self.getPiece(checked_move).getType() != None:
                        # If the piece isn't of the same color, it adds a move at that positon
                        if self.getPiece(checked_move).getColor() != color or attacking:
                            piece.addMove(checked_move)
                        # If it ran into a piece, it stops the loop
                        break
                    else:
                        piece.addMove(checked_move)
        
        # Bishop Movement
        if piece.getType() == "Bishop":
            # Generates moves along two diagonals, one in the increasing x, increasing y and the other in the increasing x, decreasing y
            # Then uses raycast from to order the points from the center in all four directs, seperationg them into 4 lists that are combined using itertools.chain
            for raycast in itertools.chain(raycastFrom([(x + i, y + i) for i in range(-7, 8)], pos), raycastFrom([(x + i, y - i) for i in range(-7, 8)], pos)):
                for checked_move in raycast:
                    # Check if move is in bounds
                    if checked_move[0] >= 0 and checked_move[0] < 8 and checked_move[1] >= 0 and checked_move[1] < 8:
                        if self.getPiece(checked_move).getType() != None:
                            # If the piece isn't of the same color, it adds a move at that positon
                            if self.getPiece(checked_move).getColor() != color or attacking:
                                piece.addMove(checked_move)
                            # If it ran into a piece, it stops the loop
                            break
                        else:
                            piece.addMove(checked_move)
        
        # Queen Movement
        if piece.getType() == "Queen":
            # Generates moves along two diagonals, one in the increasing x, increasing y and the other in the increasing x, decreasing y
            # Then generates moves along the straights, same code as rook
            # First is (x, +y), then (+x, y) then (+x, +y), then (+x, -y)
            for raycast in itertools.chain(raycastFrom([(x, i) for i in range(8)], pos), raycastFrom([(i, y) for i in range(8)], pos), raycastFrom([(x + i, y + i) for i in range(-7, 8)], pos), raycastFrom([(x + i, y - i) for i in range(-7, 8)], pos)):
                for checked_move in raycast:
                    # Check if move is in bounds
                    if checked_move[0] >= 0 and checked_move[0] < 8 and checked_move[1] >= 0 and checked_move[1] < 8:
                        if self.getPiece(checked_move).getType() != None:
                            # If the piece isn't of the same color, it adds a move at that positon
                            if self.getPiece(checked_move).getColor() != color or attacking:
                                piece.addMove(checked_move)
                            # If it ran into a piece, it stops the loop
                            break
                        else:
                            piece.addMove(checked_move)
        
        # King Movement
        if piece.getType() == "King":
            # Iterates through a 3x3 square around the king
            for x_offset, y_offset in itertools.product(range(-1, 2), range(-1, 2)):
                checked_move = (x + x_offset, y + y_offset)
                # Checks if the king is trying to move into Check
                if checked_move not in self.attacked_squares:
                    # Checks if move is the current position of the king
                    if checked_move != (x, y):
                        # Check if move is in bounds
                        if checked_move[0] >= 0 and checked_move[0] < 8 and checked_move[1] >= 0 and checked_move[1] < 8:
                            # Checks if area is occupied by a piece of the same color
                            if self.getPiece(checked_move).getColor() != color or attacking:
                                piece.addMove(checked_move)
                                
        return piece.available_moves
    
    # Moves Piece from target pos to dest
    def movePiece(self, pos:tuple, dest:tuple) -> None:
        piece, color = self.getPiece(pos).getType(), self.getPiece(pos).getColor()
        
        # Reset halfmoves if pawn move
        if piece == "Pawn":
            self.halfmove = 0
            # En passant handling
            if pos[1] + 2 == dest[1]:
                self.passant = self.getNotation((pos[0], pos[1] + 1))
                self.passant_time = 2
            elif pos[1] - 2 == dest[1]:
                self.passant = self.getNotation((pos[0], pos[1] - 1))
                self.passant_time = 1
                
        # Reset halfmoves if capture, otherwise incriment
        elif self.getPiece(dest).getType() != None:
            self.halfmove = 0
        else:
            self.halfmove += 1
        
        # En Passont movement
        if piece == "Pawn":
            if self.getPiece(dest).getType() == None and dest[0] != pos[0]:
                if color == "White":
                    self.board[dest[1] + 1][dest[0]] = Piece(None, None)
                else:
                    self.board[dest[1] - 1][dest[0]] = Piece(None, None)
        
        # Actually move piece
        self.board[dest[1]][dest[0]] = self.getPiece(pos)
        self.board[pos[1]][pos[0]] = Piece(None, None)

        # Switch turn
        self.turn = not self.turn
        
        # Increment fullmove
        if self.getPiece(dest).getColor() == "Black":
            self.fullmove += 1
        
        # Make En Passant Expire
        if self.passant_time != 0:
            self.passant_time += -1
        else:
            self.passant = None
        
        # Recalculate all attacked positions
        self.setAttackedSquares()
            
    # Generates all squares that are under attack by the opposing color
    def setAttackedSquares(self) -> None:
        self.attacked_squares = []
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece.getType() != None and piece.getColor() != self.getTurn():
                    for square in self.getAvailableMoves((x, y), True):
                        self.attacked_squares.append(square)
    
    # Sets the board state to a specific FEN Notation
    def setFEN(self, fen:str) -> None:
        fen = fen.split()
        
        x, y = 0, 0
        for char in fen[0]:
            if char == '/':
                y += 1
                x = 0
            elif char.isdigit(): 
                for i in range(int(char)):
                    self.board[y][x] = Piece(None, None)
                    x += 1
            else:
                self.board[y][x] = Piece(FEN_SYMBOLS[char][0], FEN_SYMBOLS[char][1])
                x += 1
                    
        # The non-piece stuff
        self.turn = fen[1] == 'w'
        self.castling = fen[2]
        self.passant = fen[3]
        self.halfmove = int(fen[4])
        self.fullmove = int(fen[5])

        self.setAttackedSquares()


    # Represent Board as a string, mostly for debugging
    def __repr__(self) -> str:
        if self.turn:
            output = "White's Turn"
        else:
            output = "Black's Turn"
        output += f"\nCastling: {self.castling}\nEn passant: {self.passant}\nHalfmoves: {self.halfmove}\nFullmoves: {self.fullmove}\n  "
        
        # Headers for columns
        for column_index, _ in enumerate(self.board[0]):
            output += f"    --- {column_index} ---  "
        output += "\n"
        
        for row_index, row in enumerate(self.board):
            
            # Label for rows
            output += f"{row_index} | "
            
            # Main Bulk of the Display
            for column_index, _ in enumerate(row):
                
                # Adds whitespace so everything is the same size
                for i in range(12 - len(str(self.getPiece((column_index, row_index))))):
                    output += " "
                    
                # Add Pieces and shit to the table
                output += f"{self.getPiece((column_index, row_index))} | "
            output += "\n"    
        return(output)