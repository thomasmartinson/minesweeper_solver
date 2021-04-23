// then this

let solver = new BoardSolver(16, 31);
solver.solve();

// // returns all the current values of all the cells in a 2D array
// function loadBoard() {
//   let squares = $("[ondragstart]");
//   let board = [];
//   for (let i = 0; i < width; i++) {
//     let row = [];
//     for (let j = 0; j < length; j++) {
//       let index = j * width + i;
//       row.push(squares[index]);
//     }
//     board.push(row);
//   }
//   return board;
// }

// // returns a list of all adjacent square coordinates
// function getNeighbors(x, y) {
//   let neighbors = [];
//   for (let i = -1; i <= 1; i++) {
//     for (let j = -1; j <= 1; j++) {
//       // skip the square itself
//       if (i == 0 && j == 0) {
//         continue;
//       }

//       if (x + i >= 0 && x + i < width && y + j >= 0 && y + j < length) {
//         neighbors.push({
//           x: x + i,
//           y: y + j,
//         });
//       }
//     }
//   }
//   return neighbors;
// }

// function solvePuzzle() {
//   for (let col = 0; col < width; col++) {
//     for (let row = 0; row < length; row++) {
//       const n = getValue(board[col][row]);
//       if (n == 0 || n === "x" || n === "o") {
//         continue;
//       }

//       const neighbors = getNeighbors(col, row);

//       // count flagged
//       let flagged = 0;
//       for (let coord of neighbors) {
//         if (getValue(board[coord.x][coord.y]) === "x") {
//           flagged++;
//         }
//       }

//       // count blank
//       let blank = 0;
//       for (let coord of neighbors) {
//         if (getValue(board[coord.x][coord.y]) === "o") {
//           blank++;
//         }
//       }

//       // flag all neighbors
//       if (blank + flagged == n && blank > 0) {
//         for (let coord of neighbors) {
//           if (getValue(board[coord.x][coord.y]) === "o") {
//             cellClick(coord.x, coord.y, mouse.right);
//           }
//         }
//       }

//       // reveal all neighbors
//       if (flagged == n) {
//         console.log(neighbors);
//         for (let coord of neighbors) {
//           if (getValue(board[coord.x][coord.y]) === "o") {
//             try {
//               cellClick(coord.x, coord.y, mouse.left);
//             } catch (error) {
//               console.log(`failed when clicking (${coord.x},${coord.y})`);
//             }
//           }
//         }
//       }

//       board = loadBoard();
//     }
//   }
// }

// cellClick(3, 3, mouse.left);

// board = loadBoard();

// let k = 0;
// while (k < 50) {
//   solvePuzzle();
//   k++;
// }
