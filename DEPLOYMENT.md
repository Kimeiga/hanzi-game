# Deployment Guide

## Deploying to Vercel

### Option 1: Using Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and sign in with your GitHub account

2. Click "Add New Project"

3. Import your repository: `Kimeiga/hanzi-game`

4. Configure the project settings:
   - **Framework Preset**: SvelteKit
   - **Root Directory**: `web-app` ⚠️ **IMPORTANT**
   - **Build Command**: `pnpm run build` (or leave default)
   - **Output Directory**: Leave default (`.svelte-kit`)
   - **Install Command**: `pnpm install` (or leave default)

5. Click "Deploy"

That's it! Vercel will automatically deploy on every push to `main`.

### Option 2: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from the web-app directory
cd web-app
vercel

# For production deployment
vercel --prod
```

## What Gets Deployed

Only the `web-app/` directory gets deployed, which includes:
- SvelteKit application code
- `static/game_data/` folder (15MB of game data)
- All necessary dependencies

The following are **NOT** deployed (they're only for local development):
- `chinese_dictionary_*.jsonl` files (139MB total)
- `ids/` directory (IDS decomposition files)
- Rust source code (`src/`)

## Build Process

The game data in `web-app/static/game_data/` is pre-built using the Rust program.

To regenerate game data locally:
```bash
# Run the Rust data builder
cargo run --release

# Copy generated data to web-app
cp -r game_data/* web-app/static/game_data/

# Commit and push
git add web-app/static/game_data/
git commit -m "Update game data"
git push
```

## Performance

- **Uncompressed**: 15MB total game data
- **With Gzip** (automatic on Vercel): ~4-5MB
- **With Brotli** (automatic on Vercel): ~3-4MB

Vercel automatically serves compressed files, so users will download ~3-5MB total.

## Environment Variables

No environment variables are needed for this project.

## Custom Domain (Optional)

After deployment, you can add a custom domain in the Vercel dashboard:
1. Go to your project settings
2. Click "Domains"
3. Add your custom domain
4. Follow the DNS configuration instructions

## Troubleshooting

### Build fails with "Cannot find module"
- Make sure "Root Directory" is set to `web-app` in Vercel settings

### Game data not loading
- Check that `web-app/static/game_data/` contains all 5 JSON files
- Verify the files are committed to git: `git ls-files web-app/static/game_data/`

### Large deployment size warning
- This is normal! The game data is 15MB, which is fine for modern web apps
- Vercel will automatically compress it to ~3-5MB for users

