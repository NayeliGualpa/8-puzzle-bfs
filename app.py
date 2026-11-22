from collections import deque
from typing import Dict, List, Optional, Tuple
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder=".")

GOAL_STATE: Tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6, 7, 8)
GOAL_POSITIONS: Dict[int, Tuple[int, int]] = {
    tile: (idx // 3, idx % 3)
    for idx, tile in enumerate(GOAL_STATE)
    if tile != 0
}


def count_inversions(state: Tuple[int, ...]) -> int:
    tiles = [x for x in state if x != 0]
    inv = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inv += 1
    return inv


def is_solvable(state: Tuple[int, ...], goal: Tuple[int, ...] = GOAL_STATE) -> bool:
    return (count_inversions(state) % 2) == (count_inversions(goal) % 2)


def manhattan_distance(state: Tuple[int, ...]) -> int:
    total = 0
    for idx, tile in enumerate(state):
        if tile != 0:
            row, col = divmod(idx, 3)
            goal_row, goal_col = GOAL_POSITIONS[tile]
            total += abs(row - goal_row) + abs(col - goal_col)
    return total


def get_neighbors(state: Tuple[int, ...]) -> List[Tuple[int, ...]]:
    blank_idx = state.index(0)
    row, col = divmod(blank_idx, 3)
    neighbors: List[Tuple[int, ...]] = []

    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_idx = new_row * 3 + new_col
            state_list = list(state)
            state_list[blank_idx], state_list[new_idx] = (
                state_list[new_idx],
                state_list[blank_idx],
            )
            neighbors.append(tuple(state_list))

    return neighbors


def reconstruct_path(
    came_from: Dict[Tuple[int, ...], Optional[Tuple[int, ...]]],
    goal: Tuple[int, ...],
) -> List[Tuple[int, ...]]:
    path: List[Tuple[int, ...]] = []
    current: Optional[Tuple[int, ...]] = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def describe_move(prev_state: Tuple[int, ...], curr_state: Tuple[int, ...]) -> str:
    prev_zero = prev_state.index(0)
    curr_zero = curr_state.index(0)
    moved_tile = prev_state[curr_zero]

    pr, pc = divmod(prev_zero, 3)
    cr, cc = divmod(curr_zero, 3)

    if cr < pr:
        direction = "abajo"
    elif cr > pr:
        direction = "arriba"
    elif cc < pc:
        direction = "derecha"
    else:
        direction = "izquierda"

    return f"Mover ficha {moved_tile} hacia {direction}"


def bfs(start: Tuple[int, ...], goal: Tuple[int, ...] = GOAL_STATE) -> dict:
    if start == goal:
        return {
            "found": True,
            "iterations": 0,
            "path": [list(start)],
            "steps": [
                {
                    "step": 0,
                    "action": "Estado inicial",
                    "h": manhattan_distance(start),
                    "state": list(start),
                }
            ],
        }

    frontier = deque([start])
    visited = {start}
    came_from: Dict[Tuple[int, ...], Optional[Tuple[int, ...]]] = {start: None}
    iterations = 0

    while frontier:
        iterations += 1
        current = frontier.popleft()

        if current == goal:
            raw_path = reconstruct_path(came_from, goal)
            steps = []
            for idx, st in enumerate(raw_path):
                action = "Estado inicial" if idx == 0 else describe_move(raw_path[idx - 1], st)
                steps.append({
                    "step": idx,
                    "action": action,
                    "h": manhattan_distance(st),
                    "state": list(st),
                })
            return {
                "found": True,
                "iterations": iterations,
                "path": [list(p) for p in raw_path],
                "steps": steps,
            }

        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                frontier.append(neighbor)

    return {"found": False, "iterations": iterations, "path": [], "steps": []}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/solve", methods=["POST"])
def api_solve():
    data = request.get_json(silent=True) or {}
    raw_state = data.get("state")

    if not isinstance(raw_state, list) or len(raw_state) != 9:
        return jsonify({"error": "Debes enviar una lista de 9 números del 0 al 8."}), 400

    try:
        state = tuple(int(x) for x in raw_state)
    except (ValueError, TypeError):
        return jsonify({"error": "Todos los valores deben ser enteros del 0 al 8."}), 400

    if sorted(state) != list(range(9)):
        return jsonify({"error": "El tablero debe contener exactamente los números 0..8 sin repetir."}), 400

    inv = count_inversions(state)
    solvable = is_solvable(state, GOAL_STATE)

    if not solvable:
        return jsonify({
            "solvable": False,
            "inversions": inv,
            "message": f"No resoluble: {inv} inversiones (impar) frente a 0 de la meta (par).",
        })

    result = bfs(state, GOAL_STATE)
    result["solvable"] = True
    result["inversions"] = inv
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)