import sys
import math

from crossword import Crossword, Variable


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            failed_words = []
            for word in self.domains[var]:
                if len(word) != var.length:
                    failed_words.append(word)
            for word in failed_words:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        i,j = self.crossword.overlaps[x,y]
        revised = False

        for wordX in self.domains[x]:
            combination = False
            failed_words = []
            for wordY in self.domains[y]:
                if wordX[i] == wordY[j]:
                    combination = True

            if combination == False: 
                failed_words.append(wordX)
                revised = True
            
        for word in failed_words:
            self.domains[x].remove(word)

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        #from week 3 sudo code "function AC-3(csp)"
        if arcs == None:
            arcs = [] 
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x,y)) 

        while len(arcs) != 0:
            x, y = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbour_x in self.crossword.neighbors(x):
                    if neighbour_x != y:
                        arcs.append((neighbour_x, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if assignment.keys() == self.crossword.variables:
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for word1 in assignment:
            for word2 in assignment:
                if word1 != word2: 
                    if self.crossword.overlaps[word1, word2]: 
                        i, j = self.crossword.overlaps[word1, word2]
                        i_word1 = assignment[word1]
                        j_word2 = assignment[word2]
                        if i_word1[i] != j_word2[j]:
                            return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        conflicts = {}
        for value in self.domains[var]:
            num_conflicts = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    for neighbor_value in self.domains[neighbor]:
                        if not self.crossword.overlaps[var, neighbor]:
                            continue
                        i, j = self.crossword.overlaps[var, neighbor]
                        if value[i] != neighbor_value[j]:
                            num_conflicts += 1
            conflicts[value] = num_conflicts

        return sorted(self.domains[var], key=lambda value: conflicts[value])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = []
        for var in self.crossword.variables:
            if var not in assignment:
                unassigned_vars.append(var)

        min_remaining_values = math.inf
        max_degree = -math.inf
        selected_var = None

        for var in unassigned_vars:
            remaining_values = len(self.domains[var])
            degree = len(self.crossword.neighbors(var))
            if remaining_values < min_remaining_values:
                min_remaining_values = remaining_values
                max_degree = degree
                selected_var = var
            elif remaining_values == min_remaining_values and degree > max_degree:
                min_remaining_values = remaining_values
                max_degree = degree
                selected_var = var

        return selected_var 

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        else:
            var = self.select_unassigned_variable(assignment)
            for word in self.order_domain_values(var,assignment):
                assignment[var] = word
                if self.consistent(assignment):
                    result = self.backtrack(assignment) 
                    if result is not None: 
                        return result
                assignment.pop(var)
            return None
                        

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
