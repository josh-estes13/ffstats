import sys
import UrlBuilder
from bs4 import BeautifulSoup
import requests

class ActivityData:
	def __init__(self, league_id, data_store, season = '2017'):
		self.league_id = league_id
		self.season_year = season
		self.url_builder = UrlBuilder.UrlBuilder(league_id, season)
		self.data_store = data_store
		
	def activity_table(self, url):
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'lxml')
		
		table = soup.select('table.tableBody')[0]
		rows = table.select('tr')
		
		return rows
		
	def set_player_data(self, name, position, team):
		player = dict()
		player['Name'] = name
		player['Position'] = position
		player['Team'] = team
		
		return player
		
	def parse_activity_date(self, date):
		children = self.get_child_list(date)
		date_tokens = (str(children[0])).split()
		
		return date_tokens[1] + ' ' + date_tokens[2]
			
	def parse_player_name(self, player_name_data):
		player_name = player_name_data.replace('<b>', '')
		player_name = player_name.replace('</b>', '')
		player_name = player_name.replace('*', '')
		
		return player_name
	
	def get_child_list(self, transaction_data):
		children = list()
		for x in transaction_data.childGenerator():
			children.append(x)
		
		return children
		
	def update_waiver_data(self):
		waiver_activity_url = self.url_builder.activity_url('Waivers')
		waiver_rows = self.activity_table(waiver_activity_url)
		
		for i in range(2, len(waiver_rows)):
			waiver_row = waiver_rows[i].select('td')
			transaction_data = waiver_row[2]
			
			children = self.get_child_list(transaction_data)
			
			j = 0
			while j < (len(children)):
				date = self.parse_activity_date(waiver_row[0]) + ', ' + self.season_year
				team = str(children[j]).split()[0]
				player = self.set_player_data(self.parse_player_name(str(children[j+1])), str(children[j+2]).split()[2], str(children[j+2]).split()[1])
				
				player_id = self.data_store.select_player_id(player['Name'], player['Position'], player['Team'])
				if player_id != 0:
					self.data_store.insert_waiver(self.league_id, team, player_id, date, self.season_year)
				
				j = j + 4
						
	def update_trade_data(self):
		trade_activity_url = self.url_builder.activity_url('Trades')
		trade_rows = self.activity_table(trade_activity_url)
		
		i = 2
		trade_id = 0
		while i < (len(trade_rows)):
			trade_id = trade_id + 1
			trade_row = trade_rows[i].select('td')
			
			transaction_data = trade_row[2]
			children = self.get_child_list(transaction_data)
			
			j = 0
			while j < (len(children)):
				date = self.parse_activity_date(trade_row[0]) + ', ' + self.season_year
				sender = str(children[j]).split()[0]
				receiver = str(children[j+2]).split()[4]
				player = self.set_player_data(self.parse_player_name(str(children[j+1])), str(children[j+2]).split()[2], str(children[j+2]).split()[1])
				
				player_id = self.data_store.select_player_id(player['Name'], player['Position'], player['Team'])
				self.data_store.insert_trade(self.league_id, trade_id, sender, receiver, player_id, date, self.season_year)
				
				j = j + 4
			
			i = i + 2
