# block until connection is possible. 
import logging
import requests
import time

def wait_for_connection():
    while True:
        # Make the request
        r = requests.get("https://license.fiberlink.com/internettest")
        if r.status_code in [200, 201]:
            print("Network tested successfully...")
            return
        else:
            print(r)
            time.sleep(1000)

if __name__ == "__main__":
    wait_for_connection()
