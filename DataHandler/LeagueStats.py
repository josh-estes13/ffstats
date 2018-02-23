import statistics
import copy

class ExpectedRecord:
	def __init__(self, league_id, data_store, team_id, year = '2017'):
		self.league_id = league_id
		self.data_store = data_store
		self.year = year
		self._expected_record = dict()
		self.calculate_expected_record(team_id)

	@property
	def expected_record(self):
		return self._expected_record

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
		self.expected_record['expectedWins'] = expected_wins
		self.expected_record['expectedLosses'] = expected_losses

class LeagueAverages:
	def __init__(self, league_id, data_store, team_id, year = '2017'):
		self.league_id = league_id
		self.data_store = data_store
		self.year = year
		self._team_scores = dict()
		self._league_median_scores = dict()
		self._team_scores_by_position = dict()
		self._league_scores_by_position = dict()
		self.calculate_player_scores(team_id)
		self.calculate_median_scores()
		self.team_position_scores(team_id)
		self.league_position_scores()

	@property
	def team_scores(self):
		return self._team_scores

	@property
	def league_median_scores(self):
		return self._league_median_scores

	@property
	def team_scores_by_position(self):
		data = dict()
		for slot_id in self._team_scores_by_position:
			position = self.data_store.select_slot(slot_id)
			data[position] = self._team_scores_by_position[slot_id]
		self._team_scores_by_position = data
		return self._team_scores_by_position

	@property
	def league_scores_by_position(self):
		data = dict()
		for slot_id in self._league_scores_by_position:
			position = self.data_store.select_slot(slot_id)
			data[position] = self._league_scores_by_position[slot_id]
		self._league_scores_by_position = data
		return self._league_scores_by_position

	def calculate_player_scores(self, team_id):
		scores = self.data_store.select_team_scores(self.league_id, self.year, team_id)
		self._team_scores = dict(scores)

	def calculate_median_scores(self):
		scores = dict()
		matchup_ids = self.data_store.select_matchup_ids(self.league_id, self.year)
		for matchup_id in matchup_ids:
			week_scores = self.data_store.select_league_scores_by_week(self.league_id, self.year, matchup_id)
			scores[matchup_id] = statistics.median(week_scores)
		self._league_median_scores = dict(scores)

	def team_position_scores(self, team_id):
		scores = self.data_store.select_team_scores_by_position(self.league_id, self.year, team_id)
		position_scores = dict()
		for slot in scores:
			position_scores[slot] = round(sum(scores[slot]) / float(len(scores[slot])), 2)
		self._team_scores_by_position = dict(position_scores)

	def league_position_scores(self):
		scores = self.data_store.select_league_scores_by_position(self.league_id, self.year)
		position_scores = dict()
		for slot in scores:
			position_scores[slot] = round(sum(scores[slot]) / float(len(scores[slot])), 2)
		self._league_scores_by_position = dict(position_scores)

class TransactionStats:
	def __init__(self, league_id, data_store, team_id, year = '2017'):
		self.league_id = league_id
		self.data_store = data_store
		self.year = year
		self._points_breakdown = dict()
		self._team_trades = dict()
		self._trade_players = list()
		self._waiver_players = list()
		self._all_players = list()
		self.calc_point_breakdown(team_id)
		self.trades(team_id)

	@property
	def points_breakdown(self):
		return self._points_breakdown

	@property
	def trade_players(self):
		return self._trade_players

	@property
	def waiver_players(self):
		return self._waiver_players

	@property
	def all_players(self):
		return self._all_players

	@property
	def team_trades(self):
		return self._team_trades

	def calc_point_breakdown(self, team_id):

		def points_from_trades():
			trade_items = self.data_store.select_trades_by_team(self.league_id, self.year, team_id)
			points, players = self.data_store.select_points_from_addition(self.league_id, self.year, team_id, trade_items)
			return points, players

		def points_from_adds():
			add_items = self.data_store.select_adds_by_team(self.league_id, self.year, team_id)
			points, players = self.data_store.select_points_from_addition(self.league_id, self.year, team_id, add_items)
			return points, players

		trade_points, traded_players = points_from_trades()
		waiver_points, added_players = points_from_adds()
		draft_points = self.data_store.select_total_points(self.league_id, self.year, team_id) - trade_points - waiver_points
		all_players = self.data_store.select_all_starters(self.league_id, self.year, team_id)
		
		player_list = list()
		for player in all_players:
			player_info = self.data_store.select_player(player)
			player_info['points'] = round(all_players[player]['score'], 2)
			player_info['projected'] = round(all_players[player]['projected'], 2)
			player_info['starts'] = self.data_store.select_player_starts(self.league_id, self.year, team_id, player)
			player_list.append(dict(player_info))

		self._all_players = player_list
		self._points_breakdown['pointsFromTrade'] = round(trade_points, 2)
		self._points_breakdown['pointsFromWaivers'] = round(waiver_points, 2)
		self._points_breakdown['pointsFromDraft'] = round(draft_points, 2)

		self._trade_players = traded_players
		self._waiver_players = added_players

	def trades(self, team_id):
		something = dict()
		trades = self.data_store.select_trades_by_trade_id(self.league_id, self.year, team_id)
		for trade_id in trades:
			something[trade_id] = dict()
			something[trade_id]['sent'] = list()
			something[trade_id]['received'] = list()
			something[trade_id]['team'] = None
			for trade in trades[trade_id]:
				points = round(self.data_store.select_points_since_trade(self.league_id, self.year, trade['player'], trade['date']), 2)
				player = self.data_store.select_player(trade['player'])
				player['points'] = points
				something[trade_id]['date'] = trade['date']
				if int(team_id) == int(trade['team']):
					if trade['send'] == 1:
						something[trade_id]['sent'].append(dict(player))
					else:
						something[trade_id]['received'].append(dict(player))
				else:
					if something[trade_id]['team'] == None:
						something[trade_id]['team'] = self.data_store.select_team_name(self.league_id, self.year, trade['team'])
		self._team_trades = dict(something)

class OptimalLineups:
	def __init__(self, league_id, data_store, team_id, year = '2017'):
		self.league_id = league_id
		self.data_store = data_store
		self.year = year
		self.team_id = team_id
		self.position_order = (0, 1, 2, 4, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 3, 5, 23, 7, 15)
		self._optimal_lineup = dict()
		self._team_lineups = dict()
		self.optimal_lineups(team_id)

	@property
	def team_lineups(self):
		lineups = dict()
		rosters = self.data_store.select_starter_by_matchup(self.league_id, self.year, self.team_id)
		for matchup_id in rosters:
			lineups[matchup_id] = dict()
			for slot_id in rosters[matchup_id]:
				slot = self.data_store.select_slot(slot_id)
				if slot not in lineups[matchup_id]:
					lineups[matchup_id][slot] = list()
				for player_id, score in rosters[matchup_id][slot_id]:
					player = self.data_store.select_player(player_id)
					player['points'] = score
					lineups[matchup_id][slot].append(player)
		self._team_lineups = dict(lineups)
		return self._team_lineups

	@property
	def optimal_lineup(self):
		data = dict()
		for matchup_id in self._optimal_lineup:
			data[matchup_id] = dict()
			for position in self._optimal_lineup[matchup_id]:
				slot = self.data_store.select_slot(position)
				data[matchup_id][slot] = list()
				for player_id, score in self._optimal_lineup[matchup_id][position]:
					player = self.data_store.select_player(player_id)
					player['points'] = score
					data[matchup_id][slot].append(dict(player))
		self._optimal_lineup = data
		return self._optimal_lineup

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
		self._optimal_lineup = optimal_lineups

