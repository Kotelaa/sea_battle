from random import randint, choice

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределами доски! "

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже делали выстрел в эту клетку! "

class BoardWrongShipException(BoardException):
    pass



class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Dot) and self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Dot ({self.x}, {self.y})"


class Ship:
    def __init__(self, length: int, bow: Dot, direction: "", hp = None):
        self.length = length
        self.bow = bow
        self.direction = direction

        valid_directions = {"горизонтально", "г", "вертикально", "в"}
        if direction not in valid_directions:
            raise ValueError ("Неверная ориентация! Используйте горизонтально (г), вертикально, в")
        self.hp = hp if hp is not None else length


    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x, cur_y = self.bow.x, self.bow.y

            if self.direction in ["горизонтально", "г"]:
                cur_y += i
            elif self.direction in ["вертикально", "в"]:
                cur_x += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots


    def shooten (self, shot):
        return shot in self.dots


    def shooten(self, shot: Dot):
        return shot in self.dots


class Board:
    def __init__(self, size: int, hid = False):
        self.size = size
        self.hid = hid

        self.field = [["೦"] * self.size for _ in range (self.size)]

        self.count = 0
        self.ships = []
        self.ship_placement_busy_dots = set()
        self.shot_dots = set()

    def __str__(self):
        board = ""
        board += "    " + " | ".join(map(str, range(1, self.size + 1))) + " | "
        for i, row in enumerate(self.field):
            board += f"\n{i + 1: >2} | " + " | ".join(row) + " | "


        if self.hid:
            board = board.replace("◼", "೦")

        return board


    def out(self, dot):
        return not (0 <= dot.x < self.size and 0 <= dot.y < self.size)


    def contour (self, ship: Ship, verb = False):
        near_dots = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1), (0, 0), (0, 1),
                     (1, -1), (1, 0), (1, 1)]

        for dot in ship.dots:
            for dot_x, dot_y in near_dots:
                cur_dot = Dot(dot.x + dot_x, dot.y + dot_y)
                if not (self.out(cur_dot)) and cur_dot not in self.ship_placement_busy_dots:
                    if verb:
                        self.field[cur_dot.x][cur_dot.y] = "."
                    self.ship_placement_busy_dots.add(cur_dot)


    def add_ship(self, ship: Ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.ship_placement_busy_dots:
                raise BoardWrongShipException()

        for dot in ship.dots:
            self.field[dot.x][dot.y] = "◼"
            self.ship_placement_busy_dots.add(dot)

        self.ships.append(ship)
        self.contour(ship)


    def shot(self, dot: Dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.shot_dots:
            raise BoardUsedException()

        self.shot_dots.add(dot)

        for ship in self.ships:
            if ship.shooten(dot):
                ship.hp -= 1
                self.field[dot.x][dot.y] = "×"
                if ship.hp == 0:
                    self.count += 1
                    self.contour(ship, True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False


    def begin(self):
        self.shot_dots.clear()

    def defeat(self):
        return self.count == len(self.ships)



class Player:
    def __init__(self, board: Board, enemy: Board):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()


    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        while True:
            dot = Dot(randint(0, 5), randint(0, 5))
            if dot not in self.enemy.shot_dots:
                print (f"Ход компьютера: {dot.x + 1}{dot.y + 1}")
                return dot


class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход (например, 3 2): ").split()

            if len(coords) != 2:
                print ("Введите 2 координаты!")
                continue

            x, y = coords

            if not x.isdigit() or not y.isdigit():
                print ("Введите числа!")
                continue

            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class GameLoop:
    def __init__(self, size=6):
        self.ships_set = [3, 2, 2, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        ai = self.random_board()
        ai.hid = True

        self.ai = AI (ai, pl)
        self.pl = User(pl, ai)


    def create_board(self):
        board = Board(size = self.size)
        attempts = 0
        for lens in self.ships_set:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None

                bow = Dot(randint(0, self.size - 1), randint(0, self.size - 1))
                direction = choice(["горизонтально", "г", "вертикально", "в"])
                ship = Ship(lens, bow, direction)

                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass

        board.begin()
        return board


    def random_board(self):
        board = None
        while board is None:
            board = self.create_board()
        return board


    def greet(self):
        print ("---" * 10)
        print (" Добро пожаловать ")
        print("      в игру        ")
        print("    морской бой    ")
        print("---" * 10)
        print("  формат ввода: x y ")
        print("   x - номер строки  ")
        print("   y - номер столбца  ")
        print("---" * 10)

    def print_boards(self):
        print("---" * 10)
        print("Доска пользователя: ")
        print(self.pl.board)
        print("---" * 10)
        print("Доска компьютера: ")
        print(self.ai.board)
        print("---" * 10)

    def loop(self):
        turn = 0 # номер хода
        while True:
            self.print_boards()

            if turn % 2 == 0:
                print ("Ход пользователя!")
                repeat = self.pl.move()
            else:
                print ("Ход компьютера!")
                repeat = self.ai.move()

            if repeat:
                turn =- 1

            if self.ai.board.defeat():
                self.print_boards()
                print ("---" * 10)
                print ("Пользователь выйграл!")
                break

            if self.pl.board.defeat():
                self.print_boards()
                print ("---" * 10)
                print ("Компьютер выйграл!")
                break

            turn += 1


    def start(self):
        self.greet()
        self.loop()


g = GameLoop()
g.start()
