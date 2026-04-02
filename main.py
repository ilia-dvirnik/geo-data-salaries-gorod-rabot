import html as html_lib
import json
import os
import random
import re
import time
from datetime import datetime

import pandas as pd
import requests

try:
    from google.colab import files
    UPLOAD_FROM_COLAB = True
except ImportError:
    UPLOAD_FROM_COLAB = False


# ===================== SETTINGS =====================

INPUT_FILE = "Города для расчета ЗП.xlsx"
OUTPUT_FILE = "gorodrabot_salaries.xlsx"
CACHE_FILE = "gorodrabot_cache.json"

START_YEAR = 2025
END_YEAR = datetime.now().year

REQUEST_TIMEOUT = 20
MAX_RETRIES = 8

SESSION = requests.Session()
URL_CACHE = {}


# ===================== FILE HELPERS =====================

def load_input_file():
    if UPLOAD_FROM_COLAB:
        print(f"Загрузи файл '{INPUT_FILE}'")
        uploaded = files.upload()
        filename = list(uploaded.keys())[0]
    else:
        filename = INPUT_FILE
    return filename


def load_cache():
    global URL_CACHE

    if not os.path.exists(CACHE_FILE):
        URL_CACHE = {}
        return

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            URL_CACHE = json.load(f)
        print(f"Загружен кэш: {len(URL_CACHE)} URL")
    except Exception as e:
        print("Не удалось прочитать кэш, создаю новый:", e)
        URL_CACHE = {}


def save_cache():
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(URL_CACHE, f, ensure_ascii=False)
    except Exception as e:
        print("Не удалось сохранить кэш:", e)


# ===================== DATAFRAME HELPERS =====================

def find_col(columns, substring, default_name):
    for col in columns:
        if substring.lower() in str(col).lower():
            return col
    return default_name


# ===================== TEXT HELPERS =====================

