#!/usr/bin/python3

from os import path
import time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, Gtk

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import Gdk, GstVideo


GObject.threads_init()
from ctypes import *
gstreamer = cdll.LoadLibrary("D:\Python33\Lib\site-packages\gtk\libgstreamer-1.0-0.dll")
gdkwin32 = cdll.LoadLibrary('D:\Python33\Lib\site-packages\gtk\libgdk-3-0.dll')
gstreamer.gst_init(None, None)
filename = path.join(path.dirname(path.abspath(__file__)), 'MVI_5751.MOV')
global uri
uri = 'file:///E:/BUGs/samples/720x384.MP4'


class Player(object):
    def __init__(self):
        self.window = Gtk.Window()
        self.window.connect('destroy', self.quit)
        
        self.window.set_default_size(800, 600)
        
        self.Hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 2)
        self.drawingarea = Gtk.DrawingArea()
        #print(self.drwa)
        self.controls =  Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 2)
        self.ProgressBar = Gtk.ProgressBar()
        self.timeout_id = GObject.timeout_add_seconds(1,self.on_timeout, None)
        btn_stop = Gtk.Button(stock=Gtk.STOCK_MEDIA_STOP)
        btn_stop.connect("clicked", self.stop_cb)
        btn_pause = Gtk.Button(stock=Gtk.STOCK_MEDIA_PAUSE)
        btn_pause.connect("clicked", self.pause_cb)
        btn_play = Gtk.Button(stock=Gtk.STOCK_MEDIA_PLAY)
        btn_play.connect("clicked", self.play_cb)
        btn_open = Gtk.Button(stock=Gtk.STOCK_OPEN)
        btn_open.connect("clicked", self.on_open_clicked)
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
        
    def buildpipeline(self):
        self.pipeline = Gst.Pipeline()
        print("buildpipeline" + uri)
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
        print("Create Gstreamer playbin")
        self.playbin = Gst.ElementFactory.make('playbin', None)
        self.audiosink = Gst.ElementFactory.make("waveformsink", None)
        self.videosink = Gst.ElementFactory.make("cluttersink", None)
        # Add playbin to the pipeline
        self.pipeline.add(self.playbin)
        #self.pipeline.add(self.audiosink)
        self.state = Gst.State.READY
        # Set properties
        print("set property uri = " + uri)
        self.playbin.set_property('uri', uri)
        self.playbin.set_property('audio-sink', self.audiosink)
        #self.playbin.set_property('video-sink', self.videosink)
    def play(self):
        print(self.pipeline)
        self.pipeline.set_state(Gst.State.PLAYING)
        self.playbin.expose()
    
    def pause_cb(self, widget):
        self.pipeline.set_state(Gst.State.PAUSED)
    def play_cb(self, widget):
        self.pipeline.set_state(Gst.State.PLAYING)
    def stop_cb(self, widget):
        self.pipeline.set_state(Gst.State.NULL)
    def open_cb(self, uri):
        self.pipeline.set_state(Gst.State.NULL)
        Gst.Object.unref(self.pipeline)
        self.duration = None
        self.position = None
        self.buildpipeline()
        self.play()
    def on_open_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        self.add_filters(dialog)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            global uri
            uri = dialog.get_uri()
            print("uri = "+ uri)
            self.open_cb(uri)
        dialog.destroy()
    def add_filters(self, dialog):
        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        filter_mm = Gtk.FileFilter()
        filter_mm.set_name("MultiMedia files")
        filter_mm.add_pattern("*.mp4")
        dialog.add_filter(filter_mm)
        

    def run(self):
        self.window.show_all()
        # You need to get the XID after window.show_all().  You shouldn't get it
        # in the on_sync_message() handler because threading issues will cause
        # segfaults there.
        self.win_id = gdkwin32.gdk_win32_window_get_handle(0x11194b0)
        self.drawingarea.get_window().ensure_native()
        print(self.drawingarea.get_property('window'))
        print('win_id = ' + str(self.win_id))
        #for _attr in dir(Gdk.Window):
        #   if _attr.find('get') > 0 :
        #       print(_attr)
        self.buildpipeline()
        self.play()
        Gtk.main()

    def quit(self, window):
        self.pipeline.set_state(Gst.State.NULL)
        #time.sleep(10)
        Gtk.main_quit()

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            print('prepare-window-handle')
            #msg.src.set_window_handle(self.win_id)
            msg.src.expose()
            print(msg.src)
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
        duration = Gst.CLOCK_TIME_NONE
        positon = Gst.CLOCK_TIME_NONE
        fmt = Gst.Format.TIME
        if self.state == Gst.State.PAUSED :
            return True
        else :
            duration = self.pipeline.query_duration(fmt)[1]
            #print ( duration )
            position = self.pipeline.query_position(fmt)[1]
            if duration <= 0 :
                val = 0
            else :
                val = position / duration
            self.ProgressBar.set_fraction(val)
        return True
p = Player()
p.run()
