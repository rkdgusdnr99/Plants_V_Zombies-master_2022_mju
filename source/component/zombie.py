import pygame as pg
from .. import tool
from .. import constants as c

class Zombie(pg.sprite.Sprite):#pg.sprite.Sprite: 눈에 보이는 게임 객체의 간단한 기본 클래스
    def __init__(self, x, y, name, health, head_group=None, damage=1):#좀비 상태에 대한 선언
        pg.sprite.Sprite.__init__(self)
        
        self.name = name
        self.frames = []
        self.frame_index = 0
        self.loadImages()#이미지 로드
        self.frame_num = len(self.frames)

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()#이미지 크기 구해줌
        self.rect.centerx = x
        self.rect.bottom = y
        
        self.health = health
        self.damage = damage
        self.dead = False
        self.losHead = False
        self.helmet = False
        self.head_group = head_group

        self.walk_timer = 0
        self.animate_timer = 0
        self.attack_timer = 0
        self.state = c.WALK
        self.animate_interval = 150
        self.ice_slow_ratio = 1
        self.ice_slow_timer = 0
        self.hit_timer = 0
        self.speed = 1
        self.freeze_timer = 0
        self.is_hypno = False  #좀비가 HypnoShroom을 먹었을 때 다른 좀비를 공격한다.

    def loadFrames(self, frames, name, image_x, colorkey=c.BLACK):#이미지 불러오는 역할
        frame_list = tool.GFX[name]
        rect = frame_list[0].get_rect()
        width, height = rect.w, rect.h
        width -= image_x

        for frame in frame_list:
            frames.append(tool.get_image(frame, image_x, 0, width, height, colorkey))#이미지 속성 설정해줌

    def update(self, game_info):
        self.current_time = game_info[c.CURRENT_TIME]
        self.handleState()
        self.updateIceSlow()
        self.animation()

    def handleState(self):#좀비의 상태(걷기, 공격, 죽음, 얼음)
        if self.state == c.WALK:
            self.walking()
        elif self.state == c.ATTACK:
            self.attacking()
        elif self.state == c.DIE:
            self.dying()
        elif self.state == c.FREEZE:
            self.freezing()

    def walking(self):
        if self.health <= 0:#좀비 피가 0이되면
            self.setDie()#죽음
        elif self.health <= c.LOSTHEAD_HEALTH and not self.losHead:#일정 이상 데미지 입으면 머리 잃음
            self.changeFrames(self.losthead_walk_frames)#머리잃고 걷는 모습
            self.setLostHead()#머리 잃음
        elif self.health <= c.NORMAL_HEALTH and self.helmet:#헬멧이 있고 그냥 좀비 피 이하로 떨어지면
            self.changeFrames(self.walk_frames)#그냥 걷는 모습으로 바뀜
            self.helmet = False#헬멧 떨어짐
            if self.name == c.NEWSPAPER_ZOMBIE:
                self.speed = 2#신문지좀비면 속도가 2임(다른 좀비의 2배)

        if (self.current_time - self.walk_timer) > (c.ZOMBIE_WALK_INTERVAL * self.getTimeRatio()):
            self.walk_timer = self.current_time/1000 #크게 곱하면 좀비 속도가 느려지고 크게 나누면 좀비 속도가 빨라짐--------------------------------------------------------
            if self.is_hypno:#만일 배신버섯에 감염된 좀비라면 스피드 빨라짐? 하지만 배신버섯에 감염되면 식물의 공격 안받음
                self.rect.x += self.speed
            else:
                self.rect.x -= self.speed
    
    def attacking(self):
        if self.health <= 0:
            self.setDie()
        elif self.health <= c.LOSTHEAD_HEALTH and not self.losHead:#일정 이상 피해 입으면 머리 잃음
            self.changeFrames(self.losthead_attack_frames)
            self.setLostHead()
        elif self.health <= c.NORMAL_HEALTH and self.helmet:# 헬멧잃고 보통 좀비 처럼 됨
            self.changeFrames(self.attack_frames)
            self.helmet = False
        if (self.current_time - self.attack_timer) > (c.ATTACK_INTERVAL * self.getTimeRatio()):
            if self.prey.health > 0:#적(식물)의 hp가 0보다 크면
                if self.prey_is_plant:
                    self.prey.setDamage(self.damage, self)#적에게 데미지를 준다.
                else:
                    self.prey.setDamage(self.damage)
            self.attack_timer = self.current_time#공격속도 아닐까 추측 크게 곱해보니까 식물이 공격을 받지 않았음

        if self.prey.health <= 0:#아마 식물이 죽으면 다시 걸어가란 뜻 같다. 하지만 값을 0보다 큰 값으로 바꾸면 식물이 죽지 않기때문에 공격 모션 상태로 가만히 있는다.
            self.prey = None
            self.setWalk()
    
    def dying(self):#죽음
        pass

    def freezing(self):#어는것에 대한 함수(얼음 버섯)
        if self.health <= 0:#얼릴때 데미지 줘가지고 죽일 수도 있음
            self.setDie()
        elif self.health <= c.LOSTHEAD_HEALTH and not self.losHead:#그냥 데미지 입을때랑 같은 문장임
            if self.old_state == c.WALK:
                self.changeFrames(self.losthead_walk_frames)
            else:
                self.changeFrames(self.losthead_attack_frames)
            self.setLostHead()
        if (self.current_time - self.freeze_timer) > c.FREEZE_TIME:
            self.setWalk()#얼어있는 시간이 끝나면 다시 걸을 수 있음

    def setLostHead(self):#머리를 잃는 것
        self.losHead = True
        if self.head_group is not None:
            self.head_group.add(ZombieHead(self.rect.centerx, self.rect.bottom))

    def changeFrames(self, frames):#상태에 따른 이미지 바꿔주는 것
        self.frames = frames
        self.frame_num = len(self.frames)
        self.frame_index = 0
        
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom
        self.rect.centerx = centerx

    def animation(self):
        if self.state == c.FREEZE:
            self.image.set_alpha(192)#얼어있는 상태에서 투명도 조절
            return

        if (self.current_time - self.animate_timer) > (self.animate_interval * self.getTimeRatio()):
            self.frame_index += 1
            if self.frame_index >= self.frame_num:
                if self.state == c.DIE:
                    self.kill()#지정된 프로세스 ID를 가진 프로세스에 지정된 신호를 보내는 데 사용된다.
                    return
                self.frame_index = 0
            self.animate_timer = self.current_time

        self.image = self.frames[self.frame_index]
        if self.is_hypno:#배신좀비
            self.image = pg.transform.flip(self.image, True, False)#좀비 이미지를 뒤집는것(뒤돌게 하는 것)
        if(self.current_time - self.hit_timer) >= 200:
            self.image.set_alpha(255)#안맞았을때 선명
        else:
            self.image.set_alpha(192)#맞았을때는 좀 투명해짐 0으로 가까울수록 투명

    def getTimeRatio(self):
        return self.ice_slow_ratio#좀비 얼음맞고 둔화

    def setIceSlow(self):#얼음맞고 느려지는 정도
        # when get a ice bullet damage, slow the attack or walk speed of the zombie
        self.ice_slow_timer = self.current_time
        self.ice_slow_ratio = 2#얼마나 느려지나

    def updateIceSlow(self):
        if self.ice_slow_ratio > 1:
            if (self.current_time - self.ice_slow_timer) > c.ICE_SLOW_TIME:
                self.ice_slow_ratio = 1

    def setDamage(self, damage, ice=False):
        self.health -= damage
        self.hit_timer = self.current_time
        if ice:#얼음 맞으면 공속도 느려지는 듯
            self.setIceSlow()
    
    def setWalk(self):
        self.state = c.WALK
        self.animate_interval = 150#어떤 기능인지 잘 모르겠음. 1000배를 곱해봐도 별 달라지는게 없음
        
        if self.helmet:#헬멧좀비 걷는것
            self.changeFrames(self.helmet_walk_frames)
        elif self.losHead:#머리없는 좀비 걷는것
            self.changeFrames(self.losthead_walk_frames)
        else:#일반좀비 걷는것
            self.changeFrames(self.walk_frames)

    def setAttack(self, prey, is_plant=True):
        self.prey = prey  # 배신한 좀비나 식물이 먹이로 취급
        self.prey_is_plant = is_plant
        self.state = c.ATTACK
        self.attack_timer = self.current_time
        self.animate_interval = 100
        
        if self.helmet:
            self.changeFrames(self.helmet_attack_frames)
        elif self.losHead:
            self.changeFrames(self.losthead_attack_frames)
        else:
            self.changeFrames(self.attack_frames)
    
    def setDie(self):#죽는걸 설정함
        self.state = c.DIE
        self.animate_interval = 200
        self.changeFrames(self.die_frames)#죽는 모습
    
    def setBoomDie(self):#폭발로 인해 죽는것?
        self.state = c.DIE
        self.animate_interval = 200
        self.changeFrames(self.boomdie_frames)

    def setFreeze(self, ice_trap_image):#얼음 버섯이 얼리는 것
        self.old_state = self.state
        self.state = c.FREEZE
        self.freeze_timer = self.current_time
        self.ice_trap_image = ice_trap_image
        self.ice_trap_rect = ice_trap_image.get_rect()
        self.ice_trap_rect.centerx = self.rect.centerx
        self.ice_trap_rect.bottom = self.rect.bottom

    def drawFreezeTrap(self, surface):#얼음 버섯 그리는 기능, 제거하면 얼음버섯 설치시 게임 틩김
        if self.state == c.FREEZE:
            surface.blit(self.ice_trap_image, self.ice_trap_rect)

    def setHypno(self):#배신좀비 세팅
        self.is_hypno = True
        self.setWalk()

