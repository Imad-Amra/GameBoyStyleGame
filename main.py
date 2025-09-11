from tkinter import *
from turtle import *
from math import radians, sin, cos
import random

is_on = True
island_list = []
score = 0

window = Tk()
window.title("Game Boy")
window.config(bg="gray")
window.geometry("312x600")

# Frame around canvas
frame = Frame(window, bg="black", bd=5, relief="sunken")
frame.pack()

canvas = Canvas(frame, width=300, height=300, highlightthickness=0)
canvas.pack(padx=0, pady=0)

# Used when creating turtle inside canvas
screen = TurtleScreen(canvas)
screen.bgpic("images/bg_sea.gif")

# ------------------------------ Score Setup ------------------------------------ #

def update_score(s):
    s.clear()
    s.write(f"Score: {score}", align="center", font=("Courier", 20, "bold"))

scoreboard = RawTurtle(screen)
scoreboard.color("black")
scoreboard.hideturtle()
scoreboard.penup()
scoreboard.speed(0)
scoreboard.goto(3, 120)
update_score(scoreboard)

# ------------------------------ Map Builder ------------------------------------ #

def get_coords(event):
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    turtle_x = event.x - canvas_width // 2
    turtle_y = canvas_height // 2 - event.y
    print(f"Turtle coords: ({turtle_x}, {turtle_y})")
canvas.bind("<Button-1>", get_coords)

def place_island(image, coords, width, height):
    screen.register_shape(f"images/islands/{image}")
    island = RawTurtle(screen)
    island.shape(f"images/islands/{image}")
    island.penup()
    island.goto(coords)
    island.speed()
    island_list.append({
        "turtle": island,
        "width": width,
        "height": height
    })

place_island("island3.gif", (-50, -108), width=150, height=10)
place_island("island2.gif", (-35, 85), width=107, height=25)
place_island("island1.gif", (79, -27), width=80, height=20)

# ------------------------------ Player Setup ------------------------------------ #

# Used to put object in custom canvas/screen
player = RawTurtle(screen)
player.penup()
screen.register_shape("images/luffy.gif")
player.shape("images/luffy.gif")

def reset_player():
    player.goto(0, 0)

# ------------------------------ Enemy Setup ------------------------------------ #

enemy = RawTurtle(screen)
screen.register_shape("images/navy.gif")
enemy.shape("images/navy.gif")
enemy.penup()
enemy.goto(100, 100)

game_over = RawTurtle(screen)
game_over.hideturtle()

def update_enemy():
    if not is_on:
        return

    px, py = player.pos()
    angle = enemy.towards(px, py)

    new_x = enemy.xcor() + 2 * cos(radians(angle))
    new_y = enemy.ycor() + 2 * sin(radians(angle))

    blocked = False
    for island_data in island_list:
        island = island_data["turtle"]
        half_w = island_data["width"] / 2
        half_h = island_data["height"] / 2

        dx = abs(new_x - island.xcor())
        dy = abs(new_y - island.ycor())

        if dx < half_w and dy < half_h:
            blocked = True
            break

    if blocked or not (-140 < new_x < 140 and -140 < new_y < 140):
        enemy.setheading(random.randint(1, 359))
        enemy.forward(5)
    else:
        enemy.forward(5)
        enemy.setheading(angle)

    screen.ontimer(update_enemy, 100)

def enemy_collision():
    global is_on
    if player.distance(enemy) < 12:
        scoreboard.goto(0, -25)
        update_score(scoreboard)

        try:
            with open("highscore.txt", mode="r") as high:
                highscore = int(high.read())
        except FileNotFoundError:
            highscore = 0

        if score > highscore:
            highscore = score
            with open("highscore.txt", mode="w") as high:
                high.write(str(highscore))

        scoreboard.goto(0, -50)
        scoreboard.write(f"High Score: {highscore}", align="center", font=("Courier", 20, "bold"))

        game_over.goto(0, 0)
        game_over.write("GAME OVER", align="center", font=("Courier", 20, "bold"))
        is_on = False
    if is_on:
        screen.ontimer(enemy_collision, 100)

