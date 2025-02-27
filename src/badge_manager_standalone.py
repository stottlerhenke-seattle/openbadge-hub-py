from __future__ import absolute_import, division, print_function
import os
import re
import datetime
import logging
import requests
from server import BADGE_ENDPOINT, BADGES_ENDPOINT, request_headers
from badge import Badge,now_utc_epoch
from settings import DATA_DIR, LOG_DIR, CONFIG_DIR
import collections

devices_file = CONFIG_DIR + 'devices.txt'


class BadgeManagerStandalone():
    def __init__(self, logger,timestamp):
        self._badges= None
        self.logger = logger
        self._device_file = devices_file

        if timestamp:
            self._init_ts = timestamp
            self._init_ts_fract = 0
        else:
            self._init_ts, self._init_ts_fract = now_utc_epoch()
            # self._init_ts -= 5 * 60 # start pulling data from the 5 minutes
            self._init_ts -= 24 * 60 * 60 # start pulling data from 12 hours ago
        ts_pretty = datetime.datetime.fromtimestamp(self._init_ts).strftime("%Y-%m-%d@%H:%M: UTC")
        logger.debug("[Badges] Standalone version. Will request data since {} {} ({}))".format(
            self._init_ts, self._init_ts_fract, ts_pretty))

    def _read_file(self,device_file):
        """
        refreshes an internal list of devices included in devices.txt
        Format is device_mac<space>badge_id<space>project_id<space>device_name
        :param device_file:
        :return:
        """
        if not os.path.isfile(device_file):
            self.logger.error("Cannot find badge devices file: {}".format(device_file))
            exit(1)
        self.logger.info("Reading badges from file: {}".format(device_file))

        #extracting badge id, project id and mac address
        with open(device_file, 'r') as devices_macs:

            badge_project_ids =[]
            devices = []

            for line in devices_macs:
                stripped = line.lstrip()
                # skip empty lines and # comments
                if stripped and not stripped.startswith('#'):
                    device_details = stripped.split()
                    devices.append(
                        {"mac": device_details[0],
                         "badge_id": device_details[1],
                         "project_id": device_details[2],
                        })

        for d in devices:
            self.logger.debug("    {}".format(d))

        badges = {device["mac"]: Badge(device["mac"],
                            self.logger,
                            key=device["mac"],  # using mac as key since no other key exists
                            badge_id=int(device["badge_id"]),
                            project_id=int(device["project_id"]),
                            init_audio_ts_int=self._init_ts,
                            init_audio_ts_fract=self._init_ts_fract,
                            init_proximity_ts=self._init_ts,
                            ) for device in devices
        }

        badges = collections.OrderedDict(sorted(badges.items(), key=lambda t: t[1].badge_id))

        return badges

    def pull_badges_list(self):
        if not self._badges:
            file_badges = self._read_file(self._device_file)
            self._badges = file_badges

    def pull_badge(self, mac):
        """
        Contacts to server (if responding) and updates the given badge data
        :param mac:
        :return success?:
        """
        # Return success so it doesn't break everything else
        return True

    def send_badge(self, mac):
        """
        Sends timestamps of the given badge to the server
        :param mac:
        :return:
        """
        pass # not implemented in standalone

    def create_badge(self, name, email, mac):
        """
        Creates a badge using the giving information
        :param name: user name
        :param email: user email
        :param mac: badge mac
        :return:
        """
        self.logger.debug("Command 'create_badge' is not implemented for standalone mode'")
        pass # not implemented in standalone

    @property
    def badges(self):
        if self._badges is None:
            raise Exception('Badges list has not been initialized yet')
        return self._badges


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger('badge_server')
    logger.setLevel(logging.DEBUG)

    mgr = BadgeManagerStandalone(logger=logger,timestamp=1520270000)
    mgr.pull_badges_list()
    print(mgr.badges)
