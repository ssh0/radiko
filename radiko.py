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
    parser.add_argument('--gui',
                        help='Set the option for gui',
                        action='store_true'
                        )
    parser.add_argument('-v', '--verbose',
                        help='verbose (debug) mode',
                        action='store_true'
                        )

    args = parser.parse_args()
    gui = args.gui
    app = Radiko()
    app.areaid = args.areaid
    app.channel = args.channel
    app.test = args.verbose
    app.get_player()
    app.get_keydata()
    if gui:
        player = Player(app, app.areaid, app.channel)
    else:
        app.get_auth1()
        app.get_auth2()
        app.get_channels()
        app.set_channel()
        if not app.channel in app.channels:
            print("station {0} is not available.".format(app.channel))
            app.show_channel()
        app.get_stream_url()
        app.play()

