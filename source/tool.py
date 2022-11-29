import os
import json
import pygame as pg
from pygame import mixer
from abc import abstractmethod
from . import constants as c

class State():
    def __init__(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.done = False
        self.next = None
        self.persist = {}

    def startup(self, current_time, persist):
        '''abstract method'''

    def cleanup(self):
        self.done = False
        return self.persist

    def update(self, surface, keys, current_time):
        '''abstract method'''
#------------------------------------------------------------------------------------------------------
class Control():
    def __init__(self): #초기화
        self.screen = pg.display.get_surface() #현재 설정된 디스플레이 표면에 대한 참조를 반환합니다. 디스플레이 모드가 설정되지 않은 경우 None을 반환합니다
        self.done = False
        self.clock = pg.time.Clock() #시간을 추적하는 개체 만들기
        self.fps = 60
        self.keys = pg.key.get_pressed() #키보드의 모든 키 상태를 나타내는 일련의 부울 값을 반환, True 값은 버튼을 눌렀음을 의미
        self.mouse_pos = None
        self.mouse_click = [False, False]  #[left,right]
        self.current_time = 0.0
        self.state_dict = {}
        self.state_name = None
        self.state = None
        self.game_info = {c.CURRENT_TIME:0.0,
                          c.LEVEL_NUM:c.START_LEVEL_NUM} #게임 시작시 정보
 
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, self.game_info)

    def update(self):
        self.current_time = pg.time.get_ticks() #pygame.init()가 호출된 이후의 밀리초 수를 반환합니다. 파이게임이 초기화되기 전에는 항상 0
        if self.state.done:
            self.flip_state() #현재 애니메이션의 상태
        self.state.update(self.screen, self.current_time, self.mouse_pos, self.mouse_click)
        self.mouse_pos = None
        self.mouse_click[0] = False #왼쪽
        self.mouse_click[1] = False #오른쪽

    def flip_state(self):
        previous, self.state_name = self.state_name, self.state.next
        persist = self.state.cleanup()#프로그램을 종료하기전, 리소스를 반납
        self.state = self.state_dict[self.state_name]
        self.state.startup(self.current_time, persist)

    def event_loop(self):#아마 라운드를 넘기는 기능 하는것 같음
        for event in pg.event.get(): #queue에서 이벤트 가져옴
            if event.type == pg.QUIT:#이벤트가 끝났을 때
                self.done = True
            elif event.type == pg.KEYDOWN: #키를 누름
                self.keys = pg.key.get_pressed()
            elif event.type == pg.KEYUP: #키를 땜
                self.keys = pg.key.get_pressed()
            elif event.type == pg.MOUSEBUTTONDOWN: #마우스 버튼 누름
                self.mouse_pos = pg.mouse.get_pos() #마우스 커서의 x 및 y 위치를 반환합니다. 
                self.mouse_click[0], _, self.mouse_click[1] = pg.mouse.get_pressed()
                print('pos:', self.mouse_pos, ' mouse:', self.mouse_click) #마우스 클릭한 위치를 보여줌

    def main(self): #게임에서 졌을 때 
        while not self.done: #게임을 마쳤을 때
            self.event_loop()
            self.update()
            pg.display.update() #화면 부분 업데이트
            self.clock.tick(self.fps)
        print('Game over')
#-------------------------------------------------------------------------------------------------------------------
def get_image(sheet, x, y, width, height, colorkey=c.BLACK, scale=1):
        image = pg.Surface([width, height])
        rect = image.get_rect()#이미지의 크기 구해주는 것

        image.blit(sheet, (0, 0), (x, y, width, height))#이미지 복사
        image.set_colorkey(colorkey)#부분적인 투명함
        image = pg.transform.scale(image,
                                   (int(rect.width*scale),
                                    int(rect.height*scale)))#새 해상도로 크기 조정
        return image

