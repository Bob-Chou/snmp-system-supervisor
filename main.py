from tkinter import *
from utils import *
import tkinter.font as tkFont  
import time
import threading
from math import floor, ceil
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np

matplotlib.use('TkAgg')

def get_intval_color(rate):
	r = min(255, floor(rate * 2 * 255))
	g = max(0, min(255, floor((2 - rate * 2) * 255)))
	return '#{:0>2x}{:0>2x}{:0>2x}'.format(r, g, 0)


class AweMonitor(object):
	"""docstring for AweMonitor"""
	def __init__(self, oids, font=None):
		super(AweMonitor, self).__init__()
		self.oids = oids
		# self.font = font
		self.root = Tk()
		self.font = tkFont.Font(family=font, size=10)
		self.cnt = 0
		self.time_track = [i for i in range(100)]
		self.cpu_track = [0]*100
		self.ram_track = [0]*100
		self.refresh_timer = threading.Timer(5, self._refresh)
		self._init_gui()
		self._pack_gui()

	def _init_gui(self):

		self.root.title('awesome supervisor')
		self.root.configure(background='white')
		# CPU and RAM
		self.cpu_info = Label(self.root, text='CPU Utilization', font=self.font, bg='white')
		self.ram_info = Label(self.root, text='RAM Utilization', font=self.font, bg='white')
		# Plot
		self.figure = Figure(dpi=100)
		self.figure_canvas =FigureCanvasTkAgg(self.figure, master=self.root)

		# network flow
		self.flow_in_info = Label(self.root, text='network flow in', font=self.font, bg='white')
		self.flow_out_info = Label(self.root, text='network flow out', font=self.font, bg='white')
		self.flow_in_text = StringVar()
		self.flow_out_text = StringVar()
		self.flow_in = Label(self.root, textvariable=self.flow_in_text, font=self.font, bg='white')
		self.flow_out = Label(self.root, textvariable=self.flow_out_text, font=self.font, bg='white')

		# CPU canvas
		self.cpu_canvas = Canvas(self.root, width=300, height=20, bg='white', highlightthickness=0)
		self.cpu_bar = self.cpu_canvas.create_rectangle(0, 0, 300, 20, fill='#CCCCCC', outline='#CCCCCC', tags='cpu_bar')
		self.cpu_used = self.cpu_canvas.create_rectangle(0, 0, 300, 20, fill='#1E8CE8', outline='#1E8CE8', tags='cpu_fill')
		self.cpu_text = self.cpu_canvas.create_text(150, 10, font=self.font, tag='cpu_text')
		
		# RAM canvas
		self.ram_canvas = Canvas(self.root, width=300, height=20, bg='white', highlightthickness=0)
		self.ram_bar = self.ram_canvas.create_rectangle(0, 0, 300, 20, fill='#CCCCCC', outline='#CCCCCC', tags='ram_bar')
		self.ram_used = self.ram_canvas.create_rectangle(0, 0, 300, 20, fill='#1E8CE8', outline='#1E8CE8', tags='ram_fill')
		self.ram_text = self.ram_canvas.create_text(150, 10, font=self.font, tag='ram_text')

		# Disk canvas
		disk_utils = get_disk(self.oids)
		disk_num = len(disk_utils)
		cols, rows = 3, ceil(disk_num/3)
		self.disk_canvas = Canvas(self.root, width=cols*150, height=rows*150, bg='white', highlightthickness=0)
		self.disk_bar,  self.disk_used, self.disk_mask, self.disk_text, self.disk_letter = {}, {}, {}, {}, {}
		for i, k in enumerate(sorted(disk_utils.keys())):
			_total, _usage = disk_utils[k][0], disk_utils[k][1]
			coord = 150*(i%3)+25, 150*(i//3)+25, 150*(i%3)+125, 150*(i//3)+125
			center = 75+150*(i%3), 150*(i//3)+75
			top = 75+150*(i%3), 150*(i//3)+13
			self.disk_letter[k] = self.disk_canvas.create_text(top, font=self.font, tag='{}_disk'.format(k), text='{}: {:.1f}G/{:.1f}G'.format(k, _usage, _total))
			self.disk_bar[k] = self.disk_canvas.create_oval(coord, fill='#CCCCCC', outline='#CCCCCC', tags='{}_bar'.format(k))
			start, extent = 90, floor(360*(_usage/_total))
			color = get_intval_color(_usage/_total)
			self.disk_used[k] = self.disk_canvas.create_arc(coord, start=start, extent=extent, fill=color, outline=color, tags='{}_fill'.format(k))
			coord = 150*(i%3)+35, 150*(i//3)+35, 150*(i%3)+115, 150*(i//3)+115
			self.disk_mask[k] = self.disk_canvas.create_oval(coord, fill='white', outline='white', tags='{}_bar'.format(k))
			self.disk_text[k] = self.disk_canvas.create_text(center, font=self.font, tag='{}_text'.format(k), text='{:.1f}%'.format(100*_usage/_total))

		# CPU threshold entry
		self.warn_info = Label(self.root, text='CPU watchdog', font=self.font, bg='white')
		self.threshold = None
		self.cpu_set = Entry(self.root)
		self.cpu_alarm = Button(self.root, text='set alarm', width=25, command=self._set_cpu_threshold)
		self.warn_canvas = Canvas(self.root, width=400, height=20, bg='white', highlightthickness=0)
		self.warn_text = self.warn_canvas.create_text(200, 10, font=self.font, tag='warning', text='CPU OVERLOADED!', fill='red', state='hidden')

	def _set_cpu_threshold(self):
		try:
			self.threshold = float(self.cpu_set.get())
		except:
			self.threshold = None
		# self._refresh()

	def _pack_gui(self):
		# CPU and RAM
		self.cpu_info.grid(sticky=W, padx=20, pady=5)
		self.cpu_canvas.grid(row=0, column=1, padx=20, pady=5) 
		self.ram_info.grid(row=1, column=0, sticky=W, padx=20, pady=5)
		self.ram_canvas.grid(row=1, column=1, padx=20, pady=5)
		# Plot canvas
		self.figure_canvas.get_tk_widget().grid(row=0, column=2, rowspan=8, padx=20, pady=5)
		# Network
		self.flow_in_info.grid(row=2, column=0, padx=20, pady=5, sticky=W)
		self.flow_in.grid(row=2, column=1, padx=20, pady=5, sticky=W+E)
		self.flow_out_info.grid(row=3, column=0, padx=20, pady=5, sticky=W)
		self.flow_out.grid(row=3, column=1, padx=20, pady=5, sticky=W+E)

		# Disk
		self.disk_canvas.grid(row=4, column=0, columnspan=2, padx=20, pady=5)

		# CPU watchdog
		self.warn_info.grid(row=5, columnspan=2, padx=20, pady=5, sticky=W)
		self.cpu_set.grid(row=6, column=0, padx=20, pady=5)
		self.cpu_alarm.grid(row=6, column=1, padx=20, pady=5)
		self.warn_canvas.grid(row=7, column=0, columnspan=2, padx=20, pady=5, sticky=W+E)
		# self.btn1.grid(row=3, sticky=W+E, padx=5, pady=5)

	def _refresh(self):
		self.cnt += 1
		# Update CPU utilities
		_per = get_cpu_usage(self.oids)
		self.cpu_track = self.cpu_track[1:] + [_per/100]
		self.cpu_canvas.coords(self.cpu_used, (0, 0, floor(_per * 3), 20))
		self.cpu_canvas.coords(self.cpu_text, (floor(_per * 3), 10))
		self.cpu_canvas.itemconfigure(self.cpu_text, text='{:.2f}%'.format(_per))
		# CPU warning
		if self.threshold is not None:
			if _per > self.threshold:
				self.cpu_canvas.itemconfigure(self.cpu_used, fill='#FF0000', outline='#FF0000')
				self.warn_canvas.itemconfigure(self.warn_text, state='normal')
			else:
				self.cpu_canvas.itemconfigure(self.cpu_used, fill='#1E8CE8', outline='#1E8CE8')
				self.warn_canvas.itemconfigure(self.warn_text, state='hidden')

		# Update RAM utilities
		_total, _usage = get_memory(self.oids)
		_per = 100 * _usage / _total
		self.ram_track = self.ram_track[1:] + [_per/100]
		self.ram_canvas.coords(self.ram_used, (0, 0, floor(_per * 3), 20))
		self.ram_canvas.coords(self.ram_text, (floor(_per * 3), 10))
		self.ram_canvas.itemconfigure(self.ram_text, text='{:.1f}%, {:.2f}G/{:.2f}G'.format(_per, _usage, _total))

		# Update Network
		_in, _out = get_network(self.oids)
		self.flow_in_text.set('{:.2f}M'.format(_in))
		self.flow_out_text.set('{:.2f}M'.format(_out))

		# Update the plot
		self.figure.clf()
		self.axes = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])
		self.axes.plot(self.time_track, self.cpu_track, label='CPU')
		self.axes.plot(self.time_track, self.ram_track, label='RAM')
		self.axes.grid(True, linestyle='--')
		self.axes.set_xticks([])
		self.axes.set_yticks(np.arange(0, 1, step=0.1))
		self.axes.set_yticklabels(['{}%'.format(i) for i in range(0, 100, 10)])
		self.axes.set_title('Realtime Utilization Curve')
		self.axes.legend(bbox_to_anchor=(1.0, 1), loc=1, borderaxespad=0.1)
		self.figure_canvas.show()

		# Start a new timer
		self.refresh_timer = threading.Timer(1, self._refresh)
		self.refresh_timer.start()

	def show(self):
		self._refresh()
		self.root.mainloop()
		self.refresh_timer.cancel()

	def __del__(self):
		self.refresh_timer.cancel()

if __name__ == '__main__':
	monitor = AweMonitor(oids=get_oid_config('./oids.config'), font='Monaco')
	monitor.show()
