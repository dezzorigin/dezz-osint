import requests
import json
from rich import print
from .config import GOOGLE_API_KEY, GOOGLE_CX, NUMVERIFY_API_KEY, RAPIDAPI_WHATSAPP_KEY, REQUEST_TIMEOUT, HEADERS_DEFAULT, data_path
from .phone_offline import print_phone_report, analyze_phone

# NOTE: search_google / numverify-online / WhatsappInfo need API keys (.env).
# Without keys they SKIP honestly — the offline path below always works.

def search_google(query):
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        print("[yellow][SKIP][/yellow] Google Custom Search skipped (set GOOGLE_API_KEY + GOOGLE_CX in .env).")
        print("[dim]Get free key: https://developers.google.com/custom-search/v1/introduction[/dim]")
        return

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": 10
    }

    print("\n[green][FIND][/green] Searching Google...")
    try:
        response = requests.get(url, params=params, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        print(f"[red]Google request failed: {e}[/red]")
        return

    if response.status_code == 200:
        data = response.json()
        with open(data_path("google_search_results.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print("[yellow]google_search_results.json saved in Data folder[/yellow]\n")
        results = data.get("items", [])
        print(f"[pink][+][/pink] Top {len(results)} Results for '{query}':")
        for index, item in enumerate(results, start=1):
            print(f"{index}. {item['title']}")
            print(f"   {item['link']}\n")
    else:
        print("[pink][-][/pink] Google Search Error:", response.status_code)
        print(response.text[:500])

def validate_phone_number(number):
    # Offline first (always works, no key) — ala PhoneInfoga offline
    print("\n[cyan]--- Offline phone analysis (no API key) ---[/cyan]")
    try:
        print_phone_report(str(number))
    except Exception as e:
        print(f"[!] Offline analysis failed: {e}")
    if not NUMVERIFY_API_KEY:
        print("\n[yellow][SKIP][/yellow] numverify online validation skipped (set NUMVERIFY_API_KEY in .env).")
        return
    try:
        url = "https://apilayer.net/api/validate"
        num = str(number).strip().replace(" ", "").replace("-", "")
        # auto-detect country from prefix instead of hardcoded IN
        cc = ""
        if num.startswith("+62") or num.startswith("62") or num.startswith("08"):
            cc = "ID"
        elif num.startswith("+91") or num.startswith("91"):
            cc = "IN"
        elif num.startswith("+1"):
            cc = "US"
        querystring = {"access_key": NUMVERIFY_API_KEY, "number": num, "format": "1"}
        if cc:
            querystring["country_code"] = cc

        print("[red][+] Validating phone number online...[/red]\n")
        response = requests.get(url, params=querystring, headers=HEADERS_DEFAULT, timeout=REQUEST_TIMEOUT)
        data = response.json()
        with open(data_path("phone_validation.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            print("[yellow]phone_validation.json saved in Data folder[/yellow]\n")
        if data.get("valid"):
            print("[pink][<->][/pink] Phone Number is valid:")
            print(f"[pink][<->][/pink] Number: {data.get('number')}")
            print(f"[pink][<->][/pink] Country: {data.get('country_name')}")
            print(f"[pink][<->][/pink] Location: {data.get('location')}")
            print(f"[pink][<->][/pink] Carrier: {data.get('carrier')}")
            print(f"[pink][<->][/pink] Line Type: {data.get('line_type')}")
            print(f"[pink][<->][/pink] International Format: {data.get('international_format')}")
        else:
            print("[!] Invalid phone number.")
    except Exception as e:
        print("[!] Error during phone validation.")
        print("Reason:", e)
def look(query):
    print("\nTAKE A LOOK [0_0]")
    print(f"[pink][+][/pink] Look For Whatsapp : https://wa.me/{query}")
    print(f"[pink][+][/pink] Look For Telegram : https://t.me/{query}")

def WhatsappInfo(query):
    if not RAPIDAPI_WHATSAPP_KEY:
        print("[yellow][SKIP][/yellow] WhatsApp lookup skipped (set RAPIDAPI_WHATSAPP_KEY in .env).")
        return
    url = f"https://whatsapp-data1.p.rapidapi.com/number/91{query}"
    print("WAIT......")
    print("Retriving Data From Whatsapp")
    headers = {
	"x-rapidapi-key": RAPIDAPI_WHATSAPP_KEY,
	"x-rapidapi-host": "whatsapp-data1.p.rapidapi.com"
	}

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        print(f"WhatsApp lookup failed: {e}")
        return

    if response.status_code==200:
        try:
            data = response.json()
    
            with open(data_path("whatsapp_information.json"), "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print("[yellow]whatsapp_information.json saved in Data folder[/yellow]\n")
        
            print("[pink][<->][/pink] Profile Pic :" , data.get("profilePic"))
            print("[pink][<->][/pink] Phone Number :" , data.get("phone"))
            print("[pink][<->][/pink] About :" , data.get("about\n"))


        except Exception as e:
            print("Failed to Retrive Data:", str(e))

def analyze_number(raw: str) -> dict:
    """Honest number pipeline: offline analysis (always) + online only if keys set."""
    info = analyze_phone(raw)
    online = {}
    if GOOGLE_API_KEY and GOOGLE_CX:
        online["google"] = "configured (use search_google)"
    if NUMVERIFY_API_KEY:
        online["numverify"] = "configured"
    if RAPIDAPI_WHATSAPP_KEY:
        online["whatsapp"] = "configured"
    return {"offline": info, "online_configured": online}


if __name__ == "__main__":
    query = input("Phone (+62...): ").strip()
    print_phone_report(query)
    search_google(query)
    print("\n" + "=" * 50 + "\n")
    validate_phone_number(query)
    look(query)
    WhatsappInfo(query)

