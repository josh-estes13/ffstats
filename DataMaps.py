class DataMaps:
	def __init__(self):
		self._position_map = {
			0: 'QB',
			1: 'TQB',
			2: 'RB',
			3: 'RB/WR',
			4: 'WR',
			5: 'WR/TE',
			6: 'TE',
			7: 'OP',
			8: 'DT',
			9: 'DE',
			10: 'LB',
			11: 'DL',
			12: 'CB',
			13: 'S',
			14: 'DB',
			15: 'DP',
			16: 'D/ST',
			17: 'K',
			18: 'P',
			19: 'HC',
			20: 'BE',
			21: 'IR',
			22: '',
			23: 'RB/WR/TE'
		}

	@property
	def position_map(self):
		return self._position_map