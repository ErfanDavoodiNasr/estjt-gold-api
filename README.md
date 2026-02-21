<div dir="rtl" align="right">

# API قیمت طلا و سکه

این سرویس با `FastAPI` ساخته شده و قیمت لحظه‌ای طلا و سکه را از صفحه زیر اسکرپ می‌کند:

`https://www.estjt.ir/price/`

## پیش‌نیازها

- `Python 3.11+`
- `Docker` و `Docker Compose` (برای اجرای ساده‌تر)

## اجرای سریع

```bash
docker compose up --build -d
```

توقف سرویس:

```bash
docker compose down
```

آدرس سرویس:

`http://localhost:8000`


## تنظیمات کش (Redis)

مقادیر پیش‌فرض کش مستقیماً داخل `docker-compose.yml` تعریف شده‌اند و نیازی به `.env` نیست.

- `CACHE_ENABLED`: فعال/غیرفعال کردن کش (`true` یا `false`) - پیش‌فرض: `true`
- `CACHE_TTL_SECONDS`: مدت اعتبار کش بر حسب ثانیه - پیش‌فرض: `300`
- `CACHE_KEY_PRICES`: کلید کش برای نتیجه کامل قیمت‌ها - پیش‌فرض: `estjt:prices`
- `REDIS_URL`: آدرس اتصال Redis - پیش‌فرض: `redis://redis:6379/0`
- `REDIS_CONNECT_TIMEOUT_SECONDS`: timeout اتصال Redis - پیش‌فرض: `0.4`
- `REDIS_SOCKET_TIMEOUT_SECONDS`: timeout خواندن/نوشتن Redis - پیش‌فرض: `0.4`

نکته: علاوه‌بر کلید اصلی TTLدار، سرویس آخرین داده معتبر را در کلید `:stale` هم نگه می‌دارد تا هنگام اختلال منبع مبدا، پاسخ از کش ادامه پیدا کند.

برای override کردن هر مقدار، می‌توانید همان لحظه‌ی اجرا متغیر را ست کنید:

```bash
CACHE_TTL_SECONDS=20 docker compose up -d
```

## Endpoint ها

### 1) دریافت همه قیمت‌ها

`GET /v1/prices`

نمونه:

```bash
curl -X GET "http://localhost:8000/v1/prices"
```

### 2) دریافت فقط طلا

`GET /v1/prices/gold`

نمونه:

```bash
curl -X GET "http://localhost:8000/v1/prices/gold"
```

### 3) دریافت فقط سکه

`GET /v1/prices/coin`

نمونه:

```bash
curl -X GET "http://localhost:8000/v1/prices/coin"
```

## فرمت خروجی API

```json
{
  "code": 0,
  "message": "عملیات موفق بود.",
  "referenceId": "11111111-2222-4333-8444-555555555555",
  "result": {}
}
```

## نمونه پاسخ موفق

```json
{
  "code": 0,
  "message": "عملیات موفق بود.",
  "referenceId": "11111111-2222-4333-8444-555555555555",
  "result": {
    "source": {
      "name": "estjt",
      "url": "https://www.estjt.ir/price/",
      "fetchedAt": "2026-02-21T09:00:00Z"
    },
    "gold": [
      {
        "type": "انس طلا",
        "current": {"value": 5107, "raw": "$ ۵۱۰۷", "currency": "$"},
        "high": {"value": null, "raw": "—"},
        "low": {"value": null, "raw": "—"},
        "yesterdayAvg": {"value": 5028.01, "raw": "$ ۵۰۲۸٫۰۱", "currency": "$"},
        "change": {"value": 78.99, "percent": 1.57, "direction": "asc", "raw": "۷۸٫۹۹ (۱٫۵۷)"}
      }
    ],
    "coin": [
      {
        "type": "سکه طرح جدید",
        "current": {"value": 200000000, "raw": "۲۰۰٫۰۰۰٫۰۰۰"},
        "high": {"value": null, "raw": "—"},
        "low": {"value": null, "raw": "—"},
        "yesterdayAvg": {"value": 198402710, "raw": "۱۹۸٫۴۰۲٫۷۱۰"},
        "change": {"value": 1597290, "percent": 0.81, "direction": "asc", "raw": "۱٫۵۹۷٫۲۹۰ (۰٫۸۱)"}
      }
    ]
  }
}
```

## نمونه پاسخ خطا

تغییر ساختار سایت مبدا:

```json
{
  "code": 1003,
  "message": "ساختار صفحه منبع تغییر کرده است.",
  "referenceId": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
  "result": null
}
```

## خطاهای رایج

- `1001`: خطای شبکه / timeout / محدودیت دسترسی مبدا
- `1002`: خطای پردازش داخلی یا parse
- `1003`: تغییر ساختار HTML سایت مبدا
- `1004`: ورودی نامعتبر (رزرو برای توسعه بعدی)

</div>
