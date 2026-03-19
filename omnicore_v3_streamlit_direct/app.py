from __future__ import annotations

import io
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR / "workspace"
PROJECTS_DIR = WORKSPACE_DIR / "projects"
UPLOADS_DIR = WORKSPACE_DIR / "uploads"

for path in [WORKSPACE_DIR, PROJECTS_DIR, UPLOADS_DIR]:
    path.mkdir(parents=True, exist_ok=True)


def project_path(project_name: str) -> Path:
    safe_name = project_name.strip().replace(" ", "_")
    return PROJECTS_DIR / safe_name


def create_project(project_name: str, project_type: str) -> dict:
    pdir = project_path(project_name)
    pdir.mkdir(parents=True, exist_ok=True)
    folders = [
        "src",
        "assets",
        "assets/textures",
        "assets/audio",
        "build",
        "docs",
        "configs",
        "tests",
    ]
    for folder in folders:
        (pdir / folder).mkdir(parents=True, exist_ok=True)

    metadata = {
        "name": project_name,
        "type": project_type,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "initialized",
        "session": "session_3_streamlit_direct",
    }
    (pdir / "project.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (pdir / "README.md").write_text(
        f"# {project_name}\n\nProyecto inicial generado por OmniCore V3 Streamlit Direct.\n",
        encoding="utf-8",
    )
    return {"ok": True, "project": metadata, "path": str(pdir.relative_to(BASE_DIR))}


def save_upload(uploaded_file) -> dict:
    destination = UPLOADS_DIR / uploaded_file.name
    destination.write_bytes(uploaded_file.getvalue())
    return {"ok": True, "filename": uploaded_file.name, "path": str(destination.relative_to(BASE_DIR))}


def game_template(template: str) -> dict[str, str]:
    base_settings = '''WIDTH = 960
HEIGHT = 540
FPS = 60
TITLE = "OmniCore Game Forge"
BG_COLOR = (18, 18, 28)
ROAD_COLOR = (40, 40, 40)
LINE_COLOR = (255, 230, 120)
PLAYER_COLOR = (255, 70, 70)
ENEMY_COLOR = (90, 180, 255)
'''

    game_code = '''import random
import sys

import pygame

from settings import WIDTH, HEIGHT, FPS, TITLE, BG_COLOR, ROAD_COLOR, LINE_COLOR, PLAYER_COLOR, ENEMY_COLOR


class CarGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.reset()

    def reset(self):
        self.player = pygame.Rect(WIDTH // 2 - 30, HEIGHT - 120, 60, 100)
        self.enemies = []
        self.road_lines = [i for i in range(-40, HEIGHT, 80)]
        self.speed = 7
        self.spawn_timer = 0
        self.score = 0
        self.running = True
        self.game_over = False

    def spawn_enemy(self):
        lane_positions = [WIDTH // 2 - 140, WIDTH // 2, WIDTH // 2 + 140]
        x = random.choice(lane_positions)
        self.enemies.append(pygame.Rect(x - 30, -110, 60, 100))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.player.x += self.speed
        self.player.x = max(WIDTH // 2 - 190, min(WIDTH // 2 + 130, self.player.x))

        self.spawn_timer += 1
        if self.spawn_timer >= 35:
            self.spawn_enemy()
            self.spawn_timer = 0

        for enemy in list(self.enemies):
            enemy.y += self.speed
            if enemy.top > HEIGHT:
                self.enemies.remove(enemy)
                self.score += 1
            elif enemy.colliderect(self.player):
                self.game_over = True

        for i in range(len(self.road_lines)):
            self.road_lines[i] += self.speed
            if self.road_lines[i] > HEIGHT:
                self.road_lines[i] = -60

    def draw(self):
        self.screen.fill(BG_COLOR)
        road = pygame.Rect(WIDTH // 2 - 220, 0, 440, HEIGHT)
        pygame.draw.rect(self.screen, ROAD_COLOR, road, border_radius=6)

        for line_y in self.road_lines:
            pygame.draw.rect(self.screen, LINE_COLOR, (WIDTH // 2 - 6, line_y, 12, 50), border_radius=4)

        pygame.draw.rect(self.screen, PLAYER_COLOR, self.player, border_radius=8)
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, ENEMY_COLOR, enemy, border_radius=8)

        score_text = self.font.render(f"Score: {self.score}", True, (245, 245, 245))
        self.screen.blit(score_text, (20, 20))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            text = self.big_font.render("Game Over", True, (255, 255, 255))
            hint = self.font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and self.game_over:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

            if not self.game_over:
                self.update()
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    CarGame().run()
'''

    main_code = '''from game import CarGame


if __name__ == "__main__":
    CarGame().run()
'''

    test_code = '''from pathlib import Path


def test_main_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "src" / "main.py").exists()
'''

    readme = f'''# Session 3 Game Forge

Juego base generado por OmniCore.

## Tipo
- Template: {template}
- Engine: Pygame

## Cómo correr
```bash
pip install -r requirements.txt
python src/main.py
```

## Controles
- Flecha izquierda / derecha
- R para reiniciar
- ESC para salir
'''

    return {
        "src/settings.py": base_settings,
        "src/game.py": game_code,
        "src/main.py": main_code,
        "tests/test_smoke.py": test_code,
        "requirements.txt": "pygame==2.6.1\n",
        "README.md": readme,
    }


