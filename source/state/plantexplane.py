import pygame as pg
from .. import tool
from .. import constants as c

class Menu(tool.State):#모든 시간이 0으로 되어있는 tool의 시간
    def __init__(self):
        tool.State.__init__(self)
    
    def startup(self, current_time, persist):#게임 시작전 세팅
        self.next = c.LEVEL#레벨 설정
        self.persist = persist
        self.game_info = persist
        
        self.setupBackground()
        self.setupOption()

    def setupBackground(self):
        frame_rect = [0, -10, 800, 600]#[80,0,800,600]
        self.bg_image = tool.get_image(tool.GFX[c.PLANT_EXPLANE_IMAGE], *frame_rect)#MAIN_MENU_IMAGE 이미지 가지고 와줌
        self.bg_rect = self.bg_image.get_rect()#이미지 크기 구해줌
        self.bg_rect.x = 0#메인 메뉴의 이미지 시작부분(값 바꾸면 밀림)
        self.bg_rect.y = 0
        
    def setupOption(self):#맨 처음 옵션을 세팅해줌

        frame_rect = [0, 0, 800, 600]
        self.option_image = tool.get_image(tool.GFX[c.OPTION_GAME_START], *frame_rect)#MAIN_MENU_IMAGE 이미지 가지고 와줌
        self.option_rect = self.option_image.get_rect()#이미지 크기 구해줌
        
        self.option_frame_index = 0#ADVENTURE버튼 위치 설정
        self.option_rect = self.option_image.get_rect()
        self.option_rect.x = 638 #435
        self.option_rect.y = 500 #75
        
        self.option_start = 0
        self.option_timer = 0
        self.option_clicked = False
    
    def checkOptionClick(self, mouse_pos):#시작 버튼을 눌렀는지? 눌러야 시작됨
        x, y = mouse_pos
        if(x >= self.option_rect.x and x <= self.option_rect.right and
           y >= self.option_rect.y and y <= self.option_rect.bottom):
            self.option_clicked = True#클릭버튼, FALSE로 바꾸면 시작 불가
            self.option_timer = self.option_start = self.current_time#시간 동일하게 설정
        return False
        
    def update(self, surface, current_time, mouse_pos, mouse_click):#시작부위의 업데이트
        self.current_time = self.game_info[c.CURRENT_TIME] = current_time
        
        if not self.option_clicked:#클릭하지 않으면 시작 x
            if mouse_pos:
                self.checkOptionClick(mouse_pos)
        else:
            self.done = True#이부분만 남기면 넘어감

        surface.blit(self.bg_image, self.bg_rect)#시작 부분 빌드해줌
        surface.blit(self.option_image, self.option_rect)