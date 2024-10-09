import os
import logging
import requests
import yfinance as yf

TMP_FILE = "/tmp/broadcom_price.txt"


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_price(ticker):
    try:
        quote = yf.Ticker(ticker)
        price = quote.info['currentPrice']
    except Exception as e:
        logging.error(f"Failed to fetch price: {e}")
        raise
    return price


def update_price(price):
        try:
            with open(TMP_FILE, "w") as f:
                f.write(str(price))
            s3_upload_command = f"aws s3 cp {TMP_FILE} s3://voll-bucket-test/broadcom_price.txt"
            result = os.system(s3_upload_command)
            if result != 0:
                raise Exception("Failed to upload the file to S3")
        except Exception as e:
            logging.error(f"Error writing to file or uploading to S3: {e}")
            return


def trigger_announcement(change):
    access_token = os.getenv('access_token')
    secret_token = os.getenv('secret_token')
    if not access_token or not secret_token:
        logging.error("voicemonkey access token or secret token is not set in environment variables.")
        return

    # Format voice monkey URL
    url = f"https://api.voicemonkey.io/trigger?access_token={access_token}&secret_token={secret_token}&monkey=max-monkey&announcement=Broadcom%20Boosted%20{change}%20Percent%20Today&voice=Salli"
    
    # trigger announcement
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json={})
        if response.status_code != 200:
            raise Exception(f"Failed to trigger announcement, status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error making request to VoiceMonkey API: {e}")
        raise


def main():
    price = fetch_price("AVGO")
    # Copy last price from S3 to local file
    try:
        s3_command = f"aws s3 cp s3://voll-bucket-test/broadcom_price.txt {TMP_FILE}"
        result = os.system(s3_command)
        if result != 0:
            raise Exception("Failed to download the file from S3")
    except Exception as e:
        logging.error(f"Error downloading file from S3: {e}")
        return

    # Read last saved value from local file
    try:
        with open(TMP_FILE, "r") as f:
            last_value = float(f.read().strip())
    except FileNotFoundError:
        logging.warning(f"{TMP_FILE} not found, assuming first run with no previous value.")
        last_value = None
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return

    # Calculate diff
    if last_value is not None:
        change = int(((price - last_value) / last_value) * 100)
    else:
        change = 0
    
    logging.info(f"Broadcom changed: {change}%")

    # Trigger announcement and update price
    if change > 2:
        update_price(price)
        trigger_announcement(change)

if __name__ == "__main__":
    main()
