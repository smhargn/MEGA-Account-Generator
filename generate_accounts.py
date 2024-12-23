import requests
import random
import string
import subprocess
import time
import csv
import os
import threading
import argparse
from faker import Faker
from bs4 import BeautifulSoup

fake = Faker()

username = "ENTER USERNAME"
password = "ENTER PASSWORD"
proxydomain = "ENTER"
proxyport = "ENTER"
proxy = f"http://{username}:{password}@{proxydomain}:{proxyport}"  # Proxy address Change Domain

os.environ["http_proxy"] = proxy
os.environ["https_proxy"] = proxy

proxies = {
    "http": proxy,
    "https": proxy,
}

# Custom function for checking if the argument is below a certain value
def check_limit(value):
    ivalue = int(value)
    if ivalue <= 8:
        return ivalue
    else:
        raise argparse.ArgumentTypeError(f"You cannot use more than 8 threads.")

# Command line arguments
parser = argparse.ArgumentParser(description="Create New Mega Accounts")
parser.add_argument("-n", "--number", type=int, default=2500, help="Number of accounts to create")  # CHANGE DEFAULT 
parser.add_argument("-t", "--threads", type=check_limit, default=None, help="Number of threads to use for concurrent account creation")
parser.add_argument("-p", "--password", type=str, default=None, help="Password to use for all accounts")
args = parser.parse_args()

def get_random_string(length):
    """Generate a random string with a given length."""
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))

def fetch_with_retry(url, proxies, retries=3, delay=5):
    """Retries a GET request in case of a ProxyError."""
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, proxies=proxies)
            if response.status_code == 200:
                return response
            else:
                print(f"HTTP {response.status_code}: Retrying...")
        except requests.exceptions.ProxyError as e:
            print(f"ProxyError on attempt {attempt + 1}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"RequestException on attempt {attempt + 1}: {e}")
        attempt += 1
        if attempt < retries:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"Failed after {retries} attempts to fetch URL: {url}")

class MegaAccount:

    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.email = None
        self.email_domain = None

    def generate_email(self):
        """Generate a random email address using 1secmail API."""
        url = "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1"
        response = fetch_with_retry(url, proxies)
        email = response.json()[0]
        self.email, self.email_domain = email.split("@")
        print(f"Generated email: {email}")

    def get_email_messages(self):
        """Fetch emails for the generated email address."""
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={self.email}&domain={self.email_domain}"
        response = fetch_with_retry(url, proxies)
        return response.json()

    def read_email(self, message_id):
        """Read a specific email by ID."""
        url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={self.email}&domain={self.email_domain}&id={message_id}"
        response = fetch_with_retry(url, proxies)
        return response.json()

    def register(self):
        self.generate_email()
        print(f"Registering account for {self.email}@{self.email_domain}...")
        registration = subprocess.run(
            [
                "megatools",
                "reg",
                "--scripted",
                "--register",
                "--email",
                f"{self.email}@{self.email_domain}",
                "--name",
                self.name,
                "--password",
                self.password,
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ
        )
        self.verify_command = registration.stdout
        return self.email

    def verify(self):
        """Wait for the verification email and process it."""
        for _ in range(5):  # Retry for a certain number of attempts
            emails = self.get_email_messages()
            for email in emails:
                print(email)
                if email["subject"] and "mega" in email["subject"].lower():
                    email_data = self.read_email(email["id"])
                    html_content = email_data.get("body", "")
                    soup = BeautifulSoup(html_content, "html.parser")
                    a_tag = soup.find("a", id="bottom-button")
                    if a_tag and "href" in a_tag.attrs:
                        link = a_tag["href"]
                        self.verify_command = self.verify_command.replace("@LINK@", link)
                        attempt = 0
                        retries = 3
                        delay = 5
                        while attempt < retries:
                            try:
                                subprocess.run(
                                    self.verify_command,
                                    shell=True,
                                    check=True,
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True,
                                    env=os.environ
                                )
                                print("Verified account: "+self.email+"@"+self.email_domain+":"+self.password)
                                with open("acc12.csv", "a", newline="") as csvfile:
                                    writer = csv.writer(csvfile)
                                    writer.writerow([f"{self.email}@{self.email_domain}", self.password])
                                return
                            except subprocess.CalledProcessError as e:
                                print(f"Attempt {attempt + 1} failed. Error: {e}")
                                print(f"Stdout: {e.stdout}")
                                print(f"Stderr: {e.stderr}")
                                attempt += 1
                                if attempt < retries:
                                    print(f"Retrying in {delay} seconds...")
                                    time.sleep(delay)
                                else:
                                    print("Max retries reached. Command failed.")
                        return
            print(f"Waiting for verification email for {self.email}@{self.email_domain}...")
            time.sleep(4)
        print(f"Verification failed for {self.email}@{self.email_domain}")

    def run(self):
        self.register()
        self.verify()

def new_account():
    password = args.password or get_random_string(random.randint(8, 14))
    acc = MegaAccount(fake.name(), password)
    acc.run()

if __name__ == "__main__":
    # Ensure CSV exists
    if not os.path.exists("output.csv"): # CHANGE CSV FILE
        with open("output.csv", "w", newline="") as csvfile: # CHANGE CSV FILE
            writer = csv.writer(csvfile)
            writer.writerow(["Email", "Password"])

    # Create accounts
    if args.threads:
        threads = []
        for _ in range(args.number):
            t = threading.Thread(target=new_account)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    else:
        for _ in range(args.number):
            new_account()
