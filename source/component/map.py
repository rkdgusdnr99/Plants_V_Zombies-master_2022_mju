import random
import pygame as pg
from .. import tool
from .. import constants as c

class Map():
    def __init__(self, width, height):#호출할 수 있는 __init__함수 사용
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]#map에 대한 크기 범위 지정

    def isValid(self, map_x, map_y):#map 밖에 벗어나면 안된다.
        if (map_x < 0 or map_x >= self.width or
            map_y < 0 or map_y >= self.height):
            return False
        return True
    
    def isMovable(self, map_x, map_y):
        return (self.map[map_y][map_x] == c.MAP_EMPTY)
    
    def getMapIndex(self, x, y):#map에서 위치에 대한 정보 얻음
        x -= c.MAP_OFFSET_X#35
        y -= c.MAP_OFFSET_Y#100
        return (x // c.GRID_X_SIZE, y // c.GRID_Y_SIZE)
    
    def getMapGridPos(self, map_x, map_y):# 어떤 기능인진 모르겠으나 값을 바꾸면 카드를 맵에 배치할 때 게임이 틩김, 밑의 함수를 해석해 봤을 때 마우스가 어디를 클릭하는지 반환해주는 역할 같음
        return (map_x * c.GRID_X_SIZE + c.GRID_X_SIZE//2 + c.MAP_OFFSET_X,
                map_y * c.GRID_Y_SIZE + c.GRID_Y_SIZE//5 * 3 + c.MAP_OFFSET_Y)#GRID_X_SIZE = 80, GRID_Y_SIZE = 100, MAP_OFFSET_X = 35, MAP_OFFSET_Y = 100
    
    def setMapGridType(self, map_x, map_y, type):# 아마 위의 함수와 더불어 div기능을 하는 것으로 추측된다.
        self.map[map_y][map_x] = type

    def getRandomMapIndex(self):#햇빛이 떨어지는 위치!
        map_x = random.randint(0, self.width-1)
        map_y = random.randint(0, self.height-1)
        return (map_x, map_y)

    def showPlant(self, x, y):#map에 식물을 어디놓을지 결정하는 함수
        pos = None
        map_x, map_y = self.getMapIndex(x, y)#여기 값을 더하고 빼보니 마우스 커서에서 그만큼 이동된 곳에 식물 놓아졌음
        if self.isValid(map_x, map_y) and self.isMovable(map_x, map_y):#범위안에 있으면 pos에 getMapGridPos의 리턴값을 리턴해줌. 이 과정에서 getMapGridPos의 기능 추측 가능
            pos = self.getMapGridPos(map_x, map_y)
        return pos
