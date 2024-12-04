#!/usr/bin/env python 
import math
from array import array

BOARD_WIDTH = 24
BOARD_HEIGHT = 12
LINE_LENGTH = 5


# algo needs to balance between creating more options for us + blocking other player
# weights for choices
# if we can make 4: 100000 points
# if we can block 4: 10000 points
# if we can make 3: 1000 points
# if we can block 3: 1000 points
# if we can make 2: 10 points
# if we can block 2: 10 points

SCORE_LOG = lambda i: math.exp(math.log(1000)/(6*i+1))
SCORE_BASIC = [round(SCORE_LOG(i/LINE_LENGTH)) for i in reversed(range(LINE_LENGTH))]
SCORE_PLAYER_MAP = SCORE_BASIC + [100000]
SCORE_OPPONENT_MAP = SCORE_BASIC + [10000]


def add_token(state: array[int], column: int, token: int) -> array[int]:
    result = array('B', state.tobytes())
    if column >= BOARD_WIDTH:
        raise ValueError("column out of range")
    if result[0 + column] != 0:
        raise ValueError("column full")
    for i in range(BOARD_HEIGHT - 1, -1, -1):
        if result[i*BOARD_WIDTH + column] == 0:
            result[i*BOARD_WIDTH + column] = token
    return result


def get_y_pos(state: array[int]) -> list[int]:
    result = []
    for x in range(BOARD_WIDTH):
        dest = BOARD_HEIGHT - 1
        for y in range(BOARD_HEIGHT):
            if state[y*BOARD_WIDTH + x] != 0:
                dest = y - 1
                break
        result.append(dest)
    return result


