import sys
import UrlBuilder
from bs4 import BeautifulSoup
import requests

class GameData:
	def __init__(self, league_id, season = '2017'):
		self.league_id = league_id
		self.season_year = season
		self.url_builder = UrlBuilder.UrlBuilder(league_id, season)
		
	def get_game_data(self):
		
		def parse_player_table(table):
			
			def parse_player_row(player_row):
				player_data_row = player_row.select('td.playertablePlayerName')[0].text
				player_tokens = player_data_row.split(',')
				
				player_data = dict()
				player_data['Points'] = player_row.select('td.playertableStat.appliedPoints')[0].text
				
				if(len(player_tokens) == 1):
					player_tokens = player_tokens[0].split()
					player_data['Name'] = player_tokens[0]
					player_data['Team'] = player_tokens[1]
					player_data['Position'] = player_tokens[2]
					
				else:
					player_data['Name'] = player_tokens[0]
					player_tokens = player_tokens[1].split()
					player_data['Team'] = player_tokens[0]
					player_data['Position'] = player_tokens[1]
					
				return player_data
				
			player_rows = table.select('tr.pncPlayerRow')
			
			player_data = dict()
			for player_row in player_rows:
				slot = player_row.select('td.playerSlot')[0].text
				if slot not in player_data:
					player_data[slot] = list()

				player_data[slot].insert(0, parse_player_row(player_row))

			return player_data
		
		def get_name(table):
			name_row = table.select('tr.playerTableBgRowHead.tableHead.playertableTableHeader')[0]
			name = name_row.find('td').text.replace(' Box Score', '')
			return name
		
		league_schedule_url = self.url_builder.league_schedule_url()
		page = requests.get(league_schedule_url)
		soup = BeautifulSoup(page.content, 'lxml')
		
		schedule_table = soup.select('table.tableBody')[0]
		table_rows = schedule_table.select('tr')
		
		game_data = list()
		week_number = 0
		game_number = 1
		for table_row in table_rows:
			if table_row.has_attr('class') and table_row['class'][0] == 'tableHead':
				week_number = week_number + 1
				game_number = 1
			else:
				contest_page = table_row.select('nobr')
				if len(contest_page) != 0:
					contest = contest_page[0].find('a')
					link = contest['href']
					link_text = contest.text
					
					if link_text != 'Preview' and link_text != 'Box':
						contest_link = self.url_builder.contest_url(link)
						page = requests.get(contest_link)
						soup = BeautifulSoup(page.content, 'lxml')
						
						week_data = dict()
						table = soup.find('table', id='playertable_0')
						week_data['Name'] = get_name(table)
						week_data['Starters'] = parse_player_table(table)
						
						table = soup.find('table', id='playertable_1')
						week_data['Bench'] = parse_player_table(table)
						game_data.insert(0, week_data)
						
						week_data = dict()
						table = soup.find('table', id='playertable_2')
						week_data['Week'] = week_number
						week_data['GameId'] = game_number
						week_data['Name'] = get_name(table)
						week_data['Starters'] = parse_player_table(table)
						
						table = soup.find('table', id='playertable_3')
						week_data['Bench'] = parse_player_table(table)
						game_data.insert(0, week_data)
						
						game_number = game_number + 1
			
		return game_data

	def get_expected_wins(self, game_data):

		pass


