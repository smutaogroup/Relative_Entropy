#!/bin/env python
from tkinter import *
from tkinter import ttk
import tkinter.font as font
from tkinter import filedialog

def fetch_all(data):
	value_get = {}
	value_get['psf'] = data['psf'].get().split('/')[-1]
	value_get['dcd1'] = data['dcd1'].get().split('/')[-1]
	value_get['dcd2'] = data['dcd2'].get().split('/')[-1]
	value_get['reuse_alphadist'] = data['reuse_alphadist'].get()
	value_get['reuse_densdist'] = data['reuse_densdist'].get()
	value_get['reuse_re'] = data['reuse_re'].get()
	value_get['cutoff'] = data['cutoff'].get()
	value_get['reuse_graph'] = data['reuse_graph'].get()
	value_get['source'] = data['source'].get()
	value_get['target'] = data['target'].get()
	value_get['selectalgrithm'] = data['selectalgrithm'].get()
	value_get['commu'] = data['commu'].get()
	value_get['repeat'] = data['repeat'].get()

	for i,v in value_get.items():
		print(i,v)

	background_run(data)

def callback(entry):
	name = filedialog.askopenfilename()
	print(name)
	entry.insert(10, name)

if __name__ == '__main__':
	root = Tk()
	root.option_add("*Background", "white")
	root.option_add('*font', ('Times New Roman', 14))
	buttonfont = font.Font(family='Helvetica', size=18, weight='bold')
	titlefont = font.Font(family='Times New Roman', size=24, weight='bold', slant='italic')
	textfontbold = font.Font(family='Times New Roman', size=14, weight='bold')
	textfontitalic = font.Font(family='Times New Roman', size=14, slant='italic')

	root.minsize(700,730)
	root['bg'] = "white"
	
	for col in range(12):
		root.columnconfigure(col, weight=1)
	for row in range(32):
		root.rowconfigure(row, weight=1)

	#ZERO
	Label(root, text='Relative Entropy based \n Community and Shortest Path Detection', font=titlefont).grid(row=0, rowspan=2,column=0, columnspan = 12, padx=30, pady=25)

	t1 = Label(root, text='Set up all the files', font=textfontbold)
	t1.grid(row=2, column=0, columnspan = 12, sticky="w", padx=(30,30))

	psf = Label(root, text='PSF'); psf.grid(row=3, column=0, sticky='e', padx=(50,0))
	psf_file_entr = Entry(root,width=40); psf_file_entr.grid(row=3, column=1, columnspan=9,padx=30,sticky='w') 
	psf_file_sele = Button(text='File Open', width=10, height=2, command= lambda: callback(psf_file_entr)); psf_file_sele.grid(row=3, column=10,sticky='w', pady=2)

	dcd1 = Label(root, text='DCD1'); dcd1.grid(row=4, column=0, sticky='e', padx=(50,0))
	dcd1_file_entr = Entry(root, width=40); dcd1_file_entr.grid(row=4, column=1, columnspan=9,padx=30, sticky='w')
	dcd1_file_sele = Button(text='File Open', width=10, height=2, command= lambda: callback(dcd1_file_entr)); dcd1_file_sele.grid(row=4, column=10,sticky='w', pady=2)
	
	dcd2 = Label(root, text='DCD2'); dcd2.grid(row=5, column=0, sticky='e', padx=(50,0))
	dcd2_file_entr = Entry(root, width=40); dcd2_file_entr.grid(row=5, column=1, columnspan=9,padx=30, sticky='w')
	dcd2_file_sele = Button(text='File Open',  width=10, height=2, command= lambda: callback(dcd2_file_entr)); dcd2_file_sele.grid(row=5, column=10, sticky='w', pady=2)


	## step 1 calculate atom_pair
	t1 = Label(root, text='1. Identify alpha carbon from psf file', font=textfontbold);
	t1.grid(row=6, column=0, columnspan = 12, sticky="w", padx=(30,30))

	## step 2 Calculate pairwise alpha distance
	Label(root, text='2. Calculate pairwise alpha distance', font=textfontbold).grid(row=7,column=0,columnspan=8,sticky=W,padx=30);
	reuse_alphadist = IntVar()
	reuse_alphadist.set(1)
	Checkbutton(root, text="Reuse Data", variable=reuse_alphadist).grid(row=7, column=8, columnspan=4,sticky=W)

	## step 3. Estimate density distributions for each feature
	Label(root, text='3. Estimate density distributions for each feature', font=textfontbold).grid(row=8,column=0,columnspan=8,sticky=W,padx=30);
	reuse_densdist = IntVar()
	reuse_densdist.set(1)
	Checkbutton(root, text="Reuse Data", variable=reuse_densdist).grid(row=8, column=8, columnspan=4,sticky=W)

	# step 4. Calculate Relative Entropy for each residue
	Label(root, text='4. Calculate Relative Entropy for each feature', font=textfontbold).grid(row=9,column=0,columnspan=8,sticky=W,padx=30);
	reuse_re = IntVar()
	reuse_re.set(1)
	Checkbutton(root, text="Reuse Data", variable=reuse_re).grid(row=9, column=8, columnspan=4,sticky=W)

	# step 5. Applied Networkx to Build Graph
	Label(root, text='5. Applied Networkx to Build Graph', font=textfontbold).grid(row=10,column=0, columnspan=8,sticky=W,padx=30);
	Label(root, text='Cutoff Value (A)', padx=60).grid(row=11,column=0, columnspan=3,sticky=W, padx=(30,30))
	cutoff = Entry(root, width=7); cutoff.grid(row=11,column=3, columnspan=2,sticky='w');
	reuse_graph = IntVar()
	reuse_graph.set(1)
	Checkbutton(root, text="Reuse Data", variable=reuse_graph).grid(row=11, column=8, columnspan=4,sticky=W)

	# step 6. Calculate Shorest Path
	Label(root, text='6. Calculate shortest path between source and target', font=textfontbold).grid(row=12,column=0, columnspan=8,sticky=W, padx=30)
	Label(root, text='Source: ').grid(row=13,column=0, columnspan=3,sticky=E, padx=(100,10))
	source = Entry(root, width=3); source.grid(row=13,column=3, columnspan=2,sticky='w');
	Label(root, text='Target: ').grid(row=13,column=5, columnspan=3,sticky=E, padx=(30,10))
	target = Entry(root, width=3); target.grid(row=13,column=8, columnspan=2,sticky='w');

	# step 7. find the seperation of communities
	Label(root, text='7. find the seperation of communities', font=textfontbold).grid(row=14,column=0, columnspan=8,sticky=W,padx=30)
	selectalgrithm = IntVar()
	selectalgrithm.set(1)

	Radiobutton(root, text="Kernighan Lin algorithm", variable=selectalgrithm, value=1).grid(row=15,column=0, columnspan=3,sticky=E,padx=(30,5))
	Radiobutton(root, text="Girvan Newman algorithm", variable=selectalgrithm, value=2).grid(row=15,column=3, columnspan=5,sticky=W,padx=(5,5))
	Radiobutton(root, text="Hybrid Algorithm", variable=selectalgrithm, value=3).grid(row=15,column=8, columnspan=4,sticky=W,padx=(5,30))

	Label(root, text='Number of communities: ').grid(row=16,column=0, columnspan=3,sticky=E, padx=(10,10))
	commu = Entry(root, width=3); commu.grid(row=16,column=3,sticky='w');
	Label(root, text='Repeat Times: ').grid(row=16,column=4, columnspan=4,sticky=W, padx=(30,10))
	repeat = Entry(root, width=3); repeat.grid(row=16,column=8, columnspan=2,sticky='w');

	Message(root, text="Kernighan Lin algorithm need the number of communities and repeat times\nGirvan Newman algorithm do not need any parameters \nHybrid Algorithm can specify number of communities or use Girvan Newman algorithm guess the communities", width=600, font=textfontitalic).grid(row=17,column=0,columnspan=16,rowspan=2,sticky='news')

	data = {}
	data['psf'] = psf_file_entr
	data['dcd1'] = dcd1_file_entr
	data['dcd2'] = dcd2_file_entr
	data['reuse_alphadist'] = reuse_alphadist
	data['reuse_densdist'] = reuse_densdist
	data['reuse_re'] = reuse_re
	data['cutoff'] = cutoff
	data['reuse_graph'] = reuse_graph
	data['source'] = source
	data['target'] = target
	data['selectalgrithm'] = selectalgrithm
	data['commu'] = commu
	data['repeat'] = repeat

	# run or exit
	b1 = Button(root, text='Run', borderwidth=3, font=buttonfont, height=2,width=7, command=lambda: fetch_all(data))
	b1.grid(row=19, column=0, columnspan=4,padx=20,pady=20)
	b2 = Button(root, text='Quit', borderwidth=3, command=root.destroy, height=2,width=7, font=buttonfont)
	b2.grid(row=19, column=7, columnspan=4,padx=20,pady=20)


	root.mainloop()
