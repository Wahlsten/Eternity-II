import numpy as np
import matplotlib.pyplot as plt
import copy
import random
import os

def LoadPieces(filename):
    
    f = open(filename,'r')
    lines = f.readlines()
    n_corners = 4
    i_count = -1
    Pieces = dict()
    for line in lines:
        if not (line == ''):
            i_count = i_count + 1
            line = line.replace('\n', '')
            line = line.replace('[', '')
            line = line.replace(']', '')
            line = line.split(':')
            split_line = line[1].split(',')
            int_map = map(int, split_line)
            int_list = np.array(list(int_map))
            Pieces[str(int(line[0]) - 1)] = int_list

    return Pieces

def FindBestSolution(pieces, n_iterations):
    
    n_best = 0
    best_board = list()
    for k in range(n_iterations):
        solution_board, solution_pieces = EternitySolver(pieces)
        n_sol_pieces = CountMatchingEdges(solution_pieces)
        if n_sol_pieces > n_best:
            n_best = n_sol_pieces
            print('New best: ', n_best)
            best_pieces = copy.deepcopy(solution_pieces)
        print('current:', n_sol_pieces)

    return best_pieces

def EternitySolver(pieces):
    
    board_size = 16
    n_pieces = board_size ** 2
    
    board = InitializeBoard(board_size)
    pieces_left = copy.deepcopy(pieces)
    del pieces_left['135']
    board_pieces = list()
    edges_fit = 4
    for k in range(n_pieces):
        if k == 135:
            tmp_piece = dict()
            tmp_piece['index'] = '135'
            tmp_piece['array'] = pieces['135']
            tmp_piece['rotation'] = 0
            piece = copy.deepcopy(tmp_piece)
        else:
            piece = FindPiece(pieces_left, board[k], edges_fit)
            
        if len(piece) == 0:
            tmp_piece = dict()
            tmp_piece['index'] = -1
            tmp_piece['array'] = [-1, -1, -1, -1]
            tmp_piece['rotation'] = 0
            piece = copy.deepcopy(tmp_piece)
        else:
            board = InsertPiece(piece, board, k)

        board_pieces.append(piece)
        pieces_left = RemovePiece(pieces_left, piece)

    for m in range(edges_fit):
        tmp_fit = edges_fit - m - 1
        for k in range(n_pieces):
            if board_pieces[k]['index'] == -1:
                piece = FindPiece(pieces_left, board[k], tmp_fit)
                if piece == []:
                    continue
            else:
                continue

            board = InsertPiece(piece, board, k)
            board_pieces = AppendPiece(board_pieces, piece, k)
            pieces_left  = RemovePiece(pieces_left, piece)

    solution = copy.deepcopy(board)

    return solution, board_pieces

def AppendPiece(board_pieces, piece, k):

    if k > len(board_pieces):
        board_pieces.append(piece)
    else:
        board_pieces[k] = piece

    return board_pieces

def CountMatchingEdges(solution_pieces):
    
    n_rows = 16
    n_cols = 16
    n_edges_match = 0
    for row in range(n_rows):
        for col in range(n_cols):
            ind = row * n_rows + col

            current_rot   = solution_pieces[ind]['rotation']
            current_piece = np.roll(solution_pieces[ind]['array'], current_rot)
            if not ((ind + 1) % n_cols == 0):
                right_rot = solution_pieces[ind + 1]['rotation']
                right_piece = np.roll(solution_pieces[ind + 1]['array'], right_rot)
                if current_piece[1] == right_piece[3]:
                    n_edges_match = n_edges_match + 1

            if row < n_rows - 1:
                below_rot   = solution_pieces[ind + n_cols]['rotation']
                below_piece = np.roll(solution_pieces[ind + n_cols]['array'], below_rot)
                if current_piece[2] == below_piece[0]:
                    n_edges_match = n_edges_match + 1
                
    return n_edges_match

