
import copy
import pygame
import random
import schedule
import numpy as np
import time

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 205, 50)
RED = (255, 0, 0)
BLUE = (65, 105, 225)
CYAN = (0, 238, 238)
ORANGE = (255, 153, 51)
MAGENTA = (178, 102, 255)
YELLOW = (238, 238, 0)
GRAY = (224,224,224)
ALICE = (240,248,255)
LIGHTGRAY = (231, 231, 231)

NUM_COLS = 10
NUM_ROWS = 24

width = 20
height = 20
margin = 1
fallRate = .4
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()


score = 0
font = pygame.font.SysFont("helvetica", 32)

BOARD_HEIGHT = 505
BOARD_WIDTH = 211

SCORE_HEIGHT = 80
SCORE_WIDTH = BOARD_WIDTH

# Set the width and height of the screen [width, height]
size = (BOARD_WIDTH, BOARD_HEIGHT+SCORE_HEIGHT)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Pytris")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

grid = [[0 for x in range(NUM_COLS)] for y in range(NUM_ROWS)]
pieces = ['I', 'O', 'Z', 'S', 'J', 'L', 'T']
colors = {'C': CYAN, 'R': RED, 'B': BLUE, 'O':ORANGE, 'M':MAGENTA, 'Y':YELLOW, 'G':GREEN,
          'CX':CYAN, 'RX': RED, 'BX':BLUE, 'OX':ORANGE, 'MX':MAGENTA,'YX':YELLOW,'GX':GREEN, 'GR':GRAY, 'GRX':GRAY,
          'LG':LIGHTGRAY, 'LGX':LIGHTGRAY}



def insertPiece(type):
    if type == 'I':
        shape = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 'C', 'C', 'C', 'C', 0, 0, 0]]
    elif type == 'O':
        shape = [[0, 0, 0, 0, 'Y', 'Y', 0, 0, 0, 0],
                 [0, 0, 0, 0, 'Y', 'Y', 0, 0, 0, 0]]
    elif type == 'T':
        shape = [[0, 0, 0, 0, 'M', 0, 0, 0, 0, 0],
                 [0, 0, 0, 'M', 'M', 'M', 0, 0, 0, 0]]
    elif type == 'S':
        shape = [[0, 0, 0, 0, 'G', 'G', 0, 0, 0, 0],
                 [0, 0, 0, 'G', 'G', 0, 0, 0, 0, 0]]
    elif type == 'Z':
        shape = [[0, 0, 0, 'R', 'R', 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 'R', 'R', 0, 0, 0, 0]]
    elif type == 'J':
        shape = [[0, 0, 0, 'B', 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 'B', 'B', 'B', 0, 0, 0, 0]]
    else:
        shape = [[0, 0, 0, 0, 0, 'O', 0, 0, 0, 0],
                 [0, 0, 0, 'O', 'O', 'O', 0, 0, 0, 0]]

    for idx, row in enumerate(shape):
        grid[idx] = shape[idx]

def findShapeAroundPosition(row,col,color):
    if row+1 == NUM_ROWS:
        row-=1
    if row+1 < NUM_ROWS:
        occupiedInRow1 = [0 for x in range(NUM_COLS)]
        occupiedInRow2 = [0 for x in range(NUM_COLS)]
        occupiedInRow3 = [0 for x in range(NUM_COLS)]
        occupiedInRow4 = [0 for x in range(NUM_COLS)]

        for idx, cell in enumerate(grid[row]):
            if cell == color:
                occupiedInRow1[idx] = 1
        for idx, cell in enumerate(grid[row+1]):
            if cell == color:
                occupiedInRow2[idx] = 1
        if row+2 < NUM_ROWS:
            for idx, cell in enumerate(grid[row+2]):
                if cell == color:
                    occupiedInRow3[idx] = 1
        if row+3 < NUM_ROWS:
            for idx, cell in enumerate(grid[row+3]):
                if cell == color:
                    occupiedInRow4[idx] = 1


        if color == 'C' and all(x == 0 for x in occupiedInRow2):
            shape = [occupiedInRow2, occupiedInRow1, occupiedInRow3, occupiedInRow4]
        else:
            shape = [occupiedInRow1, occupiedInRow2, occupiedInRow3, occupiedInRow4]
        return shape

