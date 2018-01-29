class OptimalLineup:
	def __init__(self):
		self.position_map = {'FLEX': ['RB', 'WR', 'TE'], 'DP': ['DT', 'DE', 'LB', 'DL', 'CB', 'S', 'DB'], 'OP': ['QB', 'RB', 'WR', 'TE'], 'RB/WR': ['RB', 'WR']}

	def optimal_lineups(self, league_data):

		def optimize_lineup(starters, bench):
			optimal_lineup = starters
			for player_data in bench['Bench']:
				potential_subs = compare_bench_player_to_starters(player_data, optimal_lineup)

			return optimal_lineup

		def compare_bench_player_to_starters(bench_player, starters):
			low_player = bench_player
			low_slot = None
			low_player_points = 0.0

			try:
				low_player_points = float(low_player['Points'])
			except:
				return

			bench_position = bench_player['Position']

			for slot in starters:
				for starter in starters[slot]:
					if starter != {}:
						starter_points = 0.0
						try:
							starter_points = float(starter['Points'])
						except:
							pass

						starter_position = starter['Position']

						if (starter_position == bench_position) or (slot in self.position_map and bench_position in self.position_map[slot]):
							if (starter_points < low_player_points):
								low_player = starter
								low_slot = slot
								try:
									low_player_points = float(low_player['Points'])
								except:
									pass

			if low_slot is not None:
				starters[low_slot].remove(low_player)
				starters[low_slot].insert(0, bench_player)


		def calculate_points(players):
			points_scored = 0.00
			for slot in players:
				for starter in players[slot]:
					try:
						points_scored = points_scored + float(starter['Points'])
					except:
						pass

			return points_scored

		rankings = dict()
		number_games = len(league_data)

		for item in league_data:
			team_name = item['Name']
			week_number = item['Week']

			points_scored = calculate_points(item['Starters'])
			optimal_lineup = optimize_lineup(item['Starters'], item['Bench'])

			difference = calculate_points(optimal_lineup) - points_scored

			week_data = {'Week': week_number, 'Starters': item['Starters'], 'OptimalLineup': optimal_lineup, 'Difference': difference}
			if team_name not in rankings:
				rankings[team_name] = list()

			rankings[team_name].append(dict(week_data))

		return rankings