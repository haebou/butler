import logging
import json
import os
from time import sleep

from sampler import Sampler
from scrobbler import Scrobbler
from fingerprinter import Fingerprinter

FINGERPRINT_API_KEY = os.environ.get("FINGERPRINT_API_KEY")
LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")

SAMPLE_FILENAME = "sample.wav"
SLEEP_SEC = 30

logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
  datefmt='%Y-%m-%d_%I:%M:%S'
)
logger = logging.getLogger("main")

# Configuration

class InterfaceConfiguration:
    def __init__(self, json_data = {}):
        self.channels = 2
        self.interface_name = ""
        self.sample_format = 16
        self.sample_rate = 44100

        if (json_data):
            from_json(json_data)

    def from_json(self, json_data):
        self.channels = json_data["channels"]
        self.interface_name = json_data["name"]
        self.sample_format = json_data["sample_format"]
        self.sample_rate = json_data["sample_rate"]



class App:
  def __init__(self):
    config = {}
    with open("config.json") as f:
      raw_config = f.read()
      config = json.loads(raw_config)
    config_i = config["interface"]

    self.sampler = Sampler(
      interface_name = config_i["name"],
      channels = config_i["channels"],
      sample_format = config_i["sample_format"],
      sample_rate = config_i["sample_rate"],
    )
    self.fp = Fingerprinter(FINGERPRINT_API_KEY)
    self.fm = Scrobbler(LASTFM_API_KEY)

  def run(self):
    while(True):
      logger.info(f'Recording and fingerprinting sample')
      self.sampler.record()
      self.sampler.save(SAMPLE_FILENAME)
      res = self.fp.run(SAMPLE_FILENAME)

      if (res["status"] != "success"):
        logger.error(f'Failed to fingerprint sample');

      elif (res["result"] == None):
        logger.info('Not listening to a song');

      else:
        logger.info(
          f'Currently listening to "{res["result"]["artist"]}" - '
          f'"{res["result"]["title"]}"');

        
      sleep(SLEEP_SEC)

if __name__ == "__main__":
  app = App()
  app.run()