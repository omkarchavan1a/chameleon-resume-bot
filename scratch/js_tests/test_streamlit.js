const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
    let browser;
    try {
        console.log("Launching browser...");
        browser = await chromium.launch({ headless: true });
        const context = await browser.newContext();
        const page = await context.newPage();
        
        console.log("Navigating to Streamlit app...");
        await page.goto('http://localhost:8501', { waitUntil: 'networkidle' });

        await page.waitForTimeout(5000);
        
        // Take a screenshot to debug
        await page.screenshot({ path: 'screenshot.png' });
        console.log("Screenshot saved.");
        
        // Dump the page text
        const content = await page.textContent('body');
        console.log("Page Content:", content.substring(0, 500).replace(/\s+/g, ' '));
        
    } catch (e) {
        console.error("Test failed with exception:", e);
        process.exit(1);
    } finally {
        if (browser) await browser.close();
    }
})();
