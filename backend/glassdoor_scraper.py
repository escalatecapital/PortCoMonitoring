from playwright.sync_api import sync_playwright

def get_glassdoor_data(glassdoor_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(glassdoor_url, timeout=30000)
            page.wait_for_timeout(3000)

            # Find the average rating
            rating_selector = 'span[data-test="rating"]'
            rating = page.query_selector(rating_selector)
            average_rating = rating.inner_text().strip() if rating else "N/A"

            # Grab top 3 reviews
            review_selector = 'div[data-test="review"]'
            review_elements = page.query_selector_all(review_selector)

            recent_reviews = []
            for el in review_elements[:1]:
                title = el.query_selector('span[data-test="review-title"]')
                snippet = el.query_selector('span[data-test="review-snippet"]')
                review_data = {
                    "title": title.inner_text().strip() if title else "No title",
                    "snippet": snippet.inner_text().strip() if snippet else "No snippet"
                }
                recent_reviews.append(review_data)

            return average_rating, recent_reviews

        except Exception as e:
            print(f"❌ Glassdoor scraping failed: {e}")
            return "N/A", []

        finally:
            browser.close()