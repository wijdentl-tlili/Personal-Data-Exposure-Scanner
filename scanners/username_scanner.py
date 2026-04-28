import httpx


PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "GitLab": "https://gitlab.com/{}",
    "Pinterest": "https://www.pinterest.com/{}",
    "TikTok": "https://www.tiktok.com/@{}"
}


def scan_username(username: str):
    results = []

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for platform, url in PLATFORMS.items():

        profile_url = url.format(username)

        try:
            response = httpx.get(
                profile_url,
                headers=headers,
                timeout=5,
                follow_redirects=True
            )

            found = response.status_code == 200

            results.append({
                "platform": platform,
                "url": profile_url,
                "found": found
            })

        except Exception:
            results.append({
                "platform": platform,
                "url": profile_url,
                "found": False
            })

    return results