import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import datetime
import pytz


async def main():
    # Start Playwright in asynchronous mode
    async with async_playwright() as p:
        # Launch the browser (you can also use firefox or webkit)
        browser = await p.chromium.launch()

        # Open a new page
        page = await browser.new_page()

        # Go to the target webpage
        await page.goto('https://developer.chrome.com/blog')  # Replace with your target URL

        # Wait for the content to load (modify as needed)
        await page.wait_for_selector('.devsite-card-wrapper')  # Replace with relevant selector

        # Get the page content
        content = await page.content()

        # Close the browser
        await browser.close()

        # Parse with Beautiful Soup
        soup = BeautifulSoup(content, 'html.parser')

        # Now you can use soup to find elements, parse content, etc.
        # Example: print(soup.prettify())

        # Extract the card details
        cards = soup.find_all("div", class_="devsite-card-wrapper")
        card_data = []

        for card in cards:
            card_info = {
                "displaytitle": card.get("displaytitle", ""),
                "image": card.get("image", ""),
                "summary": card.get("summary", ""),
                "url": card.get("url", ""),
                "timestamp": card.get("timestamp", "")
            }
            card_data.append(card_info)

        # Generate RSS feed

        fg = FeedGenerator()
        fg.title('Google Chrome Developer Blog')
        fg.link(href='https://developer.chrome.com/blog', rel='alternate')
        fg.description('Latest blog posts from the Google Developer Blog')

        # Get the current timestamp
        current_timestamp = datetime.datetime.now(pytz.utc)

        # Format the timestamp as per RSS specification
        formatted_timestamp = current_timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')

        fg.pubDate(formatted_timestamp)  # Add pubDate with the formatted timestamp


        for card in card_data:
            fe = fg.add_entry()
            fe.title(card['displaytitle'])
            fe.link(href=card['url'])
            fe.description(card['summary'])

            # Convert timestamp from epoch to datetime
            timestamp = datetime.datetime.fromtimestamp(int(card['timestamp']), pytz.utc)

            # Format the timestamp as per RSS specification
            formatted_timestamp = timestamp.strftime('%a, %d %b %Y %H:%M:%S %z')

            fe.pubDate(formatted_timestamp)  # Add pubDate with the formatted timestamp

        # Generate the RSS feed XML
        #rss_feed = fg.rss_str(pretty=True)
        #print(rss_feed)

        fg.rss_file('rss/bring_back_reader.xml', extensions=True, pretty=True, encoding='UTF-8', xml_declaration=True)

asyncio.run(main())