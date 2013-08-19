#!/usr/bin/python3

from os import path

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import Gdk, GstVideo


GObject.threads_init()
from ctypes import *
gstreamer = cdll.LoadLibrary("E:\Python33\Lib\site-packages\gtk\libgstreamer-1.0-0.dll")
gstreamer.gst_init(None, None)
filename = path.join(path.dirname(path.abspath(__file__)), 'MVI_5751.MOV')
uri = 'file:///E:\\Movies\\720x384.mp4'


class Player(object):
    def __init__(self):
        self.window = Gtk.Window()
        self.window.connect('destroy', self.quit)
        
        self.window.set_default_size(800, 450)
        
        self.Hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 2)
        self.drawingarea = Gtk.DrawingArea()
        #print(self.drwa)
        self.controls =  Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 2)
        self.ProgressBar = Gtk.ProgressBar()
        self.timeout_id = GObject.timeout_add_seconds(1,self.on_timeout, None)
        btn_stop = Gtk.Button(stock=Gtk.STOCK_MEDIA_STOP)
        btn_pause = Gtk.Button(stock=Gtk.STOCK_MEDIA_PAUSE)
        btn_pause.connect("clicked", self.pause_cb)
        btn_play = Gtk.Button(stock=Gtk.STOCK_MEDIA_PLAY)
        btn_play.connect("clicked", self.play_cb)
        btn_open = Gtk.Button(stock=Gtk.STOCK_OPEN)
        
        self.controls.pack_start(btn_stop, False, False, 0)
        self.controls.pack_start(btn_play, False, False, 0)
        self.controls.pack_start(btn_pause, False, False, 0)
        self.controls.pack_start(btn_open, False, False, 0)
        self.controls.pack_start(self.ProgressBar, True, True, 2)
        
        
        self.Hbox.pack_start(self.drawingarea, False, False, 0)
        self.mainbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.mainbox.pack_start(self.Hbox, True, True, 0)
        self.mainbox.pack_start(self.controls, False, False, 0)
        self.window.add(self.mainbox)
        # Create GStreamer pipeline

        self.pipeline = Gst.Pipeline()
    
        # Create bus to get events from GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        self.bus.connect('message::error', self.on_error)
        self.bus.connect('message::state-changed', self.on_state_changed)
        # This is needed to make the video output in our DrawingArea:
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message::element', self.on_sync_message)

        # Create GStreamer elements
        self.playbin = Gst.ElementFactory.make('playbin', None)

        # Add playbin to the pipeline
        self.pipeline.add(self.playbin)
        self.state = Gst.State.READY
        # Set properties
        self.playbin.set_property('uri', uri)
    def pause_cb(self, widget):
        self.pipeline.set_state(Gst.State.PAUSED)
    def play_cb(self, widget):
        self.pipeline.set_state(Gst.State.PLAYING)
	def stop_cb(self, widget):
		self.pipeline.set_state(Gst.State.READY)
    def run(self):
        self.window.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.xid = self.drawingarea.get_property('window')
        for _attr in dir(Gdk.Window):
            if _attr.find('get') > 0 :
                print(_attr)
        self.pipeline.set_state(Gst.State.PLAYING)
        Gtk.main()

    def quit(self, window):
        self.pipeline.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            msg.src.set_window_handle(self.xid)

    def on_eos(self, bus, msg):
        print('on_eos(): seeking to start of video')
        self.pipeline.seek_simple(
            Gst.Format.TIME,        
            Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
            0
        )
    def on_state_changed(self, bus, msg):
        old_state, new_state, pending_state = Gst.Message.parse_state_changed(msg)
        if msg.src == self.playbin :
            self.state = new_state
            if (old_state == Gst.State.READY)&(new_state == Gst.State.PAUSED):
                self.on_timeout
    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())
    def on_timeout(self, data):
        if self.state == Gst.State.PAUSED :
            return True
        else :
            duration = self.pipeline.query_duration(Gst.Format.TIME)[1]
            #print ( duration )
            position = self.pipeline.query_position(Gst.Format.TIME)[1]
            val = position / duration
            self.ProgressBar.set_fraction(val)
        return True
p = Player()
p.run()