class ZombieHead(Zombie):#좀비 머리 클래스
    def __init__(self, x, y):
        Zombie.__init__(self, x, y, c.ZOMBIE_HEAD, 0)
        self.state = c.DIE
    
    def loadImages(self):#이미지 로드해줌
        self.die_frames = []
        die_name =  self.name
        self.loadFrames(self.die_frames, die_name, 0)
        self.frames = self.die_frames

    def setWalk(self):
        self.animate_interval = 100

class NormalZombie(Zombie):#일반좀비 클래스
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.NORMAL_ZOMBIE, c.NORMAL_HEALTH, head_group)

    def loadImages(self):
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        walk_name = self.name
        attack_name = self.name + 'Attack'#공격
        losthead_walk_name = self.name + 'LostHead'#머리 잃음
        losthead_attack_name = self.name + 'LostHeadAttack'#머리 잃은 좀비 공격
        die_name =  self.name + 'Die'#죽음
        boomdie_name = c.BOOMDIE#폭사

        frame_list = [self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]
        
        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name, tool.ZOMBIE_RECT[name]['x'])#name_list에 있는 좀비 상태 이미지 모두 불러와줌

        self.frames = self.walk_frames

class ConeHeadZombie(Zombie):#머리에 꼬깔콘 쓰고있는 좀비 클래스
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.CONEHEAD_ZOMBIE, c.CONEHEAD_HEALTH, head_group)
        self.helmet = True

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []
        
        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'#헬멧 있을 때
        walk_name = c.NORMAL_ZOMBIE#헬멧 떨어졌을 때
        attack_name = c.NORMAL_ZOMBIE + 'Attack'#나머진 일반 좀비와 동일
        losthead_walk_name = c.NORMAL_ZOMBIE + 'LostHead'
        losthead_attack_name = c.NORMAL_ZOMBIE + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]
        
        for i, name in enumerate(name_list): #name_list에 있는 꼬깔콘 좀비 상태 이미지 모두 불러와줌
            self.loadFrames(frame_list[i], name, tool.ZOMBIE_RECT[name]['x'])

        self.frames = self.helmet_walk_frames

