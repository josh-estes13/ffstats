from flask import Flask, jsonify, render_template, request, send_from_directory, send_file, g, url_for
from jinja2 import Template
from celery import Celery
from EspnInterface import *
from DataHandler import *
import json
import sys
import time
import statistics
import os
import psycopg2
import DataStore
import urllib.parse
import redis

app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task(bind=True)
def initialize_league_data(self, league_id, year):
	with app.app_context():

		conn = get_db()
		cursor = conn.cursor()
		data_store = DataStore.DataStore(conn, cursor)

		status = ''

		if data_store.league_exists(league_id, year):
			if data_store.select_data_status(league_id, year):
				status = 'Completed'
				self.update_state(state='PROGRESS', meta={'current': 99, 'total': 100, 'status': status})
				return {'current': 100, 'total': 100, 'status': status, 'result': 1}
			else:
				status = 'Preparing'
				self.update_state(state='PROGRESS', meta={'current': 0, 'total': 100, 'status': status})
				data_store.clear_league_data(league_id, year)

		status = 'Compiling League Data'
		self.update_state(state='PROGRESS', meta={'current': 1, 'total': 100, 'status': status})
		league_data = LeagueData.LeagueData(league_id, data_store, year)
		if not league_data.success:
			status = 'Failed to Gather League Data'
			data_store.clear_league_data(league_id, year)
			self.update_state(state='FAILURE', meta={'current': 0, 'total': 100, 'status': status})
			return {'current': 100, 'total': 100, 'status': status}
		
		status = 'Compiling Game Data'
		self.update_state(state='PROGRESS', meta={'current': 16, 'total': 100, 'status': status})
		game_data = GameData.GameData(league_id, data_store, year)
		if not game_data.success:
			status = 'Failed to Gather Game Data'
			data_store.clear_league_data(league_id, year)
			self.update_state(state='FAILURE', meta={'current': 0, 'total': 100, 'status': status})
			return {'current': 100, 'total': 100, 'status': status}

		status = 'Compiling Transaction Data'
		self.update_state(state='PROGRESS', meta={'current': 76, 'total': 100, 'status': status})
		transaction_data = TransactionData.TransactionData(league_id, data_store, year)
		if not transaction_data.success:
			status = 'Failed to Gather Transaction Data'
			data_store.clear_league_data(league_id, year)
			self.update_state(state='FAILURE', meta={'current': 0, 'total': 100, 'status': status})
		
		status = 'Finalizing'
		self.update_state(state='PROGRESS', meta={'current': 98, 'total': 100, 'status': 'Finalizing'})
		data_store.insert_data_status(league_id, year, True)

		status = 'Completed'
		return {'current': 100, 'total': 100, 'status': status, 'result': 1}

def connect_db():
	try:
		urllib.parse.uses_netloc.append("postgres")
		url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_GOLD_URL"])
		conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
		return conn
	except e:
		pass

def get_db():
	if not hasattr(g, 'ffstats_db'):
		g.ffstats_db = connect_db()
	return g.ffstats_db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'ffstats_db'):
		g.ffstats_db.close()
 
@app.route('/')
def index():
	return send_from_directory('src', 'index.html')

@app.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('src/js', path)

@app.route('/css/<path:path>')
def send_css(path):
	return send_from_directory('src/css', path)

@app.route('/img/<path:path>')
def send_image(path):
	return send_from_directory('src/img', path)

@app.route('/scss/<path:path>')
def send_scss(path):
	return send_from_directory('src/scss', path)

@app.route('/node_modules/<path:path>')
def send_node_modules(path):
	return send_from_directory('node_modules', path)

@app.route('/<path:path>')
def send_file(path):
	return send_from_directory('src', path)

@app.route('/status/<task_id>')
def taskstatus(task_id):
	task = initialize_league_data.AsyncResult(task_id)
	if task.state == 'PENDING':
		# job did not start yet
		response = {
			'state': task.state,
			'current': 1,
			'total': 100,
			'status': 'Pending...'
		}
	elif task.state != 'FAILURE':
		response = {
			'state': task.state,
			'current': task.info.get('current', 1),
			'total': task.info.get('total', 100),
			'status': task.info.get('status', '')
		}
		if 'result' in task.info:
			response['result'] = task.info['result']
	else:
		response = {
			'state': task.state,
			'current': 1,
			'total': 1,
			'status': str(task.info)
		}

	return jsonify(response)