def introducePiece():

    insertPiece(random.choice(pieces))

def markPieceStopped(row, shape):
    for idx, x in enumerate(shape[0]):
        if x == 1:
            grid[row][idx] =  str(grid[row][idx]) + 'X'
    for idx, x in enumerate(shape[1]):
        if x == 1:
            grid[row+1][idx] = str(grid[row+1][idx]) + 'X'
    for idx, x in enumerate(shape[2]):
        if x == 1:
            grid[row+2][idx] = str(grid[row+2][idx]) + 'X'
    for idx, x in enumerate(shape[3]):
        if x == 1:
            grid[row+3][idx] = str(grid[row+3][idx]) + 'X'

def imminentCollision(row, shape, color):
    if all(x== 0 for x in shape[0]):
        row-=1
    if all(x == 0 for x in shape[1]):
        for idx, x in enumerate(shape[0]):
            if x == 1 and (row+1 >= NUM_ROWS or grid[row+1][idx] != 0):
                markPieceStopped(row, shape)
                return True
    else:
        height = 0
        if 1 in shape[0]:
            height+=1
        if 1 in shape[1]:
            height+=1
        if 1 in shape[2]:
            height+=1
        if 1 in shape[3]:
            height+=1

        if height >= 2:
            for idx, x in enumerate(shape[height-1]):
                if x == 1 and (row+height >= NUM_ROWS or (grid[row+height][idx] not in (0, 'LG'))):
                    markPieceStopped(row, shape)
                    return True
            for idx, x in enumerate(shape[height-2]):
                if x == 1 and grid[row+height-1][idx] not in (0,color, 'LG'):
                    markPieceStopped(row, shape)
                    return True
            if height >=3:
                for idx, x in enumerate(shape[height-3]):
                    if x == 1 and grid[row+height-2][idx] not in (0,color,'LG'):
                        markPieceStopped(row, shape)
                        return True
        else:
            for idx, x in enumerate(shape[height]):
                if x == 1 and (row+height+1 >= NUM_ROWS or grid[row+height+1][idx] not in (0,'LG')):
                    markPieceStopped(row, shape)
                    return True

    return False


def removeCompletedLines():
    global grid
    global score
    copyGrid = copy.deepcopy(grid)
    completeLines = []
    for idxRow, row in enumerate(copyGrid):
        if all(copyGrid[idxRow][idxCol] != 0 for idxCol, col in enumerate(row)) and all('X' in copyGrid[idxRow][idxCol] for idxCol, col in enumerate(row)):
            completeLines.append(idxRow)

    if len(completeLines)>0:
        for completeIdx in completeLines:
            row = copyGrid[completeIdx]
            for idxY, y in enumerate(row):
                copyGrid[completeIdx][idxY] = 'GRX'

        grid = copyGrid

        numComplete = len(completeLines)
        if numComplete == 4:
            sound = pygame.mixer.Sound("tetris.wav")
        else:
            sound = pygame.mixer.Sound("complete.wav")
        pygame.mixer.Sound.play(sound)

        paint()
        time.sleep(.2)
        copyGrid = copy.deepcopy(grid)
        lowerLimit = completeLines[0] - 1
        for x in range(lowerLimit, -1, -1):
            currentRow = grid[x]
            copyGrid[x+numComplete] = currentRow
        grid=copyGrid
        multiplier = 1.5*numComplete
        score+=int(500*multiplier)
        paint()
        introducePieceIfNeeded()

def getColAndOffset():
    startCol = NUM_COLS
    offsetCol = 0
    copyGrid = copy.deepcopy(grid)
    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            if copyGrid[row][col] !=0 and 'X' not in grid[row][col]:
                color = grid[row][col]
                startCol = min(startCol, col)
                shape = findShapeAroundPosition(row,col,color)
                for row2 in shape:
                    offsetCol = max(offsetCol, row2.count(1))
    return {'data': [startCol, offsetCol]}








