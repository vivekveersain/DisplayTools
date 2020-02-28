import seaborn as sns
from IPython.display import clear_output
from matplotlib import pyplot as plt
import pandas as pd

import sys
import time
import os
import requests
import threading

#%matplotlib inline   #uncomment in Jupyer
sns.set()

class LivePlot:
    def __init__(self):
        pass

    def plot(self, data_dict, start = 0, xlable = "Epochs", figsize=(12,5), title=''):
        clear_output(wait=True)
        plt.figure(figsize=figsize)
        for label, data in data_dict.items():
            plt.plot(data, label=label)
        plt.title(title)
        plt.grid(True)
        plt.xticks(range(len(data)) ,[str(r) for r in range(start, start+len(data))])
        plt.xlabel(xlable)
        plt.legend(loc='center left') # the plot evolves to the right
        plt.show();

class ProgressBar:
    def __init__(self, process_size, msg = '', bar_size = 50, output = sys.stdout):
        if process_size == 0: return
        self.bar_size = bar_size
        self.output = output
        self.msg = msg
        self.process_size = process_size
        self.bar_completion_ratio  = self.bar_size/self.process_size
        self.r = 1
        self.start_timer = time.time()
        self._start(msg)

    def _display(self, content):
        self.output.write(content)
        self.output.flush()

    def _time_conversion(self, secs):
        secs = int(secs)
        if secs < 3600: return '%02d:%02d' % (secs//60, secs%60)
        return '%02d:%02d:%02d' % (secs//3600, (secs//60)%60, secs%60)

    def _done(self): self._display("\n")

    def _start(self, msg = ''):
        content = "%s[>%s] 0/%d(00.00%%) [__:__<__:__] __it/sec   \r" % (msg, " "*self.bar_size, self.process_size)
        self._display(content)

    def display(self, r, msg):
        if msg is None: msg = self.msg
        completed = int(self.bar_completion_ratio * r)
        remaining = self.bar_size - completed
        elapsed = time.time() - self.start_timer
        units = 'sec/it'
        try:
            rem_tim, it_time = elapsed*(self.process_size/r - 1), elapsed/r
            if it_time < 1: it_time, units = r/elapsed, 'it/sec'
        except: rem_tim = it_time = 0
        el = self._time_conversion(elapsed)
        rm = self._time_conversion(rem_tim)
        pct = r*100/self.process_size

        content = "%s[%s>%s] %d/%d(%.2f%%) [%s<%s] %.2f%s   \r" % (msg, "="*completed, " "*remaining, r, self.process_size, pct, el, rm, it_time, units)
        self._display(content)

    def update(self, msg = None):
        self.display(self.r, msg)
        if self.r == self.process_size: self._done()
        self.r += 1

class Chart:
    def __init__(self):
        try:
            with open('./chart.js', 'r') as src: self._start, self._end = src.read().split("<<<CONTENT_HERE>>>")
        except:
            raw = requests.get("https://raw.githubusercontent.com/vivekveersain/MachineLearning/master/chart.js").content.decode()
            self._start, self._end = raw.split("<<<CONTENT_HERE>>>")
            with open('./chart.js', 'w') as src: src.write(raw)
        self.proc = list('|/-\\')

    def plot(self, data, hierarchy_column, delimiter = ";", out_file = 'chart.html', title = "Data"):
        self.start_time = time.time()
        data = self.clean(data, hierarchy_column, delimiter)
        self.write_html(data, out_file, title)

    def clean(self, df, hierarchy_column, delimiter):
        bar = ProgressBar(6, "Cleaning...")
        df = df.copy()
        bar.update()
        df = df.melt([hierarchy_column], var_name="Location", value_name="Value")
        bar.update()
        df["level"] = df["Location"] + delimiter + df[hierarchy_column]
        bar.update()
        df = df[["level", "Value"]]
        bar.update()
        df.level = df.level.apply(lambda x: x.replace('"',"").replace("'",''))
        bar.update()
        df.level = df.level.apply(lambda x: x.split(delimiter))
        bar.update()
        return df

    def _time_conversion(self, secs):
        secs = int(secs)
        return '%d:%02d' % (secs//60, secs%60)

    def _standardizer(self, value):
        if value<10**3: return '%.02f' % (value)
        elif value<10**6: return '%.02f K' % (value/10**3)
        elif value<10**9: return '%.02f M' % (value/10**6)
        else: return '%.02f B' % (value/10**9)

    def make_node(self, name, value):
        return self.node % (name,str(value),self._standardizer(value))

    def close_node(self): return '</node>\n'

    def the_great_recursion(self, data, string, current_level = 1, z = 0):
        data["level"], data["next_level"] = zip(*data["level"].apply(lambda x: (x[0], x[1:])))
        lvl = data.groupby("level").sum().T.to_dict()
        for key in lvl.keys():
            z = (z+1)%4
            print("\rProcessing... %s %s" % (self.proc[z], self._time_conversion(time.time() - self.start_time)), end = '')
            if key == '': continue
            string += '  '*current_level + self.make_node(key, round(lvl[key]["Value"], 2))
            n_data = data.query("level == '%s'" % key).groupby("next_level").sum().reset_index().rename(columns = {"next_level":"level"})
            if n_data.level.apply(lambda x: len(x)).max() > 0: string = self.the_great_recursion(n_data, string, current_level + 1, z)
            string += '  '*current_level + self.close_node()
        return string

    def write_html(self, data, output_name, title):
        string = """<attributes magnitude="magnitude">
                    <attribute display="Selection Total Raw">magnitude</attribute>
                    <attribute display="Selection Total">std_mag</attribute>
                    </attributes>"""
        self.node  = '<node name="%s"><magnitude><val>%s</val></magnitude><std_mag><val>%s</val></std_mag>\n'
        string = self.the_great_recursion(data, string, 1)
        with open(output_name,'w') as f: f.write(self._start + string + self._end)
