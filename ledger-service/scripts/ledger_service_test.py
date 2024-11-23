import requests
import threading
import random
import argparse
import uuid
import logging
import os
from decimal import Decimal, ROUND_HALF_UP
import time
from decimal import getcontext

# Set up logging
logging.basicConfig(level=logging.INFO)

# Get the base URL from an environment variable

# Create the parser and add arguments
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--num_threads", type=int, default=10)
parser.add_argument("-w", "--num_wallets", type=int, default=100)
parser.add_argument("-b", "--initial_balance", type=float, default=1000.0)
parser.add_argument("-n", "--num_iters", type=int, default=1000)
parser.add_argument("-s", "--server", type=str, default='vm', choices=['vm', 'local'])
parser.add_argument("-r", "--random_debit", action='store_true', help="Use random debit amount between 1.0 and 10.0")
args = parser.parse_args()

# Get the parameters from the arguments
num_threads = args.num_threads
num_wallets = args.num_wallets
initial_balance = args.initial_balance
num_iters = args.num_iters
server = args.server
random_debit = args.random_debit

if server == 'vm':
    base_url = 'https://api-vm.bxn.world/api/ledger-service'
elif server == 'local':
    base_url = 'http://localhost:18084'

# Print out all the parameters
logging.info(f"Number of threads: {num_threads}")
logging.info(f"Number of wallets: {num_wallets}")
logging.info(f"Initial balance: {initial_balance}")
logging.info(f"Number of iterations: {num_iters}")
logging.info(f"Server: {base_url}")

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
total_successful_debits = 0
total_failed_debits = 0
total_successful_credits = 0
total_failed_credits = 0
total_aborted_connections = 0

# Create a thread-local storage object
thread_local = threading.local()

# Set the debit amount
if random_debit:
    amount = Decimal(random.uniform(1.0, 10.0)).quantize(Decimal('0.00001'), rounding=ROUND_HALF_UP)
else:
    amount = Decimal(10.0).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
json_data = {"amount": str(amount)}
print(f"json_data: {json_data}")  # Print the json_data to check the amount

def run_thread():
    thread_local.successful_debits = 0
    thread_local.failed_debits = 0
    thread_local.successful_credits = 0
    thread_local.failed_credits = 0
    thread_local.aborted_connections = 0

    for _ in range(num_iters):
        # Pick two different wallets randomly
        wallet_id1, wallet_id2 = random.sample(wallet_ids, 2)

        # Debit a fixed amount of balance from one wallet to another
        retry_count = 0
        while True:
            try:
                response = requests.post(f"{base_url}/wallets/{wallet_id1}/debit", json=json_data)
                response.raise_for_status()
                thread_local.successful_debits += 1
                break
            except requests.exceptions.RequestException as e:
                if "Max retries exceeded" in str(e):
                    logging.error(f"Aborted connection: {e}")
                    thread_local.aborted_connections += 1
                else:
                    logging.error(f"Failed to debit balance: {e}")
                    thread_local.failed_debits += 1

                retry_count += 1
                wait_time_ms = min(100 * (2 ** retry_count), 10000)  # Exponential back-off starting at 100ms, capped at 10s
                #logging.info(f"Retrying debit in {wait_time_ms} milliseconds...")
                time.sleep(wait_time_ms / 1000)  # Convert milliseconds to seconds

        # Credit a fixed amount of balance to another wallet
        retry_count = 0
        while True:
            try:
                response = requests.post(f"{base_url}/wallets/{wallet_id2}/credit", json=json_data)
                response.raise_for_status()
                thread_local.successful_credits += 1
                break
            except requests.exceptions.RequestException as e:
                if "Max retries exceeded" in str(e):
                    logging.error(f"Aborted connection: {e}")
                    thread_local.aborted_connections += 1
                else:
                    logging.error(f"Failed to credit balance: {e}")
                    thread_local.failed_credits += 1

                retry_count += 1
                wait_time_ms = min(100 * (2 ** retry_count), 10000)  # Exponential back-off starting at 100ms, capped at 10s
                #logging.info(f"Retrying credit in {wait_time_ms} milliseconds...")
                time.sleep(wait_time_ms / 1000)  # Convert milliseconds to seconds

    return (thread_local.successful_debits, thread_local.failed_debits,
            thread_local.successful_credits, thread_local.failed_credits,
            thread_local.aborted_connections)

# Launch the num_threads threads
threads = []
results = []

def thread_wrapper():
    result = run_thread()
    results.append(result)

for _ in range(num_threads):
    thread = threading.Thread(target=thread_wrapper)
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Sum up the results from all threads
for result in results:
    total_successful_debits += result[0]
    total_failed_debits += result[1]
    total_successful_credits += result[2]
    total_failed_credits += result[3]
    total_aborted_connections += result[4]

# Print out the breakdown of successful and failed operations
logging.info(f"Successful debits: {total_successful_debits}")
logging.info(f"Retried debits: {total_failed_debits}")
logging.info(f"Successful credits: {total_successful_credits}")
logging.info(f"Retried credits: {total_failed_credits}")
logging.info(f"Aborted connections: {total_aborted_connections}")

# Set the precision for Decimal operations
getcontext().prec = 28

# Sum the balances of all wallets
final_total_balance = Decimal(0)
for wallet_id in wallet_ids:
    try:
        response = requests.get(f"{base_url}/wallets/{wallet_id}")
        response.raise_for_status()
        balance_str = response.json()['balance']
        print(f"response: {balance_str}")  # Print the balance to check the amount
        final_total_balance += Decimal(balance_str)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get wallet balance: {e}")

# Quantize the final total balance to the desired precision
final_total_balance = final_total_balance.quantize(Decimal('0.00001'), rounding=ROUND_HALF_UP)

# Print out the final balance
logging.info(f"Final total balance: {final_total_balance}")

# Add this line to print the sum of failed_credits and failed_debits
logging.info(f"Total retried transactions: {total_failed_credits + total_failed_debits}")

