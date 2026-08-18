from pathlib import Path
import zipfile

project = Path("/mnt/data/streamlit_brick_breaker")
project.mkdir(exist_ok=True)

app = r'''import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌깨기",
    page_icon="🧱",
    layout="centered",
)

st.title("🧱 벽돌깨기")
st.caption("게임 영역을 클릭한 뒤 ← → 키로 패들을 움직이세요. 스페이스바로 시작/일시정지할 수 있습니다.")

html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  html, body {
    margin: 0;
    padding: 0;
    background: #111827;
    font-family: Arial, sans-serif;
    overflow: hidden;
  }
  #wrap {
    width: 100%;
    display: flex;
    justify-content: center;
  }
  canvas {
    width: min(100%, 760px);
    height: auto;
    background: #0b1020;
    border-radius: 14px;
    border: 2px solid #374151;
    display: block;
  }
</style>
</head>
<body>
<div id="wrap">
<canvas id="game" width="760" height="620" tabindex="0"></canvas>
</div>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

let score = 0;
let lives = 3;
let level = 1;
let running = false;
let gameOver = false;
let won = false;

const paddle = {
  width: 115,
  height: 14,
  x: canvas.width / 2 - 57.5,
  y: canvas.height - 42,
  speed: 8,
  left: false,
  right: false
};

const ball = {
  x: canvas.width / 2,
  y: canvas.height - 65,
  r: 9,
  dx: 4,
  dy: -4
};

let bricks = [];
const rows = 6;
const cols = 10;
const brickW = 63;
const brickH = 23;
const gap = 9;
const startX = 28;
const startY = 65;

function makeBricks() {
  bricks = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      bricks.push({
        x: startX + c * (brickW + gap),
        y: startY + r * (brickH + gap),
        w: brickW,
        h: brickH,
        alive: true,
        hp: level >= 3 && r < 2 ? 2 : 1
      });
    }
  }
}

function resetBall() {
  ball.x = canvas.width / 2;
  ball.y = canvas.height - 65;
  const speed = 4 + (level - 1) * 0.6;
  ball.dx = (Math.random() < 0.5 ? -1 : 1) * speed;
  ball.dy = -speed;
}

function resetGame() {
  score = 0;
  lives = 3;
  level = 1;
  running = false;
  gameOver = false;
  won = false;
  paddle.x = canvas.width / 2 - paddle.width / 2;
  makeBricks();
  resetBall();
}

function nextLevel() {
  level++;
  if (level > 4) {
    won = true;
    running = false;
    return;
  }
  makeBricks();
  resetBall();
  running = false;
}

function drawRoundedRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, r);
  ctx.fill();
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // background
  const g = ctx.createLinearGradient(0, 0, 0, canvas.height);
  g.addColorStop(0, "#111827");
  g.addColorStop(1, "#0b1020");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // HUD
  ctx.fillStyle = "#f9fafb";
  ctx.font = "bold 19px Arial";
  ctx.fillText("점수: " + score, 25, 32);
  ctx.fillText("목숨: " + lives, 320, 32);
  ctx.fillText("레벨: " + level, 650, 32);

  // bricks
  bricks.forEach((b, i) => {
    if (!b.alive) return;
    const hue = (i * 31 + level * 45) % 360;
    ctx.fillStyle = `hsl(${hue}, 75%, 58%)`;
    drawRoundedRect(b.x, b.y, b.w, b.h, 5);

    if (b.hp > 1) {
      ctx.fillStyle = "rgba(255,255,255,0.75)";
      ctx.font = "bold 12px Arial";
      ctx.fillText("2", b.x + b.w / 2 - 4, b.y + 16);
    }
  });

  // paddle
  ctx.fillStyle = "#f8fafc";
  drawRoundedRect(paddle.x, paddle.y, paddle.width, paddle.height, 7);

  // ball
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
  ctx.fillStyle = "#ffffff";
  ctx.fill();

  if (!running && !gameOver && !won) {
    overlay("SPACE", "스페이스바를 눌러 시작");
  }

  if (gameOver) {
    overlay("GAME OVER", "R 키로 다시 시작");
  }

  if (won) {
    overlay("YOU WIN!", "R 키로 다시 시작");
  }
}

function overlay(title, sub) {
  ctx.fillStyle = "rgba(0,0,0,0.62)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#fff";
  ctx.textAlign = "center";
  ctx.font = "bold 48px Arial";
  ctx.fillText(title, canvas.width / 2, canvas.height / 2 - 20);

  ctx.font = "20px Arial";
  ctx.fillStyle = "#d1d5db";
  ctx.fillText(sub, canvas.width / 2, canvas.height / 2 + 28);
  ctx.textAlign = "left";
}

function update() {
  if (!running || gameOver || won) return;

  if (paddle.left) paddle.x -= paddle.speed;
  if (paddle.right) paddle.x += paddle.speed;

  paddle.x = Math.max(0, Math.min(canvas.width - paddle.width, paddle.x));

  ball.x += ball.dx;
  ball.y += ball.dy;

  // walls
  if (ball.x - ball.r <= 0 || ball.x + ball.r >= canvas.width) {
    ball.dx *= -1;
    ball.x = Math.max(ball.r, Math.min(canvas.width - ball.r, ball.x));
  }

  if (ball.y - ball.r <= 45) {
    ball.dy *= -1;
    ball.y = 45 + ball.r;
  }

  // paddle collision
  if (
    ball.y + ball.r >= paddle.y &&
    ball.y - ball.r <= paddle.y + paddle.height &&
    ball.x >= paddle.x &&
    ball.x <= paddle.x + paddle.width &&
    ball.dy > 0
  ) {
    const hit = (ball.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2);
    const speed = Math.min(9, Math.sqrt(ball.dx * ball.dx + ball.dy * ball.dy) + 0.15);
    ball.dx = hit * speed;
    ball.dy = -Math.sqrt(Math.max(4, speed * speed - ball.dx * ball.dx));
    ball.y = paddle.y - ball.r - 1;
  }

  // brick collisions
  for (const b of bricks) {
    if (!b.alive) continue;

    const closestX = Math.max(b.x, Math.min(ball.x, b.x + b.w));
    const closestY = Math.max(b.y, Math.min(ball.y, b.y + b.h));
    const dx = ball.x - closestX;
    const dy = ball.y - closestY;

    if (dx * dx + dy * dy <= ball.r * ball.r) {
      b.hp--;
      if (b.hp <= 0) {
        b.alive = false;
        score += 10 * level;
      } else {
        score += 5;
      }

      // Determine reflection direction
      if (Math.abs(dx) > Math.abs(dy)) ball.dx *= -1;
      else ball.dy *= -1;
      break;
    }
  }

  if (bricks.every(b => !b.alive)) {
    nextLevel();
    return;
  }

  // bottom
  if (ball.y - ball.r > canvas.height) {
    lives--;
    if (lives <= 0) {
      gameOver = true;
      running = false;
    } else {
      resetBall();
    }
  }
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

window.addEventListener("keydown", (e) => {
  if (["ArrowLeft", "ArrowRight", " "].includes(e.key)) e.preventDefault();

  if (e.key === "ArrowLeft") paddle.left = true;
  if (e.key === "ArrowRight") paddle.right = true;

  if (e.code === "Space") {
    if (!gameOver && !won) running = !running;
  }

  if (e.key.toLowerCase() === "r") {
    resetGame();
  }
});

window.addEventListener("keyup", (e) => {
  if (e.key === "ArrowLeft") paddle.left = false;
  if (e.key === "ArrowRight") paddle.right = false;
});

canvas.addEventListener("click", () => canvas.focus());

resetGame();
loop();
</script>
</body>
</html>
"""

components.html(html, height=660, scrolling=False)

st.info("💡 게임이 안 움직이면 게임 화면을 한 번 클릭한 후 키보드를 사용하세요.")
'''

requirements = """streamlit>=1.36,<2
"""

readme = """# Streamlit 벽돌깨기

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
