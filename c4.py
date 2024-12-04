#!/usr/bin/env python
from __future__ import annotations

import math
from array import array

from dataclasses import dataclass, field

@dataclass
class C4Turn:
    number: int = 0 #First player's first turn is 1, 2nd player's first turn is 2 etc.
    player_index: int = 0 #0 = first player, 1 = second player
    selection:int = -1 #The selected grid slot => -1 if an invalid slot was selected, -2 if they ran out of time otherwise 0 to 41(in normal 6x7 grid)
    message: str = "" #The message given by the player, empty string if no response
    game_data: C4GameData | None = None #the data given to the player as part of their turn
    time_used_ms: int = 0 #the thinking time used by the turn


class C4GameData:
	columns:int = 7 #The number of columns of the grid
	rows: int = 6 #The number of rows of the grid
	required_connections: int = 4#The number of connected tokens required to win (normally 4)
	allowed_time_ms: int = 5000 #The total allowed thinking time for each player
	
	grid: list[int] = field(default_factory=list)#Current game grid 0 = Empty, 1 = Player 1 token, 2 = Player 2 token. 0 is top left slot, goes left-right, top-bottom
	game_history: list[C4Turn] = field(default_factory=list) #Array holding all the previous turns
	my_remaining_time_s:float = 0.0 #Your total remaining thinking time in s
	my_player_index:int = 0 #0 if first player, 1 if second player
	my_opponent_name: str = "" #Your opponent's display name
	my_name: str = "" #Your display name
	my_remaining_time_ms: int = 0 #Your total remaining thinking time in ms

	my_grid: list[int] = field(default_factory=list) #Current game grid but changed to 0= empty, 1= your token, 2= your opponents tokken



import random

   
STRATEGY_MSG = [
    "I see you're familiar with {}",
    "oh, now we're pulling out {}? I see how it is.",
    "maybe now's the time for {}",
    "sorry bud, {} won't help you now",
    "{}. a move for cowards",
    "pretty brazen to try {} at this stage",
    "was that meant to be {}? cute.",
    "alright, who told you about {}",
    "",
]

START = [
    "get ready to lose",
    "you going down",
    "sure you're up to this? okay",
    "new game who dis",
    "I got high expectations of you bud",
    "ok botface",
]

WEIRD_OPENING = [
    "let's fuckin' go!",
    "hell yes. great choice",
    "okay, now I'm excited",
    "you? you're different than the others",
    "== loose unit detected ==",
    "delicious",
]

BORING_OPENING = [
    "congrats on reading the wikipedia page for Connect 4",
    "sure, I see you need the extra help",
    "dull dull DULL",
    "boooooooring",
    "let's get this over with",
    "what an imagination you must have",
    "real original, kasparov",
    "really? really???",
]

QUICK_LOSS = [
    "someone -did- tell you the rules, right?",
    "why did you throw it?",
    "c'mon at least *pretend* to try",
    "which part confuses you, connecting or the number 4?"
]

EASY_LOSS = [
    "get rekt scrub",
    "skill issue"
]

HARD_LOSS = [
    "gg",
    "ya tried at least",
    "that was rough",
    "I almost want to give this one to you. almost.",
    "geez, someone has been practicing",
]

WIN_FROM_BEHIND = [
    "sorry pal, tonight losing's not on the menu",
    "you were soooo close!!!",
]

DOUBLE_WIN = [
    "BOFA DEEZ LINES"
]

DRAW = [
    "congrats on using every game piece I GUESS",
    "what an enriching waste of thirty seconds",
    "WALLHAX AIMBOT",
    "everyone is bored now, nice work",
]

OH_SHIT = [
    "I'm feeling generous, call it a draw?",
    "it's not too late to give up. you fought well",
    "still time to resign! no-one will think less of you!",
    "eh I got this",
    "oh, a wise guy eh?",
    "fffffffine",
]

STRATEGY_NAME = ["Angstrom", "Bigglesworth", "Cloudsley", "Dodsworth", "Ezekiel", "Froberg", "Gaylord", "Hitchcock", "Ingrid", "Jurgen", "Konstantin", "Lamington", "McDougall", "Noreen", "Octavia", "Prancibald", "Quiggins", "Rizzler", "Shatner", "Touissant", "Utley", "Viscount", "Wilmot", "Xerxes", "Yankmaster", "Zachary"]
STRATEGY_MOVE = ["Axiom", "Bassoon", "Corollary", "Dogleg", "Earthworm", "Flop", "Gambit", "Hedge", "Inquiry", "Jump", "Kerplunk", "Ludo", "Mate", "Negative", "Opening", "Proposition", "Quandry", "Reverse-Ferret", "Strategem", "Table-Flip", "Upset", "Victory", "Wager", "Xerotic", "Yurt", "Ziggurat"]


