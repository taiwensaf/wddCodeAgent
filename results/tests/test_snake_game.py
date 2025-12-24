import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
source_path = os.path.join(project_root, 'results/generated_code')
sys.path.insert(0, source_path)

from snake_game import *

import pytest

@pytest.fixture
def game_state():
    return {
        'snake_list': [[100, 50], [90, 50], [80, 50]],
        'foodx': 200,
        'foody': 300,
        'game_over': False,
        'game_close': False,
        'x1_change': 0,
        'y1_change': 0,
        'length_of_snake': len([[100, 50], [90, 50], [80, 50]]),
        'score': 0
    }

@pytest.mark.parametrize('direction, expected', [
    ('LEFT', [[90, 50], [100, 50], [90, 50]]),
    ('RIGHT', [[110, 50], [100, 50], [110, 50]]),
    ('UP', [[100, 40], [100, 50], [100, 40]]),
    ('DOWN', [[100, 60], [100, 50], [100, 60]])
])
def test_move_snake(direction, expected, game_state):
    snake_list = move_snake(snake_block_size, game_state['snake_list'], {'LEFT': -snake_block_size, 'RIGHT': snake_block_size, 'UP': -snake_block_size, 'DOWN': snake_block_size}[direction], 0)
    assert snake_list == expected

def test_check_collision(game_state):
    collision = check_collision(game_state['snake_list'])
    assert collision is False

def test_generate_food(game_state):
    foodx, foody = generate_food(game_state['snake_list'], WINDOW_WIDTH, WINDOW_HEIGHT, snake_block_size)
    assert [foodx, foody] not in game_state['snake_list']

def test_update_score(game_state):
    score = update_score(game_state['score'], 'eat')
    assert score == 1
