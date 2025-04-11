from playwright.sync_api import sync_playwright

def get_glassdoor_data(glassdoor_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-US"
        )
        page = context.new_page()

        try:
            print(f"[DEBUG] Navigating to: {glassdoor_url}")
            page.goto(glassdoor_url, timeout=30000)
            page.wait_for_timeout(3000)  # Let JavaScript render content

            print("[DEBUG] Page snapshot preview (first 500 chars):")
            print(page.content()[:500])

            rating_selector = 'span[data-test="rating"]'
            rating = page.query_selector(rating_selector)
            average_rating = rating.inner_text().strip() if rating else None

            review_selector = 'div[data-test="review"]'
            review_elements = page.query_selector_all(review_selector)

            recent_reviews = []
            for el in review_elements[:3]:
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
            return None, []

        finally:
            browser.close()
