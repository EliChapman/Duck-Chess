import pygame, sys
sys.path.insert(0, "../")
import graphics, duck_chess


my_board = duck_chess.Board()
renderer = graphics.DCRenderer(600, 600, "Duck Chess", my_board, colors={"White":(255, 255, 255), "Black":(0, 0, 0)})

renderer.addPieces()

# Game loop
while renderer.isRunning():
    
    renderer.processInputs()
    renderer.update()
    
    # Done after drawing everything to the screen
    pygame.display.flip()

pygame.quit()