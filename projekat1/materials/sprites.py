import math
import random
import copy
import sys
import pygame
import os
import config


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


def greedy_dfs(visited, graph, node, path):
    if node not in visited:
        path.append(node)
        visited.add(node)
        tmp = (graph[node]).copy()
        tmp.sort(reverse=False)
        for neighbour in tmp:
            if neighbour == 0:
                continue
            index = (graph[node]).index(neighbour)
            greedy_dfs(visited, graph, index, path)


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        visited = set()
        path = []
        greedy_dfs(visited, coin_distance, 0, path)
        return path + [0]


def depth_first(visited, graph, node, all_paths):
    visited.append(node)
    for neighbour in range(1, len(graph)):
        if neighbour not in visited and graph[node][neighbour] != 0:
            depth_first(visited.copy(), graph, neighbour, all_paths)
    if len(visited) == len(graph):
        all_paths.append(visited + [0])


def find_best(all_paths, graph):
    tmp_list = []
    for tmpi in range(1, len(all_paths)):
        summ = 0
        for tmpj in range(0, len(all_paths[tmpi]) - 1):
            summ = summ + graph[all_paths[tmpi][tmpj]][all_paths[tmpi][tmpj+1]]
        tmp_list.append(summ)
    tmp = min(tmp_list)
    index = tmp_list.index(tmp)
    path = (all_paths[index+1]).copy()
    return path


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        all_paths = [[]]
        visited = []
        depth_first(visited, coin_distance, 0, all_paths)
        return find_best(all_paths, coin_distance)


def branch_and_bound(graph, start_node):
    branch = [(0, 1, [start_node])]
    while True:
        tmp = branch.pop(0)
        for neighbour in range(0, len(graph)):
            if (neighbour not in tmp[2] or (tmp[1] == len(graph) and neighbour == start_node)) \
                    and graph[(tmp[2])[-1]][neighbour] != 0:
                tmp_path = copy.deepcopy(tmp[2])
                tmp_weight = tmp[0] + graph[tmp_path[-1]][neighbour]
                tmp_len = tmp[1] + 1
                tmp_path.append(neighbour)
                branch.append((tmp_weight, tmp_len, tmp_path))
        branch.sort(key=lambda row: (row[0], -row[1], row[2][-1]))
        if branch[0][1] == len(graph) + 1:
            break
    return branch[0][2]


class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        all_paths = [[]]
        path = []
        visited = []
        path = branch_and_bound(coin_distance, 0)
        return path


def remove_nodes(graph, path):
    path.sort(reverse=True)
    for tmp in path:
        for i in range(len(graph)):
            (graph[i]).pop(tmp)
        graph.pop(tmp)


def prepare_and_call(graph, cur_path):
    tmp_path = copy.deepcopy(cur_path)
    if len(tmp_path) <= 1:
        return prim_mst(graph)
    else:
        # tmp_path.pop(-1)
        tmp_path.pop(0)
        tmp_graph = copy.deepcopy(graph)
        remove_nodes(tmp_graph, tmp_path)
        return prim_mst(tmp_graph)


def min_key(key, included, v, graph):

    # Initialize min value
    min_index = -1
    minimum = sys.maxsize

    for tmp in range(v):
        if key[tmp] < minimum and included[tmp] == False:
            minimum = key[tmp]
            min_index = tmp

    return min_index


def prim_mst(graph):
    v = len(graph)
    key = [sys.maxsize] * v
    parent = [None] * v
    key[0] = 0
    included = [False] * v

    parent[0] = -1

    for cout in range(v):
        u = min_key(key, included, v, graph)
        included[u] = True
        for tmp in range(v):
            if graph[u][tmp] > 0 and included[tmp] == False and key[tmp] > graph[u][tmp]:
                key[tmp] = graph[u][tmp]
                parent[tmp] = u
    summ = 0
    for i in range(1, len(key)):
        summ = summ + key[i]
    return summ


def a_star(graph, start_node):
    branch = [(prim_mst(graph), 1, [start_node], prim_mst(graph))]
    while True:
        tmp = branch.pop(0)
        old_heuristics = tmp[3]
        if tmp[1] != len(graph):
            new_heuristics = prepare_and_call(graph, tmp[2])
        else: new_heuristics = 0
        for neighbour in range(0, len(graph)):
            if (neighbour not in tmp[2] or (tmp[1] == len(graph) and neighbour == start_node)) \
                    and graph[(tmp[2])[-1]][neighbour] != 0:
                tmp_path = copy.deepcopy(tmp[2])
                tmp_weight = tmp[0] + graph[tmp_path[-1]][neighbour] - old_heuristics + new_heuristics
                tmp_len = tmp[1] + 1
                tmp_path.append(neighbour)
                tmp_heuristics = new_heuristics
                branch.append((tmp_weight, tmp_len, tmp_path, tmp_heuristics))
        branch.sort(key=lambda row: (row[0], -row[1], row[2][-1]))
        if branch[0][1] == len(graph) + 1:
            break
    return branch[0][2]


class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        all_paths = [[]]
        path = []
        visited = []
        path = a_star(coin_distance, 0)
        return path
