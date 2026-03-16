# Mikro-Arbitraj Ajanı (Prototip)

Bu prototip iki modla çalışır:
- `DATA_MODE=mock`: Mock marketler (test amaçlı).
- `DATA_MODE=real`: Gerçek NFT verisi (Alchemy API ile OpenSea + LooksRare).

## Çalıştırma (Lokal)

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
set DATA_MODE=real
set ALCHEMY_API_KEY=YOUR_KEY_HERE
set AI_ENABLED=1
set AI_BASE_URL=http://localhost:1234/v1
set AI_MODEL=openai/gpt-oss-20b
uvicorn app.main:app --reload
```

Tarayıcı: `http://127.0.0.1:8000`

## Docker

```bash
set DATA_MODE=real
set ALCHEMY_API_KEY=YOUR_KEY_HERE
set AI_ENABLED=1
set AI_BASE_URL=http://localhost:1234/v1
set AI_MODEL=openai/gpt-oss-20b
docker compose up --build
```

## Notlar
- Bu sürüm gerçek para kullanmaz.
- `DATA_MODE=mock` ile demo verileri görürsün.

## Sorun giderme
- Eğer loglarda `İki marketten fiyat gelen koleksiyon sayısı: 0` görürsen:
  - Alchemy panelinde ilgili app için NFT API'nin açık olduğundan emin ol.
  - `ALCHEMY_API_KEY` doğru app'e ait olmalı.
  - Test: `getFloorPrice` endpoint'i **yalnızca** `contractAddress` ile çalışmalı.
