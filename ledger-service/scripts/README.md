# delete_all_entries.sh

The `delete_all_entries.sh` script is used to delete all entries from a specified table in a database. The script reads configuration values from a `.env` file located in the user's home directory and allows overriding these values through command line arguments.

#### Command Line Arguments

- `-u`: Username for the database.
- `-p`: Password for the database.
- `-d`: Database name.
- `-t`: Table name.

#### Example Usage

```bash
delete_all_entries.sh -u myusername -p mypassword -d mydatabase -t mytable
```

# ledger_service_test.py

The `ledger_service_test.py` is designed to test the ledger service by creating wallets, performing debit and credit operations, and verifying the final balances. It uses multithreading to simulate concurrent transactions.

## Prerequisites

- Python 3.11 or higher
- Required Python packages: `requests`, `decimal`, `logging`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-repo/bxn-exchange.git
    cd bxn-exchange/ledger-service
    ```

2. Install the required packages:
    ```sh
    pip install requests
    ```

## Usage

To run the script, use the following command:

```sh
python scripts/ledger_service_test.py -t <num_threads> -w <num_wallets> -b <initial_balance> -n <num_iters> -s <server>
```

## Arguments
- -t, --threads: Number of threads to use for concurrent transactions.
- -w, --wallets: Number of wallets to create.
- -b, --balance: Initial balance for each wallet.
- -n, --iterations: Number of iterations for debit/credit operations.
- -s, --server: Server URL for the ledger service.
- -r, --random_debit: Use random debit amount between 1.0 and 10.0 (default: False)

## Examples
Run the script with 2 threads, 2 wallets, an initial balance of 1000.0, 1 iteration, and a local server:

```sh
python scripts/ledger_service_test.py -t 2 -w 2 -b 1000.0 -n 1 -s local
```

Run the script with 8 threads, 2 wallets, an initial balance of 500.0, 10 iterations, and a remote server:

```sh
python scripts/ledger_service_test.py -t 8 -w 2 -b 1000.0 -n 10 -s local
```

Run the script with 16 threads, 2 wallets, an initial balance of 1000.0, 10 iterations per thread, using the local server, and random debit amounts:

```sh
python scripts/ledger_service_test.py -t 16 -w 2 -b 1000.0 -n 10 -s local -r
```

## Description
The script performs the following steps:

1. Creates the specified number of wallets with the initial balance.
2. Spawns the specified number of threads.
3. Each thread performs the specified number of iterations, where in each iteration:
   - Two different wallets are picked randomly.
   - A debit operation is performed on one wallet.
   - A credit operation is performed on the other wallet.
   - The debit amount can be fixed or random based on the `-r` option.
4. The script logs the number of successful and failed operations, as well as the final total balance of all wallets.

## Logging
The script logs the following information:

- Number of threads
- Number of wallets
- Initial balance
- Number of iterations
- Server URL
- Initial total balance
- Successful and failed debits
- Successful and failed credits
- Aborted connections
- Final total balance
- Total retried transactions