import requests
import threading
import random
import argparse
import uuid
import logging
import os
from decimal import Decimal

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get the base URL from an environment variable
base_url = os.getenv('BASE_URL', 'http://localhost:18084')

# Create the parser and add arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--num_threads", type=int, default=10)
parser.add_argument("-w", "--num_wallets", type=int, default=100)
parser.add_argument("-b", "--initial_balance", type=float, default=1000.0)
parser.add_argument("-n", "--num_iters", type=int, default=1000)
args = parser.parse_args()

# Get the parameters from the arguments
num_threads = args.num_threads
num_wallets = args.num_wallets
initial_balance = args.initial_balance
num_iters = args.num_iters

# Print out all the parameters
logging.info(f"Number of threads: {num_threads}")
logging.info(f"Number of wallets: {num_wallets}")
logging.info(f"Initial balance: {initial_balance}")
logging.info(f"Number of iterations: {num_iters}")

# Initialize each of the wallet with initial balance
wallet_ids = []
for i in range(num_wallets):
    userId = str(uuid.uuid4())  # Generate a random UUID and convert it to a string
    wallet = {"balance": str(Decimal(initial_balance)), "userId": userId}
    try:
        response = requests.post(f"{base_url}/wallets", json=wallet)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to create wallet: {e}")
        continue
    wallet_ids.append(response.json()['id'])

# Sum the balances of all wallets
initial_total_balance = num_wallets * initial_balance

# Print out the initial balance
logging.info(f"Initial total balance: {initial_total_balance}")

# Initialize counters
successful_debits = 0
failed_debits = 0
successful_credits = 0
failed_credits = 0

# Define the function to be run in each thread
def run_thread():
    global successful_debits, failed_debits, successful_credits, failed_credits
    for _ in range(num_iters):
        # Pick two different wallets randomly
        wallet_id1, wallet_id2 = random.sample(wallet_ids, 2)
        # Debit a fixed amount of balance from one wallet to another
        try:
            amount = Decimal(10.0)
            json_data = {"amount": str(amount)}
            logging.info(f"JSON data sent: {json_data}")
            response = requests.post(f"{base_url}/wallets/{wallet_id1}/debit", json=json_data)
            response.raise_for_status()
            successful_debits += 1
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to debit balance: {e}")
            failed_debits += 1

        try:
            response = requests.post(f"{base_url}/wallets/{wallet_id2}/credit", json=json_data)
            response.raise_for_status()
            successful_credits += 1
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to credit balance: {e}")
            failed_credits += 1

# Launch the num_threads threads
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=run_thread)
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Print out the breakdown of successful and failed operations
logging.info(f"Successful debits: {successful_debits}")
logging.info(f"Failed debits: {failed_debits}")
logging.info(f"Successful credits: {successful_credits}")
logging.info(f"Failed credits: {failed_credits}")

# Sum the balances of all wallets
final_total_balance = 0
for wallet_id in wallet_ids:
    try:
        response = requests.get(f"{base_url}/wallets/{wallet_id}")
        response.raise_for_status()
        final_total_balance += response.json()['balance']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get wallet balance: {e}")

# Print out the final balance
logging.info(f"Final total balance: {final_total_balance}")

# Validate the the sum of step 2 is same as the sum of step 4
assert initial_total_balance == final_total_balance, "The total balance before and after the transactions do not match"