def generate_game(project_name: str, template: str = "car_runner") -> dict:
    pdir = project_path(project_name)
    if not pdir.exists():
        create_project(project_name, "game")
        pdir = project_path(project_name)

    files = game_template(template)
    created_files = []
    for relative_path, content in files.items():
        file_path = pdir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        created_files.append(relative_path)

    metadata_path = pdir / "project.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["status"] = "game_generated"
    metadata["template"] = template
    metadata["updated_at"] = datetime.utcnow().isoformat() + "Z"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "project": project_name,
        "template": template,
        "created_files": created_files,
        "run_command": "python src/main.py",
    }


def organize_project(project_name: str) -> dict:
    pdir = project_path(project_name)
    if not pdir.exists():
        return {"ok": False, "error": "Proyecto no encontrado."}

    moved = []
    rules = {
        ".png": "assets/textures",
        ".jpg": "assets/textures",
        ".jpeg": "assets/textures",
        ".webp": "assets/textures",
        ".mp3": "assets/audio",
        ".wav": "assets/audio",
        ".py": "src",
        ".json": "configs",
        ".md": "docs",
    }
    protected_names = {
        "project.json",
        "README.md",
        "requirements.txt",
        "Dockerfile",
        "render.yaml",
        "run_local.sh",
        "run_local.bat",
        ".gitignore",
        ".env.example",
    }

    for item in pdir.iterdir():
        if item.is_file() and item.name not in protected_names:
            target_folder = rules.get(item.suffix.lower())
            if target_folder:
                destination = pdir / target_folder / item.name
                shutil.move(str(item), str(destination))
                moved.append({"from": item.name, "to": str(destination.relative_to(pdir))})

    return {"ok": True, "moved": moved, "project": project_name}


def prepare_deploy(project_name: str) -> dict:
    pdir = project_path(project_name)
    if not pdir.exists():
        return {"ok": False, "error": "Proyecto no encontrado."}

    files_created = []
    template_files = {
        ".env.example": "APP_ENV=production\nPORT=8501\n",
        ".gitignore": "__pycache__/\n.venv/\n.env\nbuild/\n*.pyc\n",
        "docs/DEPLOY.md": (
            "# Deploy en Streamlit Cloud\n\n"
            "1. Sube este proyecto a GitHub.\n"
            "2. En Streamlit Cloud crea una app nueva.\n"
            "3. App file: app.py\n"
            "4. Python: 3.11\n"
        ),
        "Dockerfile": (
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY requirements.txt ./requirements.txt\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "COPY . .\n"
            "EXPOSE 8501\n"
            "CMD [\"streamlit\", \"run\", \"app.py\", \"--server.port=8501\", \"--server.address=0.0.0.0\"]\n"
        ),
        "render.yaml": (
            "services:\n"
            "  - type: web\n"
            "    name: omnicore-streamlit-direct\n"
            "    env: docker\n"
        ),
        "packages.txt": "libsdl2-dev\nlibsdl2-image-dev\nlibsdl2-mixer-dev\nlibsdl2-ttf-dev\n",
        "run_local.sh": "streamlit run app.py\n",
        "run_local.bat": "streamlit run app.py\n",
    }

    for relative_path, content in template_files.items():
        file_path = pdir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            files_created.append(relative_path)

    return {
        "ok": True,
        "project": project_name,
        "files_created": files_created,
        "ready_note": "Proyecto listo para deploy básico en Streamlit Cloud o Docker.",
    }