def pick_smack_talk(game_data: C4GameData, choices: list[str]):
    messages = "|".join([turn.message for turn in game_data.game_history])
    c = list(choices)
    while c:
        random.shuffle(c)
        m = c.pop()
        if m not in messages:
            return m
    return ""

 
def get_strategy_name(game_data: C4GameData) -> str:
    name = pick_smack_talk(game_data, STRATEGY_NAME)
    name += "' " if name.endswith("s") else "'s "
    name += pick_smack_talk(game_data, STRATEGY_MOVE)
    return name

# algo needs to balance between creating more options for us + blocking other player
# weights for choices
# if we can make 4: 100000 points
# if we can block 4: 10000 points
# if we can make 3: 1000 points
# if we can block 3: 1000 points
# if we can make 2: 10 points
# if we can block 2: 10 points


def add_token(state: array[int], column: int, token: int) -> array[int]:
    result = array('B', state.tobytes())
    if column >= game_data.columns:
        raise ValueError("column out of range")
    if result[0 + column] != 0:
        raise ValueError("column full")
    for i in range(game_data.rows - 1, -1, -1):
        if result[i*game_data.columns + column] == 0:
            result[i*game_data.columns + column] = token
    return result


def get_y_pos(game_data: C4GameData) -> list[int]:
    result = []
    for x in range(game_data.columns):
        dest = game_data.rows - 1
        for y in range(game_data.rows):
            if game_data.grid[y*game_data.columns + x] != 0:
                dest = y - 1
                break
        result.append(dest)
    return result


