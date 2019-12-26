# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:52:28 2019

@author: Vievk V. Arya [github.com/vivekveersain]
"""

import requests, os 
from bs4 import BeautifulSoup as bs4
import warnings
import pandas as pd
import re

warnings.filterwarnings('ignore')

pd.set_option('display.expand_frame_repr', True)
pd.set_option("display.max_rows", 20)
pd.set_option("display.max_columns", 8)
pd.set_option("display.width", 190)

def show(df, n):
    with pd.option_context('display.max_rows', n): print(df)

class Friends:
    def __init__(self):
        print('F.R.I.E.N.D.S')
        self.raw = 'Downloads/'
        self.folder = 'Cleaned/'
        try: os.mkdir("Downloads")
        except: pass
        try: os.mkdir("Cleaned")
        except: pass
        self.alpha = re.compile('[^a-zA-Z\\s]')
        self.friends = ['Monica', 'Chandler', 'Joey','Phoebe','Ross', 'Rachel']

    def download(self):
        get_text  = lambda link: bs4(requests.get(link).text).get_text().encode('ascii','ignore').decode()
        get_links = lambda link: [(line.get('href'), line.contents[0]) for line in bs4(requests.get(link).text).find_all('a', href = True)]
        home = 'https://fangj.github.io/friends/'
        links = get_links(home)
        spaces = ''
        for link, name in links:
            name = name.strip().replace("  "," ").replace('"','')
            if int(name.split(" ")[0].split("-")[0])<999: name = '0'+name
            print("\rDownloading... [%s]%s" % (name, spaces), end ='\r')
            spaces = ' '*len(name)
            if not os.path.isfile(r'%s%s.txt'%(self.raw,name)):
                with open(r'%s%s.txt'%(self.raw,name), 'w') as f:
                    f.write(get_text(home+link))
            else: print("\rExists: %s%s.txt"%(self.raw,name), end = '\r')

    def clean(self):
        folder = self.folder
        spaces = ''
        for file in os.listdir(self.raw):
            print("\rCleaning... [%s]%s" % (file, spaces), end ='\r')
            spaces = ' '*len(file)
            with open(self.raw+file) as f: data = f.readlines()
            for r, line in enumerate(data):
                if line[0].isupper() and ": " in line and " : " not in line:
                    p = r
                elif line == '\n': p = r
                elif line == 'End\n': break
                else:
                    data[p] = data[p].strip('\n').title() + ' ' + data[r]
                    data[r] = None

            data = ''.join([line for line in data if line is not  None])
            with open(folder+file, 'w') as f: f.write(data)

    def freq_analysis(self):
        folder = self.folder
        files = os.listdir(folder)
        speakers = {}
        for file in files:
            with open(folder+file) as f: data = f.readlines()
            for line in data[9:]:
                if ":" in line and line[0].isupper():
                    t = line.split(":")
                    speaker, sent = t[0].split('(')[0].strip().title(), self.alpha.sub('',':'.join(t[1:]).strip(" ").strip("\n").lower())
                    try:
                        for word in sent.split(" "):
                            if word == '': continue
                            try:speakers[speaker][word] += 1
                            except:speakers[speaker][word] = 1
                    except:
                        speakers[speaker] = {}
                        for word in sent.split(" "):
                            if word == '': continue
                            try:speakers[speaker][word] += 1
                            except:speakers[speaker][word] = 1
        return pd.DataFrame(speakers).fillna(0).astype(int).sort_values(by = friends.friends,ascending= False).reset_index().rename(columns = {'index':'word'})

friends = Friends()
friends.download()
friends.clean()
#raw = friends.freq_analysis()
#df = raw[friends.friends+['word']]
#df = df[df.sum(axis = 1)>1]
#df[df.word.apply(lambda x : x in [n.lower() for n in friends.friends])]
