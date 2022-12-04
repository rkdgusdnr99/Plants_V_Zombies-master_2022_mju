import random
import pygame as pg
from .. import tool
from .. import constants as c

PANEL_Y_START = 87
PANEL_X_START = 22
PANEL_Y_INTERNAL = 74
PANEL_X_INTERNAL = 53
CARD_LIST_NUM = 8

card_name_list = [c.CARD_SUNFLOWER, c.CARD_PEASHOOTER, c.CARD_SNOWPEASHOOTER, c.CARD_WALLNUT,
                  c.CARD_CHERRYBOMB, c.CARD_THREEPEASHOOTER, c.CARD_REPEATERPEA, c.CARD_CHOMPER,
                  c.CARD_PUFFSHROOM, c.CARD_POTATOMINE, c.CARD_SQUASH, c.CARD_SPIKEWEED,
                  c.CARD_JALAPENO, c.CARD_SCAREDYSHROOM, c.CARD_SUNSHROOM, c.CARD_ICESHROOM,
                  c.CARD_HYPNOSHROOM, c.CARD_WALLNUT, c.CARD_REDWALLNUT]
plant_name_list = [c.SUNFLOWER, c.PEASHOOTER, c.SNOWPEASHOOTER, c.WALLNUT,
                   c.CHERRYBOMB, c.THREEPEASHOOTER, c.REPEATERPEA, c.CHOMPER,
                   c.PUFFSHROOM, c.POTATOMINE, c.SQUASH, c.SPIKEWEED,
                   c.JALAPENO, c.SCAREDYSHROOM, c.SUNSHROOM, c.ICESHROOM,
                   c.HYPNOSHROOM, c.WALLNUTBOWLING, c.REDWALLNUTBOWLING]
plant_sun_list = [50, 100, 175, 50, 150, 325, 200, 150, 0, 25, 50, 100, 125, 25, 25, 75, 75, 0, 0]
plant_frozen_time_list = [7500, 7500, 7500, 30000, 50000, 7500, 7500, 7500, 7500, 30000,
                          30000, 7500, 50000, 7500, 7500, 50000, 30000, 0, 0]
all_card_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

def getSunValueImage(sun_value):#얼마나 햇빛을 가지고 있는지 알려주는 사각형
    font = pg.font.SysFont(None, 22)
    width = 32
    msg_image = font.render(str(sun_value), True, c.NAVYBLUE, c.LIGHTYELLOW)
    msg_rect = msg_image.get_rect()#이미지를 위해 사각형 객체 만들어줌(2D)
    msg_w = msg_rect.width

    image = pg.Surface([width, 17])
    x = width - msg_w

    image.fill(c.LIGHTYELLOW)
    image.blit(msg_image, (x, 0), (0, 0, msg_rect.w, msg_rect.h))#사각형 안으로 이미지 복사해서 넣음
    image.set_colorkey(c.BLACK)#이미지를 렌더링할 때 키 색상과 일치하는 픽셀을 무시하여 투명하게 만듦
    return image

def getCardPool(data):
    card_pool = []
    for card in data:
        tmp = card['name']
        for i,name in enumerate(plant_name_list):#enumerate()함수는 인덱스와 원소로 이루어진 tuple만들어줌, range 대신 쓴 것
            if name == tmp:
                card_pool.append(i)
                break
    return card_pool