def zip_project_to_bytes(project_name: str) -> bytes:
    pdir = project_path(project_name)
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in pdir.rglob("*"):
            if file_path.is_file():
                zf.write(file_path, arcname=str(file_path.relative_to(pdir.parent)))
    memory.seek(0)
    return memory.getvalue()


def list_projects() -> list[str]:
    return sorted([p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()])


def file_tree(pdir: Path) -> list[str]:
    lines: list[str] = []
    for path in sorted(pdir.rglob("*")):
        rel = path.relative_to(pdir)
        indent = "  " * (len(rel.parts) - 1)
        prefix = "📁" if path.is_dir() else "📄"
        lines.append(f"{indent}{prefix} {rel.name}")
    return lines


st.set_page_config(page_title="OmniCore V3 Streamlit Direct", page_icon="🧠", layout="wide")
st.title("🧠 OmniCore V3 — Streamlit Direct")
st.caption("Session 3 pasada a template directo, lista para deploy sin backend aparte")

with st.sidebar:
    st.success("Modo directo activo")
    st.write({
        "frontend": "Streamlit",
        "backend": "Embebido en app.py",
        "deploy": "Streamlit Cloud / Docker / Render",
        "workspace": str(WORKSPACE_DIR.relative_to(BASE_DIR)),
    })
    st.divider()
    project_name = st.text_input("Nombre del proyecto", value="mi_juego_streamlit")
    project_type = st.selectbox("Tipo", ["game", "app", "system"])
    template = st.selectbox("Template", ["car_runner"])

    if st.button("Crear proyecto", use_container_width=True):
        st.session_state["last_result"] = create_project(project_name, project_type)
    if st.button("Generar juego", use_container_width=True):
        st.session_state["last_result"] = generate_game(project_name, template)
    if st.button("Organizar proyecto", use_container_width=True):
        st.session_state["last_result"] = organize_project(project_name)
    if st.button("Preparar deploy", use_container_width=True):
        st.session_state["last_result"] = prepare_deploy(project_name)

uploaded_file = st.file_uploader("Subir archivo al workspace", type=None)
if uploaded_file is not None:
    st.info(f"Archivo listo para guardar: {uploaded_file.name}")
    if st.button("Guardar archivo subido"):
        st.session_state["last_result"] = save_upload(uploaded_file)

left, right = st.columns([1.3, 1])
with left:
    st.subheader("Resultado")
    result = st.session_state.get("last_result", {"status": "Sin acciones todavía."})
    st.json(result)

    st.subheader("Chat local")
    prompt = st.text_area(
        "Dile algo a OmniCore",
        value="Créame un juego de carros básico y déjalo listo para deploy.",
        height=100,
    )
    if st.button("Procesar prompt"):
        lower = prompt.lower()
        if "juego" in lower or "carro" in lower:
            create_project(project_name, "game")
            generate_game(project_name, template)
            prepare_deploy(project_name)
            st.session_state["last_result"] = {
                "ok": True,
                "prompt": prompt,
                "action": "create_game_pipeline",
                "project": project_name,
                "message": "Proyecto creado, juego generado y deploy preparado.",
            }
        else:
            st.session_state["last_result"] = {
                "ok": True,
                "prompt": prompt,
                "message": "Session 3 entendió tu mensaje. Para crear juego usa palabras como juego, carro o deploy.",
            }
        st.rerun()

with right:
    st.subheader("Proyectos")
    projects = list_projects()
    selected = st.selectbox("Selecciona proyecto", projects if projects else ["(sin proyectos)"])
    if projects:
        pdir = project_path(selected)
        st.code("\n".join(file_tree(pdir)) or "Vacío")
        zip_bytes = zip_project_to_bytes(selected)
        st.download_button(
            "Descargar ZIP del proyecto",
            data=zip_bytes,
            file_name=f"{selected}_streamlit_direct.zip",
            mime="application/zip",
            use_container_width=True,
        )

st.divider()
st.subheader("Qué trae este template directo")
st.markdown(
    """
- Todo corre dentro de `app.py`
- No necesita FastAPI ni `uvicorn`
- Puede subirse directo a Streamlit Cloud
- Genera proyecto, juego base, archivos de deploy y ZIP
- Mantiene la Session 3 activa con `Game Forge` básico
    """
)
