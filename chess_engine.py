'''
this class is responsible for storing all the information, about the current state of chess
game, it will also be responsible for determiining the valid moves at the current state,
it will also keep a move log
  -- undo move
  -- current move  

'''


class gamestate:
    def __init__(self):
        '''
        board is 8 X 8 representing by 2d list, each element of the list has 2 characters.
        the first characters represent the color of the piece 'b' or 'w'
        the sec characters represent the type of the piece 
        "--" represent empty space with no space
        '''
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        
        self.moveFunctions = {'p' : self.getPawnMoves , 'R' : self.getRookMoves , 'N' : self.getKnightMoves,
                              'B' : self.getBishopMoves , 'Q' : self.getQueenMoves , 'K' : self.getKingMoves}
        
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False

    '''
    take a move as parameter and execute it.
    '''
    def makeMove(self ,move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later and print them
        self.whiteToMove = not self.whiteToMove # swap the player 

        # update the king location if moved 
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow,move.endCol)           
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow,move.endCol)
            

    '''
    undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: # make sure that there is move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # switch turns back
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow,move.startCol)           
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow,move.startCol)
    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        # 1) generate all possible moves
        moves = self.getAllPossibleMoves()  # for now, we will not worry about checks
        # 2) for each move, make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # 3) generate all opponent's moves
            # 4) for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # 5) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves
    
    '''
    determine if the current player is in check  
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    '''
    determine if the enemy can attack the square r , c
    '''
    def squareUnderAttack(self , r , c):
        self.whiteToMove = not self.whiteToMove # switch to oppenent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch turn back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # square is under attack
                return True
        return False

    '''
    All moes without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of cols in 
                turn = self.board[r][c][0]                
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r ,c ,moves)
        return moves
    '''
    get all pawn moves for the pawn located at row ,col and add these moves to the list
    '''
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # white pawn 
            if self.board[r-1][c] == "--": # 1 square pawn advance
                moves.append(move((r,c),(r-1,c),self.board))
                if r == 6 and self.board[r-2][c] == "--": # 2 square pawn advance
                    moves.append(move((r,c),(r-2,c),self.board))
            if c-1 >= 0: # captured to left
                if self.board[r-1][c-1][0] == 'b': # enemy piece to captured 
                    moves.append(move((r,c),(r-1,c-1),self.board))
            if c+1 <= 7: # captured to right 
                if self.board[r-1][c+1][0] == 'b': 
                    moves.append(move((r,c),(r-1,c+1),self.board))
        else: # black pawn
            if self.board[r+1][c] == "--": # 1 square pawn advance
                moves.append(move((r,c),(r+1,c),self.board))
                if r == 1 and self.board[r+2][c] == "--": # 2 square pawn advance
                    moves.append(move((r,c),(r+2,c),self.board))            
            # captured 
            if c-1 >= 0: # captured to left
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(move((r,c),(r+1,c-1),self.board))
            if c+1 <= 7: # captured to right
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(move((r,c),(r+1,c+1),self.board))
                   
    '''
    Get all Rook moves for the Rook located at row ,col and add these moves to the list
    '''
    def getRookMoves(self ,r , c ,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1)) # up ,left ,down ,right 
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board 
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space valid 
                        moves.append(move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor: # enemy piece valid 
                        moves.append(move((r,c),(endRow,endCol),self.board))
                        break
                    else: # friendly piece in valid
                        break
                else:
                    break

    '''
    Get all knight moves for the knight located at row ,col and add these moves to the list
    '''
    def getKnightMoves(self ,r , c ,moves):
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol] 
                if endPiece[0] != allyColor: # empty or enemypiece 
                    moves.append(move((r,c),(endRow,endCol),self.board))

    '''
    Get all Bishop moves for the Bishop located at row ,col and add these moves to the list
    '''
    def getBishopMoves(self ,r , c ,moves):
        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space valid 
                        moves.append(move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(move((r,c),(endRow,endCol),self.board))
                        break
                    else: # friendly piece invalid
                        break
                else: # off board 
                    break



    '''
    Get all Queen moves for the Queen located at row ,col and add these moves to the list
    '''
    def getQueenMoves(self ,r , c ,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    '''
    Get all king moves for the king located at row ,col and add these moves to the list
    '''
    def getKingMoves(self ,r , c ,moves):
        KingMoves = ((-1,-1),(-1,0),(-1,1),
                    (0,-1),(0,1),
                    (1,-1),(1,0),(1,1))
        allyColor = "w" if self.whiteToMove else "b"

        for i in range(8):
            endRow = r + KingMoves[i][0]
            endCol = c + KingMoves[i][1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]

                # 🚀 THIS LINE FIXES EVERYTHING
                if endPiece[0] != allyColor:
                    moves.append(move((r,c),(endRow,endCol),self.board))

class move():
    # map keys to values 
    # key : value
    ranksToRows = {"1": 7, "2": 6 ,"3": 5,"4": 4,
                   "5": 3, "6": 2 ,"7": 1, "8":0}
    
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}

    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self ,startSq ,endSq ,board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        

    '''
    overriding The equals method
    '''
    def __eq__(self ,other):
        if isinstance(other ,move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow ,self.startCol) + self.getRankFile(self.endRow ,self.endCol)

    def getRankFile(self ,r ,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]