def reset_enemy():
    enemy.goto(100, 100)

update_enemy()
enemy_collision()

# ------------------------------ Gold Setup ------------------------------------ #

def in_forbidden(x, y):
    if -145 <= x <= 38 and -133 <= y <= -127:
        return True
    if 20 <= x <= 143 and y == -46:
        return True
    if -114 <= x <= 46 and 65 <= y <= 66:
        return True
    if -35 <= x <= -34 and 52 <= y <= 119:
        return True
    if 77 <= x <= 78 and -47 <= y <= -6:
        return True
    return False

def refresh_gold(g):
    ran_x = random.randint(-140, 140)
    ran_y = random.randint(-140, 140)

    if not in_forbidden(ran_x, ran_y):
        g.goto(ran_x, ran_y)

def gold_collision(g, p):
    return p.distance(g) < 20

gold = RawTurtle(screen)
gold.shape("circle")
gold.color("gold")
gold.penup()
gold.speed(0)
gold.shapesize(0.5)
refresh_gold(gold)

def gold_loop():
    global score
    if gold_collision(gold, player):
        refresh_gold(gold)
        score += 1
        update_score(scoreboard)
    screen.update()
    screen.ontimer(gold_loop, 30)

def  reset_gold():
    gold.goto(random.randint(-140, 140), random.randint(-140, 140))

gold_loop()

# ------------------------------ UI Setup ------------------------------------ #

def move(dx, dy):
    if not is_on:
        return

    new_x = player.xcor() + dx
    new_y = player.ycor() + dy

    if not (-140 < new_x < 140 and -140 < new_y < 140):
        return

    for island_data in island_list:
        island = island_data["turtle"]
        half_w = island_data["width"] / 2
        half_h = island_data["height"] / 2

        dx = abs(new_x - island.xcor())
        dy = abs(new_y - island.ycor())

        if dx < half_w and dy < half_h:
            return

    player.goto(new_x, new_y)

def up_arrow_clicked():
    move(0, 10)

def down_arrow_clicked():
    move(0, -10)

def right_arrow_clicked():
    move(10, 0)

def left_arrow_clicked():
    move(-10, 0)

def reset_game():
    global score, is_on
    score = 0
    is_on = True

    scoreboard.clear()
    game_over.clear()

    reset_player()
    reset_enemy()
    reset_gold()

    scoreboard.goto(3, 120)
    update_score(scoreboard)

    enemy_collision()
    update_enemy()

screen.listen()
screen.onkey(up_arrow_clicked, "Up")
screen.onkey(down_arrow_clicked, "Down")
screen.onkey(left_arrow_clicked, "Left")
screen.onkey(right_arrow_clicked, "Right")

reset = Button(text="reset", bg="gray", command=reset_game)
reset.place(x=200, y=360)

up_arrow_image = PhotoImage(file="images/arrows/up_arrow.png")
up_arrow = Button(image=up_arrow_image, bg="gray", command=up_arrow_clicked)
up_arrow.place(x=60, y=360)

down_arrow_image = PhotoImage(file="images/arrows/down_arrow.png")
down_arrow = Button(image=down_arrow_image, bg="gray", command=down_arrow_clicked)
down_arrow.place(x=60, y=480)

left_arrow_image = PhotoImage(file="images/arrows/left_arrow.png")
left_arrow = Button(image=left_arrow_image, bg="gray", command=left_arrow_clicked)
left_arrow.place(x=5, y=425)

right_arrow_image = PhotoImage(file="images/arrows/right_arrow.png")
right_arrow = Button(image=right_arrow_image, bg="gray", command=right_arrow_clicked)
right_arrow.place(x=115, y=425)

window.mainloop()