import statistics
import copy
import DataMaps

class ExpectedRecord:
	def __init__(self, league_id, data_store, year = '2017'):
		self.league_id = league_id
		self.data_store = data_store
		self.year = year
		self.data_maps = DataMaps.DataMaps()
		self.expected_wins = 0.0
		self.expected_losses = 0.0

	def calculate_expected_record(self, team_id):
		team_scores = self.data_store.select_team_scores(self.league_id, self.year, team_id)
		league_scores = self.data_store.select_league_scores(self.league_id, self.year)

		total_wins = 0
		total_losses = 0
		for team_matchup_period in team_scores:
			team_score = team_scores[team_matchup_period]

			for league_matchup_period in league_scores:
				if team_matchup_period == league_matchup_period:
					for league_score in league_scores[league_matchup_period]:
						if (team_score > league_score) : total_wins = total_wins + 1
						if (team_score < league_score) : total_losses = total_losses + 1

		percentage = total_wins / (total_wins + total_losses)
		expected_wins = round((percentage * len(team_scores)), 1)
		expected_losses = round((len(team_scores) - expected_wins), 1)
		self.expected_wins = expected_wins
		self.expected_losses = expected_losses

class LeagueAverages:
	def __init__(self, league_id, data_store, year = '2017'):
		self.league_id = league_id
		self.data_store = data_store
		self.year = year
		self.team_scores = dict()
		self.league_median_scores = dict()
		self.team_scores_by_position = dict()
		self.league_scores_by_position = dict()

	def calculate_player_scores(self, team_id):
		scores = self.data_store.select_team_scores(self.league_id, self.year, team_id)
		self.team_scores = dict(scores)

	def calculate_median_scores(self):
		scores = dict()
		matchup_ids = self.data_store.select_matchup_ids(self.league_id, self.year)
		for matchup_id in matchup_ids:
			week_scores = self.data_store.select_league_scores_by_week(self.league_id, self.year, matchup_id)
			scores[matchup_id] = statistics.median(week_scores)
		self.league_median_scores = dict(scores)

	def team_position_scores(self, team_id):
		scores = self.data_store.select_team_scores_by_position(self.league_id, self.year, team_id)
		position_scores = dict()
		for slot in scores:
			position_scores[slot] = statistics.median(scores[slot])
		self.team_scores_by_position = dict(position_scores)

	def league_position_scores(self):
		scores = self.data_store.select_league_scores_by_position(self.league_id, self.year)
		position_scores = dict()
		for slot in scores:
			position_scores[slot] = statistics.median(scores[slot])
		self.league_scores_by_position = dict(position_scores)

class TransactionStats:
	def __init__(self, league_id, data_store, year = '2017'):
		self.league_id = league_id
		self.data_store = data_store
		self.year = year
		self.points_breakdown = dict()
		self.team_trades = dict()

	def points_from_trades(self, team_id):
		trade_items = self.data_store.select_trades_by_team(self.league_id, self.year, team_id)
		points = self.data_store.select_points_from_addition(self.league_id, self.year, team_id, trade_items)
		self.points_breakdown['pointsFromTrade'] = points

	def points_from_adds(self, team_id):
		add_items = self.data_store.select_adds_by_team(self.league_id, self.year, team_id)
		points = self.data_store.select_points_from_addition(self.league_id, self.year, team_id, add_items)
		self.points_breakdown['pointsFromWaivers'] = points

	def trades(self, team_id):
		trades = self.data_store.select_trades_by_trade_id(self.league_id, self.year, team_id)
		for trade_id in trades:
			for trade in trades[trade_id]:
				trade['points'] = self.data_store.select_points_since_trade(self.league_id, self.year, trade['player'], trade['date'])
		self.team_trades = dict(trades)

class OptimalLineups:
	def __init__(self, league_id, data_store, year = '2017'):
		self.league_id = league_id
		self.data_store = data_store
		self.year = year
		self.position_order = (0, 1, 2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 3, 5, 23, 7, 15)
		self.optimal_lineup = dict()

	def optimal_lineups(self, team_id):
		optimal_lineups = dict()
		rosters = self.data_store.select_roster_slots(self.league_id, self.year, team_id)

		for matchup_id in rosters:
			used_players = list()
			optimal_lineups[matchup_id] = dict()
			for position in self.position_order:
				if position in rosters[matchup_id]:
					eligible_players = self.data_store.select_eligible_players(self.league_id, self.year, team_id, matchup_id, position)
					optimal_lineups[matchup_id][position] = list()
					for i in range(0, rosters[matchup_id][position]):
						for eligible_player in eligible_players:
							if eligible_player not in used_players:
								optimal_lineups[matchup_id][position].append(eligible_player)
								used_players.append(eligible_player)
								break
		self.optimal_lineup = optimal_lineups

