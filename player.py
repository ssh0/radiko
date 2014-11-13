# /usr/bin/env python
# -*- coding:utf-8 -*-


from gi.repository import Gtk, Gio
import time

class Player(Gtk.Window):

    def __init__(self, app, area_id, station_id):
        self.radiko = app
        self.radiko.areaid = area_id
        self.radiko.channel = station_id
        
        self.setupwindow()
        self.display()
        
    def setupwindow(self):
        Gtk.Window.__init__(self, title="radiko player")
        self.set_default_size(400, 300)
        hb = Gtk.HeaderBar()
        hb.props.show_close_button = True
        hb.props.title = "radiko player"
        self.set_titlebar(hb)
        
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect('clicked', self.connect_server)
        hb.pack_end(button)
        
        self.button = Gtk.Button()
        icon = Gio.ThemedIcon(name="media-playback-start")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.button.add(image)
        self.button.connect('clicked', self.play)
        self.button.set_sensitive(False)
        hb.pack_end(self.button)

        self.masterbox = Gtk.VBox(spacing=6)
        self.add(self.masterbox)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.masterbox.pack_start(self.listbox, False, False, 0)        
        
        self.entry_area_id()
        self.entry_station_id()
        self.textview_channels()
        
    def display(self):
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
        Gtk.main()

    def _add_entry(self, kw, arg, entry):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        
        label = Gtk.Label(kw, xalign=0)
        hbox.pack_start(label, False, True, 10)
        if arg:
            entry.set_text(arg)
        hbox.pack_start(entry, True, True, 10)

        self.listbox.add(row)
    
    def entry_area_id(self):
        kw = "area Id"
        arg = self.radiko.areaid
        self.area_entry = Gtk.Entry()
        self._add_entry(kw, arg, self.area_entry)
    
    def entry_station_id(self):
        kw = "station Id"
        arg = self.radiko.channel
        self.station_entry = Gtk.Entry()
        self._add_entry(kw, arg, self.station_entry)
        
    def textview_channels(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)

        self.tv = Gtk.TextView()
        self.textbuffer = self.tv.get_buffer()
        scrolledwindow.add(self.tv)
        
        self.masterbox.pack_start(scrolledwindow, True, True, 0)
        
    def connect_server(self, event):
        if len(self.area_entry.get_text()) > 0:
            self.radiko.areaid = self.area_entry.get_text()
        if len(self.station_entry.get_text()) > 0:
            self.radiko.channel = self.station_entry.get_text()
        self.radiko.get_auth1()
        self.radiko.get_auth2()
        self.area_entry.set_text(self.radiko.areaid)
        self.radiko.get_channels()
        self.textbuffer.set_text(self.radiko.channels)
        self.button.set_sensitive(True)
        
    def play(self, event):
        self.radiko.channel = self.station_entry.get_text()
        if len(self.radiko.channel) == 0:
            return
        elif not self.radiko.channel in self.radiko.channels:
            return
        self.radiko.get_stream_url()
        self.radiko.play()
