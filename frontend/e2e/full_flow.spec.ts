import { test, expect } from '@playwright/test';

test.describe('Procon Ágil E2E Flow', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to the app
        await page.goto('http://localhost:5173');
        // Wait for initial load
        await expect(page.locator('text=Procon Ágil')).toBeVisible();
    });

    test('displays initial welcome messages', async ({ page }) => {
        // Check that welcome messages are visible
        await expect(page.locator('text=Olá! Sou o assistente')).toBeVisible();
        await expect(page.locator('text=qual é o problema principal')).toBeVisible();
    });

    test('shows category selector on initial load', async ({ page }) => {
        // Category buttons should be visible
        await expect(page.locator('text=Problemas de Manutenção')).toBeVisible();
        await expect(page.locator('text=Cobranças / Multas')).toBeVisible();
        await expect(page.locator('text=Retenção de Caução')).toBeVisible();
    });

    test('can select a category and receive response', async ({ page }) => {
        // Click on maintenance category
        await page.click('text=Problemas de Manutenção');

        // Wait for user message to appear
        await expect(page.locator('text=Problemas de Manutenção').last()).toBeVisible();

        // Wait for bot response (allow time for API call)
        await page.waitForTimeout(2000);

        // Bot should respond with legal analysis
        const messages = page.locator('[class*="bg-slate-800"]'); // Bot message bubbles
        await expect(messages.locator('text=/Score|Lei|detalhes/i').first()).toBeVisible({ timeout: 5000 });
    });

    test('can send a message via input', async ({ page }) => {
        // First select a category to enable input
        await page.click('text=Problemas de Manutenção');
        await page.waitForTimeout(1000);

        // Type a message
        const input = page.locator('textarea[placeholder*="Conte"]');
        await input.fill('Tenho vazamento no banheiro há 3 meses');

        // Click send button
        await page.click('button:has(svg)'); // Send button with icon

        // Wait for response
        await page.waitForTimeout(2000);

        // User message should appear
        await expect(page.locator('text=vazamento no banheiro')).toBeVisible();
    });

    test('can trigger upload widget', async ({ page }) => {
        // Select category first
        await page.click('text=Problemas de Manutenção');
        await page.waitForTimeout(1500);

        // Type "foto" to trigger upload widget
        const input = page.locator('textarea[placeholder*="Conte"]');
        await input.fill('Quero enviar uma foto');
        await page.keyboard.press('Enter');

        await page.waitForTimeout(1500);

        // Upload widget should appear
        await expect(page.locator('text=Upload de Evidência')).toBeVisible({ timeout: 5000 });
    });

    test('can generate claim document', async ({ page }) => {
        // Select category
        await page.click('text=Problemas de Manutenção');
        await page.waitForTimeout(1500);

        // Type "gerar reclamação" to trigger document generation
        const input = page.locator('textarea[placeholder*="Conte"]');
        await input.fill('gerar reclamação');
        await page.keyboard.press('Enter');

        // Wait for generation and navigation to review screen
        await page.waitForTimeout(3000);

        // Review screen should appear
        await expect(page.locator('text=Revisão Final')).toBeVisible({ timeout: 10000 });
        await expect(page.locator('text=CONFIRMAR E REGISTRAR')).toBeVisible();
    });

    test('review screen has editable fields', async ({ page }) => {
        // Go to review screen
        await page.click('text=Problemas de Manutenção');
        await page.waitForTimeout(1500);

        const input = page.locator('textarea[placeholder*="Conte"]');
        await input.fill('gerar reclamação');
        await page.keyboard.press('Enter');

        await page.waitForTimeout(3000);

        // Check editable fields exist
        await expect(page.locator('input[type="text"]').first()).toBeVisible();
        await expect(page.locator('textarea').first()).toBeVisible();

        // Check back button works
        await page.click('text=Voltar ao Chat');
        await expect(page.locator('text=Procon Ágil')).toBeVisible();
    });
});
