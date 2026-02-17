import { faker } from '@faker-js/faker';
import { test } from '@playwright/test';

/**
 * DataFactory centralise la génération de données de test et les logs de reporting.
 * Il permet d'assurer l'unicité et la lisibilité des rapports Playwright.
 */
export class DataFactory {
    
    /**
     * Génère un username unique basé sur un pattern ou faker.
     */
    static async generateUniqueUsername(firstName?: string, lastName?: string): Promise<string> {
        return test.step(`Génération d'un username unique pour ${firstName || 'utilisateur'}`, async () => {
            const username = faker.internet.username({ firstName, lastName });
            console.log(`[DATA] Unique Username généré : ${username}`);
            return username;
        });
    }

    /**
     * Génère un email unique.
     */
    static async generateUniqueEmail(firstName?: string, lastName?: string): Promise<string> {
        return test.step(`Génération d'un email unique`, async () => {
            const email = faker.internet.email({ firstName, lastName });
            console.log(`[DATA] Unique Email généré : ${email}`);
            return email;
        });
    }

    /**
     * Log une étape de donnée dans le rapport Playwright.
     */
    static async logDataUsage(key: string, value: string) {
        await test.step(`Utilisation de la donnée : ${key} = ${value}`, async () => {
            // Uniquement pour le reporting
        });
    }
}
