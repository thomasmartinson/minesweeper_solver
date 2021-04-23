// do this

// load jQuery
var script = document.createElement("script");
script.src = "https://code.jquery.com/jquery-3.4.1.min.js";
document.getElementsByTagName("head")[0].appendChild(script);

// set functions from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set
function isSuperset(set, subset) {
  for (let elem of subset) {
    if (!set.has(elem)) {
      return false;
    }
  }
  return true;
}

function union(setA, setB) {
  let _union = new Set(setA);
  for (let elem of setB) {
    _union.add(elem);
  }
  return _union;
}

function intersection(setA, setB) {
  let _intersection = new Set();
  for (let elem of setB) {
    if (setA.has(elem)) {
      _intersection.add(elem);
    }
  }
  return _intersection;
}

function symmetricDifference(setA, setB) {
  let _difference = new Set(setA);
  for (let elem of setB) {
    if (_difference.has(elem)) {
      _difference.delete(elem);
    } else {
      _difference.add(elem);
    }
  }
  return _difference;
}

function difference(setA, setB) {
  let _difference = new Set(setA);
  for (let elem of setB) {
    _difference.delete(elem);
  }
  return _difference;
}

// my own code

class BoardSolver {
  height; // number of cells along vertical axis
  width; // number of cells along horizontal axis
  mouse = { left: 0, right: undefined }; // defines values for left and right clicks
  board; // 2D array of all cell values, board[x][y] is the value of cell at (x, y)
  flag = "x"; // stand-in for the value of a flagged cell
  blank = "o"; // stand-in for the value of an unrevealed cell
  cells; // 1D array of all the cell elements on the page
  isCellSolved; // 2D array of booleans tracking if the cell has been solved
  boardElems; // 2D array of all cell elements on the board
  mines;
  flagsLeft;

  constructor(height, width, mines) {
    this.height = height;
    this.width = width;
    this.cells = $("[ondragstart]");
    this.board = this.initializeBoard(this.blank);
    this.boardElems = this.initializeBoard("");
    this.isCellSolved = this.initializeBoard(false);
    this.mines = mines;
    this.flagsLeft = mines;
  }

  // flag the cell at (x, y) if it is blank and update the board
  // returns 1 if click was executed
  flagCell(x, y) {
    if (this.getValueOf(x, y) === this.blank) {
      cellClick(x, y, this.mouse.right);
      this.board[x][y] = this.flag;
      return 1;
    }
    return 0;
  }

  // reveal the cell at (x, y) if board says it is blank
  // returns 1 if click was executed
  revealCell(x, y) {
    if (this.getValueOf(x, y) === this.blank) {
      cellClick(x, y, this.mouse.left);
      return 1;
    }
    return 0;
  }

  // flag all of the cells in the given set
  flagAll(cellSet) {
    let totalClicks = 0;
    for (let cell of cellSet) {
      totalClicks += this.flagCell(cell.x, cell.y);
    }
    return totalClicks;
  }

  // reveal all of the cells in the given set
  revealAll(cellSet) {
    let totalClicks = 0;
    for (let cell of cellSet) {
      totalClicks += this.revealCell(cell.x, cell.y);
    }
    return totalClicks;
  }

  // returns a set of coordinates of all adjacent cells
  getNeighborsOf(x, y) {
    const neighbors = new Set();
    for (let i = -1; i <= 1; i++) {
      for (let j = -1; j <= 1; j++) {
        // skip the square itself
        if (i == 0 && j == 0) {
          continue;
        }

        if (
          x + i >= 0 &&
          x + i < this.width &&
          y + j >= 0 &&
          y + j < this.height
        ) {
          neighbors.add(this.boardElems[x + i][y + j]);
        }
      }
    }
    return neighbors;
  }

  // converts 2D coordinates to 1D index
  to_1d(x, y) {
    return y * this.width + x;
  }

  // updates the board array with new values based on the page document
  // returns true if no cells are blank, otherwise returns false
  // N.B.: this is a costly operation
  loadBoard() {
    // load board elems
    for (let x = 0; x < this.width; x++) {
      for (let y = 0; y < this.height; y++) {
        this.boardElems[x][y] = {
          x: x,
          y: y,
          elem: this.cells[this.to_1d(x, y)],
        };
      }
    }

    let solved = true;
    let flags = 0;
    for (let x = 0; x < this.width; x++) {
      for (let y = 0; y < this.height; y++) {
        const newValue = this.getValueOf(x, y);
        if (newValue === this.blank) {
          solved = false;
        } else if (newValue === this.flag) {
          flags++;
        }
        this.board[x][y] = newValue;
      }
    }
    this.flagsLeft = this.mines - flags;
    return solved;
  }

  // initializes the board object as a 2D array of all blank cells
  initializeBoard(val) {
    let newBoard = [];
    for (let i = 0; i < this.width; i++) {
      let newCol = [];
      for (let j = 0; j < this.height; j++) {
        newCol.push(val);
      }
      newBoard.push(newCol);
    }
    return newBoard;
  }

