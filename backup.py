#! /usr/bin/env python

# Imports
import datetime
import os
import sys
import tarfile
import subprocess
from datetime import timedelta

# Global variables
sourcefile = "/home/"
timestamp = str(datetime.datetime.now().strftime("%Y%m%d"))
backupfile = "/backup/"
script_location = os.path.realpath(__file__)
script_name = os.path.basename(__file__)
logfile = ""
cron = ""

# Functions
def run_as_root():
	euid = os.geteuid()
	if euid is not 0:
		print "Script has to be ran as root. Running sudo..."
		args = ['sudo', sys.executable] + sys.argv + [os.environ]
		os.execlpe('sudo', *args)
		print "Script is continuing as root"

def do_backup():
	if check_last_backup():
		create_tarfile(sourcefile, backupfile)
	else:
		incremental_backup(sourcefile, backupfile)

def incremental_backup(in, out):
	subprocess.call(["rsync", "-a "+in , "--force", "--backup", "--backup-dir="+out])
	

def check_last_backup():
	dir = os.listdir(backupfile)
	if any(timestamp+".tar.gz" in tar for tar in dir):
		return True
	
	return False

def create_tarfile(input, output):
	print_and_log("Backing up " + input + " to " + output)

	if not os.path.isdir(output):
		os.makedir(output)
		print_and_log("Folder " + output + "has been created")
	
	output_filename = str(timestamp + ".tar.gz")
	tar = tarfile.open(output + output_filename, "w:gz")
	tar.add(input)
	tar.close()
	print_and_log("Backup finished")
	return tar

def create_dirlist(directory):
	tree = ""
	for path, dirs, files in os.walk(directory):
		tree += path + "\n"
		for file in files:
			tree += os.path.join(path, file) + "\n"
	return str(tree)

def create_log_entry(data):
	filename = timestamp + ".log"
	if not os.path.exists(backupfile + filename):
		print "Creating new logfile: " + filename	
		open(timestamp + ".log", "w+")
	
	file = open(backupfile + filename, "a")
	file.write(data + "\n")
	file.close()

def print_and_log(message):
	f = str(message)
	print f
	create_log_entry(f)	

#Start of the script
print " _______________________________"
print "| Linux Server Security		|"
print "| Linux Backup Script		|"
print "| David Louagie			|"
print "| 3 CCCP		        |"
print "|_______________________________|"

print_and_log("Starting backup script at " + timestamp)

#Creating a log from the files that have to be backed up
dirlist = create_dirlist(sourcefile)
logfile = create_log_entry(dirlist)

#Backing up the files
create_tarfile(sourcefile, backupfile)

print_and_log("End of the script")