def fallPieces():

    global score

    copyGrid = copy.deepcopy(grid)

    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            if copyGrid[row][col] !=0 and copyGrid[row][col] != 'T' and 'X' not in grid[row][col] and copyGrid[row][col] not in ('LGX'):
                color = copyGrid[row][col]
                shape = findShapeAroundPosition(row,col,color)
                if not imminentCollision(row, shape, color):
                    shapeRow1 = shape[0]
                    shapeRow2 = shape[1]
                    shapeRow3 = shape[2]
                    shapeRow4 = shape[3]

                    if all(x == 0 for x in shapeRow1):
                        row-=1

                    for idx, val in enumerate(shapeRow4):
                        if val == 1:
                            grid[row+4][idx] = color
                            grid[row+3][idx] = 0
                            copyGrid[row+4][idx] = 'T'
                            copyGrid[row+3][idx]=0
                    for idx, val in enumerate(shapeRow3):
                        if val == 1:
                            grid[row+3][idx] = color
                            grid[row+2][idx] = 0
                            copyGrid[row+3][idx] = 'T'
                            copyGrid[row+2][idx]=0

                    for idx, val in enumerate(shapeRow2):
                        if val == 1:
                            grid[row+2][idx] = color
                            grid[row+1][idx] = 0
                            copyGrid[row+2][idx] = 'T'
                            copyGrid[row+1][idx]=0


                    for idx, val in enumerate(shapeRow1):
                        if val == 1:
                            grid[row+1][idx] = color
                            grid[row][idx] = 0
                            copyGrid[row+1][idx] = 'T'
                            copyGrid[row][idx] = 0

                    score+=1

                    return True
                else:
                    return False
    introducePieceIfNeeded()


def introducePieceIfNeeded():
    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            if grid[row][col] != 0 and 'X' not in grid[row][col]:
                return
    introducePiece()


def shiftLeft():
    copyGrid = copy.deepcopy(grid)
    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            if copyGrid[row][col] !=0 and 'X' not in grid[row][col]:
                color = copyGrid[row][col]
                shape = findShapeAroundPosition(row,col,color)
                if all(x==0 for x in shape[0]):
                    row-=1
                try:
                    row1FirstIndex = shape[0].index(1)
                    if row1FirstIndex > 0 and grid[row][row1FirstIndex-1] not in (0,'LG'):
                        return
                except ValueError:
                    pass
                try:
                    row2FirstIndex = shape[1].index(1)
                    if row2FirstIndex > 0 and grid[row+1][row2FirstIndex-1] not in (0,'LG'):
                        return
                except ValueError:
                    pass
                try:
                    row3FirstIndex = shape[2].index(1)
                    if row3FirstIndex > 0 and grid[row+2][row3FirstIndex-1] not in (0,'LG'):
                        return
                except ValueError:
                    pass
                try:
                    row4FirstIndex = shape[3].index(1)
                    if row4FirstIndex > 0 and grid[row+3][row4FirstIndex-1] not in (0,'LG'):
                        return
                except ValueError:
                    pass

                if (shape[0][0] == 0 and shape[1][0] == 0 and shape[2][0] == 0 and shape[3][0] == 0):
                    for idx, x in enumerate(shape[0]):
                        if x == 1:
                            if idx-1 >= 0:
                                grid[row][idx - 1] = grid[row][idx]
                                if idx+1 < NUM_COLS and 'X' not in str(grid[row][idx+1]):
                                    grid[row][idx] = grid[row][idx+1]
                                else:
                                    grid[row][idx] = 0
                    for idx, x in enumerate(shape[1]):
                        if x == 1:
                            if idx-1 >= 0:
                                grid[row+1][idx - 1] = grid[row+1][idx]
                                if idx+1 < NUM_COLS and 'X' not in str(grid[row+1][idx+1]):
                                    grid[row+1][idx] = grid[row+1][idx+1]
                                else:
                                    grid[row+1][idx] = 0
                    for idx, x in enumerate(shape[2]):
                        if x == 1:
                            if idx-1 >= 0:
                                grid[row+2][idx - 1] = grid[row+2][idx]
                                if idx+1 < NUM_COLS and 'X' not in str(grid[row+2][idx+1]):
                                    grid[row+2][idx] = grid[row+2][idx+1]
                                else:
                                    grid[row+2][idx] = 0
                    for idx, x in enumerate(shape[3]):
                        if x == 1:
                            if idx-1 >= 0:
                                grid[row+3][idx - 1] = grid[row+3][idx]
                                if idx+1 < NUM_COLS and 'X' not in str(grid[row+3][idx+1]):
                                    grid[row+3][idx] = grid[row+3][idx+1]
                                else:
                                    grid[row+3][idx] = 0

                return

