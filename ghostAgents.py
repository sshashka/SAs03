from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util

class GhostAgent( Agent ): # Створюємо базовий клас, унаслідуючись від класу агент
    def __init__( self, index ):
        super().__init__(index)
        self.index = index

    def getAction(self, state): # Метод для повернення події від гравця
        dist = self.getDistribution(state)
        return util.chooseFromDistribution(dist)

    def getDistribution(self, state):
        
        util.raiseNotDefined()

class RandomGhost( GhostAgent ): # Створюємо привида, що ходить рандомно

    def getDistribution( self, state ): # Повертаємо к-сть очок для певного стану
        dist = util.Counter()
        for a in state.getLegalActions( self.index ): dist[a] = 1.0
        dist.normalize()
        return dist
class DirectionalGhost( GhostAgent ): # Привид, що ходить за напрямами
    # Привид завжди атакує пакмана або тікає тоді, коли його можуть з'їсти
    def __init__( self, index, prob_attack=0.8, prob_scaredFlee=0.8 ):
        self.index = index # індекс бота
        self.prob_attack = prob_attack # ймовірність атаки
        self.prob_scaredFlee = prob_scaredFlee # ймовірність втечі

    def getDistribution( self, state ):
        
        ghostState = state.getGhostState( self.index ) # Отримання стану
        legalActions = state.getLegalActions( self.index ) # отримання можливих дій
        pos = state.getGhostPosition( self.index ) # позиція
        isScared = ghostState.scaredTimer > 0 # чи наляканий(у нас є таймер наляканості)
        # змінюємо швидкість взалежності від того чи наляканий привид чи ні
        speed = 1
        if isScared: speed = 0.5

        actionVectors = [Actions.directionToVector( a, speed ) for a in legalActions]
        newPositions = [( pos[0]+a[0], pos[1]+a[1] ) for a in actionVectors]
        pacmanPosition = state.getPacmanPosition()

        # Вираховуємо найкращий стан для нашого привида
        distancesToPacman = [manhattanDistance( pos, pacmanPosition ) for pos in newPositions]
        if isScared:
            bestScore = max( distancesToPacman )
            bestProb = self.prob_scaredFlee
        else:
            bestScore = min( distancesToPacman )
            bestProb = self.prob_attack
        bestActions = [action for action, distance in zip( legalActions, distancesToPacman ) if distance == bestScore]

        # Так само рахуємо очки для стану
        dist = util.Counter()
        for a in bestActions: dist[a] = bestProb / len(bestActions)
        for a in legalActions: dist[a] += ( 1-bestProb ) / len(legalActions)
        dist.normalize()
        return dist