def get_best_span(span: list[int], player: int):
    best = 0
    for i in range(len(span) - (LINE_LENGTH-1)):
        best = max(best, sum(span[i:i+LINE_LENGTH]) // player)
    return best


def get_span(state: array[int], player: int, x: int, y: int, x_inc: int, y_inc: int):
    span = []
    xx = x - x_inc
    yy = y - y_inc
    y_inv = y_inc < 0
    while xx >= max(x - (LINE_LENGTH-1), 0) and ((yy <= min(y + (LINE_LENGTH-1), BOARD_HEIGHT - 1)) if y_inv else (yy >= max(y - (LINE_LENGTH-1), 0))):
        if state[yy*BOARD_WIDTH + xx] in (0, player):
            span.append(state[yy*BOARD_WIDTH + xx])
            xx -= x_inc
            yy -= y_inc
        else:
            break
    span.reverse()
    span.append(player)
    xx = x + x_inc
    yy = y + y_inc
    while xx <= min(x + (LINE_LENGTH-1), BOARD_WIDTH - 1) and ((yy >= max(y - (LINE_LENGTH-1), 0)) if y_inv else (yy <= min(y + (LINE_LENGTH-1), BOARD_HEIGHT - 1))):
        if state[yy*BOARD_WIDTH + xx] in (0, player):
            span.append(state[yy*BOARD_WIDTH + xx])
            xx += x_inc
            yy += y_inc
        else:
            break
    return span 

def get_best_move(state: array[int], player: int, opponent: int):
    y_pos = get_y_pos(state)
    scores = [0]*len(y_pos)
    # horizontal
    for x, y in enumerate(y_pos):
        if y == -1: # full column
            continue

        h_span = get_span(state, player, x, y, 1, 0)
        h_best = get_best_span(h_span, player)
        v_span = get_span(state, player, x, y, 0, 1)
        v_best = get_best_span(v_span, player)
        br_span = get_span(state, player, x, y, 1, 1)
        br_best = get_best_span(br_span, player)
        ur_span = get_span(state, player, x, y, 1, -1)
        ur_best = get_best_span(ur_span, player)
        h_opp_span = get_span(state, opponent, x, y, 1, 0)
        h_opp_best = get_best_span(h_opp_span, opponent)
        v_opp_span = get_span(state, opponent, x, y, 0, 1)
        v_opp_best = get_best_span(v_opp_span, opponent)
        br_opp_span = get_span(state, opponent, x, y, 1, 1)
        br_opp_best = get_best_span(br_opp_span, opponent)
        ur_opp_span = get_span(state, opponent, x, y, 1, -1)
        ur_opp_best = get_best_span(ur_opp_span, opponent)
        
        my_score = SCORE_PLAYER_MAP[h_best] + SCORE_PLAYER_MAP[v_best] + SCORE_PLAYER_MAP[br_best] + SCORE_PLAYER_MAP[ur_best]
        opp_score = SCORE_OPPONENT_MAP[h_opp_best] + SCORE_OPPONENT_MAP[v_opp_best] + SCORE_OPPONENT_MAP[br_opp_best] + SCORE_OPPONENT_MAP[ur_opp_best]

        post_score = 0
        if y > 0:
            state[y*BOARD_WIDTH+x] = player
            h_post_span = get_span(state, opponent, x, y-1, 1, 0)
            h_post_best = get_best_span(h_post_span, opponent)
            v_post_span = get_span(state, opponent, x, y-1, 0, 1)
            v_post_best = get_best_span(v_post_span, opponent)
            br_post_span = get_span(state, opponent, x, y-1, 1, 1)
            br_post_best = get_best_span(br_post_span, opponent)
            ur_post_span = get_span(state, opponent, x, y-1, 1, -1)
            ur_post_best = get_best_span(ur_post_span, opponent)
            
            state[y*BOARD_WIDTH+x] = 0

            post_score = -1000000 if LINE_LENGTH in [h_post_best, v_post_best, br_post_best, ur_post_best] else 0

        scores[x] = my_score + opp_score + post_score
        print((x,y, my_score, opp_score, post_score))
        #print((h_span, h_best, h_opp_span, h_opp_best))  
        #print((v_span, v_best, v_opp_span, v_opp_best))  
        #print((br_span, br_best, br_opp_span, br_opp_best))  
        #print((ur_span, ur_best, ur_opp_span, ur_opp_best))  
        if LINE_LENGTH in [h_best, v_best, br_best, ur_best]:
            raise ValueError(f"Player {player} wins")


    candidates = [i for i in range(len(y_pos)) if y_pos[i] != -1]
    candidates.sort(key=lambda i: (scores[i], BOARD_WIDTH-abs((BOARD_WIDTH//2) - i)), reverse=True)
    if not candidates:
        raise ValueError("draw!!!")
    return candidates[0]


def play_move(state: array[int], player: int, x: int):
    y_pos = get_y_pos(state)
    if y_pos[x] == -1:
        raise ValueError("illegal move")
    state[y_pos[x]*BOARD_WIDTH + x] = player


test = [0] * BOARD_WIDTH * BOARD_HEIGHT

#play_move(test, 1, 3)
#move = get_best_move(test, 1, 2); play_move(test, 1, move)

print("Type \"play(x)\" -- where x is a column between 1 and 7")

def print_board(state: array[int]):
    for y in range(BOARD_HEIGHT):
        result = ""
        for v in state[y*BOARD_WIDTH:(y+1)*BOARD_WIDTH]:
            if v == 0:
                result += "_ "
            elif v == 1:
                result += "O "
            elif v == 2:
                result += "x "
        print(result)
    print()

 

def play(column):
    play_move(test, 1, column-1)
    move = get_best_move(test, 2, 1)
    play_move(test, 2, move)
    print_board(test)

def autoplay():
    state = [0] * BOARD_WIDTH * BOARD_HEIGHT
    while True:
        move = get_best_move(state, 1, 2)
        play_move(state, 1, move)
        print_board(state)
        move = get_best_move(state, 2, 1)
        play_move(state, 2, move)
        print_board(state)


import random

STRATEGY_NAME = ["Angstrom", "Bigglesworth", "Cloudsley", "Dodsworth", "Ezekiel", "Froberg", "Gaylord", "Hitchcock", "Ingrid", "Jurgen", "Konstantin", "Lamington", "McDougall", "Noreen", "Octavia", "Prancibald", "Quiggins", "Rizzler", "Shatner", "Touissant", "Utley", "Viscount", "Wilmot", "Xerxes", "Yankmaster", "Zachary"]
STRATEGY_MOVE = ["Axiom", "Bassoon", "Corollary", "Dogleg", "Earthworm", "Flop", "Gambit", "Hedge", "Inquiry", "Jump", "Kerplunk", "Ludo", "Mate", "Negative", "Opening", "Proposition", "Quandry", "Reverse-Ferret", "Strategem", "Table-Flip", "Upset", "Victory", "Wager", "Xerotic", "Yurt", "Ziggurat"]

def get_strategy_name() -> str:
    name = random.choice(STRATEGY_NAME)
    name += "' " if name.endswith("s") else "'s "
    name += random.choice(STRATEGY_MOVE)
    return name

STRATEGY_MSG = [
    "I see you're familiar with {}.",
    "Oh, now we're pulling out {}? I see how it is.",
    "Maybe now's the time for {}.",
    "Sorry bud, {} won't help you now.",
    "{}. A move for cowards.",
    "Pretty brazen to try {} at this stage.",
    "Was that meant to be {}? Cute.",
]

WEIRD_OPENING = [
    "Let's fuckin' go!",
    "Hell yes. Great choice.",
    "Okay, now I'm excited.",
    "Wanna dance?",
    "You? You're different than the others.",
    "Loose unit detected.",
    "Delicious.",
]

BORING_OPENING = [
    "Congrats on reading the Wikipedia page for Connect 4.",
    "Sure, I guess you needed the leg-up.",
    "Dull dull dull.",
    "Boooooooring.",
    "Let's get this over with.",
    "What an imagination you must have.",
    "How original.",
    "Really? Really???",
]

QUICK_LOSS = [
    "Someone -did- tell you the rules, right?",
    "Why did you throw it?",
    "C'mon at least -pretend- to try???",
    "Which part confuses you, connecting or the number 4?"
]

EASY_LOSS = [
    "Get rekt scrub.",
    "Skill issue."
]

HARD_LOSS = [
    "That was rough. Nice going.",
    "I almost want to give this one to you. Almost.",
    "Geez someone has been practicing.",
]

WIN_FROM_BEHIND = [
    "Sorry pal, tonight losing's not on the menu."
]

DOUBLE_WIN = [
    "BOFA DEEZ LINES"
]

OH_SHIT = [
    "I'm feeling generous, how about we call it a draw?",
    "It's not too late to give up. You fought well.",
    "Still time to resign! No-one will think any less of you!",
]
