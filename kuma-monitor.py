#!/usr/bin/env python3

import requests
import re
import sys
import time
import os
import signal
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

def parse_monitor_status(metrics_data: str) -> List[Tuple[str, str, str, str]]:
	monitors = []
	pattern = r'monitor_status\{monitor_name="([^"]+)",monitor_type="([^"]+)"[^}]*\} (\d+)'
	matches = re.findall(pattern, metrics_data)

	for monitor_name, monitor_type, status_code in matches:
		status = STATUS_MAP.get(status_code, "UNKNOWN")

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

		monitors.append((monitor_name, status, color, monitor_type))

	return monitors

def display_monitors(monitors: List[Tuple[str, str, str, str]]):
	if not monitors:
		print("No monitors found")
		return

	monitors.sort(key=lambda x: x[0])
	max_name_length = max(len(monitor_name) for monitor_name, _, _, _ in monitors) if monitors else 0
	max_type_length = max(len(monitor_type) for _, _, _, monitor_type in monitors) if monitors else 0

	if SHOW_HEADER:
		header = f"{'STATUS':<15} {'NAME':<{max_name_length + 2}} {'TYPE':<{max_type_length + 2}}"
		print(f"{Colors.NC}{header}{Colors.NC}")

	for monitor_name, status, color, monitor_type in monitors:
		status_formatted = f"[{status}]"
		status_padded = f"{status_formatted:<15}"
		name_padded = f"{monitor_name:<{max_name_length + 2}}"
		type_padded = f"{monitor_type:<{max_type_length + 2}}"
		print(f"{color}{status_padded} {name_padded} {type_padded}{Colors.NC}")

def signal_handler(signum, frame):
	print(f"\n{Colors.YELLOW}exiting...{Colors.NC}")
	sys.exit(0)

def main():
	signal.signal(signal.SIGINT, signal_handler)
	first_run = True

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
		print('\033[H', end='', flush=True)
		display_monitors(monitors)

		if SHOW_COUNTDOWN:
			for i in range(UPDATE_INTERVAL, 0, -1):
				print(f"next update: {i}s", end='', flush=True)
				time.sleep(1)
				print('\r' + ' ' * 50 + '\r', end='', flush=True)
		else:
			time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
	main()