  // get the value of the cell at (x, y) based on the current elements on the wepage
  getValueOf(x, y) {
    // get 1D index of (x, y)
    const index = y * this.width + x;
    const elem = this.cells[index];
    const filename = elem
      .getElementsByTagName("img")[0]
      .src.split("/")
      .slice(-1)[0];

    // find value based on the name of the img file
    switch (filename) {
      case "blank.gif":
        return "o";
      case "bombflagged.gif":
        return "x";
      default:
        return parseInt(filename[4]);
    }
  }

  // returns a set of all the neighbors with the given value of the cell at (x,y)
  getNeighborsWithValue(x, y, val) {
    const neighbors = this.getNeighborsOf(x, y);
    const neighborsWithValue = new Set();
    for (let cell of neighbors) {
      if (this.getValueOf(cell.x, cell.y) === val) {
        neighborsWithValue.add(cell);
      }
    }
    return neighborsWithValue;
  }

  // returns the number of adjacent mines that are still hidden
  nAdj(x, y) {
    const n = this.getValueOf(x, y);
    const flagged = this.getNeighborsWithValue(x, y, this.flag).size;
    return n - flagged;
  }

  // solves the puzzle
  solve() {
    // reveal middle cell
    this.revealCell(Math.floor(this.width / 2), Math.floor(this.height / 2));
    this.loadBoard();

    let solved = false;
    let stuck = false;
    let loops = 0;

    while (!solved && !stuck && loops < 100) {
      console.log(`loop ${loops}`);
      let numClicks = 0;

      // iterate over each cell
      for (let x = 0; x < this.width; x++) {
        for (let y = 0; y < this.height; y++) {
          // skip if cell is solved
          if (this.isCellSolved[x][y]) {
            continue;
          }

          const val = this.board[x][y];
          // skip if blank or flagged or empty
          if ([0, this.blank, this.flag].includes(val)) {
            continue;
          }

          const n = val;
          const neighbors = this.getNeighborsOf(x, y);

          // count flagged
          let flagged = this.getNeighborsWithValue(x, y, this.flag);

          // count blank
          let blank = this.getNeighborsWithValue(x, y, this.blank);

          // flag all neighbors
          if (blank.size + flagged.size == n && blank > 0) {
            console.log(`flagging all neighbors of (${x},${y})`);
            numClicks += this.flagAll(blank);
            this.isCellSolved = true;
            continue;
          }

          // reveal all neighbors
          if (flagged.size == n) {
            console.log(`revealing all neighbors of (${x},${y})`);
            numClicks += this.revealAll(blank);
            this.isCellSolved[x][y] = true;
            continue;
          }

          for (let cell of neighbors) {
            // if all of a neighbor's blank neighbors are also neighbors of the current cell...
            const blankNeighborsOfNeighbor = this.getNeighborsWithValue(
              cell.x,
              cell.y,
              this.blank
            );

            if (isSuperset(neighbors, blankNeighborsOfNeighbor)) {
              // if n_adj of the neighbor = n_adj of current cell...
              if (this.nAdj(x, y) == this.nAdj(cell.x, cell.y)) {
                // reveal all other neighbors
                console.log(`revealing all other neighbors of (${x},${y})`);
                numClicks += this.revealAll(
                  difference(neighbors, blankNeighborsOfNeighbor)
                );
              }
            }
          }

          for (let cell of neighbors) {
            const greater_n = this.nAdj(x, y);
            const lesser_n = this.nAdj(cell.x, cell.y);
            if (greater_n > lesser_n) {
              // if difference of n_adj equals number of blank cells not shared
              const blankNeighbors = this.getNeighborsWithValue(
                x,
                y,
                this.blank
              );
              const blankNeighborsOfNeighbor = this.getNeighborsWithValue(
                cell.x,
                cell.y,
                this.blank
              );
              const sharedBlankNeighbors = intersection(
                blankNeighbors,
                blankNeighborsOfNeighbor
              );
              if (
                greater_n - lesser_n ==
                blankNeighbors.size - sharedBlankNeighbors.size
              ) {
                console.log("DOING THE THING");

                // reveal all other neighbors of lesser
                numClicks += this.revealAll(
                  difference(blankNeighborsOfNeighbor, sharedBlankNeighbors)
                );

                // flag all other neighbors of greater
                numClicks += this.flagAll(
                  difference(blankNeighbors, sharedBlankNeighbors)
                );
              }
            }
          }
        }
      }

      if (stuck) {
        // deploy endgame techniques
        this.loadBoard();
      }

      // determine outcome and load board
      stuck = numClicks == 0;
      solved = this.loadBoard();
      loops++;
    }

    // report outcome
    if (solved) {
      console.log("Puzzle solved!");
    }
    if (stuck) {
      console.log("Solver got stuck :(");
    }
    console.log(`${loops} total loops`);
  }
}
