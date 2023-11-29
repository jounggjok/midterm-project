# *********************************************
# 프로그램 관리
# 최초 작성일 : 2020.7.
# 작성자 : hazel (hazelnuttree@naver.com)
# =============================================
# 업데이트 : 2022.05.19
# 버전 : v2.0
# 업데이트 주요 내용 : 동료거북이 움직임 업데이트
# *********************************************

import turtle as t
import random
from tkinter import Tk, Label, messagebox, LEFT

# 초기값
score = 0 #점수
playing = False #플레이 정보
special = False #특수먹이 정보
shadow = False #동료거북이 정보

# 초기 위치 셋팅

# 내거북이
tt = t.Turtle()
tt.shape("turtle")
tt.color("white")
tt.speed(0)
tt.up()
tt.goto(0,0)

# 악당 거북이
te = t.Turtle()
te.shape("turtle")
te.color("black")
te.speed(0)
te.up()
te.goto(0,200)

# 먹이
fd = t.Turtle()
fd.shape("circle")
fd.color("green")
fd.speed(0)
fd.up()
fd.goto(0,-200)

# 특수먹이
sfd = t.Turtle()
sfd.shape("circle")
sfd.color("white")
sfd.speed(0)
sfd.up()
sfd.goto(-300,-300)
sfd.hideturtle()

# 동료(그림자)거북이
tsd = t.Turtle()
tsd.shape("turtle")
tsd.color("red")
tsd.speed(0)
tsd.up()
# tsd.goto(-300,-300)
tsd.hideturtle()

# 내 거북이 움직임 정의
def turn_right():
    tt.setheading(0)

def turn_up():
    tt.setheading(90)

def turn_left():
    tt.setheading(180)

def turn_down():
    tt.setheading(270)

# 특수먹이를 먹었을 때 행동
def special_food():
    global special, dstn, destination_x, destination_y

    # 특수먹이 숨기기
    sfd.hideturtle()
    
    # 특수 먹이 반대방향에 동료거북이 출현
    start_x3 = -1*start_x2
    start_y3 = -1*start_y2
    tsd.goto(start_x3, start_y3)
    tsd.showturtle()

    # 동료 거북이 목표 방향 설정
    dstn = random.randint(1,4)
    
    if dstn == 1:
        destination_x = -230
        destination_y = random.randint(-230,230)

    elif dstn == 2:
        destination_x = 230
        destination_y = random.randint(-230,230)

    elif dstn == 3:
        destination_x = random.randint(-230,230)
        destination_y = -230
    
    else:
        destination_x = random.randint(-230,230)
        destination_y = 230

    # 특수먹이 정보 설정    
    special = False

# 게임 시작 정보
def start():
    
    global playing
    
    if playing == False:
        playing = True
        
        # 게임판 초기화
        t.clear()
        
        tt.clear()
        tt.goto(0,0)
        
        # 플레이 함수 호출
        play()

