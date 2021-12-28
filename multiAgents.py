from util import manhattanDistance
from game import Directions
import random, util

from game import Agent


def scoreEvaluationFunction(currentGameState):
    
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    

    def __init__(self, evalFn = 'betterEvaluationFunction', depth = '3'):
        self.index = 0 
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class AlphaBetaAgent(MultiAgentSearchAgent):
    

    def getAction(self, gameState):
        
        PACMAN = 0
        def maximaze(state, depth, alpha, beta): # максимізуємо стан
            if state.isWin() or state.isLose(): #  якщо у нас або перемога або програш то повертаємо рахунок
                return state.getScore()
            actions = state.getLegalActions(PACMAN) # Вибираємо доступні ходи
            best_score = -999999 # ініціюємо найкращий рахунок як дуже маленьке число
            temp_score = best_score # також записуємо тимчасовий рахунок
            best_action = Directions.STOP # тимчасовий напрямок - стояти
            for action in actions: # для кожного ходу
                temp_score = minimize(state.generateSuccessor(PACMAN, action), depth, 1, alpha, beta) # мінімізуємо хід ворога
                if temp_score > best_score: # оновлюємо рахунок якщо він більше поточного
                    best_score = temp_score
                    best_action = action
                alpha = max(alpha, best_score) # альфа відсіч
                if best_score > beta:
                    return best_score
            if depth == 0:
                return best_action
            else:
                return best_score

        def minimize(state, depth, ghost, alpha, beta): # мінінімузаємо привидів
            if state.isLose() or state.isWin():
                return state.getScore()
            next_ghost = ghost + 1
            if ghost == state.getNumAgents() - 1:
                next_ghost = PACMAN
            actions = state.getLegalActions(ghost)
            best_score = 999999
            score = best_score
            for action in actions:
                if next_ghost == PACMAN: # ми на останньому привиду і пакман наступний
                    if depth == self.depth - 1:
                        score = self.evaluationFunction(state.generateSuccessor(ghost, action))
                    else:
                        score = maximaze(state.generateSuccessor(ghost, action), depth + 1, alpha, beta)
                else:
                    score = minimize(state.generateSuccessor(ghost, action), depth, next_ghost, alpha, beta)
                if score < best_score:
                    best_score = score
                beta = min(beta, best_score)
                if best_score < alpha:
                    return best_score
            return best_score
        return maximaze(gameState, 0, -999999, 999999)

class ExpectimaxAgent(MultiAgentSearchAgent):

    def getAction(self, gameState):
        PACMAN = 0
        def max_agent(state, depth):
            if state.isWin() or state.isLose():
                return state.getScore()
            actions = state.getLegalActions(PACMAN)
            best_score = -999999
            score = best_score
            best_action = Directions.STOP
            for action in actions:
                score = min_agent(state.generateSuccessor(PACMAN, action), depth, 1)
                if score > best_score:
                    best_score = score
                    best_action = action
            if depth == 0:
                return best_action
            else:
                return best_score

        # Те саме що і попередній алгоритм тільки ми тут вважаємо що привид ходить неоптимально і тому використовуємо ймовірність кроку
        def min_agent(state, depth, ghost):
            if state.isLose():
                return state.getScore()
            next_ghost = ghost + 1
            if ghost == state.getNumAgents() - 1:

                next_ghost = PACMAN
            actions = state.getLegalActions(ghost)
            best_score = 999999
            score = best_score
            for action in actions:
                prob = 1.0/len(actions)
                if next_ghost == PACMAN:
                    if depth == self.depth - 1:
                        score = self.evaluationFunction(state.generateSuccessor(ghost, action))
                        score += prob * score
                    else:
                        score = max_agent(state.generateSuccessor(ghost, action), depth + 1)
                        score += prob * score
                else:
                    score = min_agent(state.generateSuccessor(ghost, action), depth, next_ghost)
                    score += prob * score
            return score
        return max_agent(gameState, 0)


# Оціночна функція
def betterEvaluationFunction(currentGameState):
    
    def closest_food(cur_pos, food_pos):# Оцінюємо дистанцію до їжі
        food_distances = []
        for food in food_pos:
            food_distances.append(util.manhattanDistance(food, cur_pos))
        return min(food_distances) if len(food_distances) > 0 else 1

    def closest_ghost(cur_pos, ghosts):# дистанцію до привидів
        food_distances = []
        for food in ghosts:
            food_distances.append(util.manhattanDistance(food.getPosition(), cur_pos))
        return min(food_distances) if len(food_distances) > 0 else 1


    

    def food_stuff(cur_pos, food_positions):# загальна дистанція до їжі
        food_distances = []
        for food in food_positions:
            food_distances.append(util.manhattanDistance(food, cur_pos))
        return sum(food_distances)


    pacman_pos = currentGameState.getPacmanPosition()
    score = currentGameState.getScore()
    food = currentGameState.getFood().asList()
    ghosts = currentGameState.getGhostStates()

    score = score * 3 if closest_food(pacman_pos, food) < closest_ghost(pacman_pos, ghosts) + 2 else score
    score -= .35 * food_stuff(pacman_pos, food)
    return score