class Card():
    def __init__(self, x, y, name_index, scale=0.78):
        self.loadFrame(card_name_list[name_index], scale)#card_name_list에 따라 카드 이미지 불러냄
        self.rect = self.orig_image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.name_index = name_index#card_name_list에 따라 카드 기능 불러옴
        self.sun_cost = plant_sun_list[name_index]
        self.frozen_time = plant_frozen_time_list[name_index]
        self.frozen_timer = -self.frozen_time
        self.refresh_timer = 0
        self.select = True

    def loadFrame(self, name, scale):
        frame = tool.GFX[name]#이미지 연출을 부드럽게 만들어 주는 역할 같다
        rect = frame.get_rect()#이미지를 위해 사각형 객체 만들어줌(2D)
        width, height = rect.w, rect.h

        self.orig_image = tool.get_image(frame, 0, 0, width, height, c.BLACK, scale)
        self.image = self.orig_image

    def checkMouseClick(self, mouse_pos): #마우스클릭
        x, y = mouse_pos
        if(x >= self.rect.x and x <= self.rect.right and
           y >= self.rect.y and y <= self.rect.bottom):
            return True
        return False

    def canClick(self, sun_value, current_time):
        if self.sun_cost <= sun_value and (current_time - self.frozen_timer) > self.frozen_time: #가지고 있는 돈이 아이템 가격보다 더 많아야 클릭 가능, 아이템 쿨타임 돌때는 클릭 불가능 
            return True
        return False

    def canSelect(self):
        return self.select

    def setSelect(self, can_select): #선택 가능 여부에 따른 투명도 값 설정
        self.select = can_select
        if can_select:
            self.image.set_alpha(255) 
        else:
            self.image.set_alpha(128)

    def setFrozenTime(self, current_time):
        self.frozen_timer = current_time

    def createShowImage(self, sun_value, current_time):
        time = current_time - self.frozen_timer # 쿨타임 표시
        if time < self.frozen_time:  # card cool down status
            image = pg.Surface([self.rect.w, self.rect.h])
            frozen_image = self.orig_image.copy()
            frozen_image.set_alpha(128)
            frozen_height = (self.frozen_time - time)/self.frozen_time * self.rect.h
            
            image.blit(frozen_image, (0,0), (0, 0, self.rect.w, frozen_height))
            image.blit(self.orig_image, (0,frozen_height),
                       (0, frozen_height, self.rect.w, self.rect.h - frozen_height))
        elif self.sun_cost > sun_value: # card disable status
            image = self.orig_image.copy()
            image.set_alpha(192)
        else:
            image = self.orig_image
        return image

    def update(self, sun_value, current_time):#게임에 진행됨에 따라 쿨다운 업데이트 해줌
        if (current_time - self.refresh_timer) >= 250:
            self.image = self.createShowImage(sun_value, current_time)#쿨다운 되는 이미지
            self.refresh_timer = current_time

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class MenuBar():
    def __init__(self, card_list, sun_value):
        self.loadFrame(c.MENUBAR_BACKGROUND)
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 0

        self.shovel = Shovel()
        self.shovel_image = self.shovel.image
        self.shovel_rect = self.shovel.rect
        self.shovel_rect.x = 10 + self.rect.right

        self.sun_value = sun_value
        self.card_offset_x = 32
        self.setupCards(card_list)

    def loadFrame(self, name):
        frame = tool.GFX[name]#tool 파일 줄 170에 있는 내용으로, 모든 내용 불러옴
        rect = frame.get_rect()#이미지 크기 구해줌
        frame_rect = (rect.x, rect.y, rect.w, rect.h)#이미지 크기 정리

        self.image = tool.get_image(tool.GFX[name], *frame_rect, c.WHITE, 1)#tool 84줄에 있는 내용으로 정해진 프레임에 맞춰 이미지 가져오는 것

    def update(self, current_time):#카드의 쿨타임과 가격 업뎃
        self.current_time = current_time
        for card in self.card_list:
            card.update(self.sun_value, self.current_time)

    # def createImage(self, x, y, num):#카드를 선택해 메뉴바의 이미지를 불러오는 기능 같다.
    #     if num == 1:
    #         return
    #     img = self.image
    #     rect = self.image.get_rect()
    #     width = rect.w
    #     height = rect.h
    #     self.image = pg.Surface((width * num, height)).convert()#이미지의 픽셀 형식 변경
    #     self.rect = self.image.get_rect()
    #     self.rect.x = x
    #     self.rect.y = y
    #     for i in range(num):
    #         x = i * width
    #         self.image.blit(img, (x,0))
    #     self.image.set_colorkey(c.BLACK)
    
    def setupCards(self, card_list):#모든card 모여있는 부분에 카드를 구현하는 것 같음
        self.card_list = []
        x = self.card_offset_x 
        y = 8
        for index in card_list:
            x += 55
            self.card_list.append(Card(x, y, index))

    def checkCardClick(self, mouse_pos):#게임내 메뉴바의 카드를 클릭해 식물을 가져올 수 있는지 체크
        result = None
        for card in self.card_list:
            if card.checkMouseClick(mouse_pos):
                if card.canClick(self.sun_value, self.current_time):#쿨타임과 카드 가격보다 햇빛이 많아야 클릭할 수 있다.
                    result = (plant_name_list[card.name_index], card)
                break
        return result

    def checkShovel(self, mouse_pos):
        x, y = mouse_pos
        if(x >= self.shovel_rect.x and x <= self.shovel_rect.right and
           y >= self.shovel_rect.y and y <= self.shovel_rect.bottom):
            return True
        return False
