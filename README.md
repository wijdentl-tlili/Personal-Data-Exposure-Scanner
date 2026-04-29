# 🔍 Personal Data Exposure Scanner

A modular CLI tool for scanning and assessing personal data exposure across breach databases, social platforms, phone number intelligence, and credit card validation — with enriched OSINT and a risk scoring engine.

---

## Features

| Module | What it does |
|---|---|
| **Email / Breach Scanner** | Checks email against a local breach database or you can use the API Key of the HIBP (Paid) |
| **Username Scanner** | Searches GitHub, Reddit, GitLab, Pinterest, TikTok (You can add more plateforms) |
| **Phone Scanner** | Validates, detects line type (Mobile/VoIP/Fixed), carrier, timezones |
| **Credit Card Scanner** | Luhn check + BIN lookup (issuing bank, card level, country, prepaid flag) |
| **Risk Engine** | Composite 0–100 risk score with contextual findings |
| **Report Generator** | Exports results as `.json`, `.txt`, and `.html` |

---

## Project Structure

```
personal-data-exposure-scanner/
│
├── main.py                     # CLI entrypoint (Typer)
│
├── scanners/
│   ├── breach_scanner.py       # Email breach lookup
│   ├── username_scanner.py     # Username OSINT across platforms
│   ├── phone_scanner.py        # Phone intelligence (phonenumbers lib)
│   ├── creditcard_scanner.py   # Luhn + BIN lookup via binlist.net
│   └── risk_engine.py          # Risk score calculator
│
├── utils/
│   ├── validators.py           # Input format validators
│   └── report.py               # JSON / TXT / HTML report generator
│
├── data/
│   └── breaches.json           # Local breach database
│
└── reports/                    # Output directory for generated reports
    ├── report.json
    ├── report.txt
    └── report.html
```

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/wijdentl-tlili/personal-data-exposure-scanner.git
cd personal-data-exposure-scanner
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```
---

## Usage

Run the scanner from the project root using `main.py`. All flags are optional — combine as many as you need in one command.

```bash
python main.py [OPTIONS]
```

### Options

| Flag | Type | Description |
|---|---|---|
| `--email` | `str` | Email address to check against breach databases |
| `--username` | `str` | Username to search across social platforms |
| `--phone` | `str` | Phone number in E.164 format (e.g. `+21612345678`) |
| `--card` | `str` | Credit card number to analyze (spaces/dashes allowed) |

### Examples

**Scan an email for breaches:**
```bash
python main.py --email user@example.com
```

**Scan a username across platforms:**
```bash
python main.py --username john_doe
```

**Analyze a phone number:**
```bash
python main.py --phone "+33612345678"
```

**Full scan — all modules at once:**
```bash
python main.py \
  --email user@example.com \
  --username john_doe \
  --phone "+21612345678" \
  --card "4111 1111 1111 1111"
```

---

## Output

After each scan, three report files are automatically saved to `reports/`:

```
reports/
├── report.json    # Machine-readable, includes metadata + findings
├── report.txt     # Clean plain-text summary
└── report.html    # Styled visual report — open in any browser
```

### Risk Levels

| Score | Level | Meaning |
|---|---|---|
| 0 – 19 | 🟢 LOW | Minimal exposure detected |
| 20 – 49 | 🟡 MEDIUM | Some exposure — review findings |
| 50 – 79 | 🔴 HIGH | Significant exposure — action recommended |
| 80 – 100 | 🟣 CRITICAL | Severe exposure — immediate action required |

---

## Scanner Details

### Email & Breach Scanner
Reads from `data/breaches.json`. Each record includes the breach name, year, and categories of exposed data (e.g. emails, passwords, phone numbers). If a password field is detected in a breach, the risk score receives an additional **+40 pts** penalty.

### Username Scanner
Sends HTTP requests to public profile URLs on five platforms and checks for HTTP 200 responses. Each platform hit adds **+5 pts** to the risk score (capped at +20 pts).

> **Note:** Some platforms (especially TikTok and Pinterest) may return 200 for non-existent profiles. False positives are possible — manual verification is recommended.

### Phone Scanner
Built on the `phonenumbers` library. Beyond basic validation it detects:
- **Line type** — Mobile, Fixed Line, VoIP, Toll-Free, Premium Rate, etc.
- **VoIP heuristic** — combines `PhoneNumberType.VOIP` with carrier name matching against known VoIP providers (Twilio, Google Voice, Vonage, etc.)
- **Timezones** — all possible timezones associated with the number
- **Formats** — E.164, international, and national

VoIP numbers add **+15 pts** to the risk score.

### Credit Card Scanner
1. **Luhn algorithm** — validates the check digit
2. **Network detection** — regex-based matching for Visa, MasterCard, Amex, Discover, JCB, Diners Club, UnionPay, Maestro
3. **BIN lookup** — queries `binlist.net` (free, no API key required) with the first 8 digits to retrieve:
   - Issuing bank name and URL
   - Card type (debit / credit)
   - Card brand (Classic / Gold / Platinum / Signature)
   - Prepaid flag
   - Issuing country and currency

Prepaid cards add **+15 pts** to the risk score.

---

## Risk Scoring Reference

| Finding | Points |
|---|---|
| Per email breach | +20 pts (max +40) |
| Password in breach | +40 pts |
| Per username hit | +5 pts (max +20) |
| Valid phone number | +10 pts |
| VoIP / virtual phone | +15 pts |
| Unusual line type (Premium/Toll-Free) | +10 pts |
| Valid credit card (Luhn pass) | +50 pts |
| Prepaid card | +15 pts |
| Card issued in high-risk country | +5 pts |
| **Maximum possible score** | **100 pts** |

---

## Adding Breach Data

Edit `data/breaches.json` to populate or extend the breach database. Each entry follows this schema:

```json
[
  {
    "email": "victim@example.com",
    "breach": "ExampleSite",
    "year": 2023,
    "data_exposed": ["Emails", "Passwords", "Phone Numbers"]
  }
]
```

---

## Legal & Ethical Notice

This tool is intended strictly for **personal use** — to scan your own data and assess your own exposure. Do not use it to look up information about other individuals without their explicit consent.

- The BIN lookup queries `binlist.net`, a public API. Do not abuse it.
- Username scanning sends real HTTP requests to public profile URLs. Use responsibly and respect each platform's Terms of Service.
- The author assumes no liability for misuse of this tool.

---