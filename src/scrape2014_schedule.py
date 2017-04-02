import argparse
import requests

from bs4 import BeautifulSoup

def getTalkType(header):
	if header.startswith('Tutorials '):
		return 't'
	elif header.startswith('Talks '):
		return 'n'
	elif header.startswith('Birds '):
		return 'b'
	else:
		return None

def main(outfile):
	r = requests.get('https://conference.scipy.org/scipy2014/schedule/', verify=False)
	soup = BeautifulSoup(r.text, 'html5lib')
	tables = soup.find_all('table')

	f = open(outfile, 'w')
	for tbl in tables:
		talkType = getTalkType(tbl.findPrevious().text)
		if talkType is None:
			continue

		titles = tbl.find_all('span', {'class': 'title'})
		for title in titles:
			speakers = title.findNextSibling().text.split(',')
			multiple = int(len(speakers) > 1)
			for s in speakers:
				f.write('%s@%s@%s@m@%s@s\n' % (s.strip(), title.text.strip(), talkType, multiple))
		
	f.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('outfile')
	args = parser.parse_args()
	main(args.outfile)