#----------------------------------------------------------------------------------------------수정    
    def checkMenuBarClick(self, mouse_pos):
        x, y = mouse_pos
        if(x >= self.rect.x and x <= self.shovel_rect.right and
           y >= self.rect.y and y <= self.rect.bottom):
            return True
        return False

    def decreaseSunValue(self, value):#식물을 사면 가진 햇빛이 감소함
        self.sun_value -= value

    def increaseSunValue(self, value):#햇빛을 주우면 가진 햇빛이 늘어남
        self.sun_value += value

    def setCardFrozenTime(self, plant_name):#쿨타임에 따라 카드를 선택하지 못하게 하는 기능
        for card in self.card_list:
            if plant_name_list[card.name_index] == plant_name:
                card.setFrozenTime(self.current_time)
                break

    def drawSunValue(self):#가진 햇빛을 나타내주는 글씨와 관련됨
        self.value_image = getSunValueImage(self.sun_value)
        self.value_rect = self.value_image.get_rect()
        self.value_rect.x = 21#줄어들수록 글씨가오른쪽으로 오면서 동전같이 생긴(또는 그낭 네모) 글씨가 생김 
        self.value_rect.y = self.rect.bottom - 21
        
        self.image.blit(self.value_image, self.value_rect)
#-------------------------------------------------------------------수정
    def draw(self, surface):#메뉴판을 그려줌
        self.drawSunValue()
        surface.blit(self.image, self.rect)
        for card in self.card_list:
            card.draw(surface)
        surface.blit(self.shovel_image, self.shovel_rect)

