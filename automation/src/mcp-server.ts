
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { chromium, Browser, Page } from 'playwright';

// Create server instance
const server = new Server(
    {
        name: "playwright-mcp-server",
        version: "1.0.0",
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// Helper for executing shell commands properly
const runCommand = (command: string, cwd: string = process.cwd()): Promise<string> => {
    return new Promise((resolve, reject) => {
        exec(command, { cwd, maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
            if (error) {
                resolve(`COMMAND FAILED:\n${stderr}\nSTDOUT:\n${stdout}`);
            } else {
                resolve(stdout);
            }
        });
    });
};

// Helper for Browser Actions
async function withPage(url: string, callback: (page: Page) => Promise<any>) {
    const browser = await chromium.launch({ headless: true });
    try {
        const page = await browser.newPage();
        await page.goto(url, { waitUntil: 'networkidle' });
        return await callback(page);
    } finally {
        await browser.close();
    }
}

// Handler for ListTools
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "write_file",
                description: "Write content to a file",
                inputSchema: {
                    type: "object",
                    properties: {
                        path: { type: "string" },
                        content: { type: "string" }
                    },
                    required: ["path", "content"]
                }
            },
            {
                name: "read_file",
                description: "Read content from a file",
                inputSchema: {
                    type: "object",
                    properties: {
                        path: { type: "string" }
                    },
                    required: ["path"]
                }
            },
            {
                name: "list_files",
                description: "List files in a directory (excludes node_modules, .git, etc.)",
                inputSchema: {
                    type: "object",
                    properties: {
                        directory: { type: "string" },
                        recursive: { type: "boolean", default: false }
                    },
                    required: ["directory"]
                }
            },
            {
                name: "run_playwright_test",
                description: "Run Playwright tests (optionally a specific file)",
                inputSchema: {
                    type: "object",
                    properties: {
                        testFile: { type: "string" }
                    }
                }
            },
            {
                name: "inspect_page",
                description: "Inspect a page and return accessible elements (truncated to 40 elements)",
                inputSchema: {
                    type: "object",
                    properties: {
                        url: { type: "string" }
                    },
                    required: ["url"]
                }
            },
            {
                name: "take_screenshot",
                description: "Take a screenshot of a page",
                inputSchema: {
                    type: "object",
                    properties: {
                        url: { type: "string" },
                        path: { type: "string" }
                    },
                    required: ["url", "path"]
                }
            },
            {
                name: "get_console_logs",
                description: "Get console logs from a page",
                inputSchema: {
                    type: "object",
                    properties: {
                        url: { type: "string" }
                    },
                    required: ["url"]
                }
            },
            {
                name: "explore_page_with_actions",
                description: "Navigate to a URL and perform actions to reach a specific state, then return the DOM (truncated to 40 elements).",
                inputSchema: {
                    type: "object",
                    properties: {
                        url: { type: "string" },
                        actions: {
                            type: "array",
                            items: {
                                type: "object",
                                properties: {
                                    type: { type: "string", enum: ["click", "fill", "wait", "screenshot"] },
                                    selector: { type: "string" },
                                    value: { type: "string" },
                                    timeout: { type: "number" }
                                },
                                required: ["type"]
                            }
                        }
                    },
                    required: ["url", "actions"]
                }
            }
        ]
    };
});

