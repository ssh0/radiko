#! /usr/bin/env python
# -*- coding:utf-8 -*-

from main import Radiko
from player import Player
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='radiko (FM radio service in Japan) streaming application'
        )
    parser.add_argument('-a', '--areaid',
                        dest='areaid',
                        type=str,
                        default=None,
                        help='(OPTIONAL) you can choose area id (ex: "JP13")'
                        )
    parser.add_argument('-c', '--channel',
                        dest='channel',
                        type=str,
                        default=None,
                        help='(OPTIONAL) FM channel'
                        )

    parser.add_argument('-v', '--verbose',
                        help='verbose (debug) mode',
                        action='store_true'
                        )

    args = parser.parse_args()
    area_id = args.areaid
    station_id = args.channel
    app = Radiko()
    app.test = args.verbose
    app.get_player()
    app.get_keydata()
    player = Player(app, area_id, station_id)

