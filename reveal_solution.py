from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--remote-debugging-port=9222")

# Use standard WebDriver (Selenium manages Chrome automatically)
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to your URL
    driver.get("https://examtopics_url")

    print("Chrome opened. Waiting 1 minute for manual changes...")
    time.sleep(60)  # Wait 1 minute
    print("Resuming script...")

    # Wait for page to load and reveal buttons to exist
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.reveal-solution"))
    )

    clicked_count = 0

    # Browser-side fast clicker: dispatch click events from the page with small staggered delays.
    js_clicker = """
    const buttons = Array.from(document.querySelectorAll('a.reveal-solution'));
    const total = buttons.length;
    buttons.forEach((btn, i) => {
        // stagger clicks slightly to avoid blocking UI; 40ms is fast but not instantaneous
        setTimeout(() => {
            try {
                btn.scrollIntoView({behavior: "auto", block: "center"});
                btn.click();
            } catch (e) {
                // ignore per-button errors
            }
        }, i * 40);
    });
    return total;
    """

    try:
        batch_count = driver.execute_script(js_clicker)
        print(f"Dispatched browser-side clicks for {batch_count} buttons")
    except Exception as e:
        print(f"Error executing JS clicker: {e}")
        batch_count = 0

    # Wait for the browser-side clicks to take effect. Allow some buffer.
    time.sleep(max(2, batch_count * 0.05 + 1))

    # Fallback: find any remaining buttons and click them sequentially (handles missed ones)
    while True:
        reveal_buttons = driver.find_elements(By.CSS_SELECTOR, "a.reveal-solution")
        if not reveal_buttons:
            break

        print(f"Found {len(reveal_buttons)} remaining buttons to cl ick in fallback loop")

        for button in reveal_buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.05)
                button.click()
                clicked_count += 1
                print(f"Clicked button {clicked_count} (fallback)")
            except Exception as e:
                print(f"Error clicking button in fallback: {e}")

        # small pause to allow any DOM changes
        time.sleep(0.5)

    print(f"Total buttons clicked (fallback count): {clicked_count + batch_count}")

finally:
    print("Script completed. Chrome remains open.")