class BucketHeadZombie(Zombie):#바가지 좀비 클래스, 꼬깔콘 좀비랑 다를거 없음
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.BUCKETHEAD_ZOMBIE, c.BUCKETHEAD_HEALTH, head_group)
        self.helmet = True

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'
        walk_name = c.NORMAL_ZOMBIE
        attack_name = c.NORMAL_ZOMBIE + 'Attack'
        losthead_walk_name = c.NORMAL_ZOMBIE + 'LostHead'
        losthead_attack_name = c.NORMAL_ZOMBIE + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]
        
        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name, tool.ZOMBIE_RECT[name]['x'])

        self.frames = self.helmet_walk_frames

class FlagZombie(Zombie):#깃발좀비 클래스, 일반좀비보다 피통만 좀 많음
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.FLAG_ZOMBIE, c.FLAG_HEALTH, head_group)
    
    def loadImages(self):
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        walk_name = self.name
        attack_name = self.name + 'Attack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name = c.NORMAL_ZOMBIE + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]
        
        for i, name in enumerate(name_list):
            self.loadFrames(frame_list[i], name, tool.ZOMBIE_RECT[name]['x'])

        self.frames = self.walk_frames

class NewspaperZombie(Zombie):#신문지좀비
    def __init__(self, x, y, head_group):
        Zombie.__init__(self, x, y, c.NEWSPAPER_ZOMBIE, c.NEWSPAPER_HEALTH, head_group)
        self.helmet = True

    def loadImages(self):
        self.helmet_walk_frames = []
        self.helmet_attack_frames = []
        self.walk_frames = []
        self.attack_frames = []
        self.losthead_walk_frames = []
        self.losthead_attack_frames = []
        self.die_frames = []
        self.boomdie_frames = []

        helmet_walk_name = self.name
        helmet_attack_name = self.name + 'Attack'#헬멧 좀비로 취급되는 것을 알 수 있음
        walk_name = self.name + 'NoPaper'#헬멧이 떨어지면 NoPaper로 취급, 공격력도 같이 떨어짐
        attack_name = self.name + 'NoPaperAttack'
        losthead_walk_name = self.name + 'LostHead'
        losthead_attack_name = self.name + 'LostHeadAttack'
        die_name = self.name + 'Die'
        boomdie_name = c.BOOMDIE

        frame_list = [self.helmet_walk_frames, self.helmet_attack_frames,
                      self.walk_frames, self.attack_frames, self.losthead_walk_frames,
                      self.losthead_attack_frames, self.die_frames, self.boomdie_frames]
        name_list = [helmet_walk_name, helmet_attack_name,
                     walk_name, attack_name, losthead_walk_name,
                     losthead_attack_name, die_name, boomdie_name]

        for i, name in enumerate(name_list):
            if name == c.BOOMDIE:#신문지는 타니까 폭사시 다른 좀비와 다르게 검게 나옴
                color = c.BLACK
            else:
                color = c.WHITE
            self.loadFrames(frame_list[i], name, tool.ZOMBIE_RECT[name]['x'], color)

        self.frames = self.helmet_walk_frames