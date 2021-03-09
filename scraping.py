# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import sys

def scrape_all():
   # Initiate headless driver for deployment
   # browser = Browser("chrome", executable_path="chromedriver", headless=True)
    # Windows users
    executable_path = {'executable_path':'C:\\Users\\16084\\.wdm\\drivers\\chromedriver\\win32\\88.0.4324.96\\chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # why isn't this in the function anymore???
        # slide_elem.find("div", class_='content_title')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    return img_url

def mars_facts():
# why do we read html into a df to turn it back out to html from the df???
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)
    # Convert dataframe into HTML format, add bootstrap (what does this mean???)
    return df.to_html(classes="table table-striped")



def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    html = browser.html
    main_page_soup = soup(html, 'html.parser')

        # Add try/except for error handling
    try:
        # Find the number of pictures to scan
        pics_count = len(main_page_soup.select("div.item"))

        for i in range(pics_count):  # iterate through css/html tags with for loop
            # inside for loop put empty dictionary
            hemispheres = {}
    
            #use loop to open each link and navigate to full-resolution image
            link_image = main_page_soup.select("div.description a")[i].get('href')
            browser.visit(f'https://astrogeology.usgs.gov{link_image}') 
    
            # Parse the new html page with soup
            html = browser.html
            sample_image_soup = soup(html, 'html.parser')
            # retrieve full-resolution URL string for each hemisphere
            img_url = sample_image_soup.select_one("div.downloads ul li a").get('href')
            # retrieve title for each hemisphere 
            img_title = sample_image_soup.select_one("h2.title").get_text()

            # Add extracts to the results dict
            hemispheres = {
                'img_url': img_url,
                'title': img_title}
    
            #add dictionary to hemisphere_image_urls list before next iteration
            hemisphere_image_urls.append(hemispheres)
            browser.back()
        #return the scraped data as a list of dictionaries with the URL string and title of each hemisphere image

    except:
           e = sys.exc_info()[0]
           write_to_page( "<p>Error: %s</p>" % e )
    return hemisphere_image_urls
        

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())