def InitializeBoard(board_size):
    
    n_pieces = board_size ** 2
    board = dict()

    for k in range(n_pieces):
        tmp_list = -np.ones(4)
        if k < board_size:
            tmp_list[0] = 0

        if (k + 1) % board_size == 0:
            tmp_list[1] = 0

        if k >= n_pieces - board_size:
            tmp_list[2] = 0

        if (k + 1) % board_size == 1:
            tmp_list[3] = 0
        
        if k == 135 - 16:
            tmp_list[2] = 2
        if k == 134:
            tmp_list[1] = 12
        if k == 136:
            tmp_list = [2, 4, 4, 12]
        if k == 135:
            tmp_list[3] = 4
        if k == 135 + 16:
            tmp_list[0] = 4

        board[k] = copy.deepcopy(tmp_list)

    return board

def FindPiece(pieces_left, board_piece, edges_fit):
    
    pieces_list = list(pieces_left.keys())
    rand_piece_indices = random.sample(pieces_list, len(pieces_list))
    for piece_ind in rand_piece_indices:
        piece = pieces_left[piece_ind]
        fit_rotation = CheckPieceFit(piece, board_piece, edges_fit)
        if not (fit_rotation == -1):
            tmp_piece = dict()
            tmp_piece['index'] = piece_ind
            tmp_piece['array'] = piece
            tmp_piece['rotation'] = fit_rotation
            return tmp_piece

    return []

def RemovePiece(pieces_left, piece):

    if not piece['index'] == -1:
        try:
            del pieces_left[piece['index']]
        except:
            pass

    return pieces_left

def CheckPieceFit(piece, board_piece, edges_fit):
    rotations = 4
    n_edges = rotations
    fit_rotations = list()
    for r in range(rotations):
        tmp_piece = np.roll(piece, r)
        n_fit_edges = 0
        for k in range(n_edges):
            if (board_piece[k] == -1 and not (tmp_piece[k] == 0)) or board_piece[k] == tmp_piece[k]:
                n_fit_edges = n_fit_edges + 1

            if edges_fit < 4 and ((board_piece[k] == 0 and not tmp_piece[k] == 0) or (tmp_piece[k] == 0 and not board_piece[k] == 0)):
                n_fit_edges = 0
                break
                
        if n_fit_edges == edges_fit:
            fit_rotations.append(r)

    if fit_rotations == []:
        return -1
    else:
        return random.choice(fit_rotations)

def InsertPiece(piece, board, n_piece):
    
    board_size = 16
    n_pieces   = board_size ** 2
    piece_array = np.roll(piece['array'], piece['rotation'])
    board[n_piece] = piece_array

    # If not last row
    if n_piece < n_pieces - board_size:
        board[n_piece + board_size][0] = piece_array[2]
    
    # If not last column
    if not ((n_piece + 1) % board_size == 0):
        board[n_piece + 1][3] = piece_array[1]

    # If not first row
    if not n_piece < board_size:
        # If piece above is not placed
        if board[n_piece - board_size][2] == -1:
            board[n_piece - board_size][2] = piece_array[0]

    # If not first row
    if not ((n_piece) % board_size == 0):
        # If previous piece is not placed
        if board[n_piece - 1][1] == -1: 
            board[n_piece - 1][1] = piece_array[3]

    return board

def PlotSolution(solution):

    plot_width  = 1
    plot_height = 1
    board_size  = 4
    col_width = 2
    row_width = 2
    board_size = 16
    n_pieces = board_size ** 2
    i_count = -1
    ax1 = plt.gca()
    n_pieces = len(solution)
    for row in range(board_size):
        for col in range(board_size):
            i_count = i_count + 1
            x_place = col_width * col
            y_place = -row_width * row
            piece   = solution[i_count]
            if not piece['index'] == -1:
                color_array = piece['array']
                rotation    = piece['rotation']
                color_id    = np.roll(color_array, rotation)
            elif row == 0 and col == 0:
                color_id = [0, -1, -1, 0]
            elif row == 0 and  col == board_size-1:
                color_id = [0, 0, -1, -1]
            elif row == board_size - 1 and  col == 0:
                color_id = [-1, -1, 0, 0]
            elif row == board_size - 1 and  col == board_size - 1:
                color_id = [-1, 0, 0, -1]
            elif row == 0:
                color_id = [0, -1, -1, -1]
            elif row == board_size - 1:
                color_id = [-1, -1, 0, -1]
            elif col == 0:
                color_id = [-1, -1, -1, 0]
            elif col == board_size - 1:
                color_id = [-1, 0, -1, -1]
            else:
                color_id = [-1, -1, -1, -1]

            PlotPiece(color_id, [x_place, y_place], ax1)
    ax1.set_aspect('equal', 'box')
    plt.show()

