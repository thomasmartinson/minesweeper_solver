import time, math
from typing import Iterable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
from pyautogui import click, rightClick
from webdriver_manager.driver import OperaDriver

import cProfile

difficulty = "expert"
pyautogui.PAUSE = 0

# initialize driver
chrome_options = Options()
chrome_options.add_experimental_option(
    "excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(
    executable_path=ChromeDriverManager().install(), options=chrome_options)

class Cell:
  def __init__(self, x, y, value, elem, solved=False):
    self.x = x
    self.y = y
    self.value = value
    self.elem = elem
    self.point = elem.location
    self.solved = solved

if difficulty == 'beginner':
    width = 9
    height = 9
    mines = 10
elif difficulty == 'intermediate':
    width = 16
    height = 16
    mines = 40
else: # expert
    width = 30
    height = 16
    mines = 99 

flags_left = mines

#
def get_value_of_elem(elem : WebElement):
    class_name = elem.get_attribute('class')
    if 'blank' in class_name:
        return 'o'
    elif 'bombflagged' in class_name:
        return 'x'
    elif 'bombdeath' in class_name:
        raise Exception('It\'s a boy!')
    else:
        return int(class_name[-1])

cells = []

def initialize_cells():
    # remove existing columns
    while len(cells) > 0:
      cells.pop(0)

    # add new columns
    for x in range(width):
        column = []
        for y in range(height):
            elem = driver.find_element_by_id('{}_{}'.format(y+1, x+1))
            value = 'o'
            column.append(Cell(x, y, value, elem))
        cells.append(column)


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
                neighbors.add(cells[x+i][y+j])
        
    return neighbors
  

# returns a set of all the neighbors with the given value of the cell at (x,y)
def get_neighbors_with_value(x, y, val) -> Iterable[Cell]:
    neighbors = get_neighbors_of(x, y)
    neighbors_with_val = set()
    for cell in neighbors:
        if cell.value == val:
            neighbors_with_val.add(cell)
    
    return neighbors_with_val


# reads and updates the values of cells revealed by a pocket
def read_pocket(this_cell):
  this_cell.solved = True
  # print("pocket at ({}, {})".format(this_cell.x, this_cell.y))
  for that_cell in get_neighbors_with_value(this_cell.x, this_cell.y, 'o'):
    that_cell.value = get_value_of_elem(that_cell.elem)
    if that_cell.value == 0:
      read_pocket(that_cell)

  return

def click_cell(cell: Cell):
    point = cell.point
    pyautogui.click(point['x']+8, point['y']+8)

# reveals the cell
def reveal(cell : Cell):
    if cell.value == 'o':
        click_cell(cell)
        cell.value = get_value_of_elem(cell.elem)
        if cell.value == 0:
          read_pocket(cell)
        return 1
    return 0

# flag the cell
def flag(cell : Cell):
    cell.value = 'x'
    cell.solved = True
    # point = cell.elem.location
    # rightClick(point['x']+8, point['y']+8)
    return 1


# flag all of the cells in the given set
def flag_all(cell_set : Iterable[Cell]):
    total_clicks = 0
    for cell in cell_set:
      total_clicks += flag(cell)
    return total_clicks
  

# reveal all of the cells in the given set
def reveal_all(cellSet : Iterable[Cell]):
    total_clicks = 0
    for cell in cellSet:
      total_clicks += reveal(cell)
    return total_clicks

# reveal all the neighbors of the given cell by using the spacebar shortcut
# def reveal_all_neighbors_of():
#     # TODO
#     return 1



# converts 2D coordinates to 1D index
def to_1d(x, y):
    return y * width + x


# updates the board array with new values based on the page document
# returns True if no cells are blank, otherwise returns False
# N.B.: this is a costly operation
def load_board():
    solved = False
    for column in cells:
        for cell in column:
            if cell.value == 'o':
                solved = False

    return solved

