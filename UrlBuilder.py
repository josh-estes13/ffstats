import re
import sys

class UrlBuilder:
	def __init__(self, league_id, season_id):
		self.league_id = league_id
		self.season_id = season_id

	def valid_url(self, url):
		return True

	def league_standings_url(self):
		owner_info_url = 'http://games.espn.com/ffl/standings'
		id_tag = 'leagueId=' + self.league_id
		season_tag = 'seasonId=' + self.season_id
		
		url = owner_info_url + '?' + id_tag + '&' + season_tag
		if self.valid_url(url):
			return url
		return False
		
	def team_page_url(self, team_page):
		url = 'http://games.espn.com' + team_page
		if self.valid_url(url):
			return url
		return False
		
	def league_schedule_url(self):
		league_schedule_url = 'http://games.espn.com/ffl/schedule'
		id_tag = 'leagueId=' + self.league_id
		season_tag = 'seasonId=' + self.season_id
		
		url = league_schedule_url + '?' + id_tag + '&' + season_tag
		if self.valid_url(url):
			return url
		return False
		
	def contest_url(self, contest_page):
		url = 'http://games.espn.com' + contest_page
		if self.valid_url(url):
			return url
		return False
		
	def activity_url(self, activity_type):
		id_tag = 'leagueId=' + self.league_id
		season_tag = 'seasonId=' + self.season_id
		start_date = 'startDate=' + self.season_id + '0731'
		end_date = 'endDate=' + self.season_id + '1226'
		activity_tag = 'activityType=2'
		transaction_tag = ''
		
		if activity_type == 'Waivers':
			transaction_tag = 'tranType=2'
		elif activity_type == 'Trades':
			transaction_tag = 'tranType=4'
		
		activity_url = 'http://games.espn.com/ffl/recentactivity'
		url = activity_url + '?' + id_tag + '&' + season_tag + '&' + start_date + '&' + end_date + '&' + activity_tag + '&' + transaction_tag
		
		if self.valid_url(url):
			return url
		return False
		