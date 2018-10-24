from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
import requests
import sqlite3

conn = sqlite3.connect('INTERNSHALA.db')

c = conn.cursor()

c.execute(
	"""
	CREATE TABLE IF NOT EXISTS Internshala
	(Company_name TEXT,
	Position TEXT,          
	Location TEXT,		         
	Start_date DATE,	         
	Duration TEXT,		         
	Stipend REAL,		         
	Posted_on DATE,		         
	Apply_by DATE, 		 		 
	Rewards_and_incentives TEXT, 
	About TEXT,					 
	Responsibilites TEXT,		 
	Who_can_apply TEXT,			 	
	Perks TEXT,					 
	No_of_interns REAL,		 
	Skills TEXT)				 	
	""")

internshala_link = "https://internshala.com/internships"

session = HTMLSession()

r = session.get(internshala_link)

print('Initializing Scraping...')
for index, link in enumerate(r.html):
	req = requests.get(link.url)
	contents = bs(req.text, 'lxml')
	contents = contents.find_all('div', attrs = {'class': 'internship_meta'})
	print('Scraping link: {} at Page no: {} having {} available internships.'.format(link, index + 1, len(contents)))
	
	for content in contents:
		values = []
		current_link = content.find(name = 'a')['href']
		link = 'https://internshala.com' + current_link
		r = requests.get(link)
		contents = bs(r.text, 'lxml')
		
		company_name = contents.find(name = 'a', attrs = {'class': 'link_display_like_text'})['title']
		position = contents.find(attrs = {'class': 'profile_on_detail_page'}).text
		
		info_content = contents.find(attrs = {'class': 'individual_internship_details'})
		location = info_content.find(attrs = {'class': 'location_link'}).text

		td_tags = info_content.find_all('td')
		start_date = td_tags[0].find('div').text
		duration = td_tags[1].text
		stipend = td_tags[2].text
		posted_on = td_tags[3].text
		apply_by = td_tags[4].text
		try:
			rewards_and_incentives = td_tags[2].find('i')['title']
		except:
			rewards_and_incentives = None

		info_contents = contents.find_all(attrs = {'class': 'internship_details', 'class': 'freetext-container'})

		about = info_contents[0].text
		responsibilities = info_contents[1].text
		who_can_apply = '\n'.join([str(n+1) +'.' + info.text for n, info in enumerate(info_contents[2].find_all('span'))])
		
		try:
			perks = info_contents[3].text
		except:
			perks = None

		try:
			interns_available_no = contents.find(attrs = {'class': 'number_of_internships_available'}).text
		except:
			interns_available_no = None
		
		try:
			skills = contents.find(attrs = {'id': 'skillNames'}).text
		except:
			skills = None
	
		attributes = [company_name, position, location, start_date, duration, stipend, posted_on, 
					  apply_by, rewards_and_incentives, about, responsibilities, who_can_apply, perks, interns_available_no, 
					  skills]

		for attribute in attributes:
			values.append(attribute)

		c.execute("""INSERT INTO Internshala 
			(Company_name,
			Position,          
			Location,		         
			Start_date,	         
			Duration,		         
			Stipend,		         
			Posted_on,		         
			Apply_by, 		 		 
			Rewards_and_incentives, 
			About,					 
			Responsibilites,		 
			Who_can_apply,			 	
			Perks,					 
			No_of_interns,		 
			Skills)				 
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", (values[0], values[1], values[2], values[3], values[4], values[5],
				values[6], values[7], values[8], values[9], values[10], values[11], values[12], values[13], values[14]))
		conn.commit()
	
	#Specifies the number of pages to be scraped in one run. 
	if index >= 10:
		break
	#Remove the above till the above comment to have no limit.

c.close()
conn.close()
