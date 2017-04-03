import argparse
import requests

from bs4 import BeautifulSoup

def isFirstLast(author_token):
	if not ',' in author_token:
		return True
	
	comma_tokens = author_token.split(', ')
	return ' ' in comma_tokens[0]

def main(outfile):
	r = requests.get('http://conference.scipy.org/scipy2013/conference_talks_schedule.php')
	soup = BeautifulSoup(r.text, 'html5lib')
	tables = soup.find_all('table')

	f = open(outfile, 'w')
	for tbl in tables:
		author_tags = tbl.find_all('span', {'class': 'authors'})
		for author_tag in author_tags:
			if author_tag.text == '':
				continue
			
			cell = author_tag.findParent()
			a = cell.find_all('a')
			if len(a) != 1:
				continue
			title = a[0].text
			if 'Keynote' in cell.text:
				talkType = 'k'
			elif 'BoF' in cell.text:
				talkType = 'b'
			else:
				talkType = 'n'
			
			authors = author_tag.text.split('; ')
			multiple = int(len(authors) > 1)
			if isFirstLast(authors[0]):
				for a in authors:
					f.write('%s@%s@%s@m@%s@s\n' % (a.split(', ')[0].strip(), title.strip(), talkType, multiple))

			else:
				for a in authors:
					if len(a) > 2:
						name_tokens = a.split(', ')
						try:
							f.write('%s@%s@%s@m@%s@s\n' % (name_tokens[1] + ' ' + name_tokens[0], title.strip(), talkType, multiple))
						except:
							pass
	f.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('outfile')
	args = parser.parse_args()
	main(args.outfile)