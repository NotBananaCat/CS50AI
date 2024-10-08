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
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
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
        #print(len(self.knowledge))
        self.moves_made.add(cell)
        self.mark_safe(cell)

        neighbors = set() 
        i, j = cell
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if 0 <= x < self.height and 0 <= y < self.width:
                    neighbor = (x, y)
                    if neighbor != cell:
                        neighbors.add(neighbor)
        if count == 0:
            for neighbor_cell in neighbors:
                self.knowledge.append(Sentence({neighbor_cell}, 0))
        else:
            self.knowledge.append(Sentence(neighbors, count))


        for x in range(2): #only need to check depth 2 for end solving more is almost completely redundant and slow
            for sentence in self.knowledge:
                safe = sentence.known_safes()
                if sentence.known_safes():
                    self.safes.update(safe)

                mines = sentence.known_mines()
                if mines:
                    self.mines.update(mines)

            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:

                    sub_set = all(cell in sentence2.cells for cell in sentence1.cells) #intersections
                    if sub_set:
                        new_cells = sentence2.cells - (sentence1.cells | self.moves_made)
                        new_count = sentence2.count - sentence1.count

                        if new_count == 0: #simplify 0 count sentences
                             for cell in new_cells:
                                new_sentence = Sentence({cell}, 0)
                                if new_sentence not in self.knowledge:
                                    self.knowledge.append(new_sentence)
                        else:
                            new_sentence = Sentence(new_cells, new_count)
                            if new_sentence not in self.knowledge:
                                if not all(cell in self.moves_made for cell in new_sentence.cells):
                                    self.knowledge.append(new_sentence)

        for sentence in self.knowledge:
            if all(cell in self.moves_made for cell in sentence.cells):
                self.knowledge.remove(sentence)
            else:
                set_of_set = False
                for other_sentence in self.knowledge:
                    if other_sentence != sentence:
                        # Check if sentence.cells is a subset of other_sentence.cells
                        set_of_set = all(cell in other_sentence.cells for cell in sentence.cells)
                        if set_of_set and sentence.count == other_sentence.count:
                            break
                if set_of_set:
                    self.knowledge.remove(sentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = self.safes - self.moves_made
        if safe_moves:
            return random.choice(list(safe_moves))
        return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        cells = set()
        for x in range(self.height):
            for y in range(self.width):
                cells.add((x,y))

        empty_cell = cells - self.moves_made - self.mines

        if empty_cell:
            return random.choice(list(empty_cell))
        return None