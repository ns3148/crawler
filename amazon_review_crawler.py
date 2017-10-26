import requests
import os
from bs4 import BeautifulSoup
import pprint 
import json
import re
import pandas as pd
import time

reviews = []
products_list = {'dove':'https://www.amazon.com/Dove-Beauty-Sensitive-Ounce-Count/product-reviews/B005HO0AR2/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&reviewerType=all_reviews&pageNumber=',
				 'axe_deo':'https://www.amazon.com/Stick-Excite-Unilever-Hpc-Usa-11475/product-reviews/B00V6C766W/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&reviewerType=all_reviews&pageNumber=',
				 'vaseline_intensive_lotion':'https://www.amazon.com/Vaseline-Intensive-Lotion-Advanced-Unscented/product-reviews/B00I69TBUW/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&reviewerType=all_reviews&pageNumber=',
				 'lipton':'https://www.amazon.com/Lipton-Family-Black-Iced-Unsweetened/product-reviews/B00I8GPUDU/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&reviewerType=all_reviews&pageNumber=',
				 'cif':'https://www.amazon.com/Frosch-Natural-Lemon-Scouring-Cleaner/product-reviews/B00XASY7T4/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&reviewerType=all_reviews&pageNumber='
				}


def getReviews(page, product_name):
	global reviews

	content = requests.get(page)
	html = content.text
	soup = BeautifulSoup(html, "lxml")
	total = 0

	try:
		for level1 in soup.find_all("div", {'class': 'a-section a-spacing-none reviews-content a-size-base'}):
			for level2 in level1("div", {'id': 'cm_cr-review_list'}):
				for level3 in level2("div", {'class': 'a-section review'}):
					review = {}
					review['product'] = product_name

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

	except:
		return 0


def extractReviews():
	global reviews

	for product_name, product_page in products_list.items():
		print(product_name)
		reviews =  []

		pageno = 1

		# Set this for required no. of pages
		total_pages = 10000

		total_reviews = 0

		while(pageno <= total_pages):
			page = product_page + str(pageno)
			total = getReviews(page, product_name)
			
			print("Page No. = " + str(pageno))

			if total == 0:
				break

			total_reviews += total

			if pageno % 10 == 0:
				time.sleep(60)

			pageno += 1

		print(total_reviews)

		df1 = pd.DataFrame.from_dict(reviews)
		writer = pd.ExcelWriter('storage.tmp/' + product_name + '.xlsx')
		df1.to_excel(writer)

		time.sleep(120)


if __name__ == "__main__":
	extractReviews()