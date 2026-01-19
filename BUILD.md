# Building the TeleTask Test Card

This guide explains how to build the frontend Lovelace card from TypeScript source.

## Prerequisites

- **Node.js** 18.x or newer
- **npm** (comes with Node.js)

## Installation

1. **Install dependencies:**

```bash
cd hacs-teletask-micros-rs232
npm install
```

This will install:
- `lit` - Web component framework
- `rollup` - Module bundler
- `typescript` - TypeScript compiler
- Required plugins and tools

## Building

### Production Build

To compile the TypeScript source into a single JavaScript bundle:

```bash
npm run build
```

This will:
1. Compile all TypeScript files in `src/` directory
2. Bundle into a single ES module
3. Minify/optimize the code
4. Generate `dist/teletask-test-card.js`

### Development Build with Watch Mode

For active development with automatic rebuilding on file changes:

```bash
npm run watch
```

This runs the build in watch mode - any changes to `src/*.ts` files will trigger an automatic rebuild.

## Deploying to Integration

After building, copy the compiled JavaScript to the integration's static directory:

```bash
# Windows (PowerShell)
Copy-Item dist/teletask-test-card.js custom_components/teletask/static/

# Linux/macOS
cp dist/teletask-test-card.js custom_components/teletask/static/
```

## Project Structure

```
hacs-teletask-micros-rs232/
├── src/                              # TypeScript source files
│   ├── teletask-test-card.ts        # Main card component (entry point)
│   ├── device-control-tab.ts        # Device control tab
│   ├── event-monitor-tab.ts         # Event monitor tab
│   ├── types.ts                     # TypeScript type definitions
│   └── styles.ts                    # Shared CSS styles
├── dist/                             # Build output
│   └── teletask-test-card.js        # Compiled bundle (generated)
├── custom_components/teletask/
│   └── static/                       # Integration static files
│       └── teletask-test-card.js    # Copy of compiled bundle (for distribution)
├── package.json                      # Node.js dependencies and scripts
├── tsconfig.json                     # TypeScript compiler options
├── rollup.config.js                  # Rollup bundler configuration
└── BUILD.md                          # This file
```

## Development Workflow

1. **Make changes** to TypeScript files in `src/`
2. **Run build** with `npm run build` or `npm run watch`
3. **Copy to static** directory: `cp dist/teletask-test-card.js custom_components/teletask/static/`
4. **Reload browser** in Home Assistant (Ctrl+F5) to see changes
5. **Test the card** in your dashboard

## Testing in Home Assistant

### Quick Test Setup

1. Build the card: `npm run build`
2. Copy to static: `cp dist/teletask-test-card.js custom_components/teletask/static/`
3. Restart Home Assistant (only needed first time)
4. Add card to dashboard:
   - Edit dashboard
   - Add card
   - Search "TeleTask Test Card"
   - Add and configure

### Testing Changes

After making code changes:

1. Rebuild: `npm run build`
2. Copy to static directory
3. **Hard refresh browser**: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (macOS)
4. Changes should appear immediately (no HA restart needed)

## Troubleshooting

### `npm install` fails

**Issue:** Missing Node.js or npm

**Solution:**
- Install Node.js from https://nodejs.org/
- Verify with `node --version` and `npm --version`

### Build fails with TypeScript errors

**Issue:** Type errors in source code

**Solution:**
- Check console output for specific error messages
- Fix type errors in the indicated files
- Run `npm run build` again

### Card not updating in browser

**Issue:** Browser caching old version

**Solution:**
- Hard refresh: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (macOS)
- Clear browser cache completely
- Try incognito/private browsing mode
- Check browser console for JavaScript errors

### Card not appearing in card picker

**Issue:** Home Assistant hasn't loaded the resource

**Solution:**
- Verify file exists: `custom_components/teletask/static/teletask-test-card.js`
- Restart Home Assistant
- Check browser console for loading errors
- Verify manifest.json has frontend section

## Build Configuration

### rollup.config.js

Configures the bundler:
- **Input**: `src/teletask-test-card.ts`
- **Output**: `dist/teletask-test-card.js` (ES module format)
- **Plugins**: TypeScript compilation, module resolution, minification

### tsconfig.json

TypeScript compiler options:
- **Target**: ES2020
- **Module**: ESNext (ES modules)
- **Strict mode**: Enabled
- **Decorators**: Enabled (for Lit framework)

### package.json Scripts

- `npm run build` - One-time production build
- `npm run watch` - Development mode with auto-rebuild
- `npm run serve` - Alias for watch mode

## Release Checklist

Before releasing a new version:

1. ✅ Update version in `custom_components/teletask/manifest.json`
2. ✅ Update version in `src/teletask-test-card.ts` console.info()
3. ✅ Update CHANGELOG.md with changes
4. ✅ Run `npm run build` to create production bundle
5. ✅ Copy `dist/teletask-test-card.js` to `custom_components/teletask/static/`
6. ✅ Test in Home Assistant
7. ✅ Commit all changes including compiled JS
8. ✅ Create GitHub release with tag
9. ✅ HACS will distribute the static JS file automatically

## Notes

- **Compiled JS is committed to git**: The `custom_components/teletask/static/teletask-test-card.js` file should be committed so HACS can distribute it.
- **Build artifacts are gitignored**: `node_modules/`, `dist/`, and build cache files are excluded from git.
- **HACS distribution**: When users install via HACS, they get the pre-compiled JS from the `static/` directory - they don't need Node.js or to build anything.