def get_best_span(game_data: C4GameData, span: list[int], player: int) -> int:
    best = 0
    for i in range(len(span) - (game_data.required_connections-1)):
        best = max(best, sum(span[i:i+game_data.required_connections]) // player)
    return best


def get_span(game_data: C4GameData, player: int, x: int, y: int, x_inc: int, y_inc: int) -> list[int]:
    span: list[int] = []
    xx = x - x_inc
    yy = y - y_inc
    y_inv = y_inc < 0
    while xx >= max(x - (game_data.required_connections-1), 0) and ((yy <= min(y + (game_data.required_connections-1), game_data.rows - 1)) if y_inv else (yy >= max(y - (game_data.required_connections-1), 0))):
        if game_data.grid[yy*game_data.columns + xx] in (0, player):
            span.append(game_data.grid[yy*game_data.columns + xx])
            xx -= x_inc
            yy -= y_inc
        else:
            break
    span.reverse()
    span.append(player)
    xx = x + x_inc
    yy = y + y_inc
    while xx <= min(x + (game_data.required_connections-1), game_data.columns - 1) and ((yy >= max(y - (game_data.required_connections-1), 0)) if y_inv else (yy <= min(y + (game_data.required_connections-1), game_data.rows - 1))):
        if game_data.grid[yy*game_data.columns + xx] in (0, player):
            span.append(game_data.grid[yy*game_data.columns + xx])
            xx += x_inc
            yy += y_inc
        else:
            break
    return span 

def get_best_move(game_data: C4GameData, player: int, opponent: int) -> tuple[int, str]:

    SCORE_LOG = lambda i: math.exp(math.log(1000)/(6*i+1))
    SCORE_BASIC = [round(SCORE_LOG(i/game_data.required_connections)) for i in reversed(range(game_data.required_connections))]
    SCORE_PLAYER_MAP = SCORE_BASIC + [100000]
    SCORE_OPPONENT_MAP = SCORE_BASIC + [10000]

    y_pos = get_y_pos(game_data)
    scores = [0]*len(y_pos)
    # horizontal
    for x, y in enumerate(y_pos):
        if y == -1: # full column
            continue

        h_span = get_span(game_data, player, x, y, 1, 0)
        h_best = get_best_span(game_data, h_span, player)
        v_span = get_span(game_data, player, x, y, 0, 1)
        v_best = get_best_span(game_data, v_span, player)
        br_span = get_span(game_data, player, x, y, 1, 1)
        br_best = get_best_span(game_data, br_span, player)
        ur_span = get_span(game_data, player, x, y, 1, -1)
        ur_best = get_best_span(game_data, ur_span, player)
        h_opp_span = get_span(game_data, opponent, x, y, 1, 0)
        h_opp_best = get_best_span(game_data, h_opp_span, opponent)
        v_opp_span = get_span(game_data, opponent, x, y, 0, 1)
        v_opp_best = get_best_span(game_data, v_opp_span, opponent)
        br_opp_span = get_span(game_data, opponent, x, y, 1, 1)
        br_opp_best = get_best_span(game_data, br_opp_span, opponent)
        ur_opp_span = get_span(game_data, opponent, x, y, 1, -1)
        ur_opp_best = get_best_span(game_data, ur_opp_span, opponent)
        
        my_score = SCORE_PLAYER_MAP[h_best] + SCORE_PLAYER_MAP[v_best] + SCORE_PLAYER_MAP[br_best] + SCORE_PLAYER_MAP[ur_best]
        opp_score = SCORE_OPPONENT_MAP[h_opp_best] + SCORE_OPPONENT_MAP[v_opp_best] + SCORE_OPPONENT_MAP[br_opp_best] + SCORE_OPPONENT_MAP[ur_opp_best]

        post_score = 0
        if y > 0:
            game_data.grid[y*game_data.columns+x] = player
            h_post_span = get_span(game_data, opponent, x, y-1, 1, 0)
            h_post_best = get_best_span(game_data, h_post_span, opponent)
            v_post_span = get_span(game_data, opponent, x, y-1, 0, 1)
            v_post_best = get_best_span(game_data, v_post_span, opponent)
            br_post_span = get_span(game_data, opponent, x, y-1, 1, 1)
            br_post_best = get_best_span(game_data, br_post_span, opponent)
            ur_post_span = get_span(game_data, opponent, x, y-1, 1, -1)
            ur_post_best = get_best_span(game_data, ur_post_span, opponent)
            
            game_data.grid[y*game_data.columns+x] = 0

            post_score = -1000000 if game_data.required_connections in [h_post_best, v_post_best, br_post_best, ur_post_best] else 0

        scores[x] = my_score + opp_score + post_score
        print((x,y, my_score, opp_score, post_score))
        #print((h_span, h_best, h_opp_span, h_opp_best))  
        #print((v_span, v_best, v_opp_span, v_opp_best))  
        #print((br_span, br_best, br_opp_span, br_opp_best))  
        #print((ur_span, ur_best, ur_opp_span, ur_opp_best))  
        if game_data.required_connections in [h_best, v_best, br_best, ur_best]:
            raise ValueError(f"Player {player} wins")

    smack = ""

    candidates = [i for i in range(len(y_pos)) if y_pos[i] != -1]
    candidates.sort(key=lambda i: (scores[i], game_data.columns-abs((game_data.columns//2) - i)), reverse=True)
    if not candidates:
        raise ValueError("draw!!!")

    result = candidates[0]
    if scores[result] >= 200000:
        smack = pick_smack_talk(game_data,DOUBLE_WIN)
    elif scores[result] >= 100000:
        if len(game_data.game_history) <= game_data.required_connections*2:
            smack = pick_smack_talk(game_data,QUICK_LOSS)
        elif ((scores[result] % 100000) >= 10000):
            smack = pick_smack_talk(game_data,WIN_FROM_BEHIND)
        elif len(game_data.game_history) <= game_data.required_connections*4:
            smack = pick_smack_talk(game_data, EASY_LOSS)
        else:
            smack = pick_smack_talk(game_data, HARD_LOSS)
    elif (len(game_data.game_history) == 1):
        if game_data.game_history[0].selection == (game_data.columns // 2):
            smack = pick_smack_talk(game_data, BORING_OPENING)
        else:
            smack = pick_smack_talk(game_data, WEIRD_OPENING)
    elif (scores[result] % 100000) >= 10000:
        smack = pick_smack_talk(game_data, OH_SHIT)
    elif len(game_data.game_history) == 0:
        smack = pick_smack_talk(game_data, START)
    elif len(game_data.game_history) >= (game_data.columns * game_data.rows - 1):
        smack = pick_smack_talk(game_data, DRAW)
    elif (len(game_data.game_history) // 2) % 4 == 0:
        smack = pick_smack_talk(game_data, STRATEGY_MSG).format(get_strategy_name(game_data))

    return result, smack


def play_move(game_data: C4GameData, player: int, x: int, smack: str):
    y_pos = get_y_pos(game_data)
    if y_pos[x] == -1:
        raise ValueError("illegal move")
    game_data.grid[y_pos[x]*game_data.columns + x] = player
    game_data.game_history.append(C4Turn(
        player_index = player-1,
        selection = x,
        message = smack,
    ))



print("Type \"play(x)\" -- where x is a column between 1 and 7")

def print_board(game_data: C4GameData, player: int, smack: str|None = None):
    if (smack):
        print(f"P{player}: {smack}")
    for y in range(game_data.rows):
        result = ""
        for v in game_data.grid[y*game_data.columns:(y+1)*game_data.columns]:
            if v == 0:
                result += "_ "
            elif v == 1:
                result += "O "
            elif v == 2:
                result += "x "
        print(result)
    print()


def c4_bastard_play(game_data: C4GameData):
    player = game_data.player_index + 1
    opponent = 2 if player == 1 else 1
    return get_best_move(game_data, player, opponent)


def autoplay():
    game_data = C4GameData()
    game_data.grid = [0] * game_data.columns * game_data.rows
    game_data.game_history = []
    while True:
        move, smack = get_best_move(game_data, 1, 2)
        play_move(game_data, 1, move, smack)
        print_board(game_data, 1, smack)
        move, smack = get_best_move(game_data, 2, 1)
        play_move(game_data, 2, move, smack)
        print_board(game_data, 2, smack)



