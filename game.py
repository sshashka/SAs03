from util import *
from datetime import datetime


class Agent:
    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        raiseNotDefined()

# Напрямики для пересування гравця та ворогів
class Directions:
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT = {NORTH: WEST,
            SOUTH: EAST,
            EAST: NORTH,
            WEST: SOUTH,
            STOP: STOP}

    RIGHT = dict([(y, x) for x, y in LEFT.items()])

    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               STOP: STOP}



class Configuration:

    def __init__(self, pos, direction): # ініцієюмо клас конфігурації
        self.pos = pos  # позиція гравця (х та у)
        self.direction = direction # напрямок пересування


    def getPosition(self): # Метод для повенення позиції гравця
        return self.pos


    def getDirection(self): # Метод для повернення напрямку руху гравця
        return self.direction

    
    def generateSuccessor(self, vector): # Створюємо поточний стан гравця через  х та у та верктор напрямку
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP:
            direction = self.direction  
        return Configuration((x + dx, y + dy), direction)


 # Класс для збереження стану всіх гравців(боти та гравець)
class AgentState:
    def __init__(self, startConfiguration, isPacman):
        self.start = startConfiguration # Отримуємо стартову конфігурацію
        self.configuration = startConfiguration
        self.isPacman = isPacman  #  оскільки тут може бути і бот то перевіряєм чи це гравець
        self.scaredTimer = 0  # час наляканості
        self.numCarrying = 0
        self.numReturned = 0

    def copy(self):  #  Метод для створення копії стану
        state = AgentState(self.start, self.isPacman)
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        return state

    def getPosition(self): # Отримання позиції гравця
        if self.configuration is None:
            return None
        return self.configuration.getPosition()

    def getDirection(self): # Тут отриманнян напрямку
        return self.configuration.getDirection()

 #  Сітка
class Grid:
    def __init__(self, width, height, initialValue=False):
        if initialValue not in [False, True]: raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width # ширина
        self.height = height # висота
        self.data = [[initialValue for y in range(height)] for x in range(width)]

    def __getitem__(self, i):
        return self.data[i]

    def __eq__(self, other):
        if other is None:
            return False
        return self.data == other.data

    def copy(self): # копія сітки
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):  # глибока копія
        return self.copy()

    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item=True):
        return sum([x.count(item) for x in self.data])

    def asList(self, key=True):
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key: list.append((x, y))
        return list


 #  Клас подій
class Actions:

    _directions = {Directions.NORTH: (0, 1),
                   Directions.SOUTH: (0, -1),
                   Directions.EAST: (1, 0),
                   Directions.WEST: (-1, 0),
                   Directions.STOP: (0, 0)}

    _directionsAsList = _directions.items()

    TOLERANCE = .001

    # Метод який інвертує напрямки для легшого розвертання на 180*
    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action

    reverseDirection = staticmethod(reverseDirection)

    # Конвертація вектору  у напрямок
    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP

    vectorToDirection = staticmethod(vectorToDirection)

    # Тут навпаки напрямок у вектор
    def directionToVector(direction, speed=1.0):
        dx, dy = Actions._directions[direction]
        return dx * speed, dy * speed

    directionToVector = staticmethod(directionToVector)

    # Метод для отримання можливих напрямків пересування, щоб неможна було ходити через стіни
    def getPossibleActions(config, walls):
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        if abs(x - x_int) + abs(y - y_int) > Actions.TOLERANCE:
            return [config.getDirection()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    # Метод для отримання сусідів для будь-якої позиції
    def getLegalNeighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width:
                continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height:
                continue
            if not walls[next_x][next_y]: neighbors.append((next_x, next_y))
        return neighbors

    getLegalNeighbors = staticmethod(getLegalNeighbors)


class GameStateData: # клас для запису ігрових станів
    def __init__(self, prevState=None): # Тут ініціюємо даний клас і копіюємо інфу з попереднього стану
        if prevState is not None:
            self.food = prevState.food.shallowCopy()
            self.capsules = prevState.capsules[:]
            self.agentStates = self.copyAgentStates(prevState.agentStates)
            self.layout = prevState.layout
            self._eaten = prevState._eaten
            self.score = prevState.score

        self._foodEaten = None
        self._foodAdded = None
        self._capsuleEaten = None
        self._agentMoved = None
        self._lose = False
        self._win = False
        self.scoreChange = 0

    # Глибоке копіювання
    def deepCopy(self):
        state = GameStateData(self)
        state.food = self.food.deepCopy()
        state.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state._foodEaten = self._foodEaten
        state._foodAdded = self._foodAdded
        state._capsuleEaten = self._capsuleEaten
        return state

    # Копія стану гравця та ботів
    def copyAgentStates(self, agentStates):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates

    # Ініціалізація для кожного з ворогів
    def initialize(self, layout, numGhostAgents):
        self.food = layout.food.copy()
        self.capsules = layout.capsules[:]
        self.layout = layout
        self.score = 0
        self.scoreChange = 0

        self.agentStates = []
        numGhosts = 0
        for isPacman, pos in layout.agentPositions:
            if not isPacman:
                if numGhosts == numGhostAgents:
                    continue
                else:
                    numGhosts += 1
            self.agentStates.append(AgentState(Configuration(pos, Directions.STOP), isPacman))
        self._eaten = [False for a in self.agentStates]

 # Сам клас гри
class Game:
    def __init__(self, agents, display, rules, startingIndex=0, muteAgents=False, catchExceptions=False):
        self.numMoves = 0
        self.state = None
        self.agentCrashed = False
        self.agents = agents
        self.display = display
        self.rules = rules
        self.startingIndex = startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        import io
        self.agentOutput = [io.StringIO() for agent in agents]

    # Основний цикл гри (Мейн гейм луп)
    def run(self):
        curentTime = datetime.now()
        self.display.initialize(self.state.data)

        
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if "registerInitialState" in dir(agent):
                agent.registerInitialState(self.state.deepCopy())

        agentIndex = self.startingIndex
        numAgents = len(self.agents)

        while not self.gameOver:
            agent = self.agents[agentIndex]
            if 'observationFunction' in dir(agent):
                observation = agent.observationFunction(self.state.deepCopy())
            else:
                observation = self.state.deepCopy()
            action = agent.getAction(observation)
            self.moveHistory.append((agentIndex, action))
            self.state = self.state.generateSuccessor(agentIndex, action)
            self.display.update(self.state.data)
            
            self.rules.process(self.state, self,curentTime)
            agentIndex = (agentIndex + 1) % numAgents
            