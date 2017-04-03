def main():
	f = open('../data/2009_bofs.csv')
	#f = open('../data/2009_talks.txt')
	#f = open('../data/2008_raw.txt')
	#f = open('../data/2008_tutorial.txt')
	last_title = ''
	for line in f:
		line = line.strip().split('(')
		title, author = line
		title = title.strip()
		author = author.replace(')','@')

		#if title == last_title:
		#	mult = '1'
		#else:
		#	mult = '0'
		#last_title = title

		mult = '1' #for bofs
		if 'eynote' in title:
			talk_type = 'k'
		else:
			talk_type = 'n'
			#talk_type = 't'
		talk_type = 'b'
		print(author+title+'@'+talk_type+'@m@'+mult+'@s')

if __name__ == '__main__':
	main()