class Panel():
    def __init__(self, card_list, sun_value):#초기화
        self.loadImages(sun_value)#sun_value 이미지 가져옴
        self.selected_cards = []
        self.selected_num = 0
        self.setupCards(card_list)

    def loadFrame(self, name):#이미지 가져오기
        frame = tool.GFX[name]#모든 내용 불러옴
        rect = frame.get_rect()
        frame_rect = (rect.x, rect.y, rect.w, rect.h)

        return tool.get_image(tool.GFX[name], *frame_rect, c.WHITE, 1)#정해진 프레임에 맞춰 이미지 가져옴

    def loadImages(self, sun_value):#이미지를 로드해줌
        self.menu_image = self.loadFrame(c.MENUBAR_BACKGROUND)#MENUBAR_BACKGROUND의 이미지 가져옴
        self.menu_rect = self.menu_image.get_rect()#이미지 크기 구해줌
        self.menu_rect.x = 0
        self.menu_rect.y = 0

        self.panel_image = self.loadFrame(c.PANEL_BACKGROUND)#PANEL_BACKGROUND의 이미지 가져옴
        self.panel_rect = self.panel_image.get_rect()
        self.panel_rect.x = 0
        self.panel_rect.y = PANEL_Y_START

        
        self.value_image = getSunValueImage(sun_value)#얼마나 햇빛을 가지고 있는지 알려주는 표시판
        self.value_rect = self.value_image.get_rect()
        self.value_rect.x = 21
        self.value_rect.y = self.menu_rect.bottom - 21

        self.button_image =  self.loadFrame(c.START_BUTTON)#버튼이 있는곳, x,y값 옮기면 자리가 바뀌며 원래 클릭하는 자리는 흐릿하게 표시
        self.button_rect = self.button_image.get_rect()
        self.button_rect.x = 155
        self.button_rect.y = 547

    def setupCards(self, card_list):#Card 선택화면에 카드를 나열해줌
        self.card_list = []
        x = PANEL_X_START - PANEL_X_INTERNAL
        y = PANEL_Y_START + 43 - PANEL_Y_INTERNAL
        for i, index in enumerate(card_list):# enumerate는 그냥 range와 비슷하다고 생각해도 된다.
            if i % 8 == 0:# 카드 선택화면에도 한줄에 8개씩 배치 되어있음 숫자를 7로 바꾸면 한줄에 7개씩 배치됨
                x = PANEL_X_START - PANEL_X_INTERNAL
                y += PANEL_Y_INTERNAL
            x += PANEL_X_INTERNAL
            self.card_list.append(Card(x, y, index, 0.75))#뒤에 숫자가 무슨 기능인진 잘 모르겠다. 지워도 눈에 띄는 문제는 생기지 않았다.

    def checkCardClick(self, mouse_pos):#카드 선택화면에서 클릭으로 카드를 선택하고, 삭제 할 수 있다.
        delete_card = None
        for card in self.selected_cards:#카드 선택화면에서 선택된 카드가 나열되어 있는곳(맨위에)
            if delete_card:
                card.rect.x -= 55
            elif card.checkMouseClick(mouse_pos):#클릭하면 선택한 카드가 삭제된다.
                self.deleteCard(card.name_index)
                delete_card = card

        if delete_card:#카드 삭제되는 과정
            self.selected_cards.remove(delete_card)
            self.selected_num -= 1

        if self.selected_num == CARD_LIST_NUM:#카드 List num은 처음에 8로 지정해놓긴 했었음
            return

        for card in self.card_list:#카드 클릭해서 카드 선택하는 것
            if card.checkMouseClick(mouse_pos):
                if card.canSelect():
                    self.addCard(card)#맨 위에 카드 추가해줌
                break

    def addCard(self, card):#카드 추가해주는 기능
        card.setSelect(False)
        y = 8
        x = 78 + self.selected_num * 55
        self.selected_cards.append(Card(x, y, card.name_index))
        self.selected_num += 1

    def deleteCard(self, index):#카드 삭제해주는 기능
        self.card_list[index].setSelect(True)

    def checkStartButtonClick(self, mouse_pos):#카드 리스트를 다 채우지 않으면 Start 버튼을 클릭할 수 없음
        if self.selected_num < CARD_LIST_NUM:
            return False

        x, y = mouse_pos#클릭범위
        if (x >= self.button_rect.x and x <= self.button_rect.right and
            y >= self.button_rect.y and y <= self.button_rect.bottom):
           return True
        return False

    def getSelectedCards(self):#카드 리스트에 선택한 카드 추가해줌
        card_index_list = []
        for card in self.selected_cards:
            card_index_list.append(card.name_index)
        return card_index_list

    def draw(self, surface):
        self.menu_image.blit(self.value_image, self.value_rect)
        surface.blit(self.menu_image, self.menu_rect)
        surface.blit(self.panel_image, self.panel_rect)
        for card in self.card_list:#지워보니 카드를 선택하는 곳의 카드 이미지가 삭제됨
            card.draw(surface)
        for card in self.selected_cards:# 맨 위에 카드의 이미지를 추가해주는 기능일 것
            card.draw(surface)

        if self.selected_num == CARD_LIST_NUM:#맨위의 리스트가 다 채워지면 start 클릭할 수 있게 해주는 기능
            surface.blit(self.button_image, self.button_rect)

