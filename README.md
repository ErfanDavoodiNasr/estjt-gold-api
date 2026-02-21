<div dir="rtl" align="right">

# API قیمت طلا و سکه

این سرویس با `FastAPI` ساخته شده و قیمت لحظه‌ای طلا و سکه را از صفحه زیر اسکرپ می‌کند:

<div dir="ltr" align="left">

`https://www.estjt.ir/price/`

</div>

## پیش‌نیازها

- `Python 3.11+`
- `Docker` و `Docker Compose` (برای اجرای ساده‌تر)

## اجرای سریع

<div dir="ltr" align="left">

```bash
docker compose up --build -d
```

</div>

توقف سرویس:

<div dir="ltr" align="left">

```bash
docker compose down
```

</div>

آدرس سرویس:

<div dir="ltr" align="left">

`http://localhost:8000`

</div>


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

<div dir="ltr" align="left">

```bash
CACHE_TTL_SECONDS=20 docker compose up -d
```

</div>

## Endpoint ها

### 1) دریافت همه قیمت‌ها

<div dir="ltr" align="left">

`GET /v1/prices`

</div>

نمونه:

<div dir="ltr" align="left">

```bash
curl -X GET "http://localhost:8000/v1/prices"
```

</div>

### 2) دریافت فقط طلا

<div dir="ltr" align="left">

`GET /v1/prices/gold`

</div>

نمونه:

<div dir="ltr" align="left">

```bash
curl -X GET "http://localhost:8000/v1/prices/gold"
```

</div>

### 3) دریافت فقط سکه

<div dir="ltr" align="left">

`GET /v1/prices/coin`

</div>

نمونه:

<div dir="ltr" align="left">

```bash
curl -X GET "http://localhost:8000/v1/prices/coin"
```

</div>

## فرمت خروجی API

<div dir="ltr" align="left">

```json
{
  "code": 0,
  "message": "عملیات موفق بود.",
  "referenceId": "11111111-2222-4333-8444-555555555555",
  "result": {}
}
```

</div>

## نمونه پاسخ موفق

<div dir="ltr" align="left">

```json
{
  "code": 0,
  "message": "عملیات موفق بود.",
  "referenceId": "c7a4198d-47e9-4271-86fe-20a3b3d08c49",
  "result": {
    "source": {
      "name": "estjt",
      "url": "https://www.estjt.ir/price/",
      "fetchedAt": "2026-02-21T12:53:51.476419Z"
    },
    "gold": [
      {
        "type": "انس طلا",
        "current": {
          "value": 5107,
          "raw": "$ ۵۱۰۷",
          "currency": "$"
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 5028.01,
          "raw": "$ ۵۰۲۸٫۰۱",
          "currency": "$"
        },
        "change": {
          "value": 78.99,
          "percent": 1.57,
          "direction": "asc",
          "raw": "۷۸٫۹۹ (۱٫۵۷)"
        }
      },
      {
        "type": "مظنه تهران",
        "current": {
          "value": 85800000,
          "raw": "۸۵٫۸۰۰٫۰۰۰",
          "currency": null
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 84685017,
          "raw": "۸۴٫۶۸۵٫۰۱۷",
          "currency": null
        },
        "change": {
          "value": 1114983,
          "percent": 1.32,
          "direction": "asc",
          "raw": "۱٫۱۱۴٫۹۸۳ (۱٫۳۲)"
        }
      },
      {
        "type": "طلای ۱۸ عیار",
        "current": {
          "value": 19807100,
          "raw": "۱۹٫۸۰۷٫۱۰۰",
          "currency": null
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 19549640,
          "raw": "۱۹٫۵۴۹٫۶۴۰",
          "currency": null
        },
        "change": {
          "value": 257460,
          "percent": 1.32,
          "direction": "asc",
          "raw": "۲۵۷٫۴۶۰ (۱٫۳۲)"
        }
      },
      {
        "type": "طلای ۲۴ عیار",
        "current": {
          "value": 26406000,
          "raw": "۲۶٫۴۰۶٫۰۰۰",
          "currency": null
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 26063298,
          "raw": "۲۶٫۰۶۳٫۲۹۸",
          "currency": null
        },
        "change": {
          "value": 342702,
          "percent": 1.31,
          "direction": "asc",
          "raw": "۳۴۲٫۷۰۲ (۱٫۳۱)"
        }
      }
    ],
    "coin": [
      {
        "type": "سکه طرح قدیم",
        "current": {
          "value": 195000000,
          "raw": "۱۹۵٫۰۰۰٫۰۰۰"
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 194583252,
          "raw": "۱۹۴٫۵۸۳٫۲۵۲"
        },
        "change": {
          "value": 416748,
          "percent": 0.21,
          "direction": "asc",
          "raw": "۴۱۶٫۷۴۸ (۰٫۲۱)"
        }
      },
      {
        "type": "سکه طرح جدید",
        "current": {
          "value": 199500000,
          "raw": "۱۹۹٫۵۰۰٫۰۰۰"
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 198402710,
          "raw": "۱۹۸٫۴۰۲٫۷۱۰"
        },
        "change": {
          "value": 1097290,
          "percent": 0.55,
          "direction": "asc",
          "raw": "۱٫۰۹۷٫۲۹۰ (۰٫۵۵)"
        }
      },
      {
        "type": "نیم سکه",
        "current": {
          "value": 102000000,
          "raw": "۱۰۲٫۰۰۰٫۰۰۰"
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 101703614,
          "raw": "۱۰۱٫۷۰۳٫۶۱۴"
        },
        "change": {
          "value": 296386,
          "percent": 0.29,
          "direction": "asc",
          "raw": "۲۹۶٫۳۸۶ (۰٫۲۹)"
        }
      },
      {
        "type": "ربع سکه",
        "current": {
          "value": 56000000,
          "raw": "۵۶٫۰۰۰٫۰۰۰"
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 56142252,
          "raw": "۵۶٫۱۴۲٫۲۵۲"
        },
        "change": {
          "value": -142252,
          "percent": 0.25,
          "direction": "desc",
          "raw": "۱۴۲٫۲۵۲ (۰٫۲۵)"
        }
      },
      {
        "type": "سکه یک گرمی",
        "current": {
          "value": 28000000,
          "raw": "۲۸٫۰۰۰٫۰۰۰"
        },
        "high": {
          "value": null,
          "raw": "—"
        },
        "low": {
          "value": null,
          "raw": "—"
        },
        "yesterdayAvg": {
          "value": 28000000,
          "raw": "۲۸٫۰۰۰٫۰۰۰"
        },
        "change": {
          "value": null,
          "percent": null,
          "direction": "none",
          "raw": "—"
        }
      }
    ]
  }
}
```

</div>

## نمونه پاسخ خطا

تغییر ساختار سایت مبدا:

<div dir="ltr" align="left">

```json
{
  "code": 1003,
  "message": "ساختار صفحه منبع تغییر کرده است.",
  "referenceId": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
  "result": null
}
```

</div>

## خطاهای رایج

- `1001`: خطای شبکه / timeout / محدودیت دسترسی مبدا
- `1002`: خطای پردازش داخلی یا parse
- `1003`: تغییر ساختار HTML سایت مبدا
- `1004`: ورودی نامعتبر (رزرو برای توسعه بعدی)

</div>
