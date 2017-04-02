from bs4 import BeautifulSoup


def get_soup():
	f = open('../data/html/2007_lightning.html','r')
	html_doc = f.read()
	#soup = BeautifulSoup(html_doc, 'html.parser')
	soup = BeautifulSoup(html_doc, 'html5lib')
	
	return soup

def main():
	soup = get_soup()
	soup = soup.find_all("p")
	time_index = 0
	i = 0
	current_string = ""
	for line in soup:
		text = line.get_text().strip()
		if i == time_index+1 and text !="" and 'reakfast' not in text and '-- Break --' not in text:
			text = text.replace('(PDF slides)','').replace("--","").strip()
			current_string = text
		#this line accidentally omits anything with a ":" in the title. Oops
		if i == time_index+2 and text!="" and (text[1] != ':' and text[5]!='m') and 'reakfast' not in text:
			talk_type = 'n'
			gender = 'm'
			multiple = '0'
			source = 's'
			if 'eynote' in text:
				talk_type = 'k'
			current_string = current_string+'@'+text+'@'+talk_type+'@'+gender+'@'+multiple+'@'+source
			print(current_string.replace('"',''))
			time_index = -2
			current_string = ''
		if ":" in text and ('am' in text or 'pm' in text) and len(text.strip())<7:
			time_index = i
		i+=1


	

if __name__ == '__main__':
	main()


