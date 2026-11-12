"""Debug script for area program analysis."""
import sys
sys.path.insert(0, '.')

from app.services.planning.area_program import build_area_program
from app.services.planning.engine import solve_layout

# Test 1: 50x80 south 2-floor WITH parking and staircase
ctx = {
    'plot_width': 50, 'plot_length': 80, 'facing': 'south',
    'floors': 2, 'bedrooms': 3, 'bathrooms': 3,
    'kitchens': 1, 'living_rooms': 1, 'balconies': 1,
    'parking': 1,
    'setbacks': {'front': 4, 'rear': 4, 'left': 3, 'right': 3}
}
reqs = [
    {'room_type': 'living_room', 'count': 1},
    {'room_type': 'kitchen', 'count': 1},
    {'room_type': 'bedroom', 'count': 3},
    {'room_type': 'bathroom', 'count': 3},
    {'room_type': 'staircase', 'count': 1},
]
try:
    prog = build_area_program(ctx, reqs)
    print('buildable_width:', prog['buildable_width'], 'buildable_length:', prog['buildable_length'])
    print('floors:', list(prog['floors_program'].keys()))
    for lvl, rooms in prog['floors_program'].items():
        total_min = sum(r['specs']['min_area'] for r in rooms)
        print(f'Floor {lvl}: {len(rooms)} rooms, min_area_total={total_min}')
        for r in rooms:
            rtype = r['type']
            sw = r['specs']['min_w']
            sh = r['specs']['min_h']
            sa = r['specs']['min_area']
            print(f'  {rtype}: min_w={sw} min_h={sh} min_area={sa}')
except Exception as e:
    print('build_area_program ERROR:', e)

# Test 2: 50x80 south 2-floor NO parking, just 2 bedrooms
ctx2 = {
    'plot_width': 50, 'plot_length': 80, 'facing': 'south',
    'floors': 2, 'bedrooms': 2, 'bathrooms': 2,
    'kitchens': 1, 'living_rooms': 1, 'balconies': 0,
    'parking': 0,
    'setbacks': {'front': 4, 'rear': 4, 'left': 3, 'right': 3}
}
reqs2 = [
    {'room_type': 'living_room', 'count': 1},
    {'room_type': 'kitchen', 'count': 1},
    {'room_type': 'bedroom', 'count': 2},
    {'room_type': 'bathroom', 'count': 2},
    {'room_type': 'staircase', 'count': 1},
]
try:
    res2 = solve_layout(ctx2, reqs2, use_gemini=False)
    print('\nTest2 SUCCESS:', res2['planner_source'], 'floors:', list(res2['floors'].keys()))
except Exception as e:
    print('\nTest2 FAILED:', e)