def load_image_frames(directory, image_name, colorkey, accept): #이미지 프레임 설정
    frame_list = []
    tmp = {}
    index_start = len(image_name) + 1 
    frame_num = 0
    for pic in os.listdir(directory): #지정된 경로(directory)에 있는 모든 파일의 이름 목록을 인쇄
        name, ext = os.path.splitext(pic) #경로 이름 경로를 쌍(root, ext)으로 분할, root + ext == pic
        if ext.lower() in accept:
            index = int(name[index_start:])
            img = pg.image.load(os.path.join(directory, pic)) #괄호안의 파일에서 이미지 불러옴
            if img.get_alpha(): #현재 표면 투명도 값 가져오기
                img = img.convert_alpha() #픽셀당 알파를 포함하여 이미지의 픽셀 형식 변경
            else:
                img = img.convert() #이미지의 픽셀 형식 변경
                img.set_colorkey(colorkey) #img의 현재 색상키를 설정
            tmp[index]= img
            frame_num += 1

    for i in range(frame_num):
        frame_list.append(tmp[i])
    return frame_list

def load_all_gfx(directory, colorkey=c.WHITE, accept=('.png', '.jpg', '.bmp', '.gif')):
    graphics = {}
    for name1 in os.listdir(directory): #지정된 경로(directory)에 있는 모든 파일의 이름 목록안에 name1이있는지
        dir1 = os.path.join(directory, name1) #directory, name1을 결합하여 1개로 합쳐줌
        if os.path.isdir(dir1): #dir1이 존재하는 디렉터리이면 True를 반환합니다.
            for name2 in os.listdir(dir1): #지정된 경로(dir1)에 있는 모든 파일의 이름 목록안에 name2가 있는지
                dir2 = os.path.join(dir1, name2)
                if os.path.isdir(dir2):
                    for name3 in os.listdir(dir2):#지정된 경로(dir2)에 있는 모든 파일의 이름 목록안에 name3가 있는 동안
                        dir3 = os.path.join(dir2, name3)
                        if os.path.isdir(dir3):
                            image_name, _ = os.path.splitext(name3)#경로 이름 경로를 쌍(root, ext)으로 분할, root + ext == name3
                            graphics[image_name] = load_image_frames(dir3, image_name, colorkey, accept)
                        else:
                            image_name, _ = os.path.splitext(name2)
                            graphics[image_name] = load_image_frames(dir2, image_name, colorkey, accept)#이미지 해상도등 설정
                            break
                else:
                    name, ext = os.path.splitext(name2)
                    if ext.lower() in accept: #'.png', '.jpg', '.bmp', '.gif'목록에 ext에 저장된 문자열이있으면 
                        img = pg.image.load(dir2) #dir2에서 이미지 불러옴
                        if img.get_alpha(): #이 밑은 해상도 투명도 등 조절
                            img = img.convert_alpha()
                        else:
                            img = img.convert()
                            img.set_colorkey(colorkey)
                        graphics[name] = img
    return graphics

def loadZombieImageRect():
    file_path = os.path.join('source', 'data', 'entity', 'zombie.json') #'source', 'data', 'entity', 'zombie.json'들을 결합하여 하나로 합침
    f = open(file_path)#위에서 합친 파일명을 열음
    data = json.load(f)#파일안의 json형식 불러옴
    f.close()
    return data[c.ZOMBIE_IMAGE_RECT]#좀비 이미지 리턴해줌

def loadPlantImageRect():#좀비와 형식 같음
    file_path = os.path.join('source', 'data', 'entity', 'plant.json')
    f = open(file_path)
    data = json.load(f)
    f.close()
    return data[c.PLANT_IMAGE_RECT]

pg.init()
mixer.music.load('source\\bgm.mp3') #첫 화면 음악
mixer.music.play(-1)

rz = pg.image.load('resources\\graphics\\Screen\\icon.jpg') #첫 화면 좀비얼굴
pg.display.set_icon(rz)

pg.display.set_caption(c.ORIGINAL_CAPTION) #현재 창 캡션 설정
SCREEN = pg.display.set_mode(c.SCREEN_SIZE) #화면초기화

GFX = load_all_gfx(os.path.join("resources", "graphics")) #모든 이미지 불러옴
ZOMBIE_RECT = loadZombieImageRect() #좀비형식
PLANT_RECT = loadPlantImageRect() #식물형식
