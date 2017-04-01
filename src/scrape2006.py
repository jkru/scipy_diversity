from bs4 import BeautifulSoup


def get_soup():
	f = open('../data/html/2006.html','r')
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
		if i == time_index+1 and text !="" and '(provided)' not in text and '-- Break --' not in text:
			text = text.replace('(PDF slides)','').replace("--","").strip()
			current_string = text
		if i == time_index+2 and text!="":
			talk_type = 'n'
			gender = 'm'
			multiple = '0'
			source = 's'

			if 'eynote' in current_string:
				talk_type = 'k'
			current_string = text+'@'+current_string+'@'+talk_type+'@'+gender+'@'+multiple+'@'+source
			print(current_string)
			time_index = -2
			current_string = ''
		if ":" in text and len(text.strip())<6:
			time_index = i
		i+=1


	

if __name__ == '__main__':
	main()


