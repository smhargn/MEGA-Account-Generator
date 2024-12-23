
# Mega Account Generator

This script is designed to generate new accounts for MEGA.nz using a proxy for enhanced privacy. The script also automates email generation, account registration, and verification using `megatools`. It supports multithreaded account creation for efficiency.

## Reference

This project is inspired by and references the [MEGA Account Generator](https://github.com/f-o/MEGA-Account-Generator).

## Features

- Automatic email generation using the 1secmail API
- Proxy support for anonymity
- Multithreaded account creation for speed
- Automatic account verification and saving to CSV

### Prerequisites

- Python 3.7 or later
- Required Python libraries (install via `requirements.txt`)
- `megatools` installed and available in your system path

### Proxy Configuration
You need a proxy with a username, password, domain, and port. Update the `proxy` variable in the script:
```python
proxy = f"http://{username}:{password}@{proxydomain}:{proxyport}"
```

### Email API
The script uses the [1secmail](https://www.1secmail.com/) API to generate temporary email addresses for account registration.

## Setup
1. Clone the repository or copy the script file.
2. Ensure `megatools` is installed on your system and accessible from the command line.
3. Update the proxy details in the script.
4. If using a specific password for all accounts, pass it via the `-p` flag.
5. Run the script with the desired number of accounts and threads.

### Installation

1. Clone this repository or download the script.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Output

The script saves the generated accounts in a CSV file (`output.csv`) with the following format:

| Email                | Password        |
|----------------------|-----------------|
| example@domain.com   | examplepassword |

## Troubleshooting
- **ProxyError**: Ensure the proxy details are correct and the server is reachable.
- **Email issues**: Check the 1secmail API status if email generation or fetching fails.
- **Command not found**: Verify that `megatools` is installed and accessible in your PATH.

## Notes

- Modify the proxy details in the script before running.
- Adjust the default account number or thread limit as needed.