def html_unescape(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = html_lib.unescape(text)
    return text.replace("\xa0", " ")


def normalize_spaces(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return " ".join(text.replace("\xa0", " ").split())


# ===================== DATE PARSING =====================

def ru_month_to_num(month_text: str):
    if not isinstance(month_text, str):
        return None

    month_text = month_text.lower()
    mapping = [
        ("январ", 1),
        ("феврал", 2),
        ("март", 3),
        ("апрел", 4),
        ("май", 5),
        ("июн", 6),
        ("июл", 7),
        ("август", 8),
        ("сентябр", 9),
        ("октябр", 10),
        ("ноябр", 11),
        ("декабр", 12),
    ]

    for key, value in mapping:
        if key in month_text:
            return value

    return None


def year_from_date_text(text: str):
    normalized = normalize_spaces(text)
    if not normalized:
        return None

    parts = [part for part in normalized.split(" ") if part]
    if not parts:
        return None

    last_part = parts[-1]
    digits = "".join(ch for ch in last_part if ch.isdigit())

    if not digits:
        return None

    try:
        return int(digits)
    except ValueError:
        return None


def month_from_date_text(text: str):
    normalized = normalize_spaces(text)
    if not normalized:
        return None

    parts = [part for part in normalized.split(" ") if part]
    if not parts:
        return None

    return ru_month_to_num(parts[0])


# ===================== URL / HTML PARSING =====================

def with_year_param(base_url: str, year: int) -> str:
    if "?" in base_url:
        if "y=" in base_url:
            before_y, after_y = base_url.split("y=", 1)
            if "&" in after_y:
                _, after_value = after_y.split("&", 1)
                return f"{before_y}y={year}&{after_value}"
            return f"{before_y}y={year}"
        return f"{base_url}&y={year}"

    return f"{base_url}?y={year}"


def extract_data_configs(html: str):
    if not html:
        return []

    matches = re.findall(r'data-config=["\'](.*?)["\']', html, flags=re.DOTALL)
    configs = [html_unescape(match) for match in matches]

    return list(dict.fromkeys(configs))


def table_from_config(config: str):
    try:
        parsed_json = json.loads(config)
    except json.JSONDecodeError:
        return []

    data = parsed_json.get("data")
    if not isinstance(data, list) or len(data) == 0:
        return []

    valid_rows = [row for row in data if isinstance(row, list) and len(row) >= 4]
    if not valid_rows:
        return []

    first_row = valid_rows[0]
    first_cell = str(first_row[0]).lower()
    start_index = 1 if "дата" in first_cell else 0

    records = []

    for row in valid_rows[start_index:]:
        date_text = str(row[0])

        records.append(
            {
                "year": year_from_date_text(date_text),
                "month": month_from_date_text(date_text),
                "avg_rub": row[1],
                "median_rub": row[2],
                "mode_rub": row[3],
            }
        )

    return records


# ===================== REQUESTS =====================

def fetch_html(url: str, max_retries: int = MAX_RETRIES) -> str:
    if url in URL_CACHE:
        print(f"  ♻ Из кэша: {url}")
        return URL_CACHE[url]

    for attempt in range(1, max_retries + 1):
        try:
            response = SESSION.get(
                url,
                headers={
                    "User-Agent": (
                        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; "
                        f"rv:{random.randint(70, 120)}) "
                        f"Gecko/20100101 Firefox/{random.randint(70, 120)}"
                    ),
                    "Accept-Language": "ru,en;q=0.8",
                    "Cache-Control": "no-cache",
                },
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                html = response.text
                URL_CACHE[url] = html
                save_cache()
                return html

            if response.status_code == 429:
                wait_time = 2 ** attempt + random.uniform(0.2, 1.4)
                print(f"  ⚠️ 429 Too Many Requests. Жду {wait_time:.1f} сек...")
                time.sleep(wait_time)
                continue

            if response.status_code in (500, 503):
                wait_time = 1.5 ** attempt + random.uniform(0.2, 1.0)
                print(f"  ⚠️ {response.status_code} серверная ошибка. Жду {wait_time:.1f} сек...")
                time.sleep(wait_time)
                continue

            print(f"  ❌ HTTP {response.status_code} для {url}")
            return ""

        except requests.RequestException as e:
            print(f"  ⚠️ Ошибка запроса: {e}. Повтор {attempt}/{max_retries}")
            time.sleep(1.2 ** attempt)

    print(f"  ❌ Не удалось получить {url} после {max_retries} попыток.")
    return ""


# ===================== BUSINESS LOGIC =====================

def parse_page_for_year(base_url: str, year: int):
    year_url = with_year_param(base_url, year)
    print(f"  Год {year}: {year_url}")

    html = fetch_html(year_url)
    if not html:
        return []

    configs = extract_data_configs(html)
    records = []

    for config in configs:
        rows = table_from_config(config)
        for row in rows:
            if row["year"] is None:
                row["year"] = year
            row["url"] = year_url
            records.append(row)

    return records


def parse_all_years_for_city(city_url: str):
    if not isinstance(city_url, str) or not city_url.strip():
        return []

    records = []

    for year in range(START_YEAR, END_YEAR + 1):
        records.extend(parse_page_for_year(city_url, year))
        time.sleep(0.5)

    return records


def main():
    load_cache()

    filename = load_input_file()
    df_cities = pd.read_excel(filename)

    print("Колонки в файле:", df_cities.columns.tolist())
    columns = list(df_cities.columns)

    city_col = find_col(columns, "населен", "Населенный пункт")
    region_col = find_col(columns, "регион", "Регион РФ")
    url_col = find_col(columns, "город работ", "Город работ")

    print("Используем колонки:")
    print("  Населенный пункт ->", city_col)
    print("  Регион РФ        ->", region_col)
    print("  Город работ      ->", url_col)

    all_rows = []

    for idx, row in df_cities.iterrows():
        city_name = row[city_col]
        region_name = row[region_col]
        city_url = row[url_col]

        print(f"\n=== {idx + 1}/{len(df_cities)}: {city_name} ({region_name}) ===")

        city_records = parse_all_years_for_city(str(city_url) if pd.notna(city_url) else "")

        for rec in city_records:
            all_rows.append(
                {
                    "Населенный пункт": city_name,
                    "Регион РФ": region_name,
                    "year": rec.get("year"),
                    "month": rec.get("month"),
                    "avg_rub": rec.get("avg_rub"),
                    "median_rub": rec.get("median_rub"),
                    "mode_rub": rec.get("mode_rub"),
                    "url": rec.get("url"),
                }
            )

        time.sleep(random.uniform(1.0, 3.0))

    df_result = pd.DataFrame(all_rows)

    print("\nПример результата:")
    print(df_result.head())

    df_result.to_excel(OUTPUT_FILE, index=False)
    print(f"\nГотово! Результат сохранён в файл: {OUTPUT_FILE}")

    if UPLOAD_FROM_COLAB:
        files.download(OUTPUT_FILE)


if __name__ == "__main__":
    main()
