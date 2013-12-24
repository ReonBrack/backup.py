#! /usr/bin/env python

# Imports
import datetime
import os
import sys
import tarfile
import subprocess
from datetime import timedelta

# Global variables
sourcefile = os.path.expanduser("~")
backupfile = "/backup/"
date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
logfile = ""
error_flag = False

# Functions
def main():
	prepare()
	intro()
	dirlist = create_dirlist(sourcefile)
	logfile = create_log_entry(dirlist)
	do_backup()
	print_and_log("End of the script")

def prepare():
	check_sudo()
	if not os.path.isdir(backupfile):		
		os.makedirs(backupfile)
		print 'Created /backup/...'

def check_sudo():
	if os.getuid() != 0:
		print "This program is not run as sudo or super user."
		print "Please run this script as sudo."
		sys.exit()

def do_backup():
	if check_last_backup():
		print_and_log("Yesterday's backup found")
		print_and_log("Starting basic backup")
		basic_backup(sourcefile, backupfile)
	else:
		print_and_log("Yesterday's backup NOT found")
		incremental_backup(sourcefile, backupfile)

def incremental_backup(source, out):
	print_and_log("Staring incremental backup")
	command = ['rsync', '-a', '--compress', '--remove-source-files', '--log-file=[{}]'.format(logfile), source, out]
	try:
		subprocess.Popen(command, stdout=subprocess.PIPE)
	except Exception as e:
		print_and_log("/n *** ERROR *** /n")
		print_and_log(e)
		error_flag = True	

def basic_backup(input, output):
	print_and_log("Backing up " + input + " to " + output)

	if not os.path.isdir(output):
		os.makedir(output)
		print_and_log("Folder " + output + "has been created")
	
	output_filename = str(date + ".tar.gz")
	tar = tarfile.open(output + output_filename, "w:gz")
	tar.add(input)
	tar.close()
	print_and_log("Backup finished")
	return tar

def check_last_backup():
	dir = os.listdir(backupfile)
	if any(date+".tar.gz" in tar for tar in dir):
		return True	
	return False

def create_dirlist(directory):
	tree = ""
	for path, dirs, files in os.walk(directory):
		tree += path + "\n"
		for file in files:
			tree += os.path.join(path, file) + "\n"
	return str(tree)

def print_and_log(message):
	f = str(message)
	print f
	create_log_entry(f)

def create_log_entry(data):
	filename = date + ".log"
	if not os.path.exists(backupfile + filename):
		print "Creating new logfile: " + filename	
		open(date + ".log", "w+")
	
	file = open(backupfile + filename, "a")
	file.write(data + "\n")
	file.close()

def intro():
	print " _______________________________"
	print "| Linux Server Security		|"
	print "| Linux Backup Script		|"
	print "| David Louagie			|"
	print "| 3 CCCP		        |"
	print "|_______________________________|"
	print_and_log("Starting backup script @ " + str(datetime.datetime.now()))	

if __name__ == "__main__":
    main()
