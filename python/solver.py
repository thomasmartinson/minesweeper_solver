import time, math
from typing import Iterable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui as _
from webdriver_manager.driver import OperaDriver

import cProfile

# initialize driver
chrome_options = Options()
chrome_options.add_experimental_option(
    "excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(
    executable_path=ChromeDriverManager().install(), options=chrome_options)
driver.get('https://minesweeperonline.com/#beginner-200')
driver.fullscreen_window()
time.sleep(5)

width = 9
height = 9
mines = 10
flags_left = mines
# TODO might be buggy
board = [['o' for i in range(height)] for j in range(width)]
is_cell_solved = [[False for i in range(height)] for j in range(width)]


# returns the element at x, y
def get_elem(x, y) -> WebElement:
    return driver.find_element_by_id('{}_{}'.format(y+1, x+1))

class Cell:
  def __init__(self, x, y, elem):
    self.x = x
    self.y = y
    self.elem = elem

#
def get_value_of_elem(elem : WebElement):
    class_name = elem.get_attribute('class')
    if 'blank' in class_name:
        return 'o'
    elif 'bombflagged' in class_name:
        return 'x'
    else:
        return int(class_name[-1])

# get the
def get_value_of(x, y):
    return get_value_of_elem(get_elem(x, y))
    

# reveals the cell located at x, y
def reveal(x, y):
    if get_value_of(x,y) == 'o':
        point = get_elem(x,y).location
        _.click(point['x']+8, point['y']+8, duration=0.25)
        return 1
    return 0


# flag the cell located at x, y
def flag(x, y):
    if get_value_of(x,y) == 'o':
        point = get_elem(x,y).location
        _.rightClick(point['x']+8, point['y']+8, duration=0.25)
        return 1
    return 0


# flag all of the cells in the given set
def flag_all(cell_set):
    total_clicks = 0
    for cell in cell_set:
      total_clicks += flag(cell.x, cell.y)
    return total_clicks
  

# reveal all of the cells in the given set
def reveal_all(cellSet):
    total_clicks = 0
    for cell in cellSet:
      total_clicks += reveal(cell.x, cell.y)
    return total_clicks
  

# returns a set of coordinates of all adjacent cells
def get_neighbors_of(x, y) -> Iterable[Cell]:
    neighbors = set()
    for i in range (-1, 2):
        for j in range (-1, 2):
            # skip the square itself
            if i == 0 and j == 0:
                continue
        
            if (x + i >= 0 and
                x + i < width and
                y + j >= 0 and
                y + j < height):
                neighbors.add(Cell(x+i, y+j, get_elem(x+i, y+j)))
        
    return neighbors
  

# converts 2D coordinates to 1D index
def to_1d(x, y):
    return y * width + x


# updates the board array with new values based on the page document
# returns True if no cells are blank, otherwise returns False
# N.B.: this is a costly operation
def load_board():
    solved = True
    flags = 0
    for x in range(width):
        for y in range(height):
            new_value = get_value_of(x, y)
            if new_value == 'o':
                solved = False
            elif new_value == 'x':
                flags += 1
    
            board[x][y] = new_value
    

    flags_left = mines - flags
    return solved


# returns a set of all the neighbors with the given value of the cell at (x,y)
def get_neighbors_with_value(x, y, val) -> Iterable[Cell]:
    neighbors = get_neighbors_of(x, y)
    neighbors_with_val = set()
    for cell in neighbors:
        if get_value_of(cell.x, cell.y) == val:
            neighbors_with_val.add(cell)
    
    return neighbors_with_val


# returns the number of adjacent mines that are still hidden
def n_adj(x, y):
    n = get_value_of(x, y)
    flagged = len(get_neighbors_with_value(x, y, 'x'))
    return n - flagged


# solves the puzzle
def solve():
# reveal middle cell
    reveal(math.floor(width / 2), math.floor(height / 2))
    load_board()

    solved = False
    stuck = False
    loops = 0
    solved

    while not solved and not stuck and loops < 100:
        print('loop {}'.format(loops))
        num_clicks = 0

        # iterate over each cell
        for x in range(width):
            for y in range(height):
                # skip if cell is solved
                if is_cell_solved[x][y]:
                    continue
        
                val = board[x][y]
                # skip if blank or flagged or empty
                if val in [0, 'x', 'o']:
                    continue
                
                n = val
                neighbors = get_neighbors_of(x, y)

                # count flagged
                flagged = get_neighbors_with_value(x, y, 'x')

                # count blank
                blank = get_neighbors_with_value(x, y, 'o')

                # flag all neighbors
                if len(blank) + len(flagged) == n and len(blank) > 0:
                    print('flagging all neighbors of ({}, {})'.format(x, y))
                    num_clicks += flag_all(blank)
                    is_cell_solved[x][y] = True
                    continue

                # reveal all neighbors
                if len(flagged) == n:
                    print('revealing all neighbors of ({}, {})'.format(x, y))
                    num_clicks += reveal_all(blank)
                    is_cell_solved[x][y] = True
                    continue

                for cell in neighbors:
                    #
                    if get_value_of_elem(cell.elem) in ['x', 'o']:
                        continue

                    # if all of a neighbor's blank neighbors are also neighbors of the current cell...
                    blankNeighborsOfNeighbor = get_neighbors_with_value(
                        cell.x,
                        cell.y,
                        'o'
                    )

                    if neighbors.issuperset(blankNeighborsOfNeighbor):
                        # if n_adj of the neighbor = n_adj of current cell...
                        if n_adj(x, y) == n_adj(cell.x, cell.y):
                            # reveal all other neighbors
                            print('reveal all neighbors of ({}, {})'.format(x, y))
                            num_clicks += reveal_all(
                                neighbors.difference(blankNeighborsOfNeighbor)
                            )

                # for cell in neighbors:
                #     greater_n = n_adj(x, y)
                #     lesser_n = n_adj(cell.x, cell.y)
                #     if greater_n > lesser_n:
                #         # if difference of n_adj equals number of blank cells not shared
                #         blankNeighbors = get_neighbors_with_value(x, y, 'o')
                #         blankNeighborsOfNeighbor = get_neighbors_with_value(cell.x, cell.y, blank)
                #         sharedBlankNeighbors = blankNeighbors.intersection(
                #             blankNeighborsOfNeighbor
                #         )
                #         if greater_n - lesser_n == len(blankNeighbors) - len(sharedBlankNeighbors):
                #             print("DOING THE THING")

                #             # reveal all other neighbors of lesser
                #             num_clicks += reveal_all(
                #                 blankNeighborsOfNeighbor.difference(sharedBlankNeighbors)
                #             )

                #             # flag all other neighbors of greater
                #             num_clicks += flag_all(
                #                 blankNeighbors.difference(sharedBlankNeighbors)
                #             )
    

        # determine outcome and load board
        stuck = num_clicks == 0
        solved = load_board()
        loops += 1


    # report outcome
    if solved:
        print("Puzzle solved!")

    if stuck:
        print("Solver got stuck :(")

    print('{} total loops'.format(loops))

cProfile.run("solve()")
