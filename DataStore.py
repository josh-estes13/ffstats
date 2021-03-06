import json

class DataStore:
	def __init__(self, connection, cursor):
		self.connection = connection
		self.cursor = cursor

	def insert_data_status(self, league_id, year, status):
		sql = 'INSERT INTO status VALUES(%s, %s, %s);'
		self.cursor.execute(sql, (league_id, year, status))
		self.connection.commit()

	def select_data_status(self, league_id, year):
		sql = 'SELECT data_stored FROM status WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for data_stored, in self.cursor:
			return data_stored
		return False

	def insert_league(self, league_data):
		sql = 'INSERT INTO league VALUES(%s, %s, %s, %s, %s);'
		self.cursor.execute(sql, tuple(league_data))
		self.connection.commit()

	def select_league_matchup_ids(self, league_id, year):
		sql = 'SELECT last_matchup_id FROM league WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for last_matchup_id, in self.cursor:
			return last_matchup_id

	def select_league_name(self, league_id, year):
		sql = 'SELECT league_name FROM league WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for name, in self.cursor:
			return name
		return False

	def insert_team(self, team_data):
		sql = 'INSERT INTO teams VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
		self.cursor.execute(sql, tuple(team_data))
		self.connection.commit()

	def select_team_ids(self, league_id, year):
		team_ids = list()
		sql = 'SELECT team_id FROM teams WHERE league_id = %s and year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for team_id, in self.cursor:
			team_ids.append(team_id)
		return team_ids

	def league_exists(self, league_id, year):
		sql = 'SELECT league_id FROM league WHERE league_id = %s and year = %s;'
		self.cursor.execute(sql, (league_id, year))
		if len(self.cursor.fetchall()) != 0:
			return True
		return False

	def insert_matchup_data(self, matchup_data):
		sql = 'INSERT INTO matchups VALUES(%s, %s, %s, %s, %s, %s);'
		self.cursor.executemany(sql, tuple(matchup_data))
		self.connection.commit()

	def insert_roster_data(self, roster_data):
		for roster in roster_data:
			sql = 'INSERT INTO rosters VALUES(%s, %s, %s, %s, %s, %s, %s, %s);'
			self.cursor.executemany(sql, roster)
			self.connection.commit()

	def insert_eligible_data(self, eligible_slots_data):
		for eligible_slots in eligible_slots_data:
			sql = 'INSERT INTO eligibles VALUES(%s, %s, %s, %s, %s, %s);'
			self.cursor.executemany(sql, eligible_slots)
			self.connection.commit()

	def select_roster_data(self, league_id, year):
		rosters = list()
		sql = 'SELECT team_id, matchup_period_id, player_id FROM rosters WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for team_id, matchup_period_id, player_id in self.cursor:
			roster_data = {
				'team_id': team_id,
				'matchup_period_id': matchup_period_id,
				'player_id': player_id
			}
			rosters.append(dict(roster_data))
		return rosters

	def player_exists(self, player_id):
		sql = 'SELECT COUNT(player_id) FROM players WHERE player_id = %s;'
		self.cursor.execute(sql, (player_id,))
		for count in self.cursor:
			if count[0] == 0:
				return False
			return True

	def insert_player_data(self, player_data):
		for players in player_data:
			for player in players:
				player_id, first, last, position, team = player
				if not self.player_exists(player_id):
					sql = 'INSERT INTO players VALUES(%s, %s, %s, %s, %s);'
					self.cursor.execute(sql, player)
					self.connection.commit()

	def select_player_ids(self, league_id, year):
		sql = 'SELECT DISTINCT player_id FROM rosters WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		players = list(self.cursor.fetchall())
		return players

	def insert_adds(self, adds):
		sql = 'INSERT INTO adds VALUES(%s, %s, %s, %s, %s);'
		self.cursor.executemany(sql, adds)
		self.connection.commit()

	def insert_drops(self, drops):
		sql = 'INSERT INTO drops VALUES(%s, %s, %s, %s, %s);'
		self.cursor.executemany(sql, drops)
		self.connection.commit()

	def insert_trades(self, trades):
		sql = 'INSERT INTO trades VALUES(%s, %s, %s, %s, %s, %s, %s);'
		self.cursor.executemany(sql, trades)
		self.connection.commit()

	def insert_pro_game_data(self, games):
		sql = 'INSERT INTO progames VALUES(%s, %s, %s, %s, %s, %s, %s);'
		self.cursor.executemany(sql, tuple(games))
		self.connection.commit()

	def select_teams(self, league_id, year):
		teams = list()
		sql = 'SELECT team_id, team_abbreviation, team_name, logo, total_transactions, trades, wins, losses, points_scored, points_against, standing FROM teams WHERE league_id = %s and year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for team_id, team_abbreviation, team_name, logo, total_transactions, trades, wins, losses, points_scored, points_against, standing in self.cursor:
			team = dict()
			team['team'] = team_name
			team['initials'] = team_abbreviation
			team['wins'] = wins
			team['losses'] = losses
			team['image'] = logo
			team['rank'] = standing
			team['transactions'] = total_transactions
			team['trades'] = trades
			team['pointsFor'] = points_scored
			team['pointsAgainst'] = points_against
			team['id'] = team_id
			teams.append(dict(team))
		return teams

	def select_team_scores(self, league_id, year, team_id):
		scores = dict()
		sql = 'SELECT score, matchup_period_id FROM matchups WHERE league_id = %s AND year = %s AND team_id = %s;'
		self.cursor.execute(sql, (league_id, year, team_id))
		for score, matchup_period_id in self.cursor:
			scores[matchup_period_id] = score
		return scores

	def select_league_scores(self, league_id, year):
		scores = dict()
		sql = 'SELECT score, matchup_period_id FROM matchups WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for score, matchup_period_id in self.cursor:
			if matchup_period_id not in scores:
				scores[matchup_period_id] = list()
			scores[matchup_period_id].append(score)
		return scores

	def select_matchup_ids(self, league_id, year):
		matchup_ids = list()
		sql = 'SELECT matchup_period_id FROM matchups WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for matchup_id, in self.cursor:
			matchup_ids.append(matchup_id)
		return matchup_ids

	def select_league_scores_by_week(self, league_id, year, matchup_id):
		scores = list()
		sql = 'SELECT score FROM matchups WHERE league_id = %s AND year = %s AND matchup_period_id = %s;'
		self.cursor.execute(sql, (league_id, year, matchup_id))
		for score, in self.cursor:
			scores.append(score)
		return scores

	def select_team_scores_by_position(self, league_id, year, team_id):
		scores = dict()
		sql = 'SELECT slot_id, score FROM rosters WHERE league_id = %s AND year = %s AND team_id = %s;'
		self.cursor.execute(sql, (league_id, year, team_id))
		for slot_id, score in self.cursor:
			if slot_id not in scores:
				scores[slot_id] = list()
			scores[slot_id].append(score)
		return scores

	def select_league_scores_by_position(self, league_id, year):
		scores = dict()
		sql = 'SELECT slot_id, score FROM rosters WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		for slot_id, score in self.cursor:
			if slot_id not in scores:
				scores[slot_id] = list()
			scores[slot_id].append(score)
		return scores

	def select_trades_by_team(self, league_id, year, team_id):
		sql = 'SELECT player_id, date FROM trades WHERE league_id = %s AND year = %s AND team_id = %s AND send_receive = 0;'
		self.cursor.execute(sql, (league_id, year, team_id))
		return self.cursor.fetchall()

	def select_adds_by_team(self, league_id, year, team_id):
		sql = 'SELECT player_id, date FROM adds WHERE league_id = %s AND year = %s AND team_id = %s;'
		self.cursor.execute(sql, (league_id, year, team_id))
		return self.cursor.fetchall()

	def select_trades_by_trade_id(self, league_id, year, team_id):
		trades = dict()
		sql = 'SELECT trade_id, player_id, team_id, send_receive, date FROM trades WHERE league_id = %s AND year = %s AND trade_id in (SELECT DISTINCT trade_id FROM trades WHERE league_id = %s AND year = %s AND team_id = %s);'
		self.cursor.execute(sql, (league_id, year, league_id, year, team_id))
		for trade_id, player_id, team_id, send_receive, date in self.cursor:
			if trade_id not in trades:
				trades[trade_id] = list()
			trade_item = dict()
			trade_item['player'] = player_id
			trade_item['team'] = team_id
			trade_item['send'] = send_receive
			trade_item['date'] = date
			trades[trade_id].append(dict(trade_item))
		return trades

	def select_points_from_addition(self, league_id, year, team_id, items):
		total_score = 0
		players = dict()
		for item in items:
			player_id, date = item
			sql = 'SELECT DISTINCT rosters.score, rosters.matchup_period_id FROM rosters INNER JOIN players ON rosters.player_id = players.player_id LEFT OUTER JOIN progames ON (players.team_id = progames.away_team_id OR players.team_id = progames.home_team_id) AND (rosters.matchup_period_id = progames.matchup_period_id) WHERE rosters.league_id = %s AND rosters.year = %s AND rosters.team_id = %s AND rosters.player_id = %s AND rosters.slot_id != 20 AND rosters.slot_id != 21 AND rosters.slot_id != 22 AND progames.date >= %s ORDER BY rosters.matchup_period_id ASC;'
			self.cursor.execute(sql, (league_id, year, team_id, player_id, date))
			current_matchup_id = None
			for score, matchup_id in self.cursor:
				if current_matchup_id == None or current_matchup_id == matchup_id - 1:
					current_matchup_id = matchup_id
					total_score = total_score + score
					if player_id not in players:
						players[player_id] = self.select_player(player_id)
						players[player_id]['points'] = 0.0
					players[player_id]['points'] = players[player_id]['points'] + score
				else:
					break
		return total_score, players

	def select_points_since_trade(self, league_id, year, player_id, date):
		total_score = 0
		sql = 'SELECT DISTINCT rosters.score FROM rosters INNER JOIN players ON rosters.player_id = players.player_id LEFT OUTER JOIN progames ON (players.team_id = progames.away_team_id OR players.team_id = progames.home_team_id) AND (rosters.matchup_period_id = progames.matchup_period_id) WHERE rosters.league_id = %s AND rosters.year = %s AND rosters.player_id = %s AND progames.date >= %s;'
		self.cursor.execute(sql, (league_id, year, player_id, date))
		for score, in self.cursor:
			total_score = total_score + score
		return total_score

	def select_roster_slots(self, league_id, year, team_id):
		rosters = dict()
		sql = 'SELECT matchup_period_id, slot_id FROM rosters WHERE league_id = %s AND year = %s AND team_id = %s;'
		self.cursor.execute(sql, (league_id, year, team_id))
		for matchup_period, slot_id in self.cursor:
			if matchup_period not in rosters:
				rosters[matchup_period] = dict()
			if slot_id not in rosters[matchup_period]:
				rosters[matchup_period][slot_id] = 0
			rosters[matchup_period][slot_id] = rosters[matchup_period][slot_id] + 1
		return rosters

	def select_eligible_players(self, league_id, year, team_id, matchup_period, slot):
		players = list()
		sql = 'SELECT eligibles.player_id, rosters.score FROM eligibles INNER JOIN rosters ON rosters.player_id = eligibles.player_id AND rosters.team_id = eligibles.team_id AND rosters.matchup_period_id = eligibles.matchup_period_id WHERE eligibles.league_id = %s AND rosters.league_id = %s AND eligibles.year = %s AND rosters.year = %s AND eligibles.team_id = %s AND rosters.team_id = %s AND eligibles.matchup_period_id = %s AND rosters.matchup_period_id = %s AND eligibles.eligible_slot = %s ORDER BY rosters.score DESC;'
		self.cursor.execute(sql, (league_id, league_id, year, year, team_id, team_id, matchup_period, matchup_period, slot))
		for player_id, score in self.cursor:
			players.append(tuple((player_id, score)))
		return tuple(players)

	def select_total_points(self, league_id, year, team_id):
		sql = 'SELECT points_scored FROM teams WHERE league_id = %s AND year = %s AND team_id = %s;'
		self.cursor.execute(sql, (league_id, year, team_id))
		for points_scored, in self.cursor:
			return points_scored
		return False

	def select_team(self, league_id, year, team_id):
		teams = list()
		sql = 'SELECT team_abbreviation, team_name, logo, total_transactions, trades, wins, losses, points_scored, points_against, standing FROM teams WHERE league_id = %s AND year = %s AND team_id = %s;'
		self.cursor.execute(sql, (league_id, year, team_id))
		for team_abbreviation, team_name, logo, total_transactions, trades, wins, losses, points_scored, points_against, standing in self.cursor:
			team = dict()
			team['team'] = team_name
			team['initials'] = team_abbreviation
			team['wins'] = wins
			team['losses'] = losses
			team['image'] = logo
			team['rank'] = standing
			team['transactions'] = total_transactions
			team['trades'] = trades
			team['pointsFor'] = points_scored
			team['pointsAgainst'] = points_against
			team['id'] = team_id
			return team

	def select_player(self, player_id):
		sql = 'SELECT players.first_name, players.last_name, positions.position, proteams.team_city, proteams.team_name, players.image FROM players LEFT JOIN positions ON players.position_id = positions.position_id LEFT JOIN proteams ON players.team_id = proteams.team_id WHERE players.player_id = %s;'
		self.cursor.execute(sql, (player_id,))
		for first_name, last_name, position, team_city, team_name, image in self.cursor:
			player = dict()
			player['firstName'] = first_name
			player['lastName'] = last_name
			player['position'] = position
			player['city'] = team_city
			player['teamName'] = team_name
			player['image'] = image
			return player

	def select_slot(self, slot_id):
		sql = 'SELECT position FROM slots WHERE slot_id = %s;'
		self.cursor.execute(sql, (slot_id,))
		for position, in self.cursor:
			return position
		return False

	def select_all_starters(self, league_id, year, team_id):
		players = dict()
		sql = 'SELECT player_id, score, projected_points FROM rosters WHERE league_id = %s AND year = %s AND team_id = %s AND slot_id != 20 AND slot_id != 21;'
		self.cursor.execute(sql, (league_id, year, team_id))
		for player_id, score, projected_points in self.cursor:
			if player_id not in players:
				players[player_id] = {'score': 0.0, 'projected': 0.0}
			players[player_id]['score'] = players[player_id]['score'] + score
			players[player_id]['projected'] = players[player_id]['projected'] + projected_points
		return players

	def select_starter_by_matchup(self, league_id, year, team_id):
		players = dict()
		sql = 'SELECT player_id, matchup_period_id, slot_id, score FROM rosters WHERE slot_id != 20 AND slot_id != 21 AND league_id = %s AND year = %s AND team_id = %s;'
		self.cursor.execute(sql, (league_id, year, team_id))
		for player_id, matchup_id, slot_id, score in self.cursor:
			if matchup_id not in players:
				players[matchup_id] = dict()
			if slot_id not in players[matchup_id]:
				players[matchup_id][slot_id] = list()
			players[matchup_id][slot_id].append(tuple((player_id, score)))
		return players

	def select_team_name(self, league_id, year, team_id):
		sql = 'SELECT team_name FROM teams WHERE league_id = %s AND year = %s AND team_id = %s;'
		self.cursor.execute(sql, (league_id, year, team_id))
		for team_name, in self.cursor:
			return team_name
		return False

	def select_player_starts(self, league_id, year, team_id, player_id):
		sql = 'SELECT COUNT(matchup_period_id) FROM rosters WHERE league_id = %s AND year = %s AND team_id = %s AND player_id = %s AND slot_id != 20 AND slot_id != 21;'
		self.cursor.execute(sql, (league_id, year, team_id, player_id))
		for count, in self.cursor:
			return count
		return False

	def clear_league_data(self, league_id, year):
		sql = 'DELETE FROM league WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()

		sql = 'DELETE FROM rosters WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()

		sql = 'DELETE FROM matchups WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()

		sql = 'DELETE FROM teams WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()

		sql = 'DELETE FROM progames WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()

		sql = 'DELETE FROM trades WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()

		sql = 'DELETE FROM adds WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()

		sql = 'DELETE FROM drops WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()

		sql = 'DELETE FROM eligibles WHERE league_id = %s AND year = %s;'
		self.cursor.execute(sql, (league_id, year))
		self.connection.commit()


