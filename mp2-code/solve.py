# -*- coding: utf-8 -*-
import numpy as np
from random import shuffle

def solve(board, pents, app = None):
    """
    This is the function you will implement. It will take in a numpy array of the board
    as well as a list of n tiles in the form of numpy arrays. The solution returned
    is of the form [(p1, (row1, col1))...(pn,  (rown, coln))]
    where pi is a tile (may be rotated or flipped), and (rowi, coli) is 
    the coordinate of the upper left corner of pi in the board (lowest row and column index 
    that the tile covers).
    
    -Use np.flip and np.rot90 to manipulate pentominos.
    
    -You can assume there will always be a solution.
    """
    board = np.negative(board)

    coor_remain = set()
    cor_pent_dict = dict()
    value_dict = dict()

    for y in range(board.shape[0]):
        for x in range(board.shape[1]):
            coordinate = (y,x)
            cor_pent_dict[coordinate] = list()
            coor_remain.add(coordinate)

    for y in range(board.shape[0]):
        for x in range(board.shape[1]):
            coordinate = (y,x)
            for pent in pents:
                rot_flip_list = generate_ori(pent)
                for ori_pent in rot_flip_list:
                    cor_add_list =  check_placement(board, ori_pent, coordinate)
                    if cor_add_list != None:
                        for coor in cor_add_list:
                            cor_pent_dict[coor].append((coordinate, ori_pent, cor_add_list))
                            key = tuple(cor_add_list)
                            if key not in value_dict.keys():
                                value_dict[key] = set([coor])
                            else: 
                                value_dict[key].add(coor)
    
    # for c in cor_pent_dict.keys():
    #     cor_pent_dict[c] = sorted(cor_pent_dict[c], key=lambda value: len(value_dict[tuple(value[2])]), reverse = True)
    
    # for y in range(board.shape[0]):
    #     for x in range(board.shape[1]):
    #         coordinate = (y,x)
    #         shuffle(cor_pent_dict[coordinate])
                        
    pents_remain = []
    for p in pents:
        pents_remain.append(get_pent_idx(p))
    
    solution = recursion([], value_dict, cor_pent_dict, coor_remain, pents_remain)
    print(solution)
    return solution
            
def recursion(solution, value_dict, cor_pent_dict, coor_remain, pents_remain):
    least_coor = min(cor_pent_dict.keys(), key=lambda least_coor: len(cor_pent_dict[least_coor]))
    if len(cor_pent_dict[least_coor]) == 0:
        return None
    temp_cor_pent = []
    for i in range(len(cor_pent_dict[least_coor])):
        value = max(cor_pent_dict[least_coor], key=lambda value: len(value_dict[tuple(value[2])]))

        assignment_cor = value[0]
        ori_pent = value[1]
        cor_add_list = value[2]

        pidx = get_pent_idx(ori_pent)
        solution.append((ori_pent, assignment_cor))
        pents_remain.remove(pidx)
                
        for c in cor_add_list:
            coor_remain.remove(c)

        temp_list = []
        for c in cor_add_list:
            temp = cor_pent_dict[c]
            temp_list.append((c, temp))
            cor_pent_dict.pop(c)

        temp_pop_list = []
        for c in cor_pent_dict.keys():
            for i in range(len(cor_pent_dict[c])- 1, -1, -1):
                temp = cor_pent_dict[c][i]
                idx = get_pent_idx(temp[1])
                temp_set = temp[2]
                if idx == pidx or len(temp_set & cor_add_list) != 0:
                    temp_pop_list.append((c, i, temp))
                    cor_pent_dict[c].pop(i)
        
        temp_value = value_dict[tuple(cor_add_list)]
        value_dict.pop(tuple(cor_add_list))

        temp_value_list = []
        for v in value_dict.keys():
            for c in cor_add_list:
                if c in value_dict[v]:
                    temp_value_list.append((v, c))
                    value_dict[v].remove(c)

        if len(coor_remain) == 0:
            return solution

        result = recursion(solution, value_dict, cor_pent_dict, coor_remain, pents_remain)
        if result != None:
            return result
        else:
            solution.pop()
            pents_remain.append(pidx)
            coor_remain.update(cor_add_list)

            for c, i, temp in temp_pop_list:
                cor_pent_dict[c].insert(i, temp)

            for c, temp in temp_list:
                cor_pent_dict[c] = temp

            for v, c in temp_value_list:
                value_dict[v].add(c)
            
            value_dict[tuple(value[2])] = temp_value
        temp_cor_pent.append(value)
        cor_pent_dict[least_coor].remove(value)
    
    for v in temp_cor_pent:
        cor_pent_dict[least_coor].append(v)

    return None

def add_pent(board, pidx, cor_add_list):
    for c in cor_add_list:
        row = c[0]
        col = c[1]
        if board[row][col] != -1:
            print ("                                                       error")

        board[row][col] = (pidx + 1)

def check_placement(board, pent, coord):
    cor_add_list = set()
    for row in range(pent.shape[0]):
        for col in range(pent.shape[1]):
            if pent[row][col] != 0:
                if coord[0]+row >= board.shape[0] or coord[1]+col >= board.shape[1]: # outside board
                    return None
                if board[coord[0]+row][coord[1]+col] >= 0: # Overlap
                    return None
                cor_add_list.add((coord[0]+row, coord[1]+col))
    return cor_add_list

def get_pent_idx(pent):
    """
    Returns the index of a pentomino.
    """
    pidx = 0
    for i in range(pent.shape[0]):
        for j in range(pent.shape[1]):
            if pent[i][j] != 0:
                pidx = pent[i][j]
                break
        if pidx != 0:
            break
    if pidx == 0:
        return -1
    return pidx - 1

def generate_ori(pent): # idx, rot:(0 - 3), flip:(0: non_flip; 1:fliped)
    result = []

    transformed = []
    transformed += [np.rot90(pent, i) for i in range(4)]
    flipped = np.flip(pent, axis=1)
    transformed += [np.rot90(flipped, i) for i in range(4)]
    for p1 in transformed:
        flag = True
        for p2 in result:
            if (np.array_equal(p1, p2)):
                flag = False
        if flag:
            result.append(p1)
    return result