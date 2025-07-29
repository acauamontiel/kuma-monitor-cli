#!/usr/bin/env python3

import requests
import re
import sys
import time
import os
import signal
import json
from typing import Dict, List, Tuple

def load_env_file():
	env_file = '.env'
	if os.path.exists(env_file):
		with open(env_file, 'r') as f:
			for line in f:
				line = line.strip()
				if line and not line.startswith('#') and '=' in line:
					key, value = line.split('=', 1)
					os.environ[key] = value

load_env_file()

ENDPOINT_URL = os.getenv('KUMA_ENDPOINT', "https://up.engaged.com.br/metrics")
API_KEY = os.getenv('KUMA_API_KEY', "uk1_hnpQpSjo5Cg5m6zeWnBLAv0KgUiLGPt3wSPH9lPY")
UPDATE_INTERVAL = int(os.getenv('KUMA_UPDATE_INTERVAL', '30'))
SHOW_HEADER = os.getenv('KUMA_SHOW_HEADER', 'true').lower() == 'true'
SHOW_COUNTDOWN = os.getenv('KUMA_SHOW_COUNTDOWN', 'true').lower() == 'true'
SHOW_HISTORY = os.getenv('KUMA_SHOW_HISTORY', 'true').lower() == 'true'
HISTORY_LENGTH = int(os.getenv('KUMA_HISTORY_LENGTH', '60'))

class Colors:
	RED = '\033[0;31m'
	GREEN = '\033[0;32m'
	YELLOW = '\033[1;33m'
	BLUE = '\033[0;34m'
	NC = '\033[0m'

STATUS_MAP = {
	"1": "UP",
	"0": "DOWN",
	"2": "PENDING",
	"3": "MAINTENANCE"
}

def clear_screen():
	os.system('clear' if os.name == 'posix' else 'cls')

def load_history():
	history_file = '.kuma_history.json'
	if os.path.exists(history_file):
		try:
			with open(history_file, 'r') as f:
				return json.load(f)
		except:
			return {}
	return {}

def save_history(history):
	history_file = '.kuma_history.json'
	try:
		with open(history_file, 'w') as f:
			json.dump(history, f)
	except:
		pass

def update_history(monitors, history):
	for monitor_name, status, _, _, _ in monitors:
		if monitor_name not in history:
			history[monitor_name] = []

		history[monitor_name].append(status)

		if len(history[monitor_name]) > HISTORY_LENGTH:
			history[monitor_name] = history[monitor_name][-HISTORY_LENGTH:]

	return history

def get_status_color(status):
	if status == "UP":
		return Colors.GREEN
	elif status == "DOWN":
		return Colors.RED
	elif status == "PENDING":
		return Colors.YELLOW
	elif status == "MAINTENANCE":
		return Colors.BLUE
	else:
		return Colors.NC

def display_history_bar(history, monitor_name, max_name_length, max_type_length):
	if monitor_name not in history or not history[monitor_name]:
		return ""

	max_squares = HISTORY_LENGTH

	bar = ""
	for status in history[monitor_name]:
		color = get_status_color(status)
		bar += f"{color}■{Colors.NC}"

	if len(history[monitor_name]) > max_squares:
		bar = ""
		for status in history[monitor_name][-max_squares:]:
			color = get_status_color(status)
			bar += f"{color}■{Colors.NC}"

	return bar

def get_metrics_data() -> str:
	try:
		response = requests.get(
			ENDPOINT_URL,
			auth=("", API_KEY),
			timeout=10
		)
		response.raise_for_status()
		return response.text
	except requests.exceptions.RequestException as e:
		print(f"{Colors.RED}Error connecting to endpoint: {e}{Colors.NC}")
		return None

def parse_monitor_status(metrics_data: str) -> List[Tuple[str, str, str, str, str]]:
	monitors = []
	status_pattern = r'monitor_status\{monitor_name="([^"]+)",monitor_type="([^"]+)"[^}]*\} (\d+)'
	response_pattern = r'monitor_response_time\{monitor_name="([^"]+)"[^}]*\} ([0-9.]+)'

	status_matches = re.findall(status_pattern, metrics_data)
	response_matches = re.findall(response_pattern, metrics_data)

	response_times = {name: time for name, time in response_matches}

	for monitor_name, monitor_type, status_code in status_matches:
		status = STATUS_MAP.get(status_code, "UNKNOWN")
		response_time = response_times.get(monitor_name, "-")

		if status == "UP":
			color = Colors.GREEN
		elif status == "DOWN":
			color = Colors.RED
		elif status == "PENDING":
			color = Colors.YELLOW
		elif status == "MAINTENANCE":
			color = Colors.BLUE
		else:
			color = Colors.NC

		monitors.append((monitor_name, status, color, monitor_type, response_time))

	return monitors

def display_monitors(monitors: List[Tuple[str, str, str, str, str]], history: Dict = None):
	if not monitors:
		print("No monitors found")
		return

	monitors.sort(key=lambda x: x[0])
	max_name_length = max(len(monitor_name) for monitor_name, _, _, _, _ in monitors) if monitors else 0
	max_type_length = max(len(monitor_type) for _, _, _, monitor_type, _ in monitors) if monitors else 0

	if SHOW_HEADER:
		header = f"{'STATUS':<15} {'NAME':<{max_name_length + 2}} {'TYPE':<{max_type_length + 2}} {'RESPONSE':<10}"
		print(f"{Colors.NC}{header}{Colors.NC}")

	for monitor_name, status, color, monitor_type, response_time in monitors:
		status_formatted = f"[{status}]"
		status_padded = f"{status_formatted:<15}"
		name_padded = f"{monitor_name:<{max_name_length + 2}}"
		type_padded = f"{monitor_type:<{max_type_length + 2}}"

		if response_time == "-":
			response_padded = f"{response_time:<10}"
		else:
			response_padded = f"{response_time}ms"

		print(f"{color}{status_padded} {name_padded} {type_padded} {response_padded}{Colors.NC}")

		if SHOW_HISTORY and history:
			history_bar = display_history_bar(history, monitor_name, max_name_length, max_type_length)
			if history_bar:
				print(f"{history_bar}")

def signal_handler(signum, frame):
	print(f"\n{Colors.YELLOW}exiting...{Colors.NC}")
	sys.exit(0)

def main():
	signal.signal(signal.SIGINT, signal_handler)
	first_run = True
	history = load_history()

	while True:
		if first_run:
			clear_screen()
			first_run = False

		metrics_data = get_metrics_data()

		if metrics_data is None:
			print(f"{Colors.RED}Error getting data. Retrying in {UPDATE_INTERVAL} seconds...{Colors.NC}")
			time.sleep(UPDATE_INTERVAL)
			continue

		monitors = parse_monitor_status(metrics_data)

		history = update_history(monitors, history)
		save_history(history)

		print('\033[H', end='', flush=True)
		display_monitors(monitors, history)

		if SHOW_COUNTDOWN:
			for i in range(UPDATE_INTERVAL, 0, -1):
				print(f"next update: {i}s", end='', flush=True)
				time.sleep(1)
				print('\r' + ' ' * 50 + '\r', end='', flush=True)
		else:
			time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
	main()