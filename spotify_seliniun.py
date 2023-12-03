from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By



# Set up the Selenium driver with headless option
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Open Spotify
driver.get('https://open.spotify.com/')

# Find the search input field and enter the song name
search_input = driver.find_element(by=By.XPATH, value='//input[@data-testid="search-input"]')
search_input.send_keys('Memories by Maroon 5')
search_input.send_keys(Keys.ENTER)
# Wait for the search results to load
driver.implicitly_wait(5)

# Find the first song in the search results and click on it to play
first_song = driver.find_element_by_xpath('//div[@data-testid="tracklist-row"]')
first_song.click()

# Wait for the song to start playing
driver.implicitly_wait(5)
input("Press Enter to continue...")