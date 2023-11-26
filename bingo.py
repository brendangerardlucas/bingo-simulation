import random
import os
import copy

board_items = ['A', 'B', 'C', 'D', 'E',
               'F', 'G', 'H', 'I', 'J',
               'K', 'L', 'M', 'N', #There is a free space
               'O', 'P', 'Q', 'R', 'S', 
               'T', 'U', 'V', 'W', 'X']

def reset_random():
    random.seed(os.urandom(10))

def new_board(seed):
    random.seed(seed)
    this_board = [[], [], [], [], []]
    used_indices = []
    used_twice = []
    doubles = False #there should not be more than one double on the same bingo board

    for row in range(5):
        for column in range(5):
            if row is column and column is 2:
                this_board[row].append('⭐')#free space
                continue
            index = random.randint(0, 23)
            if doubles: #making sure that there can only be one identical pair on the same board
                while index in used_indices:
                    reset_random()
                    index = random.randint(0, 23)
            else: #making sure that there is never more than 2 of one character on the same board
                while index in used_twice:
                    reset_random()
                    index = random.randint(0, 23)

            this_board[row].append(board_items[index])
            
            if index in used_indices and index not in used_twice:
                used_twice.append(index)
                doubles = True
            if index not in used_indices:
                used_indices.append(index)

    return this_board

#The goal here is to figure which kind of bingo board is the most likely to win

def generate_boards(num_players):
    #introduce rules so that the same board can't have more than 2 of the same item
    boards_list = []
    
    for player in range(num_players):
        boards_list.append(new_board(player)) #the player's ID is their board's seed
    return boards_list

def draw_card(deck):
    draw = random.randint(0, len(deck) - 1)
    this_card = deck[draw]
    deck.remove(this_card)
    return deck, this_card

def play_round(boards_list):
    #play a round with the current list of boards
    boards_tokens = copy.deepcopy(boards_list)
    deck = copy.deepcopy(board_items)
    winners_list = []
    diagonal_coordinates = [[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],
                           [(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)]]
    while len(winners_list) < 1:
        deck, token = draw_card(deck) 
        #this structure actually places the tokens
        for board in boards_tokens:
            for row in board:
                for square in row:
                    if square == token:
                        board[board.index(row)][row.index(square)] = '⭐' #the token
        #this structure checks for victory
        for board in boards_tokens:
            #in each row
            for row in board:
                if all(square == '⭐' for square in row) and board not in winners_list:
                    winners_list.append(boards_list[boards_tokens.index(board)])
            if board not in winners_list: #remember to check for duplicate boards
                #by diagonals if not by rows
                diagonals = [[],[]]
                for each_diagonal in diagonal_coordinates:
                    if board not in winners_list:
                        for pair in each_diagonal:
                            diagonals[diagonal_coordinates.index(each_diagonal)].append(board[int(pair[0])][int(pair[1])])
                            if all(square == '⭐' for square in each_diagonal) and board not in winners_list:
                                winners_list.append(boards_list[boards_tokens.index(board)])
    return winners_list

def simulate_rounds(num_players, num_rounds):
    score_card = [generate_boards(num_players), 
                  [0]*num_players] #this second row of the scorecard is the number of wins in each round
    for round in range(num_rounds):
        print(f'boards list: ', score_card[0], '\n is of type: ', type(score_card[0]))
        round_winners = play_round(score_card[0])
        for winner in round_winners:
            score_card[1][score_card[0].index(winner)] += 1
    #append winrates
    score_card.append([])
    for player in score_card[1]:
        score_card[2].append(score_card[1][score_card[1].index(player)] / num_rounds)
    #print the overall results
    print('Score card: \n' + '-'*10)
    print('Boards: ', score_card[0])
    print('Win count: ', score_card[1])
    print('Win rate: ', score_card[2])
    print('Highest win rate: ', max(score_card[2]))

    best_index = score_card[2].index(max(score_card[2]))
    print('The best board is: ', score_card[0][best_index])

    worst_index = score_card[2].index(min(score_card[2]))
    print('The worst board is: ', score_card[0][worst_index])

    if num_players > 2:
        score_card_2 = copy.deepcopy(score_card)
        for i in range(len(score_card)):
            score_card_2[i].remove(score_card_2[i][best_index])
        second_best_index = score_card_2[2].index(max(score_card_2[2]))
        if second_best_index >= best_index:
            second_best_index += 1
        print('The second best board is: ', score_card[0][second_best_index])

    if num_players > 3:
        score_card_3 = copy.deepcopy(score_card)
        for i in range(len(score_card)):
            score_card_3[i].remove(score_card_3[i][worst_index])
        second_worst_index = score_card_3[2].index(min(score_card_3[2]))
        if second_worst_index >= worst_index:
            second_worst_index += 1
        print('The second worst board is: ', score_card[0][second_worst_index])

    if num_players > 4:
        import statistics
        mid_index = score_card[2].index(min(score_card[2], key=lambda x:abs(x - statistics.median(score_card[2]))))
        print('The median board is: ', score_card[0][int(mid_index)])
    #this gives us some data for analysis
    return score_card
simulate_rounds(num_players=1000, num_rounds=10000)