# returns the number of adjacent mines that are still hidden
def n_adj(cell : Cell):
    n = cell.value
    flagged = len(get_neighbors_with_value(cell.x, cell.y, 'x'))
    return n - flagged


# solves the puzzle
def solve():
    driver.refresh()
    driver.get('https://minesweeperonline.com/#{}-200'.format(difficulty))
    driver.fullscreen_window()
    time.sleep(3)
    pyautogui.press('f2')
    time.sleep(2)
    initialize_cells()

    # reveal middle cell
    reveal(cells[math.floor(width / 2)][math.floor(height / 2)])
    load_board()

    solved = False
    stuck = False
    loops = 0

    while not solved and not stuck and loops < 100:
        print('loop {}'.format(loops))
        num_clicks = 0

        # iterate over each cell
        for x in range(width):
            for y in range(height):
                # skip if cell is solved
                if cells[x][y].solved:
                    continue
        
                val = cells[x][y].value

                if flags_left == 0 and val == 'o':
                    reveal(cells[x][y])
                    cells[x][y].solved = True

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
                    # print('flagging all neighbors of ({}, {})'.format(x, y))
                    num_clicks += flag_all(blank)
                    cells[x][y].solved = True
                    continue

                # reveal all neighbors
                if len(flagged) == n:
                    # print('revealing all neighbors of ({}, {})'.format(x, y))
                    num_clicks += reveal_all(blank)
                    cells[x][y].solved = True
                    continue

                for cell in neighbors:
                    #
                    if cell.value in ['x', 'o']:
                        continue

                    # if all of a neighbor's blank neighbors are also neighbors of the current cell...
                    blankNeighborsOfNeighbor = get_neighbors_with_value(
                        cell.x,
                        cell.y,
                        'o'
                    )

                    if neighbors.issuperset(blankNeighborsOfNeighbor):
                        # if n_adj of the neighbor = n_adj of current cell...
                        if n_adj(cells[x][y]) == n_adj(cell):
                            # reveal all other neighbors
                            # print('reveal all neighbors of ({}, {})'.format(x, y))
                            num_clicks += reveal_all(
                                neighbors.difference(blankNeighborsOfNeighbor)
                            )

                for cell in neighbors:
                    #
                    if cell.value in ['x', 'o']:
                        continue

                    greater_n = n_adj(cells[x][y])
                    lesser_n = n_adj(cell)
                    if greater_n > lesser_n:
                        # if difference of n_adj equals number of blank cells not shared
                        blankNeighbors = get_neighbors_with_value(x, y, 'o')
                        blankNeighborsOfNeighbor = get_neighbors_with_value(cell.x, cell.y, 'o')
                        sharedBlankNeighbors = blankNeighbors.intersection(
                            blankNeighborsOfNeighbor
                        )
                        if greater_n - lesser_n == len(blankNeighbors) - len(sharedBlankNeighbors):
                            # print("DOING THE THING")

                            # reveal all other neighbors of lesser
                            num_clicks += reveal_all(
                                blankNeighborsOfNeighbor.difference(sharedBlankNeighbors)
                            )

                            # flag all other neighbors of greater
                            num_clicks += flag_all(
                                blankNeighbors.difference(sharedBlankNeighbors)
                            )
    

        # determine outcome and load board
        stuck = num_clicks == 0
        solved = load_board()
        loops += 1

        if stuck:
          # TODO
          print('guessing')
          try:
              for column in cells:
                  for cell in column:
                    if cell.value == 'o':
                        reveal(cell)
                        stuck = False
                        break
                  else:
                      continue
                  break
          except Exception as err:
              pass

          


    # report outcome
    if solved:
        print("Puzzle solved!")

    if stuck:
        print("Solver got stuck :(")

    print('{} total loops'.format(loops))

def solve_forever():
  cProfile.run("solve()")
  while True:
    response = input("Game over. Continue? (y/n)\n")
    if response == 'y':
        cProfile.run("solve()")
    elif response == 'n':
        driver.quit()
        break
    else:
        continue

solve_forever()
