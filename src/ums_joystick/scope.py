import time
import numpy as np

# 스코프 클래스 정의
class Scope(object):
    
    # 초기 설정
    def __init__(self,
                 ax,fn,
                 xmax=20,ymax =10,
                 xstart=0, ystart=0,
                 title='Title',xlabel='X value',ylabel='Y value',
                 color = 'b'):
        
        self.xmax = xmax #x축 길이
        self.xstart = xstart #x축 시작점
        self.ymax = ymax #y축 길이
        self.ystart = ystart #y축 시작점
        self.color = color

        # 그래프 설정
        self.ax = ax 
        self.ax.set_xlim((self.xstart,self.xmax))
        self.ax.set_ylim((self.ystart,self.ymax))
        self.ax.set_title(title)
        # self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        self.x = [0] # x축 정보 
        self.y = [0] # y축 정보
        self.value = 0 # 축 값
        self.fn = fn
        self.line, = ax.plot([],[], self.color)

        self.ti = time.time() #현재시각
        print("초기화 완료")

    # 그래프 설정
    def update(self, i):
        # 시간차
        tempo = time.time()-self.ti
        self.ti = time.time() #시간 업데이트
        
        # 값 넣기
        self.value = self.fn()# y값 함수 불러오기
        self.y.append(self.value) #y값 넣기
        self.x.append(tempo + self.x[-1]) #x값 넣기
        self.line.set_data(self.x,self.y)

        # 화면에 나타낼 x축 범위 업데이트
        if self.x[-1] >= self.xstart + self.xmax :
            #전체 x값중 반을 화면 옆으로 밀기
            self.xstart = self.xstart + self.xmax
            self.ax.set_xlim(self.xstart,self.xstart + self.xmax)

            self.ax.figure.canvas.draw()

        return (self.line, )