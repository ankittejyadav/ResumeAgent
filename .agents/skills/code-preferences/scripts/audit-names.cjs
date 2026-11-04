// .agents/skills/code-preferences/scripts/audit-names.cjs
const fs = require('fs');
const path = require('path');

function log(msg) {
    console.log(`\x1b[36m[DOMAIN-AUDIT]\x1b[0m ${msg}`);
}

function logError(msg) {
    console.error(`\x1b[31m[DOMAIN-AUDIT] WARNING:\x1b[0m ${msg}`);
}

function auditRoutes() {
    const routesDir = path.join(__dirname, '..', '..', '..', '..', 'src', 'routes');
    if (!fs.existsSync(routesDir)) {
        logError("src/routes directory not found.");
        return;
    }

    const folders = fs.readdirSync(routesDir);
    let warnings = 0;

    for (const folder of folders) {
        const routePath = path.join(routesDir, folder);
        if (!fs.statSync(routePath).isDirectory() || folder.startsWith('[') || folder === 'api') continue;

        // Scan SvelteKit page and loader files in the route folder
        const pageFiles = ['+page.svelte', '+page.server.js', '+page.js'];
        for (const file of pageFiles) {
            const filePath = path.join(routePath, file);
            if (fs.existsSync(filePath)) {
                const content = fs.readFileSync(filePath, 'utf8');

                // Regex to find server/database helper imports ending in -db or target libraries in lib/
                const dbImportRegex = /\$lib\/server\/([a-zA-Z0-9_-]+-db)/g;
                let match;
                while ((match = dbImportRegex.exec(content)) !== null) {
                    const dbName = match[1].replace('-db', '');
                    // Normalize names to compare
                    const normalizedFolder = folder.toLowerCase();
                    const normalizedDb = dbName.toLowerCase();

                    // If route doesn't match db helper name and they aren't substrings of each other
                    if (!normalizedFolder.includes(normalizedDb) && !normalizedDb.includes(normalizedFolder)) {
                        logError(`Route "/${folder}" imports database helper "${match[1]}.js". Potential context naming mismatch detected ("${folder}" vs "${dbName}").`);
                        warnings++;
                    }
                }
            }
        }
    }

    if (warnings > 0) {
        log(`Audit completed with ${warnings} potential domain mismatch warnings.`);
        process.exit(1);
    } else {
        log("✓ Domain context naming alignment audit passed!");
    }
}

auditRoutes();
