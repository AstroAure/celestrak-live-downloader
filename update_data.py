import requests
import pandas as pd
import os
import json
from datetime import datetime, timedelta

sat_ids = os.getenv('SAT_INTDES_IDS', '').split(',')

os.makedirs("data", exist_ok=True)

def download_json(id):
	"""Download latests orbital data for given sat id"""
	url = f"https://celestrak.org/NORAD/elements/gp.php?INTDES={id}&FORMAT=JSON"
	response = requests.get(url)
	response.raise_for_status()
	return response.json()[0]

def update_csv(id, new_data):
	"""Updates CSV database for given sat id"""
	csv_path = f"data/{id}.csv"
	# Loads database (if it exists)
	if os.path.exists(csv_path):
		df_existing = pd.read_csv(csv_path)
	else:
		df_existing = pd.DataFrame()
		df_existing.insert(0, 'SAVED_AT', None)
		df_existing.insert(1, 'EPOCH', None)

	if new_data['EPOCH'] and (pd.to_datetime(new_data['EPOCH']) - pd.to_datetime(df_existing['EPOCH']).max() > timedelta(hours=1)):
	# if new_data['EPOCH'] and new_data['EPOCH'] not in df_existing['EPOCH']:
		# Adds a new row and timestamp
		new_row = {**new_data, 'SAVED_AT': datetime.now().isoformat()}
		df_new = pd.DataFrame([new_row])
		df_updated = pd.concat([df_existing, df_new], ignore_index=True)
		df_updated.to_csv(csv_path, index=False)
		print(f"New line added to database for satellite {id}")
		return True
	else:
		print(f"No new update for satellite {id}")
		return False

if __name__ == "__main__":
	if not sat_ids or sat_ids == ['']:
		raise ValueError("No satellite ids defined in SAT_INTDES_IDS")
	for id in sat_ids:
		id = id.strip()
		if not id:
			continue
		try:
			data = download_json(id)
			update_csv(id, data)
		except Exception as e:
			print(f"Error for satellite {id}: {e}")
			continue
