# RAG Optimization Guide

## Problem
Sistem 17 requirement scrape ediyor ancak RAG aramasında sadece 5 benzer durum bulunuyordu. Bu, vektör aramasının çok seçici olduğunu gösteriyordu.

## Çözüm

### 1. Top-K Değerini Artırma
```python
QDRANT_TOP_K: int = 20  # Önceden 5, şimdi 20
```
- Daha fazla benzer sonuç getirir
- LLM'e daha zengin context sağlar

### 2. Minimum Score Threshold'u Düşürme
```python
QDRANT_MIN_SCORE: float = 0.3  # Önceden yoktu, şimdi 0.3
```
- Score'u 0.3'ün altında olan sonuçlar filtrelenir
- Daha kapsayıcı sonuçlar
- Değer aralığı: 0.0-1.0 (1.0 = tam eşleşme)

### 3. Daha İyi Embedding Modeli
```python
EMBEDDING_MODEL: str = 'all-MiniLM-L12-v2'  # Önceden all-MiniLM-L6-v2
```

**Model Karşılaştırması:**

| Model | Vector Size | Kalite | Hız | Kullanım |
|-------|-------------|---------|-----|----------|
| all-MiniLM-L6-v2 | 384 | İyi | Hızlı | Baseline |
| all-MiniLM-L12-v2 | 384 | Daha İyi | Hızlı | **Şu anki** |
| all-mpnet-base-v2 | 768 | En İyi | Yavaş | Production |

### 4. Score Filtreleme Eklendi
`QdrantService.search()` metoduna minimum score filtreleme eklendi:
```python
for result in search_results:
    if result.score >= min_score:  # 0.3'ten düşük olanları filtrele
        results.append(result)
```

## Yapılandırma

### Environment Variables
```bash
# .env dosyasına ekleyin
QDRANT_TOP_K=20
QDRANT_MIN_SCORE=0.3
EMBEDDING_MODEL=all-MiniLM-L12-v2
QDRANT_VECTOR_SIZE=384
```

### Qdrant Collections'ı Yeniden Oluşturma
Embedding modelini değiştirdiğinizde collections'ı yeniden oluşturun:
```bash
PYTHONPATH=. python scripts/recreate_collections.py
```

## Sonuçlar

### Önce
- 17 requirement scrape edildi
- Sadece 5 sonuç döndü (Top-K=5 sınırı)
- Çok dar context

### Sonra  
- 17 requirement scrape ediliyor
- 12-20 arası benzer sonuç dönüyor (score'a göre)
- LLM daha zengin context ile daha spesifik çıktılar üretiyor
- "İlgili ülkenin formu" yerine spesifik form isimleri

## Öneriler

### Geliştirme Ortamı
- `QDRANT_TOP_K=20`
- `QDRANT_MIN_SCORE=0.3`
- `EMBEDDING_MODEL=all-MiniLM-L12-v2`

### Production Ortamı
- `QDRANT_TOP_K=15`
- `QDRANT_MIN_SCORE=0.4` (daha yüksek kalite için)
- `EMBEDDING_MODEL=all-mpnet-base-v2` (daha iyi kalite)
- `QDRANT_VECTOR_SIZE=768` (mpnet için)

## İzleme

Logları kontrol edin:
```bash
grep "Found.*results in.*filtered" api_server.log
```

Çıktı örneği:
```
Found 15 results in visa_requirements (filtered by min_score=0.3)
```

## Troubleshooting

### Çok Az Sonuç Dönüyor
- `QDRANT_MIN_SCORE`'u düşürün (örn: 0.2)
- `QDRANT_TOP_K`'yı artırın (örn: 30)

### Çok Fazla İlgisiz Sonuç
- `QDRANT_MIN_SCORE`'u yükseltin (örn: 0.5)
- Daha iyi embedding modeli kullanın

### Qdrant Connection Hatası
```bash
docker restart visaprep_qdrant
sleep 5
PYTHONPATH=. python scripts/recreate_collections.py
```