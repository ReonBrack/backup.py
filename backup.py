#! /usr/bin/env python

# Imports
import os, sys, tarfile, smtplib, datetime, hashlib, re, optparse
from datetime import date, timedelta
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

# Global variables
tobackup = os.path.expanduser("~")
backupfolder = "/backup"
tempfolder = '/tmp'
date = str(datetime.datetime.now().strftime("%Y%m%d"))
log_entries = []

# Functions
def main():
	prepare()
	intro()
	do_backup()
	#send_mail()	

def prepare():
	check_sudo()
	if not os.path.isdir(backupfolder):		
		os.makedirs(backupfile)
	
	parser = optparse.OptionParser('usage%prog -r <to_recover>')
	parser.add_option('-r', '--recover', dest='to_recover', help='specify foldername to recover')
	(options, args) = parser.parse_args()
	if options.to_recover is not None:
		recover(options.to_recover)
		
def recover(foldername):
	location = backupfolder + '/' + foldername
	tar_location = location + '/' + foldername + '.tar.gz'
	log_location = location + '/' + foldername + '.log'
	log = open(log_location, 'a')
	log.write('Recovery started @' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
	
	try:
		tar = tarfile.open(tar_location, "r")
		tar.extractall(path=tobackup)
	except Exception as e:		
		log.write(str(e) + '\n')
		pass
	
	log.write('Recovery finished @' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
	log.close()
	sys.exit()
	
def check_sudo():
	if os.getuid() != 0:
		print "This program is not run as sudo or super user."
		print "Please run this script as sudo."
		sys.exit()

def do_backup():
	if check_empty(backupfolder):
		print 'No previous backups fould!'
		print 'Starting full backup...'
		log_entries.append('No previous backups fould!')
		log_entries.append('Starting full backup...')
		backup(list_fullbackup(tobackup), backupfolder)
	elif check_last_backup():
		print 'Yesterday\'s backup found!'
		print 'Starting full backup...'
		log_entries.append('Yesterday\'s backup found!')
		log_entries.append('Starting full backup...')
		backup(list_fullbackup(tobackup), backupfolder)
	else:
		print 'Yesterday\'s backup NOT found'
		print 'Starting incremental backup...'
		log_entries.append('Yesterday\'s backup NOT found')
		log_entries.append('Starting incremental backup...')
		create_checksum(tobackup, tempfolder)
		changed_files = compare_checksumfiles(tempfolder + '/' + date + '.chk', get_checksum_file(backupfolder))
		backup(changed_files, backupfolder)

def get_checksum_file(folder):
	folder =  backupfolder + '/' + os.listdir(folder)[0]
	for file in os.listdir(folder):
		if file.endswith('.chk'):
			return folder + '/' + file
	
def check_empty(dir):
	if not os.listdir(dir):
		return True
	return False

def list_fullbackup(tobackup):
	list = []
	for path, dirs, files in os.walk(tobackup):
		for file in files:
			list.append(os.path.join(path, file))
	return list
			
def create_checksum(folder, destination):
	f = open('{}.chk'.format(destination + '/' + date), 'w+')
	for path, dirs, files in os.walk(folder):
		for file in files:
			hash = hashlib.md5(path + '/' + file).hexdigest()
			f.write('{} - {}'.format(hash, path + '/' + file) + '\n')
	f.close()

def compare_checksumfiles(tmpfile, storagefile):
	with open(tmpfile, 'r') as f1:
		with open(storagefile, 'r') as f2:
			diff = {name.rstrip('\n') for name in set(f1).difference(f2)}
	path = []
	for item in diff:
		path.append(str(item.split(' - ')[1]))
	return path

def backup(input, output):
	Error_flag = False
	base_path = output + '/' + date
	os.makedirs(output + '/' + date)	
	
	log = open(base_path + '/' + date + '.log', 'w+')
	md5 = open(base_path + '/' + date + '.chk', 'w+')	
	tar = tarfile.open(base_path + '/' + date + '.tar.gz', "w:gz")
	
	for entry in log_entries:
		log.write(entry + '\n')
	
	for path in input:
		try:				
			tar.add(path)
			hash = hashlib.md5(path).hexdigest()
			md5.write('{} - {}'.format(hash, path) + '\n')		
		except Exception as e:
			Error_flag = True
			log.write(str(e) + '\n')
			pass
	
	if not Error_flag:
		log.write('Backup was a SUCCESFUL\n')
	else:
		log.write('Backup completed with some errors!\n')
	
	log.write('Backup ended @ ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))		
	tar.close()
	log.close()
	md5.close()
	
def check_last_backup():
	yesterday = (datetime.datetime.now() - timedelta(1)).strftime('%Y%m%d')
	dirlist = os.listdir(backupfolder)
	if any(yesterday in dir for dir in dirlist):
		return True	
	return False

def send_mail(send_from='louagie.david@gmail.com', send_to='david.louagie@student.howest.be'):
	msg = MIMEMultipart()
	msg['From']=send_from
	msg['To']=COMMASPACE.join(send_to)
	msg['Date']=formatdate(localtime=True)
	msg['Subject']='Backup Service Completed @ ' + str(datetime.datetime.now())
	msg.attach(MIMEText('Have a nice day!'))
	
	logfile = backupfolder + '/' + date + '/' + date + '.log'
	part = MIMEBase('application', "octet-stream")
	part.set_payload(open(logfile,"rb").read())
	Encoders.encode_base64(part)
	part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(logfile))
	msg.attach(part)

	smtp = smtplib.SMTP_SSL('smtp.gmail.com')
	smtp.login(send_from, 'mypwd')
	smtp.sendmail(send_from, send_to, msg.as_string())
	smtp.close()

def intro():
	print " _______________________________"
	print "| Linux Server Security		|"
	print "| Linux Backup Script		|"
	print "| David Louagie			|"
	print "| 3 CCCP		        |"
	print "|_______________________________|"
	log_entries.append('Starting backup script @ ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))	

if __name__ == "__main__":
    main()
