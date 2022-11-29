import pygame as pg
from .. import tool
from .. import constants as c

class Screen(tool.State):
    def __init__(self):
        tool.State.__init__(self)#게임 시작 초기값 설정
        self.end_time = 3000#end time 지정. 클릭하지 않았을때 victory 화면과 loose화면이 띄워져있는 시간 의미함

    def startup(self, current_time, persist):
        self.start_time = current_time
        self.next = c.LEVEL
        self.persist = persist
        self.game_info = persist
        name = self.getImageName()#이미지 이름 설정
        self.setupImage(name)#이미지 이름에 맞는 이미지 세팅
        self.next = self.set_next_state()#다음 스테이지나 메인메뉴로 가게 해주는 기능
    
    def getImageName(self):#이미지이름
        pass

    def set_next_state(self):#다음 스테이지
        pass

    def setupImage(self, name):#이미지 세팅해주는 기능
        frame_rect = [0, 0, 800, 600]
        self.image = tool.get_image(tool.GFX[name], *frame_rect)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

    def update(self, surface, current_time, mouse_pos, mouse_click):#victory 화면과 lose화면을 불러오는 기능. 지워보니 victory에서 틩김
        if(current_time - self.start_time) < self.end_time:
            surface.fill(c.WHITE)#배경은 하얗게, 뭔색으로 하든 별로 상관x
            surface.blit(self.image, self.rect)#이미지 넣어줌
        else:
            self.done = True

class GameVictoryScreen(Screen):
    def __init__(self):#위에서 해준 설정과 동일하게 설정
        Screen.__init__(self)
    
    def getImageName(self):#victory이미지 불러옴
        return c.GAME_VICTORY_IMAGE
    
    def set_next_state(self):#다음 스테이지 갈 수 있도록 다음 레벨 불러와줌
        return c.LEVEL

class GameLoseScreen(Screen):
    def __init__(self):#위에서 해준 설정과 동일하게 설정
        Screen.__init__(self)
    
    def getImageName(self):#loose이미지 불러옴
        return c.GAME_LOOSE_IMAGE
    
    def set_next_state(self):#다시 메인메뉴로 가게 해줌
        return c.MAIN_MENU