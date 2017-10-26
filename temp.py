import requests
import os
from bs4 import BeautifulSoup
import pprint 
import json
import re
import pandas as pd
reviews = []

def getReviews(page):
	global reviews

	content = requests.get(page)
	html = content.text
	soup = BeautifulSoup(html, "lxml")
	total = 1


	for level1 in soup.find_all("div", {'class': 'a-section a-spacing-none reviews-content a-size-base'}):
		for level2 in level1("div", {'id': 'cm_cr-review_list'}):
			for level3 in level2("div", {'class': 'a-section review'}):
				review = {}

				# Avoid overwriting of stars
				stars_text = ""

				# Get review ratings and title
				for level4 in level3("div", {'class': 'a-row'}):
					for level5 in level4("span", {'class': 'a-icon-alt'}):
						if stars_text == "":
							stars_text = level5.text.split(" ")[0]
							review['stars'] = stars_text
				
				for level4 in level3("a", {'class': 'a-size-base a-link-normal review-title a-color-base a-text-bold'}):
					review['title'] = level4.text

				# Get review text
				for level4 in level3("div", {'class': 'a-row review-data'}):
					for level5 in level4("span", {'class': 'a-size-base review-text'}):
						text = re.sub(r"<.*>", " ", level5.text)
						review['text'] = text.strip()

				reviews.append(review)
				total += 1

	return total



def extractReviews():
	global reviews

	all_reviews = {}
	pageno = 1

	# Set this for required no. of pages
	total_pages = 1

	total_reviews = 0

	while(pageno <= total_pages):
		page = "https://www.amazon.com/Seagate-Expansion-Portable-External-STEA2000400/product-reviews/B00TKFEE5S/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&reviewerType=all_reviews&pageNumber=" + str(pageno)
		total = getReviews(page)
		
		print("Page No. = " + str(pageno))

		if total == 0:
			break

		pageno += 1
		total_reviews += total

	print(total_reviews - 1)

	df1 = pd.DataFrame.from_dict(reviews)
	writer = pd.ExcelWriter('storage.tmp/reviews.xlsx')
	df1.to_excel(writer)


if __name__ == "__main__":
	extractReviews()