def shiftRight():
    copyGrid = copy.deepcopy(grid)
    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            if copyGrid[row][col] !=0 and 'X' not in grid[row][col]:
                color = copyGrid[row][col]
                shape = findShapeAroundPosition(row,col,color)
                if all(x==0 for x in shape[0]):
                    row-=1
                try:
                    row1LastIndex = len(shape[0]) - shape[0][::-1].index(1) - 1
                    if row1LastIndex < NUM_COLS-1 and grid[row][row1LastIndex + 1] != 0:
                        return
                except ValueError:
                    pass
                try:
                    row2LastIndex = len(shape[1]) - shape[1][::-1].index(1) - 1
                    if row2LastIndex < NUM_COLS-1 and grid[row + 1][row2LastIndex + 1] != 0:
                        return
                except ValueError:
                    pass
                try:
                    row3LastIndex = len(shape[2]) - shape[2][::-1].index(1) - 1
                    if row3LastIndex < NUM_COLS-1 and grid[row + 2][row3LastIndex + 1] != 0:
                        return
                except ValueError:
                    pass
                try:
                    row4LastIndex = len(shape[3]) - shape[3][::-1].index(1) - 1
                    if row4LastIndex < NUM_COLS-1 and grid[row + 3][row4LastIndex + 1] != 0:
                        return
                except ValueError:
                    pass

                if (shape[0][NUM_COLS-1] == 0 and shape[1][NUM_COLS-1] == 0 and shape[2][NUM_COLS-1] == 0 and shape[3][NUM_COLS-1] == 0):
                    for idx, x in reversed(list(enumerate(shape[0]))):
                        if x == 1:
                            grid[row][idx + 1] = grid[row][idx]
                            if idx+1 < NUM_COLS and 'X' not in str(grid[row][idx-1]):
                                grid[row][idx] = grid[row][idx-1]
                            else:
                                grid[row][idx] = 0
                    for idx, x in reversed(list(enumerate(shape[1]))):
                        if x == 1:
                            grid[row + 1][idx + 1] = grid[row + 1][idx]
                            if idx+1 < NUM_COLS and 'X' not in str(grid[row+1][idx-1]):
                                grid[row+1][idx] = grid[row+1][idx - 1]
                            else:
                                grid[row+1][idx] = 0
                    for idx, x in reversed(list(enumerate(shape[2]))):
                        if x == 1:
                            grid[row + 2][idx + 1] = grid[row + 2][idx]
                            if idx+1 < NUM_COLS and 'X' not in str(grid[row+2][idx-1]):
                                grid[row+2][idx] = grid[row+2][idx - 1]
                            else:
                                grid[row+2][idx] = 0
                    for idx, x in reversed(list(enumerate(shape[3]))):
                        if x == 1:
                            grid[row + 3][idx + 1] = grid[row + 3][idx]
                            if idx+1 < NUM_COLS and 'X' not in str(grid[row+3][idx-1]):
                                grid[row+3][idx] = grid[row+3][idx - 1]
                            else:
                                grid[row+3][idx] = 0
                return

def removeOldShape(board):
    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            if board[row][col]!= 0 and 'X' not in board[row][col]:
                board[row][col] = 0
    return board



def tryPlaceRotation(color, row, originalCol, shape, rotatedShape):
    global grid
    gridPositionRow = row
    gridPositionCol = originalCol
    rotatedShapeX = len(rotatedShape[0])
    rotatedShapeY = len(rotatedShape)
    boardCopy = copy.deepcopy(grid)
    #remove old shape
    boardCopy = removeOldShape(boardCopy)

    for idxRow, row in enumerate(rotatedShape):
        gridPositionCol = originalCol
        for idxCol, col in enumerate(row):
            if col == 1:
                try:
                    boardCopy[gridPositionRow][gridPositionCol] = color
                except IndexError:
                    if gridPositionCol == NUM_COLS:
                        if color=='C':
                            tryPlaceRotation(color, gridPositionRow, originalCol-2, shape, rotatedShape)
                        else:
                            tryPlaceRotation(color, gridPositionRow, originalCol-1, shape, rotatedShape)
                        return
                    elif gridPositionCol == 0:
                        if color == 'C':
                            tryPlaceRotation(color, gridPositionRow, originalCol + 2, shape, rotatedShape)
                        else:
                            tryPlaceRotation(color, gridPositionRow, originalCol + 1, shape, rotatedShape)
                    return
            gridPositionCol+=1
        gridPositionRow+=1

    permissible = True
    #compare two boards to see if rotation is allowed
    for row in range(NUM_ROWS):
        for col in range(NUM_COLS):
            currentValue = grid[row][col]
            rotatedValue = boardCopy[row][col]
            if currentValue != 0 and rotatedValue in colors.keys() and currentValue != rotatedValue:
                permissible = False
    if permissible:
        grid = boardCopy




