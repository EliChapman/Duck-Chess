import pygame, sys, time
sys.path.insert(0, "../")
import graphics, duck_chess


my_board = duck_chess.Board()
# renderer = graphics.DCRenderer(200, 200, "Duck Chess", my_board, colors={"White":(255, 255, 255), "Black":(0, 0, 0)})

# renderer.addPieces()

def movePieces(depth:int, current_depth:int = 0) -> None:
    total_moves = 0
    base_fen = my_board.getFEN()
    for piece, moves in my_board.getAllMoves(my_board.getTurn()).items():
        for move in moves:
            my_board.movePiece(piece, move)
            total_moves += 1
            # renderer.addPieces()
            # renderer.clock.tick(renderer.fps) # will make the loop run at the same speed all the time

            # for event in pygame.event.get(): # gets all the events which have occured till now and keeps tab of them.
            #     # listening for the the X button at the top
            #     if event.type == pygame.QUIT:
            #         pygame.quit()
                    
            # renderer.update(True)
            
            # Done after drawing everything to the screen
            # pygame.display.flip()
            if current_depth+1 < depth:
                total_moves += movePieces(depth, current_depth=current_depth+1)
            my_board.setFEN(base_fen)
            # renderer.addPieces()  
    return total_moves

tests = []
for i in range(10):
    i += 1
    tests.append(movePieces(i))
    print(f"Depth: {i}  Result: {tests[i - 1] - sum(tests[:i-1])}")