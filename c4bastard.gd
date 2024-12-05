   
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


func pick_smack_talk(game_data: C4GameData, choices: Array[String]) -> String:
    const messages: String = "|".join([turn.message for turn in game_data.game_history])
    var c: Array[String] = choices.duplicate()
    while c:
        c.shuffle()
        const m: String = c.pop()
        if m not in messages:
            return m
    return ""

 
func get_strategy_name(game_data: C4GameData) -> String:
    var name: String = pick_smack_talk(game_data, STRATEGY_NAME)
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


func get_y_pos(game_data: C4GameData) -> Array[int]:
    var result: Array[int] = []
    for x in range(game_data.columns):
        var dest = game_data.rows - 1
        for y in range(game_data.rows):
            if game_data.grid[y*game_data.columns + x] != 0:
                dest = y - 1
                break
        result.append(dest)
    return result


func get_best_span(game_data: C4GameData, span: Array[int], player: int) -> int:
    var best: int = 0
    for i in range(len(span) - (game_data.required_connections-1)):
        best = max(best, sum(span[i:i+game_data.required_connections]) // player)
    return best


func get_span(game_data: C4GameData, player: int, x: int, y: int, x_inc: int, y_inc: int) -> Array[int]:
    var span: Array[int] = []
    var xx: int = x - x_inc
    var yy: int = y - y_inc
    var y_inv: bool = y_inc < 0
    while xx >= max(x - (game_data.required_connections-1), 0) and ((yy <= min(y + (game_data.required_connections-1), game_data.rows - 1)) if y_inv else (yy >= max(y - (game_data.required_connections-1), 0))):
        if game_data.grid[yy*game_data.columns + xx] in [0, player]:
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
        if game_data.grid[yy*game_data.columns + xx] in [0, player]:
            span.append(game_data.grid[yy*game_data.columns + xx])
            xx += x_inc
            yy += y_inc
        else:
            break
    return span


func get_best_move(game_data: C4GameData, player: int, opponent: int) -> Array:
    const SCORE_LOG: Array[int] = lambda i: math.exp(math.log(1000)/(6*i+1))
    const SCORE_BASIC: Array[int] = [round(SCORE_LOG(i/game_data.required_connections)) for i in reversed(range(game_data.required_connections))]
    const SCORE_PLAYER_MAP: Array[int] = SCORE_BASIC + [100000]
    const SCORE_OPPONENT_MAP: Array[int] = SCORE_BASIC + [10000]

    const y_pos: Array[int] = get_y_pos(game_data)
    var scores: Array[int] = [0]*len(y_pos)
    # horizontal
    for x in range(y_pos.size):
        const y: int = y_pos[x]
        if y == -1: # full column
            continue

        const h_span: Array[int] = get_span(game_data, player, x, y, 1, 0)
        const h_best: int = get_best_span(game_data, h_span, player)
        const v_span: Array[int] = get_span(game_data, player, x, y, 0, 1)
        const v_best: int = get_best_span(game_data, v_span, player)
        const br_span: Array[int] = get_span(game_data, player, x, y, 1, 1)
        const br_best: int = get_best_span(game_data, br_span, player)
        const ur_span: Array[int] = get_span(game_data, player, x, y, 1, -1)
        const ur_best: int = get_best_span(game_data, ur_span, player)
        const h_opp_span: Array[int] = get_span(game_data, opponent, x, y, 1, 0)
        const h_opp_best: int = get_best_span(game_data, h_opp_span, opponent)
        const v_opp_span: Array[int] = get_span(game_data, opponent, x, y, 0, 1)
        const v_opp_best: int = get_best_span(game_data, v_opp_span, opponent)
        const br_opp_span: Array[int] = get_span(game_data, opponent, x, y, 1, 1)
        const br_opp_best: int = get_best_span(game_data, br_opp_span, opponent)
        const ur_opp_span: Array[int] = get_span(game_data, opponent, x, y, 1, -1)
        const ur_opp_best: int = get_best_span(game_data, ur_opp_span, opponent)
        
        const my_score: int = SCORE_PLAYER_MAP[h_best] + SCORE_PLAYER_MAP[v_best] + SCORE_PLAYER_MAP[br_best] + SCORE_PLAYER_MAP[ur_best]
        const opp_score: int = SCORE_OPPONENT_MAP[h_opp_best] + SCORE_OPPONENT_MAP[v_opp_best] + SCORE_OPPONENT_MAP[br_opp_best] + SCORE_OPPONENT_MAP[ur_opp_best]

        var post_score: int = 0
        if y > 0:
            game_data.grid[y*game_data.columns+x] = player
            const h_post_span: Array[int] = get_span(game_data, opponent, x, y-1, 1, 0)
            const h_post_best: int = get_best_span(game_data, h_post_span, opponent)
            const v_post_span: Array[int] = get_span(game_data, opponent, x, y-1, 0, 1)
            const v_post_best: int = get_best_span(game_data, v_post_span, opponent)
            const br_post_span: Array[int] = get_span(game_data, opponent, x, y-1, 1, 1)
            const br_post_best: int = get_best_span(game_data, br_post_span, opponent)
            const ur_post_span: Array[int] = get_span(game_data, opponent, x, y-1, 1, -1)
            const ur_post_best: int = get_best_span(game_data, ur_post_span, opponent)
            
            game_data.grid[y*game_data.columns+x] = 0

            post_score = -1000000 if game_data.required_connections in [h_post_best, v_post_best, br_post_best, ur_post_best] else 0

        scores[x] = my_score + opp_score + post_score
        #print((x,y, my_score, opp_score, post_score))
        #print((h_span, h_best, h_opp_span, h_opp_best))  
        #print((v_span, v_best, v_opp_span, v_opp_best))  
        #print((br_span, br_best, br_opp_span, br_opp_best))  
        #print((ur_span, ur_best, ur_opp_span, ur_opp_best))  

    smack = ""

    candidates = [i for i in range(len(y_pos)) if y_pos[i] != -1]
    candidates.sort(key=lambda i: (scores[i], game_data.columns-abs((game_data.columns//2) - i)), reverse=True)
    if candidates.size == 0:
        return [-1, ""]

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

    return [result, smack]



func c4_bastard_play(game_data: C4GameData) -> Array:
    const player = game_data.player_index + 1
    const opponent = 2 if player == 1 else 1
    return get_best_move(game_data, player, opponent)