def PlotPiece(patterns, position, axes):

    n_pattern_num = len(patterns)

    for k in range(n_pattern_num):
        pattern_num = patterns[k]
        if pattern_num == 0:
            color = 'grey'
            PlotBackground(position, axes, color, k)
        elif pattern_num == 1:
            colors = ('brown', 'yellow')
            PlotStar(position, axes, colors, k)
        elif pattern_num == 2:
            colors = ('yellow', 'cyan')
            PlotStar(position, axes, colors, k)
        elif pattern_num == 3:
            colors = ('orange', 'purple')
            PlotStar(position, axes, colors, k)
        elif pattern_num == 4:
            colors = ('purple', 'yellow')
            PlotCircleCross(position, axes, colors, k)
        elif pattern_num == 5:
            colors = ('brown', 'green')
            PlotCircleCross(position, axes, colors, k)
        elif pattern_num == 6:
            colors = ('blue', 'magenta')
            PlotCircleCross(position, axes, colors, k)
        elif pattern_num == 7:
            colors = ('magenta', 'yellow')
            PlotSquares(position, axes, colors, k)
        elif pattern_num == 8:
            colors = ('cyan', 'magenta')
            PlotSquares(position, axes, colors, k)
        elif pattern_num == 9:
            colors = ('yellow', 'blue')
            PlotSquares(position, axes, colors, k)
        elif pattern_num == 10:
            colors = ('yellow', 'green')
            PlotSquareInside(position, axes, colors, k)
        elif pattern_num == 11:
            colors = ('blue', 'cyan')
            PlotSquareInside(position, axes, colors, k)
        elif pattern_num == 12:
            colors = ('green', 'orange')
            PlotFlower(position, axes, colors, k)
        elif pattern_num == 13:
            colors = ('cyan', 'magenta')
            PlotFlower(position, axes, colors, k)
        elif pattern_num == 14:
            colors = ('purple', 'cyan')
            PlotFlower(position, axes, colors, k) 
        elif pattern_num == 15:
            colors = ('blue', 'orange')
            PlotCrossCircle(position, axes, colors, k)
        elif pattern_num == 16:
            colors = ('green', 'magenta')
            PlotCrossCircle(position, axes, colors, k)
        elif pattern_num == 17:
            colors = ('magenta', 'yellow')
            PlotCrossCircle(position, axes, colors, k)
        elif pattern_num == 18:
            colors = ('brown', 'orange')
            PlotStarFlower(position, axes, colors, k)
        elif pattern_num == 19:
            colors = ('magenta', 'cyan')
            PlotSquareRotation(position, axes, colors, k)
        elif pattern_num == 20:
            colors = ('green', 'blue')
            PlotSquareCircCorner(position, axes, colors, k)
        elif pattern_num == 21:
            colors = ('Orange', 'cyan')
            PlotSquareRotCross(position, axes, colors, k)
        elif pattern_num == 22:
            colors = ('blue', 'yellow')
            PlotFlowerCirc(position, axes, colors, k)
        else:
            pass

def RotateVectors(x, y, angle):

    x_rot = x * np.cos(angle) - y * np.sin(angle) + 1
    y_rot = x * np.sin(angle) + y * np.cos(angle) + 1

    return x_rot, y_rot

def PlotBackground(position, axes, color, direction):

    angle = -direction * np.pi/2.
    x = np.array([-1, 0, 1])
    y = np.array([1, 0, 1])
    
    x_pos = position[0]
    y_pos = position[1]
    x_rot, y_rot = RotateVectors(x, y, angle)

    axes.fill(x_rot + x_pos, y_rot + y_pos, facecolor=color)