@app.route('/seasons/', methods=['GET'])
def seasons():

	conn = get_db()
	cursor = conn.cursor()

	league_id = request.args.get('leagueId')
	data_store = DataStore.DataStore(conn, cursor)

	data = dict()
	data['status'] = False
	data['seasons'] = list()
	league_status = LeagueStatus.LeagueStatus(league_id)
	if league_status.status:
		data['status'] = True
		data['seasons'] = league_status.seasons

	return jsonify(data)

@app.route('/league/', methods=['GET'])
def league():

	conn = get_db()
	cursor = conn.cursor()

	league_id = request.args.get('leagueId')
	year = request.args.get('seasonId')
	data_store = DataStore.DataStore(conn, cursor)

	return render_template('league.html', leagueId=league_id, seasonId=year)

@app.route('/state/', methods=['GET'])
def exists():

	conn = get_db()
	cursor = conn.cursor()

	league_id = request.args.get('leagueId')
	year = request.args.get('seasonId')
	data_store = DataStore.DataStore(conn, cursor)

	task = initialize_league_data.delay(league_id, year)

	return jsonify({}), 202, {'Location': url_for('taskstatus', _external=True, _scheme='https', task_id=task.id)}

@app.route('/leagueId/', methods=['GET'])
def leagueId():

	conn = get_db()
	cursor = conn.cursor()

	league_id = request.args.get('leagueId')
	year = request.args.get('seasonId')
	data_store = DataStore.DataStore(conn, cursor)

	if not data_store.league_exists(league_id, year):
		LeagueData.LeagueData(league_id, data_store, year)
		GameData.GameData(league_id, data_store, year)
		TransactionData.TransactionData(league_id, data_store, year)

	data = dict() 
	data['league'] = data_store.select_league_name(league_id, year)
	data['teams'] = data_store.select_teams(league_id, year)

	return jsonify(data)

@app.route('/team/', methods=['GET', 'POST'])
def team_page():

	league_id = request.args.get('leagueId')
	year = request.args.get('seasonId')
	team_id = request.args.get('team')

	return render_template('team.html', leagueId=league_id, teamId=team_id, seasonId=year)

@app.route('/data/', methods=['GET', 'POST'])
def team_data():

	conn = get_db()
	cursor = conn.cursor()

	league_id = request.args.get('id')
	team_id = request.args.get('team')
	year = request.args.get('season')

	conn = get_db()
	cursor = conn.cursor()

	data_store = DataStore.DataStore(conn, cursor)

	if not data_store.league_exists(league_id, year):
		LeagueData.LeagueData(league_id, data_store, year)
		GameData.GameData(league_id, data_store, year)
		TransactionData.TransactionData(league_id, data_store, year)

	expected_record = LeagueStats.ExpectedRecord(league_id, data_store, team_id, year)
	league_averages = LeagueStats.LeagueAverages(league_id, data_store, team_id, year)
	transaction_stats = LeagueStats.TransactionStats(league_id, data_store, team_id, year)
	optimal_lineup = LeagueStats.OptimalLineups(league_id, data_store, team_id, year)

	data = dict()
	data['teamData'] = data_store.select_team(league_id, year, team_id)

	data['expectedRecordData'] = expected_record.expected_record

	data['leagueAveragesData'] = dict()
	data['leagueAveragesData']['teamScores'] = league_averages.team_scores
	data['leagueAveragesData']['leagueMedianScores'] = league_averages.league_median_scores
	data['leagueAveragesData']['teamScoresByPosition'] = league_averages.team_scores_by_position
	data['leagueAveragesData']['leagueScoresByPosition'] = league_averages.league_scores_by_position

	data['transactionData'] = dict()
	data['transactionData']['pointsBreakdown'] = transaction_stats.points_breakdown
	data['transactionData']['tradePlayers'] = transaction_stats.trade_players
	data['transactionData']['waiverPlayers'] = transaction_stats.waiver_players
	data['transactionData']['teamTrades'] = transaction_stats.team_trades
	data['transactionData']['playerList'] = transaction_stats.all_players
	data['optimalLineups'] = optimal_lineup.optimal_lineup
	data['teamLineups'] = optimal_lineup.team_lineups

	return jsonify(data)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port)
