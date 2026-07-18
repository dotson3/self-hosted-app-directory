#!/usr/bin/env python3
"""
sh.py — search a curated list of self-hostable apps, offline, no deps.

Bundles ~120 real self-hosted apps (name, tag, description, url) and lets you
filter by tag or free-text. Great for picking what to self-host next.

Usage:
  python3 sh.py search media          # list apps tagged 'media'
  python3 sh.py search "password"     # free-text
  python3 sh.py tags                  # list all tags
  python3 sh.py random                # surprise me
Stdlib only.
"""
import argparse, json, os, random, sys

DATA = [
 ("Pi-hole", "dns", "Network-wide ad & tracker blocking DNS sinkhole.", "https://pi-hole.net"),
 ("AdGuard Home", "dns", "Network-wide ads/tracking DNS with a nice UI.", "https://adguard.com"),
 ("Unbound", "dns", "Validating, recursive, caching DNS resolver.", "https://nlnetlabs.nl/projects/unbound"),
 ("WireGuard", "vpn", "Fast, modern, secure VPN tunnel.", "https://www.wireguard.com"),
 ("Tailscale", "vpn", "Zero-config mesh VPN built on WireGuard.", "https://tailscale.com"),
 ("Headscale", "vpn", "Open-source Tailscale control server.", "https://github.com/juanfont/headscale"),
 ("Jellyfin", "media", "Free software media system (emby fork).", "https://jellyfin.org"),
 ("Plex", "media", "Proprietary-but-popular media server.", "https://plex.tv"),
 ("Navidrome", "media", "Modern music server/streamer.", "https://navidrome.org"),
 ("Audiobookshelf", "media", "Self-hosted audiobook & podcast server.", "https://www.audiobookshelf.org"),
 ("Sonarr", "media", "TV series automation (usenet/torrent).", "https://sonarr.tv"),
 ("Radarr", "media", "Movie automation (usenet/torrent).", "https://radarr.video"),
 ("Plexamp", "media", "Music player for Plex.", "https://plexamp.com"),
 ("Nextcloud", "productivity", "File sync, calendar, contacts, office.", "https://nextcloud.com"),
 ("Owncloud", "productivity", "Self-hosted file sync & share.", "https://owncloud.com"),
 ("Syncthing", "productivity", "Continuous file synchronization (P2P).", "https://syncthing.net"),
 ("Paperless-ngx", "productivity", "Index & archive scanned documents.", "https://paperless-ngx.com"),
 ("Vikunja", "productivity", "Open-source to-do list & project app.", "https://vikunja.io"),
 ("Trilium", "productivity", "Hierarchical note-taking app.", "https://github.com/zadam/trilium"),
 ("Joplin", "productivity", "Open-source note app with sync.", "https://joplinapp.org"),
 ("Gitea", "dev", "Painless self-hosted Git service.", "https://gitea.io"),
 ("Forgejo", "dev", "Community fork of Gitea.", "https://forgejo.org"),
 ("GitLab CE", "dev", "Full DevOps platform, self-hosted.", "https://gitlab.com"),
 ("Woodpecker", "dev", "Simple CI/CD pipeline engine.", "https://woodpecker-ci.org"),
 ("Drone", "dev", "Container-native CI/CD.", "https://drone.io"),
 ("Portainer", "infra", "Lightweight Docker management UI.", "https://portainer.io"),
 ("CasaOS", "infra", "Simple home cloud OS.", "https://casaos.io"),
 ("Umbrel", "infra", "Personal home server OS.", "https://umbrel.com"),
 ("YunoHost", "infra", "Server OS to host apps easily.", "https://yunohost.org"),
 ("Docker", "infra", "Container runtime.", "https://docker.com"),
 ("Traefik", "infra", "Modern reverse proxy / load balancer.", "https://traefik.io"),
 ("Caddy", "infra", "Web server with automatic HTTPS.", "https://caddyserver.com"),
 ("Nginx", "infra", "High-performance web server / proxy.", "https://nginx.org"),
 ("Grafana", "monitoring", "Observability dashboards.", "https://grafana.com"),
 ("Prometheus", "monitoring", "Systems & service monitoring.", "https://prometheus.io"),
 ("Uptime Kuma", "monitoring", "Fancy self-hosted uptime monitor.", "https://uptime.kuma.pet"),
 ("Netdata", "monitoring", "Real-time performance monitoring.", "https://netdata.cloud"),
 ("Home Assistant", "home", "Open-source home automation.", "https://www.home-assistant.io"),
 ("Node-RED", "home", "Flow-based programming for IoT.", "https://nodered.org"),
 ("Mosquitto", "home", "MQTT broker.", "https://mosquitto.org"),
 ("BookStack", "knowledge", "Wiki / documentation platform.", "https://www.bookstackapp.com"),
 ("Wiki.js", "knowledge", "Modern, lightweight wiki.", "https://wiki.js.org"),
 ("Outline", "knowledge", "Fast knowledge base.", "https://www.getoutline.com"),
 ("HedgeDoc", "knowledge", "Realtime collaborative Markdown notes.", "https://hedgedoc.org"),
 ("Matrix (Synapse)", "comms", "Decentralized chat server.", "https://matrix.org"),
 ("Element", "comms", "Matrix client.", "https://element.io"),
 ("Mastodon", "comms", "Federated social network.", "https://joinmastodon.org"),
 ("XMPP (Prosody)", "comms", "Open messaging protocol server.", "https://prosody.im"),
 ("Discourse", "comms", "Modern forum software.", "https://www.discourse.org"),
 ("Email (Mailcow)", "comms", "Mail server suite.", "https://mailcow.email"),
 ("Wallabag", "reading", "Save & read later.", "https://wallabag.org"),
 ("Miniflux", "reading", "Minimalist RSS reader.", "https://miniflux.app"),
 ("FreshRSS", "reading", "Self-hosted RSS aggregator.", "https://freshrss.org"),
 ("Readflow", "reading", "Minimal read-later.", "https://readflow.app"),
 ("Photoprism", "photos", "AI photo management.", "https://photoprism.app"),
 ("Immich", "photos", "Self-hosted Google Photos alternative.", "https://immich.app"),
 ("Lychee", "photos", "Open-source photo management.", "https://lycheeorg.github.io"),
 ("Linkding", "bookmarks", "Bookmark manager & archiver.", "https://github.com/sissbruecker/linkding"),
 ("Shiori", "bookmarks", "Simple bookmarks manager.", "https://github.com/go-shiori/shiori"),
 ("Vaultwarden", "security", "Bitwarden-compatible password manager.", "https://github.com/dani-garcia/vaultwarden"),
 ("Bitwarden", "security", "Open-source password manager.", "https://bitwarden.com"),
 ("Authelia", "security", "Single sign-on & 2FA portal.", "https://www.authelia.com"),
 ("Fail2Ban", "security", "Ban hosts that attack services.", "https://www.fail2ban.org"),
 ("CrowdSec", "security", "Collaborative behavior detection.", "https://www.crowdsec.net"),
 ("Ghost", "web", "Open-source publishing platform.", "https://ghost.org"),
 ("WordPress", "web", "Most popular CMS.", "https://wordpress.org"),
 ("Hugo", "web", "Fast static site generator.", "https://gohugo.io"),
 ("Plausible", "analytics", "Privacy-friendly web analytics.", "https://plausible.io"),
 ("Umami", "analytics", "Simple, privacy-first analytics.", "https://umami.is"),
 ("Matomo", "analytics", "Google Analytics alternative.", "https://matomo.org"),
 ("Grafana Loki", "logging", "Log aggregation system.", "https://grafana.com/loki"),
 ("Meilisearch", "search", "Fast, relevant search engine.", "https://www.meilisearch.com"),
 ("Typesense", "search", "Typo-tolerant search engine.", "https://typesense.org"),
 ("SearXNG", "search", "Metasearch engine (privacy).", "https://searxng.org"),
 ("Whoogle", "search", "Google search without tracking.", "https://github.com/benbusby/whoogle-search"),
 ("Ollama", "ai", "Run LLMs locally.", "https://ollama.com"),
 ("OpenWebUI", "ai", "Web UI for local LLMs.", "https://github.com/open-webui/open-webui"),
 ("LocalAI", "ai", "Drop-in OpenAI replacement, local.", "https://localai.io"),
 ("Whisper (faster)", "ai", "Local speech-to-text.", "https://github.com/SYSTRAN/faster-whisper"),
 ("Stable Diffusion", "ai", "Local image generation.", "https://github.com/AUTOMATIC1111/stable-diffusion-webui"),
 ("n8n", "automation", "Workflow automation tool.", "https://n8n.io"),
 ("Huginn", "automation", "Agents that monitor & act.", "https://github.com/huginn/huginn"),
 ("Homebox", "home", "Inventory & home management.", "https://homebox.software"),
 ("Actual Budget", "finance", "Local-first budgeting app.", "https://actualbudget.org"),
 ("Firefly III", "finance", "Personal finance manager.", "https://firefly-iii.org"),
 ("Grocy", "home", "Grocery & household management.", "https://grocy.info"),
 ("Calibre-Web", "reading", "Web app for Calibre libraries.", "https://github.com/janeczku/calibre-web"),
 ("Kavita", "reading", "Comic/manga/book server.", "https://kavitareader.com"),
 ("Zabbix", "monitoring", "Enterprise monitoring.", "https://www.zabbix.com"),
 ("LibrePhotos", "photos", "Self-hosted photo manager.", "https://librephotos.com"),
 ("Docmost", "knowledge", "Open-source collaborative docs.", "https://docmost.com"),
 ("Plainpad", "knowledge", "Minimal notes app.", "https://github.com/ismamz/plainpad"),
 ("Listmonk", "comms", "Newsletter & mailing list manager.", "https://listmonk.app"),
 ("Postal", "comms", "Mail delivery platform.", "https://postal.stitch.monster"),
 ("Etherpad", "knowledge", "Realtime collaborative editor.", "https://etherpad.org"),
 ("Hedgedoc", "knowledge", "Markdown notes (duplicate-safe).", "https://hedgedoc.org"),
 ("Inventree", "home", "Inventory management for hardware.", "https://inventree.org"),
 ("Part-DB", "home", "Electronic parts inventory.", "https://github.com/Part-DB/Part-DB-server"),
 ("Wekan", "productivity", "Kanban board.", "https://wekan.github.io"),
 ("Kanboard", "productivity", "Simple Kanban.", "https://kanboard.org"),
 ("Focalboard", "productivity", "Project management, self-hosted.", "https://www.focalboard.com"),
 ("Documenso", "productivity", "Open-source doc signing.", "https://documenso.com"),
 ("Typebot", "web", "Conversational form builder.", "https://typebot.io"),
 ("NocoDB", "dev", "Smart spreadsheet / Airtable alt.", "https://nocodb.com"),
 ("Baserow", "dev", "Open-source no-code database.", "https://baserow.io"),
 ("Appsmith", "dev", "Low-code app builder.", "https://www.appsmith.com"),
 ("Directus", "dev", "Instant REST/GraphQL API for DBs.", "https://directus.io"),
 ("Strapi", "dev", "Headless CMS.", "https://strapi.io"),
 ("PocketBase", "dev", "Open-source backend in one file.", "https://pocketbase.io"),
 ("Supabase", "dev", "Open-source Firebase alt.", "https://supabase.com"),
 ("Mealie", "home", "Recipe & meal planner.", "https://mealie.io"),
 ("Tandoor", "home", "Recipe manager.", "https://tandoor.dev"),
 ("Changedetection.io", "automation", "Website change monitoring.", "https://changedetection.io"),
 ("TubeArchivist", "media", "YouTube media downloader.", "https://tubearchivist.com"),
 ("YoutubeDL-Material", "media", "Web UI for yt-dlp.", "https://github.com/Tzahi12345/YoutubeDL-Material"),
 ("PeerTube", "media", "Federated video platform.", "https://joinpeertube.org"),
 ("Owncast", "media", "Live video streaming server.", "https://owncast.online"),
 ("Castopod", "media", "Podcast hosting.", "https://castopod.org"),
 ("Funkwhale", "media", "Audio federation.", "https://funkwhale.audio"),
 ("Mastodon (GoToSocial)", "comms", "Lightweight Mastodon server.", "https://gotosocial.org"),
 ("Akkoma", "comms", "Federated social (light).", "https://akkoma.social"),
 ("Pixelfed", "photos", "Federated image sharing.", "https://pixelfed.org"),
 ("Lemmy", "comms", "Federated Reddit alt.", "https://join-lemmy.org"),
 ("Mbin", "comms", "Federated link aggregator.", "https://mbin.org"),
 ("Forgejo Actions", "dev", "CI for Forgejo.", "https://forgejo.org"),
 ("Element (Matrix)", "comms", "Matrix web client.", "https://element.io"),
]

def search(term):
    term = term.lower()
    out = []
    for name, tag, desc, url in DATA:
        if term in tag.lower() or term in name.lower() or term in desc.lower():
            out.append((name, tag, desc, url))
    return out

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("search"); s.add_argument("term")
    sub.add_parser("tags")
    sub.add_parser("random")
    args = ap.parse_args()
    if args.cmd == "tags":
        tags = sorted(set(t for _, t, _, _ in DATA))
        print(f"{len(tags)} tags: " + ", ".join(tags))
    elif args.cmd == "random":
        n, t, d, u = random.choice(DATA)
        print(f"{n} [{t}] — {d}\n  {u}")
    elif args.cmd == "search":
        res = search(args.term)
        if not res:
            print(f"no matches for '{args.term}'"); sys.exit(0)
        for n, t, d, u in res:
            print(f"- {n} [{t}]: {d}\n  {u}")
        print(f"\n{len(res)} match(es) for '{args.term}'")
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
