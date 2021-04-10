// do this
var script = document.createElement('script');
script.src = "https://code.jquery.com/jquery-3.4.1.min.js";
document.getElementsByTagName('head')[0].appendChild(script);

// then this
const mouse = { left: 0, right: undefined };

cellClick(3, 3, mouse.left);

const length = 8;
const width = 8;

let board = [];

let squares = $('[ondragstart]');

function getValue(elem) {
    let filename = elem.getElementsByTagName('img')[0].src.split('/').slice(-1)[0];
    switch (filename) {
        case 'blank.gif':
            return 'o'
        case 'bombflagged.gif':
            return 'x'
        default:
            return filename[4];
    }
}

function loadBoard() {
    board = [];
    for (let i = 0; i < length; i++) {
        let row = [];
        for (let j = 0; j < width; j++) {
            let index = i * width + j;
            row.push(squares[index]);
        }
        console.log(row);
        board.push(row);
    }
    return board;
}

loadBoard();

// returns a list of all adjacent square coordinates
function getNeighbors(x, y) {
    let neighbors = [];
    for (let i = -1; i <= 1; i++) {
        for (let j = -1; j <= 1; j++) {
            // skip the square itself
            if (i == 0 && j == 0) {
                continue;
            }

            if (x + i >= 0 && x + i < width && y + j >= 0 && y + j < length) {
                neighbors.push(
                    {
                        x: [x + i],
                        y: [y + j]
                    }
                );
            }
        }
    }
    return neighbors;
}

function solvePuzzle() {
    for (let i = 0; i < width; i++) {
        for (let j = 0; j < length; j++) {
            const n = getValue(board[i][j]);
            const neighbors = getNeighbors(i, j);

            // count flagged
            let flagged = 0;
            for (coord of neighbors) {
                if (getValue(board[coord.x][coord.y]) === 'x') {
                    flagged++;
                }
            }

            // reveal all neighbors
            if (flagged == n) {
                for (coord of neighbors) {
                    console.log(`clicking (${coord.x}, ${coord.y})`);
                    cellClick(coord.x, coord.y, mouse.left)
                }
            }
        }
    }
}
