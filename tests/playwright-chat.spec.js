const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false }); // Shows the browser
  const page = await browser.newPage();
  await page.goto('http://localhost:8000'); // Change to your portal's URL

  // --- Login ---
  // Wait for login form fields (update selectors as needed)
  await page.waitForSelector('input[name="username"]');
  await page.fill('input[name="username"]', 'ethan');
  await page.fill('input[name="password"]', 'hola');
  await page.click('button[type="submit"]'); // Update selector if your login button is different

  // --- Wait for portal page to load ---
  // Adjust selector to something unique on your portal page
  await page.waitForSelector('input[type="text"], textarea');

  // --- Enter chat message ---
  await page.fill('input[type="text"], textarea', 'who are you');
  await page.keyboard.press('Enter');

  // Optional: wait for response or take a screenshot
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'chat-after-login.png' });

  // await browser.close(); // Uncomment to close browser automatically
})();