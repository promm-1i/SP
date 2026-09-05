# usage: python shot.py <site-folder> <tag> [pages...] [--w=1440] [--full]
import sys, os, asyncio
from playwright.async_api import async_playwright
args=[a for a in sys.argv[1:] if not a.startswith('--')]
opts=[a for a in sys.argv[1:] if a.startswith('--')]
folder, tag = args[0], args[1]
pages = args[2:] or ['index','about','product','consult','support']
W = int([o for o in opts if o.startswith('--w=')][0][4:]) if any(o.startswith('--w=') for o in opts) else 1440
FULL = '--full' in opts
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome')
        ctx = await b.new_context(viewport={'width':W,'height':900}, device_scale_factor=1)
        pg = await ctx.new_page()
        for name in pages:
            url = 'file:///' + os.path.abspath(os.path.join(folder, name + '.html')).replace(os.sep,'/')
            await pg.goto(url); await pg.wait_for_timeout(600)
            await pg.add_style_tag(content='.rv{opacity:1!important;transform:none!important;transition:none!important}')
            await pg.wait_for_timeout(300)
            out = os.path.join(OUT, f'{tag}-{name}-{W}.png')
            await pg.screenshot(path=out, full_page=FULL)
            print(out)
        await b.close()
asyncio.run(main())