class MoveCard():#Level 5에 관련된 클래스임. 각각의 함수값을 바꿔보면 나머지 level과는 상관없지만 level5에만 영향을 미침. level1에 level5를 복붙해보면 더 와닿을 것임.
    def __init__(self, x, y, card_name, plant_name, scale=0.78):#초기화
        self.loadFrame(card_name, scale)
        self.rect = self.orig_image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.w = 1
        self.image = self.createShowImage()

        self.card_name = card_name
        self.plant_name = plant_name
        self.move_timer = 0#무슨 역할인지 잘 모르겠음 100으로 바꿔도 별 차이가 없음 아마 카드가 나오는 속도일 것이다
        self.select = True

    def loadFrame(self, name, scale):#125줄의 Menubar의 loadFrame과 같은 기능
        frame = tool.GFX[name]
        rect = frame.get_rect()
        width, height = rect.w, rect.h

        self.orig_image = tool.get_image(frame, 0, 0, width, height, c.BLACK, scale)
        self.orig_rect = self.orig_image.get_rect()
        self.image = self.orig_image

    def checkMouseClick(self, mouse_pos):# Menubar의 checkMouseClick와 같은기능
        x, y = mouse_pos
        if(x >= self.rect.x and x <= self.rect.right and
           y >= self.rect.y and y <= self.rect.bottom):
            return True
        return False

    def createShowImage(self):
        if self.rect.w < self.orig_rect.w:
            image = pg.Surface([self.rect.w, self.rect.h])
            image.blit(self.orig_image, (0, 0), (0, 0, self.rect.w, self.rect.h))
            self.rect.w += 1
        else:
            image = self.orig_image
        return image

    def update(self, left_x, current_time):
        if self.move_timer == 0:
            self.move_timer = current_time
        elif (current_time - self.move_timer) >= c.CARD_MOVE_TIME:
            if self.rect.x > left_x:
                self.rect.x -= 1
                self.image = self.createShowImage()
            self.move_timer += c.CARD_MOVE_TIME

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class MoveBar():#LEVEL 5에 관련된 기능임 직접 없애보면 틩기지만 각각의 기능이 유추됨
    def __init__(self, card_pool):
        self.loadFrame(c.MOVEBAR_BACKGROUND)
        self.rect = self.image.get_rect()
        self.rect.x = 90
        self.rect.y = 0
        
        self.card_start_x = self.rect.x + 8
        self.card_end_x = self.rect.right - 5
        self.card_pool = card_pool
        self.card_list = []
        self.create_timer = -c.MOVEBAR_CARD_FRESH_TIME

    def loadFrame(self, name):
        frame = tool.GFX[name]
        rect = frame.get_rect()
        frame_rect = (rect.x, rect.y, rect.w, rect.h)

        self.image = tool.get_image(tool.GFX[name], *frame_rect, c.WHITE, 1)

    def createCard(self):#카드가 랜덤으로 나와야하니 랜덤 기능임
        if len(self.card_list) > 0 and self.card_list[-1].rect.right > self.card_end_x:
            return False
        x = self.card_end_x
        y = 6
        index = random.randint(0, len(self.card_pool) - 1)
        card_index = self.card_pool[index]
        card_name = card_name_list[card_index] + '_move'
        plant_name = plant_name_list[card_index]
        self.card_list.append(MoveCard(x, y, card_name, plant_name))
        return True

    def update(self, current_time):#5단계 게임 업데이트에 관련함
        self.current_time = current_time
        left_x = self.card_start_x
        for card in self.card_list:
            card.update(left_x, self.current_time)
            left_x = card.rect.right + 1#카드바에서 카드가 나오는 간격을 의미함 숫자가 커지면 간격이 커짐

        if(self.current_time - self.create_timer) > c.MOVEBAR_CARD_FRESH_TIME:
            if self.createCard():
                self.create_timer = self.current_time#카드가 나오는 시간을 의미함 -5000정도로 주니까 카드들이 붙어서 따닥따닥나옴

    def checkCardClick(self, mouse_pos):
        result = None
        for index, card in enumerate(self.card_list):
            if card.checkMouseClick(mouse_pos):
                result = (card.plant_name, card)
                break
        return result
    
    def checkMenuBarClick(self, mouse_pos):
        x, y = mouse_pos
        if(x >= self.rect.x and x <= self.rect.right and
           y >= self.rect.y and y <= self.rect.bottom):
            return True
        return False

    def deleateCard(self, card):
        self.card_list.remove(card)

    def draw(self, surface):#나머지는 위의 menubar에서의 기능과 같음
        surface.blit(self.image, self.rect)
        for card in self.card_list:
            card.draw(surface)
#-----------------------------------------------------------------------------삽 이미지            
class Shovel():
    def __init__(self):
        self.loadFrame(c.SHOVEL)
        self.rect = self.image.get_rect()

    def loadFrame(self, name):
        frame = tool.GFX[name]
        rect = frame.get_rect()
        frame_rect = (rect.x, rect.y, rect.w, rect.h)

        self.image = tool.get_image(tool.GFX[name], *frame_rect, c.WHITE, 1)