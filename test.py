import subprocess
import os 

def processor(master_link):
	f = open(master_link, "r")
	link=f.readline()
	#file_path=f.readline()
	f.close()
	os.remove(master_link)
	subprocess.call(" python script.py {0}".format(link),shell=True)
