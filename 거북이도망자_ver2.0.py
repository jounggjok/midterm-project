import turtle as t
import random
from tkinter import Tk, Label

# 초기값
score = 0
playing = False
special = False
shadow = False

# 초기 위치 셋팅
tt = t.Turtle()
tt.shape("turtle")
tt.color("white")
tt.speed(0)
tt.up()
tt.goto(0, 0)

te = t.Turtle()
te.shape("turtle")
te.color("black")
te.speed(0)
te.up()
te.goto(0, 200)

fd = t.Turtle()
fd.shape("circle")
fd.color("green")
fd.speed(0)
fd.up()
fd.goto(0, -200)

sfd = t.Turtle()
sfd.shape("circle")
sfd.color("white")
sfd.speed(0)
sfd.up()
sfd.goto(-300, -300)
sfd.hideturtle()

tsd = t.Turtle()
tsd.shape("turtle")
tsd.color("red")
tsd.speed(0)
tsd.up()
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
    start_x3 = -1 * start_x2
    start_y3 = -1 * start_y2
    tsd.goto(start_x3, start_y3)
    tsd.showturtle()

    # 동료 거북이 목표 방향 설정
    dstn = random.randint(1, 4)

    if dstn == 1:
        destination_x = -230
        destination_y = random.randint(-230, 230)
    elif dstn == 2:
        destination_x = 230
        destination_y = random.randint(-230, 230)
    elif dstn == 3:
        destination_x = random.randint(-230, 230)
        destination_y = -230
    else:
        destination_x = random.randint(-230, 230)
        destination_y = 230

    # 특수먹이 정보 설정
    special = False

# 게임 시작 정보
def start():
    global playing

    if not playing:
        playing = True
        t.clear()
        tt.clear()
        tt.goto(0, 0)
        play()

# 게임 플레이
def play():
    global score, playing, special, shadow, start_x2, start_y2

    tt.forward(10)

    if random.randint(1, 5) == 3:
        if shadow:
            ang = te.towards(tsd.pos())
        else:
            ang = te.towards(tt.pos())
        te.setheading(ang)

    speed = score + 5

    if speed > 15:
        speed = 15

    te.forward(speed)

    if shadow:
        ang2 = tsd.towards(destination_x, destination_y)
        tsd.setheading(ang2)
        tsd.forward(5)

    if tt.distance(te) < 12:
        text = "Score : " + str(score)
        message("Game Over", text)
        playing = False
        score = 0

    if tt.distance(fd) < 12:
        score = score + 1
        tt.write(score)

        start_x = random.randint(-230, 230)
        start_y = random.randint(-230, 230)
        fd.goto(start_x, start_y)

        if not special and not shadow:
            if random.randint(1, 3) == 3:
                special = True
                sfd.showturtle()
                start_x2 = random.randint(-230, 230)
                start_y2 = random.randint(-230, 230)
                sfd.goto(start_x2, start_y2)

    if tt.distance(sfd) < 12:
        special_food()
        shadow = True

    if tsd.distance(te) < 12:
        tsd.hideturtle()
        shadow = False

    if playing:
        t.ontimer(play, 100)

    if tt.xcor() > 400 or tt.xcor() < -400 or tt.ycor() > 400 or tt.ycor() < -400:
        tt.setx(0)
        tt.sety(0)

    if te.xcor() > 400 or te.xcor() < -400 or te.ycor() > 400 or te.ycor() < -400:
        te.setx(0)
        te.sety(200)

# 게임 종료 시 메세지
def message(m1, m2):
    t.clear()
    t.goto(0, 100)
    t.write(m1, False, "center", ("", 20))
    t.goto(0, -100)
    t.write(m2, False, "center", ("", 15))
    t.home()

# 게임판 설정
t.title("Turtle Run")
t.setup(width=800, height=800)
t.bgcolor("violet")
t.speed(1)
t.up()
t.hideturtle()

# 게임 동작 함수
t.onkeypress(turn_right, "Right")
t.onkeypress(turn_up, "Up")
t.onkeypress(turn_left, "Left")
t.onkeypress(turn_down, "Down")
t.onkeypress(start, "space")

# listen()
t.listen()
message("Turtle Run", "Start : [Space]")

# 게임설명서
root = Tk()
root.title("게임규칙")
root.geometry("470x150")
root.resizable(900, 900)

txt1 = """1. 방향키로 하얀색 거북이를 이동합니다.
2. 초록색 먹이를 먹으면 점수가 올라갑니다.
3. 하얀색 먹이를 먹으면 동료거북이(빨강)가 나타나 악당거북이를 유혹합니다.
4. 내 거북이(흰색)만 외곽선을 통과할 수 있습니다. 도움이 될 겁니다.
5. 악당거북이(검은색)를 얕보지 마세요. 시간이 지날수록 빨라집니다.
6. 악당거북이에게 잡히지 마세요. 그럼 "SPACE BAR"를 눌러서 시작하세요.
 """

lbl3 = Label(root, justify="left", text=txt1)
lbl3.grid(row=0, column=1)

t.mainloop()
