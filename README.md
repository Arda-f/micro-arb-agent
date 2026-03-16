# Mikro-Arbitraj Ajanı (Prototip)

Bu prototip 5 mock markette fiyat tarar, fırsatları hesaplar ve bir dashboard'da gösterir.

## Çalıştırma (Lokal)

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tarayıcı: `http://127.0.0.1:8000`

## Docker

```bash
docker compose up --build
```

## Notlar
- Bu sürüm gerçek para kullanmaz; mock veri üretir.
- Gerçek market API'leri için `app/markets.py` içindeki adapter'ları genişlet.