// Handler for CallTool
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
        if (name === "write_file") {
            const { path: filePath, content } = args as { path: string, content: string };
            const fullPath = path.resolve(process.cwd(), filePath);

            // Ensure directory exists
            fs.mkdirSync(path.dirname(fullPath), { recursive: true });
            fs.writeFileSync(fullPath, content, 'utf-8');

            return {
                content: [{ type: "text", text: `Successfully wrote to ${filePath}` }]
            };
        }

        if (name === "read_file") {
            const { path: filePath } = args as { path: string };
            const fullPath = path.resolve(process.cwd(), filePath);

            if (!fs.existsSync(fullPath)) {
                return { isError: true, content: [{ type: "text", text: `File not found: ${filePath}` }] };
            }

            const content = fs.readFileSync(fullPath, 'utf-8');
            return {
                content: [{ type: "text", text: content }]
            };
        }

        if (name === "list_files") {
            const { directory, recursive } = args as { directory: string, recursive?: boolean };
            const fullPath = path.resolve(process.cwd(), directory);

            if (!fs.existsSync(fullPath)) {
                return { content: [{ type: "text", text: `Directory not found: ${directory}` }] };
            }

            const EXCLUDED_DIRS = ['node_modules', '.git', '.features-gen', 'playwright-report', '.venv', 'venv', '__pycache__'];

            const results: any[] = [];
            const walk = (dir: string, currentDepth: number) => {
                if (currentDepth > 3) return; // Limit depth to avoid explosion

                const files = fs.readdirSync(dir);
                for (const file of files) {
                    if (EXCLUDED_DIRS.includes(file)) continue;

                    const filePath = path.join(dir, file);
                    const stats = fs.statSync(filePath);
                    const relativePath = path.relative(fullPath, filePath);

                    results.push({
                        name: relativePath,
                        mtime: stats.mtimeMs,
                        size: stats.size,
                        isDir: stats.isDirectory()
                    });

                    if (recursive && stats.isDirectory()) {
                        walk(filePath, currentDepth + 1);
                    }
                }
            };

            walk(fullPath, 0);

            // Limit total files returned to avoid context bloat
            const truncated = results.slice(0, 100);
            const message = results.length > 100
                ? `Listed ${truncated.length} files (total ${results.length}, truncated to avoid explosion):\n` + JSON.stringify(truncated, null, 2)
                : JSON.stringify(results, null, 2);

            return {
                content: [{ type: "text", text: message }]
            };
        }

        if (name === "run_playwright_test") {
            const { testFile } = args as { testFile?: string };
            // Generate BDD steps first
            await runCommand("npx bddgen", process.cwd());

            let command = "npx playwright test";
            if (testFile) {
                command += ` ${testFile}`;
            }

            const output = await runCommand(command, process.cwd());
            return {
                content: [{ type: "text", text: output }]
            };
        }

        if (name === "inspect_page") {
            const { url } = args as { url: string };
            const structure = await withPage(url, async (page) => {
                // Determine interactive elements with rich metadata
                return await page.evaluate(() => {
                    const elements = document.querySelectorAll('button, input, a, select, [role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="tab"], h1, h2, h3');

                    return Array.from(elements)
                        .filter(el => {
                            const style = window.getComputedStyle(el);
                            return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
                        })
                        .map(el => {
                            const htmlEl = el as HTMLElement;

                            // Extract Aria Info
                            const role = el.getAttribute('role') || el.tagName.toLowerCase();
                            const ariaName = el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || htmlEl.innerText || (el as any).placeholder || (el as any).value || '';

                            // Generate Suggested Playwright Locator
                            let suggestedLocator = '';
                            const cleanName = ariaName.trim().replace(/\n/g, ' ').substring(0, 50);

                            if (['button', 'link', 'checkbox', 'radio', 'tab'].includes(role) || ['BUTTON', 'A'].includes(el.tagName)) {
                                const targetRole = (el.tagName === 'A') ? 'link' : (el.tagName === 'BUTTON' ? 'button' : role);
                                suggestedLocator = `page.getByRole('${targetRole}', { name: '${cleanName}' })`;
                            } else if (el.tagName === 'INPUT' && (el as any).placeholder) {
                                suggestedLocator = `page.getByPlaceholder('${(el as any).placeholder}')`;
                            } else if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                                suggestedLocator = `page.getByLabel('${cleanName}')`;
                            }

                            return {
                                tagName: el.tagName,
                                role: role,
                                name: cleanName,
                                id: el.id,
                                class: el.className,
                                suggestedLocator: suggestedLocator,
                                isVisible: true
                            };
                        });
                });
            });

            // Limit the number of elements returned to 40 to avoid token explosion
            const truncatedStructure = structure.slice(0, 40);
            const finalResult: any = structure.length > 40
                ? {
                    message: `Found ${structure.length} elements, showing first 40. Use more specific URLs or actions to filter.`,
                    elements: truncatedStructure
                }
                : structure;

            return {
                content: [{ type: "text", text: JSON.stringify(finalResult, null, 2) }]
            };
        }

        if (name === "take_screenshot") {
            const { url, path: filePath } = args as { url: string, path: string };
            await withPage(url, async (page) => {
                await page.screenshot({ path: filePath, fullPage: true });
            });
            return {
                content: [{ type: "text", text: `Screenshot saved to ${filePath}` }]
            };
        }

        if (name === "get_console_logs") {
            const { url } = args as { url: string };
            const logs: string[] = [];

            const browser = await chromium.launch({ headless: true });
            const page = await browser.newPage();
            page.on('console', msg => logs.push(msg.text()));
            try {
                await page.goto(url, { waitUntil: 'networkidle' });
            } catch (e) {
                logs.push(`Navigation failed: ${e}`);
            }
            await browser.close();

            return {
                content: [{ type: "text", text: logs.join('\n') }]
            };
        }

        if (name === "explore_page_with_actions") {
            const { url, actions } = args as { url: string, actions: any[] };

            // Custom withPage logic to return rich object
            const browser = await chromium.launch({ headless: true });
            let result: any = {};

            try {
                const page = await browser.newPage();
                await page.goto(url, { waitUntil: 'networkidle' });

                const logs: string[] = [];
                for (const action of actions) {
                    try {
                        if (action.type === 'fill') await page.fill(action.selector, action.value);
                        if (action.type === 'click') await page.click(action.selector);
                        if (action.type === 'wait') await page.waitForTimeout(action.timeout || 1000);
                        if (action.type === 'screenshot') await page.screenshot({ path: 'debug_explore.png' });
                        logs.push(`Action ${action.type} on ${action.selector || 'n/a'} success.`);
                    } catch (e: any) {
                        logs.push(`Action ${action.type} failed: ${e.message}`);
                    }
                }

                // Default screenshot after actions
                const screenshotPath = `exploration_${Date.now()}.png`;
                await page.screenshot({ path: screenshotPath, fullPage: true });

                const structure = await page.evaluate(() => {
                    const elements = document.querySelectorAll('button, input, a, select, [role="button"], [role="link"], h1, h2, h3, .title, .error');
                    return Array.from(elements)
                        .filter(el => {
                            const style = window.getComputedStyle(el);
                            return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
                        })
                        .map(el => {
                            const htmlEl = el as HTMLElement;
                            const role = el.getAttribute('role') || el.tagName.toLowerCase();
                            const ariaName = el.getAttribute('aria-label') || htmlEl.innerText || (el as any).placeholder || '';

                            return {
                                tagName: el.tagName,
                                role: role,
                                name: ariaName.trim().substring(0, 100),
                                id: el.id,
                                class: el.className,
                                suggestedLocator: `page.getByRole('${role}', { name: '${ariaName.trim().substring(0, 30)}' })`
                            };
                        });
                });

                // Limit structure elements to avoid context explosion
                const truncatedStructure = structure.slice(0, 40);
                result = {
                    structure: structure.length > 40 ? truncatedStructure : structure,
                    screenshotPath,
                    logs
                };

                if (structure.length > 40) {
                    result.message = `Found ${structure.length} elements, showing first 40.`;
                }

            } finally {
                await browser.close();
            }

            return {
                content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
            };
        }

        return {
            content: [{ type: "text", text: `Unknown tool: ${name}` }],
            isError: true
        };

    } catch (error: any) {
        return {
            content: [{ type: "text", text: `Error executing ${name}: ${error.message}` }],
            isError: true
        };
    }
});

// Start the server
const transport = new StdioServerTransport();
server.connect(transport);
