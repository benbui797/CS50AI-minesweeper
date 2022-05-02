import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # if number of cells is equal to count, then all cells are mines
        if len(self.cells) == self.count:
            return self.cells
        
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # if count is 0, all cells are safe
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # if a cell is a mine, we remove it from the set and reduce the count by 1
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        
        # If a cell is safe, we can remove it from the set, without updating the count
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        
        # Add the cell as a move that has been made
        self.moves_made.add(cell)

        # Mark the cell as safe
        self.mark_safe(cell)
        
        # Add a new sentence to the knowledge base
        neighbors = self.get_neighbors(cell)

        # if count > 0, add sentence with neighbors (not marked as safe)
        if count > 0:
            new_neighbors = [cell for cell in neighbors if cell not in self.safes]
            self.knowledge.append(Sentence(new_neighbors, count))

        # if count = 0, all neighbors are safe and can be marked as such
        # sentences that include those cells should be updated
        if count == 0:
            for neighbor in neighbors:
                if neighbor not in self.safes:
                    self.mark_safe(neighbor)

        # if there is no knowledge yet, return
        if len(self.knowledge) < 1:
            return

        # loop through sentences, mark new mines and new safes
        for sentence in self.knowledge:
            # mark new safes
            safes = sentence.known_safes()
            if safes:
                for cell in safes.copy():
                    self.mark_safe(cell)
            
            # mark new mines
            mines = sentence.known_mines()
            if mines:
                for cell in mines.copy():
                    self.mark_mine(cell)
        
        # print for debugging
        print(f"Safe: {self.safes}")
        print(f"Mines: {self.mines}")
        print("Knowledge:")
        for sentence in self.knowledge:
            print(sentence)

        # Update knowledge base with new knowledge
        self.deduce_knowledge()

        # Clean up knowledge (duplicates and empty sets)
        self.clean_knowledge()
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) == len(self.moves_made):
            return None
        
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # return None if 8 possible moves left (all mines found!)

        finished = (self.width * self.height) - len(self.mines)

        if len(self.moves_made) == finished:
            return None

        # else pick random move
        while True:
            move = tuple(
                [random.randrange(self.height),
                 random.randrange(self.width)]
            )
            if move not in self.moves_made and move not in self.mines:
                return move

    def get_neighbors(self, cell):
        """
        Returns a list of cells neighbouring the input cell.
        Check if cell is not in known safes or mines.
        """

        i, j = cell
        neighbors = []

        for r in range(-1, 2):
            for c in range(-1, 2):
                x = i - r
                y = j - c
                if 0 <= x < self.height and 0 <= y < self.width:
                    neighbor = (x, y)
                    neighbors.append(neighbor)

        return neighbors

    def deduce_knowledge(self):
        """
        Loop through knowledge and check for subsets to deduce a new sentence.

        if set1 is a subset of set2, then we can construct the new sentence: set2 - set1 = count2 - count1
        """

        deductions = []
        
        for sentence in self.knowledge:
            for subsentence in self.knowledge:
                if subsentence.cells != sentence.cells and \
                        len(subsentence.cells) > 0:
                    if subsentence.cells.issubset(sentence.cells):
                        new_cells = sentence.cells.symmetric_difference(subsentence.cells)
                        new_count = sentence.count - subsentence.count
                        # print(f"{new_cells=} {new_count=}")
                        deductions.append(Sentence(new_cells, new_count))
        
        for sentence in deductions:
            self.knowledge.append(sentence)

    def clean_knowledge(self):
        """
        Loop through knowledge and deletes empty and duplicate sets.
        """
        for sentence in self.knowledge:
            # delete empty sentences
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)      

            # clean up duplicate sentences
            for duplicates in self.knowledge:
                if duplicates is not sentence:
                    if sentence.cells == duplicates.cells:
                        self.knowledge.remove(duplicates)  