def getOffset(color, height,shape):
    if height==3 and color in ('G','R'):
        return -1
    elif height ==3 and color in ('O','B'):
        if color == 'B' and shape[0].count(1)==2:
            return 0
        else:
            return -1
    elif height==2 and color == 'B':
        if shape[0].count(1)==1:
            return 0
        else:
            return 0
    elif height==4 and color=='C':
        return -1
    elif height==1 and color=='C':
        return 1
    elif height==3 and color=='M':
        return -1
    else:
        return 0


def rotateShape(array_2d):
    list_of_tuples = zip(*array_2d[::-1])
    return [list(elem) for elem in list_of_tuples]

def rotateRight():
    copyGrid = copy.deepcopy(grid)
    for idxRow, row in enumerate(copyGrid):
        for idxCol, col in enumerate(row):
            if copyGrid[idxRow][idxCol] !=0 and 'X' not in grid[idxRow][idxCol]:
                color = copyGrid[idxRow][idxCol]
                shape = findShapeAroundPosition(idxRow,col,color)
                height = sum(1 in x for x in shape)
                if idxCol > 0:
                    offset = getOffset(color, height, shape)
                else:
                    offset = 0
                shapeCopy = copy.deepcopy(shape)
                for idxR, row in enumerate(shapeCopy):
                    if all(x == 0 for x in row):
                        shape.remove(row)
                shapeCopy2 = copy.deepcopy(shape)

                a = np.array(shape)
                trimmed = a[:, ~np.all(a==0, axis=0)].tolist()

                rotatedTrimmed = rotateShape(trimmed)
                tryPlaceRotation(color, idxRow, idxCol+offset, shape, rotatedTrimmed)
                return







schedule.every(fallRate).seconds.do(fallPieces)


def paint():
    currentY = margin
    for row in range(NUM_ROWS):
        currentX = margin
        # for every column
        for col in range(NUM_COLS):
            color = WHITE
            if grid[row][col] != 0:
                key = grid[row][col]
                color = colors[key]
            pygame.draw.rect(screen,color,(currentX,currentY,width,height))
            currentX += width + margin
        currentY += height + margin
    pygame.draw.rect(screen, ALICE, (2, BOARD_HEIGHT+2, SCORE_WIDTH-4, SCORE_HEIGHT-4))
    global font
    scoreText = font.render(str(score), 1, BLACK)
    textRect = scoreText.get_rect(center=(SCORE_WIDTH / 2, ((BOARD_HEIGHT)+ (SCORE_HEIGHT / 2))))
    screen.blit(scoreText, textRect)


    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()


pygame.mixer.music.load("theme.mp3")
pygame.mixer.music.set_volume(0.04)
sound = pygame.mixer.Sound("tick.wav")
pygame.mixer.music.play(-1)

introducePieceIfNeeded()
# -------- Main Program Loop -----------
while not done:
    schedule.run_pending()
    removeCompletedLines()
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pygame.mixer.Sound.play(sound)
                while fallPieces():
                    continue
            elif event.key == pygame.K_UP:
                pygame.mixer.Sound.play(sound)
                rotateRight()
    if keys[pygame.K_LEFT]:
        shiftLeft()
    if keys[pygame.K_RIGHT]:
        shiftRight()
    if keys[pygame.K_DOWN]:
        fallPieces()
    else:
        fallRate = 1


    screen.fill(BLACK)

    # --- Drawing code should go here
    paint()



    # --- Limit to 20 frames per second
    clock.tick(20)



# Close the window and quit.
pygame.quit()