def PlotStar(position, axes, colors, direction):
    
    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    star_color = colors[1]
    angle = -direction * np.pi/2.
    x_star = np.array([-2/6., -1.7/3., -1/6., 0,     1/6.,  1.7/3., 2/6.])
    y_star = np.array([1,      2/3.,    2/3., 1/3.,  2/3.,  2/3.,   1])
    x_star_rot, y_star_rot = RotateVectors(x_star, y_star, angle)

    axes.fill(x_star_rot + x_pos, y_star_rot + y_pos, facecolor=star_color)

def PlotCircleCross(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    circle_color = colors[1]
    angle = -direction * np.pi/2.

    circle1  = plt.Circle((1, 1), 0.5, color=circle_color)
    t = np.linspace(np.pi/2., 3*np.pi/2., 100)
    radius = 0.5
    x_circ = np.array(np.sin(t) * radius)
    y_circ = np.array(np.cos(t) * radius + 1)
    x_cross1 = np.array([-0.3,      -0.19,     0.11, -0.11])
    x_cross2 = np.array([ 0.3,       0.19,    -0.11,  0.11])
    y_cross1 = np.array([ 1 - 0.19,  1 - 0.3,  1,     1])
    y_cross2 = np.array([ 1 - 0.19,  1 - 0.3,  1,     1])
    
    x_cross1_rot, y_cross1_rot = RotateVectors(x_cross1, y_cross1, angle)
    x_cross2_rot, y_cross2_rot = RotateVectors(x_cross2, y_cross2, angle)
    x_circ_rot,   y_circ_rot   = RotateVectors(x_circ,   y_circ,   angle)

    axes.fill(x_circ_rot + x_pos, y_circ_rot + y_pos, facecolor=circle_color)
    axes.fill(x_cross1_rot + x_pos, y_cross1_rot + y_pos, facecolor=background_color)
    axes.fill(x_cross2_rot + x_pos, y_cross2_rot + y_pos, facecolor=background_color)

def PlotSquares(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    square_color = colors[1]
    angle = -direction * np.pi/2.

    x_squares1 = np.array([0.45 - 1, 0.55, 0])
    y_squares1 = np.array([1, 1, 0.45])
    x_squares2 = np.array([0.3 - 1, 0.7 - 1, -0.5])
    y_squares2 = np.array([1, 1, 0.8])
    x_squares3 = np.array([0.3, 0.7, 0.5])
    y_squares3 = np.array([1, 1, 0.8])
    x_squares4 = np.array([0.8 - 1, 0, 0.2, 0])
    y_squares4 = np.array([0.5, 0.7, 0.5, 0.3])

    x_squares1_rot, y_squares1_rot = RotateVectors(x_squares1, y_squares1, angle)
    x_squares2_rot, y_squares2_rot = RotateVectors(x_squares2, y_squares2, angle)
    x_squares3_rot, y_squares3_rot = RotateVectors(x_squares3, y_squares3, angle)
    x_squares4_rot, y_squares4_rot = RotateVectors(x_squares4, y_squares4, angle)

    axes.fill(x_squares1_rot + x_pos, y_squares1_rot + y_pos, facecolor=square_color)
    axes.fill(x_squares2_rot + x_pos, y_squares2_rot + y_pos, facecolor=square_color)
    axes.fill(x_squares3_rot + x_pos, y_squares3_rot + y_pos, facecolor=square_color)
    axes.fill(x_squares4_rot + x_pos, y_squares4_rot + y_pos, facecolor=square_color)

def PlotSquareInside(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    inner_square_color = colors[0]
    outer_square_color = colors[1]
    angle = -direction * np.pi/2.

    x_squareInside1 = np.array([0.45 - 1, 0.55, 0])
    y_squareInside1 = np.array([1, 1, 0.45])
    x_squareInside2 = np.array([0.82 - 1, 0.18, 0])
    y_squareInside2 = np.array([1, 1, 0.82])

    x_squareInside1_rot, y_squareInside1_rot = RotateVectors(x_squareInside1, y_squareInside1, angle)
    x_squareInside2_rot, y_squareInside2_rot = RotateVectors(x_squareInside2, y_squareInside2, angle)

    axes.fill(x_squareInside1_rot + x_pos, y_squareInside1_rot + y_pos, facecolor=outer_square_color)
    axes.fill(x_squareInside2_rot + x_pos, y_squareInside2_rot + y_pos, facecolor=inner_square_color)

def PlotFlower(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    flower_color = colors[1]
    angle = -direction * np.pi/2.

    x_flower1 = np.array([0.2 - 1, 0.8, 0])
    y_flower1 = np.array([1, 1, 0.2])
    x_flower2 = np.array([-0.5, 0.7 - 1, 0.9 - 1])
    y_flower2 = np.array([0.7, 0.5, 0.9])
    x_flower3 = np.array([0.5, 0.3, 0.1])
    y_flower3 = np.array([0.7, 0.5, 0.9])

    x_flower1_rot, y_flower1_rot = RotateVectors(x_flower1, y_flower1, angle)
    x_flower2_rot, y_flower2_rot = RotateVectors(x_flower2, y_flower2, angle)
    x_flower3_rot, y_flower3_rot = RotateVectors(x_flower3, y_flower3, angle)

    axes.fill(x_flower1_rot + x_pos, y_flower1_rot + y_pos, facecolor=flower_color)
    axes.fill(x_flower2_rot + x_pos, y_flower2_rot + y_pos, facecolor=background_color)
    axes.fill(x_flower3_rot + x_pos, y_flower3_rot + y_pos, facecolor=background_color)

def PlotCrossCircle(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    cross_color = colors[1]
    angle = -direction * np.pi/2.

    t1 = np.linspace(0, 2*np.pi, 100)
    radius = 0.17
    x_circ1 = np.array(np.sin(t1) * radius)
    y_circ1 = np.array(np.cos(t1) * radius + 0.4)

    t2 = np.linspace(np.pi/2., 3*np.pi/2., 100)
    x_circ2 = np.array(np.sin(t2) * radius + 0.6)
    y_circ2 = np.array(np.cos(t2) * radius + 1)
    x_circ3 = np.array(np.sin(t2) * radius - 0.6)
    y_circ3 = np.array(np.cos(t2) * radius + 1)

    x_crossCircles1 = np.array([0.88 - 1, 0.12, 0.12, 0.88 - 1])
    y_crossCircles1 = np.array([1, 1, 0.4, 0.4])
    x_crossCircles2 = np.array([0.4 - 1, 0.4 - 1, 0.6, 0.6])
    y_crossCircles2 = np.array([0.88, 1, 1, 0.88])

    x_crossCircles1_rot, y_crossCircles1_rot = RotateVectors(x_crossCircles1, y_crossCircles1, angle)
    x_crossCircles2_rot, y_crossCircles2_rot = RotateVectors(x_crossCircles2, y_crossCircles2, angle)
    x_circ1_rot, y_circ1_rot = RotateVectors(x_circ1, y_circ1, angle)
    x_circ2_rot, y_circ2_rot = RotateVectors(x_circ2, y_circ2, angle)
    x_circ3_rot, y_circ3_rot = RotateVectors(x_circ3, y_circ3, angle)

    axes.fill(x_crossCircles1_rot + x_pos, y_crossCircles1_rot + y_pos, facecolor=cross_color)
    axes.fill(x_crossCircles2_rot + x_pos, y_crossCircles2_rot + y_pos, facecolor=cross_color)
    axes.fill(x_circ1_rot + x_pos, y_circ1_rot + y_pos, facecolor = cross_color)
    axes.fill(x_circ2_rot + x_pos, y_circ2_rot + y_pos, facecolor = cross_color)
    axes.fill(x_circ3_rot + x_pos, y_circ3_rot + y_pos, facecolor = cross_color)

def PlotStarFlower(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    flower_color = colors[1]
    angle = -direction * np.pi/2.

    t1 = np.linspace(np.pi/2., 3*np.pi/2., 100)
    t2 = np.linspace(0, 2*np.pi, 100)
    radius = 0.25
    radius2 = 0.5
    x_circ1 = np.array(np.sin(t1) * radius - 1/2.)
    y_circ1 = np.array(np.cos(t1) * radius + 1)
    x_circ2 = np.array(np.sin(t1) * radius + 1/2.)
    y_circ2 = np.array(np.cos(t1) * radius + 1)
    x_circ3 = np.array(np.sin(t2) * radius)
    y_circ3 = np.array(np.cos(t2) * radius + 1/2)
    x_circ4 = np.array(np.sin(t1) * radius2)
    y_circ4 = np.array(np.cos(t1) * radius2 + 1)

    x_starFlower = np.array([0.62 - 1, 0.38, 0.1,    0, 0.9 - 1, 0.62 - 1])
    y_starFlower = np.array([1,           1, 0.9, 0.62, 0.9,            1])

    x_circ1_rot, y_circ1_rot = RotateVectors(x_circ1, y_circ1, angle)
    x_circ2_rot, y_circ2_rot = RotateVectors(x_circ2, y_circ2, angle)
    x_circ3_rot, y_circ3_rot = RotateVectors(x_circ3, y_circ3, angle)
    x_circ4_rot, y_circ4_rot = RotateVectors(x_circ4, y_circ4, angle)
    x_starFlower_rot, y_starFlower_rot = RotateVectors(x_starFlower, y_starFlower, angle)

    axes.fill(x_circ1_rot + x_pos, y_circ1_rot + y_pos, facecolor=flower_color)
    axes.fill(x_circ2_rot + x_pos, y_circ2_rot + y_pos, facecolor=flower_color)
    axes.fill(x_circ3_rot + x_pos, y_circ3_rot + y_pos, facecolor=flower_color)
    axes.fill(x_circ4_rot + x_pos, y_circ4_rot + y_pos, facecolor=flower_color)
    axes.fill(x_starFlower_rot + x_pos, y_starFlower_rot + y_pos, facecolor=background_color)

def PlotSquareRotation(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    square_color = colors[1]
    angle = -direction * np.pi/2.

    t1 = np.linspace(-0.155, np.pi/2. + 0.155, 100)
    t2 = np.linspace(-np.pi/2. - 0.155, 0.155, 100)
    radius = 0.40
    x_circ1 = np.array(np.sin(t1) * radius - 2/3.)
    y_circ1 = np.array(np.cos(t1) * radius + 1/3.)
    x_circ2 = np.array(np.sin(t2) * radius + 2/3.)
    y_circ2 = np.array(np.cos(t2) * radius + 1/3.)
    

    x_squareRot1 = np.array([1/3. - 1, 5/3 - 1., 2/3., 1/3., -1/3., -2/3.])
    y_squareRot1 = np.array([1,               1, 2/3., 1/3.,  1/3.,  2/3.])
    x_squareRot2 = np.array([2/3. - 1, 1/3., 0])
    y_squareRot2 = np.array([1.,         1., 2/3.])

    x_circ1_rot, y_circ1_rot = RotateVectors(x_circ1, y_circ1, angle)
    x_circ2_rot, y_circ2_rot = RotateVectors(x_circ2, y_circ2, angle)
    x_squareRot1_rot, y_squareRot1_rot = RotateVectors(x_squareRot1, y_squareRot1, angle)
    x_squareRot2_rot, y_squareRot2_rot = RotateVectors(x_squareRot2, y_squareRot2, angle)
    
    axes.fill(x_squareRot1_rot + x_pos, y_squareRot1_rot + y_pos, facecolor=square_color)
    axes.fill(x_squareRot2_rot + x_pos, y_squareRot2_rot + y_pos, facecolor=background_color)
    axes.fill(x_circ1_rot + x_pos, y_circ1_rot + y_pos, facecolor=background_color)
    axes.fill(x_circ2_rot + x_pos, y_circ2_rot + y_pos, facecolor=background_color)

def PlotSquareCircCorner(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    square_color = colors[1]
    angle = -direction * np.pi/2.

    t1 = np.linspace(np.pi/2., 3*np.pi/2., 100)
    radius = 1/4.
    x_circ1 = np.array(np.sin(t1) * radius)
    y_circ1 = np.array(np.cos(t1) * radius + 1)

    x_squareCircCorn1 = np.array([-1/2., 1/2., 1/2., 1/4., -1/4., -1/2.])
    y_squareCircCorn1 = np.array([1., 1., 3/4., 1/2., 1/2., 3/4.])

    x_squareCircCorn1_rot, y_squareCircCorn1_rot = RotateVectors(x_squareCircCorn1, y_squareCircCorn1, angle)
    x_circ1_rot, y_circ1_rot = RotateVectors(x_circ1, y_circ1, angle)

    axes.fill(x_squareCircCorn1_rot + x_pos, y_squareCircCorn1_rot + y_pos, facecolor=square_color)
    axes.fill(x_circ1_rot + x_pos, y_circ1_rot + y_pos, facecolor=background_color)

def PlotSquareRotCross(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    square_color = colors[1]
    angle = -direction * np.pi/2.

    t1 = np.linspace(-np.pi/2. - 0.27, 0.27, 100)
    t2 = np.linspace(-0.27, np.pi/2. + 0.27, 100)
    radius = 0.48
    x_circ1 = np.array(np.sin(t1) * radius + 2/3.)
    y_circ1 = np.array(np.cos(t1) * radius + 1/3.)
    x_circ2 = np.array(np.sin(t2) * radius - 2/3.)
    y_circ2 = np.array(np.cos(t2) * radius + 1/3.)

    x_squareRotCross1 = np.array([1/3. - 1, 2/3., 2/3., 1/3., -1/3., -2/3.])
    y_squareRotCross1 = np.array([1,           1, 2/3., 1/3.,  1/3.,  2/3.])

    x_squareRotCross1_rot, y_squareRotCross1_rot = RotateVectors(x_squareRotCross1, y_squareRotCross1, angle)
    x_circ1_rot, y_circ1_rot = RotateVectors(x_circ1, y_circ1, angle)
    x_circ2_rot, y_circ2_rot = RotateVectors(x_circ2, y_circ2, angle)

    axes.fill(x_squareRotCross1_rot + x_pos, y_squareRotCross1_rot + y_pos, facecolor=square_color)
    axes.fill(x_circ1_rot + x_pos, y_circ1_rot + y_pos, facecolor=background_color)
    axes.fill(x_circ2_rot + x_pos, y_circ2_rot + y_pos, facecolor=background_color)


def PlotFlowerCirc(position, axes, colors, direction):

    background_color = colors[0]
    PlotBackground(position, axes, background_color, direction)

    x_pos = position[0]
    y_pos = position[1]
    flower_color = colors[1]
    angle = -direction * np.pi/2.

    t1 = np.linspace(0, 2*np.pi, 100)
    t2 = np.linspace(np.pi/2., 3*np.pi/2., 100)
    radius  = 1/3.
    radius2 = 0.28
    x_circ1 = np.array(np.sin(t2) * radius - 1/3.)
    y_circ1 = np.array(np.cos(t2) * radius + 1)
    x_circ2 = np.array(np.sin(t2) * radius + 1/3.)
    y_circ2 = np.array(np.cos(t2) * radius + 1)
    x_circ3 = np.array(np.sin(t1) * radius)
    y_circ3 = np.array(np.cos(t1) * radius + 2/3.)
    x_circ4 = np.array(np.sin(t2) * radius2)
    y_circ4 = np.array(np.cos(t2) * radius2 + 1)

    x_circ1_rot, y_circ1_rot = RotateVectors(x_circ1, y_circ1, angle)
    x_circ2_rot, y_circ2_rot = RotateVectors(x_circ2, y_circ2, angle)
    x_circ3_rot, y_circ3_rot = RotateVectors(x_circ3, y_circ3, angle)
    x_circ4_rot, y_circ4_rot = RotateVectors(x_circ4, y_circ4, angle)

    axes.fill(x_circ1_rot + x_pos, y_circ1_rot + y_pos, facecolor = flower_color)
    axes.fill(x_circ2_rot + x_pos, y_circ2_rot + y_pos, facecolor = flower_color)
    axes.fill(x_circ3_rot + x_pos, y_circ3_rot + y_pos, facecolor = flower_color)
    axes.fill(x_circ4_rot + x_pos, y_circ4_rot + y_pos, facecolor = background_color)

dirname = os.path.dirname(__file__)

filename = os.path.join(dirname, 'EternityIIPiecesFull.txt')

n_iterations = 1000
pieces = LoadPieces(filename)
best_solution = FindBestSolution(pieces, n_iterations)
PlotSolution(best_solution)
