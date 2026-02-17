
#Main driver file for Chess Game
#Handles user input and displays the current GameState.

import pygame as p
import chess_engine
import random

p.init()

width = height = 512
dimension = 8
SQ_Sizee = height // dimension
Max_FPS = 60
image = {}

# ------------------ LOAD IMAGES ------------------

def loadImages():
    pieces = ['wp','wR','wN','wB','wK','wQ',
              'bp','bR','bN','bB','bK','bQ']
    for piece in pieces:
        image[piece] = p.transform.scale(
            p.image.load("image/" + piece + ".png"),
            (SQ_Sizee, SQ_Sizee)
        )

# ------------------ MENU ------------------

def drawMenu(screen, buttons, iconImg):
    screen.fill((25, 25, 35))

    titleFont = p.font.SysFont("Segoe UI", 72, True)
    titleText = titleFont.render("CHESS", True, (240,240,240))
    titleRect = titleText.get_rect(center=(width//2, 130))
    screen.blit(titleText, titleRect)

    iconRect = iconImg.get_rect()
    iconRect.midright = (titleRect.left - 10, titleRect.centery)
    screen.blit(iconImg, iconRect)

    mousePos = p.mouse.get_pos()
    font = p.font.SysFont("Segoe UI", 28, True)

    for rect, text in buttons:
        color = (100,180,255) if rect.collidepoint(mousePos) else (70,130,200)
        p.draw.rect(screen, color, rect, border_radius=12)

        textSurface = font.render(text, True, (255,255,255))
        textRect = textSurface.get_rect(center=rect.center)
        screen.blit(textSurface, textRect)

    p.display.flip()
    
    
def drawCheckmateText(screen, text, alpha, scale):
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()

    # Dark overlay
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Font size based on animation scale
    font_size = int(60 * scale)
    font = p.font.SysFont("Arial", font_size, True, False)

    # Render main text
    textSurface = font.render(text, True, p.Color("white"))
    textSurface.set_alpha(alpha)

    # Center text
    textRect = textSurface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(textSurface, textRect)

    # Smaller restart text
    smallFont = p.font.SysFont("Arial", 24, True, False)
    restartText = smallFont.render("Press R to Restart", True, p.Color("white"))
    restartText.set_alpha(alpha)

    restartRect = restartText.get_rect(
        center=(WIDTH // 2, HEIGHT // 2 + 50)
    )
    screen.blit(restartText, restartRect)

# ------------------ MAIN ------------------

def main():
    screen = p.display.set_mode((width,height))
    clock = p.time.Clock()

    # -------- MENU SETUP --------
    buttonWidth = 200
    buttonHeight = 60

    aiButton = p.Rect(width//2 - buttonWidth//2, 250, buttonWidth, buttonHeight)
    twoPlayerButton = p.Rect(width//2 - buttonWidth//2, 330, buttonWidth, buttonHeight)
    quitButton = p.Rect(width//2 - buttonWidth//2, 410, buttonWidth, buttonHeight)

    buttons = [
        (aiButton, "Play vs AI"),
        (twoPlayerButton, "Two Player"),
        (quitButton, "Quit")
    ]

    menu = True
    playerOne = True
    playerTwo = True

    iconImg = p.image.load("image/icon.png")
    iconImg = p.transform.smoothscale(iconImg, (60,60))

    # -------- MENU LOOP --------
    while menu:
        drawMenu(screen, buttons, iconImg)

        for e in p.event.get():
            if e.type == p.QUIT:
                return

            elif e.type == p.MOUSEBUTTONDOWN:
                mousePos = p.mouse.get_pos()

                if aiButton.collidepoint(mousePos):
                    playerOne = True
                    playerTwo = False
                    menu = False

                elif twoPlayerButton.collidepoint(mousePos):
                    playerOne = True
                    playerTwo = True
                    menu = False

                elif quitButton.collidepoint(mousePos):
                    return

        clock.tick(60)

    # -------- GAME SETUP --------
    gs = chess_engine.gamestate()
    validMoves = gs.getValidMoves()
    moveMade = False
    gameOver = False

    animationAlpha = 0
    animationScale = 1.0

    loadImages()

    running = True
    sqSelected = ()
    playerClicks = []

    # -------- GAME LOOP --------
    while running:

        humanTurn = (gs.whiteToMove and playerOne) or \
                    (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if humanTurn and not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_Sizee
                    row = location[1] // SQ_Sizee

                    if sqSelected == (row,col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2:
                        move = chess_engine.move(
                            playerClicks[0],
                            playerClicks[1],
                            gs.board
                        )

                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade = True

                        sqSelected = ()
                        playerClicks = []

            elif e.type == p.KEYDOWN:

                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

                if gameOver:
                    if e.key == p.K_r:
                        gs = chess_engine.gamestate()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        gameOver = False
                        animationAlpha = 0
                        animationScale = 1.0

                    elif e.key == p.K_m:
                        main()
                        return

        # -------- UPDATE MOVES --------
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

            if gs.checkMate:
                print("CHECKMATE DETECTED")

            if gs.checkMate or gs.staleMate:
                gameOver = True

        # -------- AI MOVE --------
        humanTurn = (gs.whiteToMove and playerOne) or \
                    (not gs.whiteToMove and playerTwo)

        if not gameOver and not humanTurn:
            if len(validMoves) > 0:
                aiMove = random.choice(validMoves)
                gs.makeMove(aiMove)
                moveMade = True

        # -------- DRAW BOARD --------
        drawGameState(screen, gs, sqSelected, validMoves)

        # -------- OVERLAY --------
        if gameOver:
            if animationAlpha < 255:
                animationAlpha += 5
                animationScale += 0.01

            if gs.checkMate:
                if gs.whiteToMove:
                    drawAnimatedEndGameText(
                        screen,
                        "Black Wins by Checkmate",
                        animationAlpha,
                        animationScale
                    )
                else:
                    drawAnimatedEndGameText(
                        screen,
                        "White Wins by Checkmate",
                        animationAlpha,
                        animationScale
                    )
            else:
                drawAnimatedEndGameText(
                    screen,
                    "Stalemate",
                    animationAlpha,
                    animationScale
                )

        clock.tick(Max_FPS)
        p.display.flip()

# ------------------ ANIMATED OVERLAY ------------------

def drawAnimatedEndGameText(screen, text, alpha, scale):

    WIDTH, HEIGHT = screen.get_width(), screen.get_height()

    # dark overlay
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(min(alpha, 180))
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # base font size
    baseSize = int(50 * scale)
    fontSize = min(baseSize, 80)

    font = p.font.SysFont("Segoe UI", fontSize, True)

    # shrink text if too wide
    textSurface = font.render(text, True, (255, 255, 255))
    while textSurface.get_width() > WIDTH - 40 and fontSize > 20:
        fontSize -= 2
        font = p.font.SysFont("Segoe UI", fontSize, True)
        textSurface = font.render(text, True, (255, 255, 255))

    textSurface.set_alpha(alpha)

    textRect = textSurface.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(textSurface, textRect)

    # restart text
    smallFont = p.font.SysFont("Segoe UI", 24)
    restartText = smallFont.render("Press R to Restart", True, (200, 200, 200))
    restartRect = restartText.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
    screen.blit(restartText, restartRect)

# ------------------ DRAW FUNCTIONS ------------------

def drawGameState(screen, gs, sqSelected, validMoves):
    drawBoard(screen)
    highlightSquares(screen, gs, sqSelected, validMoves)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [p.Color(240,217,181), p.Color(181,136,99)]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[(r+c)%2]
            p.draw.rect(screen,color,
                        p.Rect(c*SQ_Sizee,r*SQ_Sizee,
                               SQ_Sizee,SQ_Sizee))

def highlightSquares(screen, gs, sqSelected, validMoves):

    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_Sizee,SQ_Sizee))
        s.set_alpha(100)
        s.fill(p.Color("yellow"))
        screen.blit(s,(lastMove.startCol*SQ_Sizee,
                       lastMove.startRow*SQ_Sizee))
        screen.blit(s,(lastMove.endCol*SQ_Sizee,
                       lastMove.endRow*SQ_Sizee))

    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_Sizee,SQ_Sizee))
            s.set_alpha(120)

            s.fill(p.Color("blue"))
            screen.blit(s,(c*SQ_Sizee,r*SQ_Sizee))

            s.fill(p.Color("green"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s,
                        (move.endCol*SQ_Sizee,
                         move.endRow*SQ_Sizee))

def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(image[piece],
                    p.Rect(c*SQ_Sizee,r*SQ_Sizee,
                           SQ_Sizee,SQ_Sizee))

if __name__ == "__main__":
    main()

