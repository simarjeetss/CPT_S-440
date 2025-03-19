from game import Game
from neural_network import NeuralNetwork


player1 = "real"
player2 = 'real'

# visualization
use_window = True
time_delay = 0.3
n_games = 10


# ------------------------ no need to change anything below this line ------------------------
print("player 1:", player1)
print("player 2:", player2)


game = Game(player_1_type=player1, player_2_type=player2, window=use_window, time_delay=time_delay)
p1_wins, p2_wins, draws, _, average_game_length = game.game_loop(n_games=n_games)

print("player 1 wins:", p1_wins, "\nplayer 2 wins:", p2_wins, "\ndraws:", draws, "\naverage game length:", average_game_length)