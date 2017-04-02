import argparse
import requests

from bs4 import BeautifulSoup
from bs4 import element

def main(url, outfile):
	r = requests.get(url)
	soup = BeautifulSoup(r.text, 'html5lib')
	table = soup.find('table', {'id': lambda x: x and x.startswith('agendatable')} )
	rows = table.find_all('tr', {'class': 'data-group'})
	
	f = open(outfile, 'a')
	for r in rows:
			row_tags = [tag for tag in r.contents[0].find_all()]
			title = row_tags[0].text
			unique_authors = set()
			for t in row_tags[1:]:
					if t.name == 'br' or t.text == '[More Info]':
							continue
					else:
							c = t
							while True:
									c = c.next_element
									if isinstance(c, element.Tag) and c.name == 'tr':
											break
									elif isinstance(c, element.NavigableString) and len(c) > 2:
											if ',' in c:
													author = c.split(',')[0]
													if len(author) > 2:
															unique_authors.add(author)
											else:
													unique_authors.add(c)
			multiple = int(len(unique_authors) > 1)
			for a in unique_authors:
					f.write('%s@%s@n@@%s@s\n' % (a, title, multiple))

	f.close()
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('url', help='url of accepted talks')
	parser.add_argument('outfile')
	args = parser.parse_args()
	main(args.url, args.outfile)