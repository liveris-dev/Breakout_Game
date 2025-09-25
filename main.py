import tkinter as tk
import turtle
import random
import time
import winsound

# Geometry Configuration:
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 720
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_Y = -280
PADDLE_SPEED = 35
BALL_SPEED = 6
BRICK_ROWS = 7
BRICK_COLUMNS = 8
BRICK_WIDTH = 70
BRICK_HEIGHT = 24
BRICK_TOP = 200
BRICK_GAP = 6

class BreakoutGame:
    def __init__(self, root):
        self.root = root
        root.title("Breakout Game")

        # Create top frame
        game_frame = tk.Frame(root)
        game_frame.pack(side=tk.TOP, fill=tk.X)

        self.score_var = tk.StringVar(value="Score: 0")
        self.lives_var = tk.StringVar(value="Lives: 3")
        self.status_var = tk.StringVar(value="Press ← → to move. Press r to restart.")
        self.sound_button = tk.Button(self.root, text="Sound: On",font=("Arial", 12), command=self.toggle_sound)
        self.sound_button.pack(side="top", pady=5)
        tk.Label(game_frame, textvariable=self.score_var, font=("Arial", 12)).pack(side="left", padx=8)
        tk.Label(game_frame, textvariable=self.lives_var, font=("Arial", 12)).pack(side="left", padx=8)
        tk.Label(game_frame, textvariable=self.status_var, font=("Arial", 10)).pack(side="right", padx=8)

        # Create canvas and embed turtle screen
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.canvas.pack()
        self.screen = turtle.TurtleScreen(self.canvas)
        # Animation turn off
        self.screen.tracer(0)

        # Create Turtles (paddle, ball) as "RawTurtle" to be able to attach turtles in the canvas turtlescreen
        self.paddle = turtle.RawTurtle(self.screen)
        self.paddle.hideturtle()
        self.paddle.penup()
        self.paddle.shape("square")
        self.paddle.shapesize(stretch_wid=PADDLE_HEIGHT/20, stretch_len=PADDLE_WIDTH/20)
        self.paddle.color("black")
        self.paddle.goto(0, PADDLE_Y)
        self.paddle.showturtle()

        self.ball = turtle.RawTurtle(self.screen)
        self.ball.shape("circle")
        self.ball.color("red")
        self.ball.penup()
        self.ball_speed_x = BALL_SPEED * random.choice([-1, 1])
        self.ball_speed_y = BALL_SPEED
        self.reset_ball_position()

        self.score = 0
        self.lives = 3
        self.is_playing = True
        self.game_over = False
        self.sound_on = True

        self.bricks = []
        self.create_bricks()

        root.bind("<Left>", self.move_left)
        root.bind("<Right>", self.move_right)
        root.bind("<Motion>", self.mouse_move)
        root.bind("r", self.restart)
        root.bind("q", self.quit_app)

        self.loop()


    def reset_ball_position(self):
        self.ball.goto(0, PADDLE_Y + 30)
        self.ball_speed_x = BALL_SPEED * random.choice([-1, 1])
        self.ball_speed_y = BALL_SPEED

    def create_bricks(self):
        # clear existing
        for b in self.bricks:
            try:
                b.hideturtle()
                b.clear()
                b._destroy()
            except Exception:
                pass
        self.bricks = []

        start_x = -((BRICK_COLUMNS * (BRICK_WIDTH + BRICK_GAP)) - BRICK_GAP) / 2 + BRICK_WIDTH/2
        y = BRICK_TOP

        colors = ["#ff073a", "#ff7f50", "#f8f32b", "#04e762", "#00f5d4", "#845ec2", "#d65db1"]
        for row in range(BRICK_ROWS):
            x = start_x
            for col in range(BRICK_COLUMNS):
                brick = turtle.RawTurtle(self.screen)
                brick.hideturtle()
                brick.penup()
                brick.shape("square")
                brick.shapesize(stretch_wid=BRICK_HEIGHT/20, stretch_len=BRICK_WIDTH/20)
                brick.color(colors[row % len(colors)])
                brick.goto(x, y)
                brick.showturtle()
                # store brick as dict with turtle and dimensions
                self.bricks.append({"t": brick, "w": BRICK_WIDTH, "h": BRICK_HEIGHT})
                x += BRICK_WIDTH + BRICK_GAP
            y -= BRICK_HEIGHT + BRICK_GAP

    # Paddle movement(keyboard and mouse)
    def move_left(self, event=None):
        new_x = self.paddle.xcor() - PADDLE_SPEED
        left_limit = -WINDOW_WIDTH / 2 + PADDLE_WIDTH / 2
        if new_x < left_limit:
            new_x = left_limit
        self.paddle.setx(new_x)

    def move_right(self, event=None):
        new_x = self.paddle.xcor() + PADDLE_SPEED
        right_limit = WINDOW_WIDTH / 2 - PADDLE_WIDTH / 2
        if new_x > right_limit:
            new_x = right_limit
        self.paddle.setx(new_x)

    def mouse_move(self, event):
        # Convert Tkinter x (0..window_width) to Turtle x (-window_width/2 .. +window_width/2)
        turtle_x = event.x - self.canvas.winfo_width() // 2
        # Move paddle (center it under the mouse)
        self.paddle.setx(turtle_x)
        if self.paddle.xcor() < -250:
            self.paddle.setx(-250)
        if self.paddle.xcor() > 250:
            self.paddle.setx(250)

    # Collision
    def check_wall_collisions(self):
        x, y = self.ball.xcor(), self.ball.ycor()
        # side walls
        if x <= -WINDOW_WIDTH/2 + 9 or x >= WINDOW_WIDTH/2 - 9:
            self.ball_speed_x *= -1
        # top wall
        if y >= WINDOW_HEIGHT/2 - 8:
            self.ball_speed_y *= -1
        # bottom wall
        if y <= -WINDOW_HEIGHT/2:
            self.lives -= 1
            self.lives_var.set(f"Lives: {self.lives}")
            if self.lives <= 0:
                self.game_over = True
                self.status_var.set("Game Over! Press r to restart.")
                self.is_playing = False
            else:
                self.reset_ball_position()
                self.screen.update()
                time.sleep(0.5)

    def check_paddle_collision(self):
        bx, by = self.ball.xcor(), self.ball.ycor()
        px, py = self.paddle.xcor(), self.paddle.ycor()
        if (abs(bx - px) < (PADDLE_WIDTH/2 + 9)) and (by - py) < (PADDLE_HEIGHT/2 + 9) and (by < py + 30):
            # reflect Y
            self.ball_speed_y = abs(self.ball_speed_y)
            # change x speed depending on where the ball hit the paddle
            offset = (bx - px) / (PADDLE_WIDTH/2)  # -1 .. 1
            self.ball_speed_x = BALL_SPEED * 2 * offset
            if self.sound_on:
                winsound.Beep(500,20)

    def check_brick_collisions(self):
        bx, by = self.ball.xcor(), self.ball.ycor()
        remove_list = []
        for brick in self.bricks:
            b = brick["t"]
            bw, bh = brick["w"], brick["h"]
            if (abs(bx - b.xcor()) < (bw/2 + 9)) and (abs(by - b.ycor()) < (bh/2 + 9)):
                # ball hits the brick
                if self.sound_on:
                    winsound.Beep(800, 20)
                try:
                    b.hideturtle()
                    b.clear()
                except Exception:
                    pass
                remove_list.append(brick)
                self.ball_speed_y *= -1
                self.score += 10
                self.score_var.set(f"Score: {self.score}")
                break

        for r in remove_list:
            if r in self.bricks:
                self.bricks.remove(r)

        # win condition
        if not self.bricks:
            self.is_playing = False
            self.status_var.set("You Win! Press r to play again.")

    def loop(self):
        if not self.game_over and self.is_playing:
            # move ball
            self.ball.setx(self.ball.xcor() + self.ball_speed_x)
            self.ball.sety(self.ball.ycor() + self.ball_speed_y)

            self.check_wall_collisions()
            self.check_paddle_collision()
            self.check_brick_collisions()

            self.screen.update()

        # schedule next frame after 16ms
        self.root.after(16, self.loop)

    def restart(self, event=None):
        self.score = 0
        self.lives = 3
        self.score_var.set("Score: 0")
        self.lives_var.set("Lives: 3")
        self.status_var.set("Press ← → to move. Press r to restart.")
        self.game_over = False
        self.is_playing = True
        # reset paddle and ball
        self.paddle.setx(0)
        self.reset_ball_position()
        # recreate bricks
        self.create_bricks()
        self.screen.update()

    def quit_app(self, event=None):
        root.quit()

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        if self.sound_on:
            self.sound_button.config(text="Sound: On")
        else:
            self.sound_button.config(text="Sound: Off")

if __name__ == "__main__":
    root = tk.Tk()
    game = BreakoutGame(root)
    root.mainloop()