# 게임 플레이
def play():
    global score, playing, special, shadow, start_x2, start_y2

    # 내 거북이 속도 설정
    tt.forward(10)
    
    # 악당거북이 방향 및 속도 설정
    # 1/5 확률로 방향 전환
    if random.randint(1,5) == 3 :
        
        # 동료거북이 방향으로 목표설정 
        if shadow == True :
            ang = te.towards(tsd.pos())
        # 내 거북이 방향으로 목표설정   
        else :
            ang = te.towards(tt.pos())
        
        # 악당거북이 방향 설정
        te.setheading(ang)
    
    # 악당거북이 속도 설정    
    speed = score + 5

    # 악당거북이 최대 속도 15    
    if speed > 15:
        speed = 15
        
    te.forward(speed)

    # 동료거북이 방향 및 속도 설정
    if shadow == True:
        
        # 동료 거북이 이동 방향
        ang2 = tsd.towards(destination_x,destination_y)
        tsd.setheading(ang2)
        # 동료 거북이 이동 속도
        tsd.forward(5)                

    # 악당거북이가 내 거북이 잡다
    if tt.distance(te) < 12 :
        text = "Score : " + str(score)
        message("Game Over", text)
        playing = False
        score = 0

    # 내 거북이가 먹이를 먹다
    if tt.distance(fd) < 12:
        score = score + 1
        tt.write(score)
        
        # 다음 먹이 위치 설정
        start_x = random.randint(-230,230)
        start_y = random.randint(-230,230)
        fd.goto(start_x, start_y)

        # 스페셜 먹이 생성
        if special == False and shadow == False:
            
            # 일반 먹이를 먹을 때 1/3 확률로 특수먹이 생성
            
            if random.randint(1,3) == 3:
                special = True
                sfd.showturtle()
                
                # 특수 먹이 출현 위치 설정
                start_x2 = random.randint(-230,230)
                start_y2 = random.randint(-230,230)
                sfd.goto(start_x2, start_y2)

    # 내 거북이가 스페셜 먹이를 먹다
    if tt.distance(sfd) < 12:
        special_food()
        shadow = True

    # 동료거북이가 잡히다
    if tsd.distance(te) < 12:
        tsd.hideturtle()
        shadow = False

    # 게임 진행
    if playing == True :
        # 0.1초 단위로 play 함수 호출
        t.ontimer(play, 100)

    # 내 거북이 경계선 처리
    if tt.xcor() > 240 :
       tt.setx(-240)

    if tt.xcor() < -240 :
       tt.setx(240)

    if tt.ycor() > 240 :
       tt.sety(-240)

    if tt.ycor() < - 240 :
       tt.sety(240)

    # 악당 거북이 경계선 처리
    if te.xcor() > 240 :
       te.setx(240)

    if te.xcor() < -240 :
       te.setx(-240)

    if te.ycor() > 240 :
       te.sety(240)

    if te.ycor() < - 240 :
       te.sety(-240)

# 게임 종료 시 메세지
def message(m1, m2) :
    t.clear()
    t.goto(0,100)
    # 메세지 m1, 움직임 False, 가운데 정렬, font name None, font size 20
    t.write(m1, False, "center", ("",20))
    t.goto (0,-100)
    t.write(m2, False, "center", ("",15))
    t.home()

# 게임판 설정
t.title("Turtle Run")
t.setup(500,500)
t.bgcolor("orange")
t.speed(0)
t.up()
t.hideturtle()

# 게임 동작 함수
t.onkeypress(turn_right,"Right")
t.onkeypress(turn_up,"Up")
t.onkeypress(turn_left,"Left")
t.onkeypress(turn_down,"Down")
t.onkeypress(start,"space")

# listen() : 키 입력 모드 실행으 입력된 키에 반응 가능
t.listen() 
message("Turtle Run", "Start : [Space]")

# 게임설명서 
root = Tk()
root.title("게임규칙")
root.geometry("470x150")
root.resizable(900,900)

txt1 = """1. 방향키로 하얀색 거북이를 이동합니다.
2. 초록색 먹이를 먹으면 점수가 올라갑니다.
3. 하얀색 먹이를 먹으면 동료거북이(빨강)가 나타나 악당거북이를 유혹합니다. 
4. 내 거북이(흰색)만 외곽선을 통과할 수 있습니다. 도움이 될 겁니다.
5. 악당거북이(검은색)를 얕보지 마세요. 시간이 지날수록 빨라집니다.
6. 악당거북이에게 잡히지 마세요. 그럼 "SPACE BAR"를 눌러서 시작하세요.

※ 이 게임은 저작권 및 바이러스가 없는 안전한 게임입니다. 가볍게 즐겨주세요.
    (made by HAZEL)
 """

lbl3 = Label(root, justify=LEFT, text = txt1)
lbl3.grid(row=0, column=1)

t.mainloop()
