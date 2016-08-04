#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Justin Salisbury <justin@salisbury.de>"
__license__ = "GNU GPLv3+"
__version__ = 1.0
__date__ = "25/07/2016"

# 
# adapted from: 
# https://github.com/PabloCastellano/pablog-scripts/blob/master/mbox-extract-attachments.py
#
# fixes for a 1.2Gb google-takeout-mbox-file of about 3000 emails include:
# 
# hash-filenames for duplicates
# recurse into eml-attachments and multiparts 
# cleaned up the filename-handling
# 
# did not handle python3 

import mailbox
import base64
import os
import sys
import email
import re
import md5


BLACKLIST = ('signature.asc', 'message-footer.txt', 'smime.p7s')
VERBOSE = 1

attachments = 0  # Count extracted attachment
skipped = 0

# extracted from django
def get_valid_filename(s):
    """
    Returns the given string converted to a string that can be used for a clean
    filename. Specifically, leading and trailing spaces are removed; other
    spaces are converted to underscores; and anything that is not a unicode
    alphanumeric, dash, underscore, or dot, is removed.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = s.strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

# Search for filename or find recursively if it's multipart
def extract_attachment(payload):
	global attachments, skipped
	filename = payload.get_filename()
	if filename is not None:
		print "\nAttachment found!"
		if filename.find('=?') != -1:
			ll = email.header.decode_header(filename)
			filename = ""
			for l in ll:
				filename = filename + l[0]
			
		if filename in BLACKLIST:
			skipped = skipped + 1
			if (VERBOSE >= 1):
				print "Skipping %s (blacklist)\n" % filename
			return

		# Puede no venir especificado el nombre del archivo??		
		content = payload.as_string()
		# Skip headers, go to the content
		fh = content.find('\n\n')
		content = content[fh:]
		# if it's base64....
		if payload.get('Content-Transfer-Encoding') == 'base64':
			content = base64.decodestring(content)
		# quoted-printable
		# what else? ...

		print "Extracting %s (%d bytes)\n" % (filename, len(content))
		
		(naked_filename, extension) = os.path.splitext(filename)
		if extension == '.eml':
			em = email.message_from_string(content)
			if em.is_multipart():
				for payl in em.get_payload():
					extract_attachment(payl)
			else:
				extract_attachment(em)
			return		

		filename = get_valid_filename(filename)
		if os.path.exists(filename):
			(naked_filename, extension) = os.path.splitext(filename)
			filename = "-".join([naked_filename, md5.md5(content).hexdigest()]) + extension 
		
		with open(filename, 'wb') as fp:
			fp.write(content)
			fp.close()	
		attachments = attachments + 1
	else:
		if payload.is_multipart():
			for payl in payload.get_payload():
				extract_attachment(payl)


# ##
print "Extract attachments from mbox files"
print

if len(sys.argv) < 2 or len(sys.argv) > 3:
	print "Usage: %s <mbox_file> [directory]" % sys.argv[0]
	sys.exit(0)

filename = sys.argv[1]
directory = os.path.curdir

if not os.path.exists(filename):
	print "File doesn't exist:", filename
	sys.exit(1)

if len(sys.argv) == 3:
	directory = sys.argv[2]
	if not os.path.exists(directory) or not os.path.isdir(directory):
		print "Directory doesn't exist:", directory
		sys.exit(1)

mb = mailbox.mbox(filename)
nmes = len(mb)

os.chdir(directory)

for i in range(len(mb)):
	if (VERBOSE >= 2):
		print "Analyzing message number", i

	mes = mb.get_message(i)
	em = email.message_from_string(mes.as_string())

	subject = em.get('Subject')
	if not subject:
		continue 
	if subject.find('=?') != -1:
		ll = email.header.decode_header(subject)
		subject = ""
		for l in ll:
			subject = subject + l[0]

	em_from = em.get('From')
	if em_from.find('=?') != -1:
		ll = email.header.decode_header(em_from)
		em_from = ""
		for l in ll:
			em_from = em_from + l[0]

	if (VERBOSE >= 2):
		print "%s - From: %s" % (subject, em_from)

	filename = mes.get_filename()
	
	# Puede tener filename siendo multipart???
	if em.is_multipart():
		for payl in em.get_payload():
			extract_attachment(payl)
	else:
		extract_attachment(em)

print "\n--------------"
print "Total attachments extracted:", attachments
print "Total attachments skipped:", skipped
