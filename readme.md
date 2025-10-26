# Oto Vize App - 2025 YTU Meta Hackathon Birincisi!

## 🧭 1. Project Description and Purpose  

**Oto Vize**, vize başvuru sürecini modernleştiren yapay zeka destekli bir otomasyon platformudur.  
Geleneksel, karmaşık ve stresli vize işlemlerini basitleştirerek kullanıcıların tüm süreci **tek bir dijital ortamda**, hatasız ve hızlı şekilde tamamlamasına olanak tanır.  

**Amaç:**  
- Form doldurma, belge kontrolü ve sosyal medya inceleme adımlarını otomatikleştirmek  
- Kişiye özel belge listesi, hatasız form doldurma ve niyet mektubu oluşturma süreçlerini hızlandırmak  
- Kullanıcıların başvuru kabul oranını artırmak ve zamandan tasarruf ettirmek  

---

## ⚙️ 2. Installation Instructions  

### Prerequisites  
- Python 3.10+  
- Node.js 18+  
- npm veya yarn  
- Firebase hesabı  
- Google Cloud hesabı (AI model dağıtımı için)

### Steps  

1. **Repository’yi klonlayın:**  
   ```bash
   git clone https://github.com/Metafor-Visa-Automation/llama-hackathon.git
   cd llama-hackathon
   ```

2. **Backend kurulumu:**  
   ```bash
   cd backend
   python -m venv env
   source env/bin/activate  # (Windows için: env\Scripts\activate)
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Frontend kurulumu:**  
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

4. **Ortam değişkenlerini ekleyin (.env):**  
   ```env
   FIREBASE_API_KEY=...
   GCP_API_KEY=...
   OLLAMA_MODEL=llama3
   ```

5. **Uygulamayı tarayıcıda açın:**  
   ```
   http://localhost:5173
   ```

---

## 💻 3. Usage Guide  

### 🔹 Form Otomasyonu  
Kullanıcıdan alınan temel bilgiler, DS-160 veya Schengen gibi resmi formlara otomatik olarak işlenir.

### 🔹 Belge Kontrol Listesi  
Kullanıcının profiline (öğrenci, çalışan, aile bireyi vb.) göre kişiselleştirilmiş bir belge listesi oluşturulur.

### 🔹 Belge OCR & Doğrulama  
Yüklenen belgelerde tarih, imza veya tutarsız veri hataları otomatik olarak tespit edilir.

### 🔹 Niyet Mektubu Üretimi  
Kullanıcının profil ve seyahat planına göre profesyonel bir niyet mektubu taslağı oluşturulur.

### 🔹 Sosyal Medya Analizi  
Yapay zeka, başvuruyla çelişebilecek veya riskli sosyal medya içeriklerini tespit eder ve çözüm önerileri sunar.

---
## 💻 Demo Photos
![WhatsApp Görsel 2025-10-26 saat 11 57 27_0950d49b](https://github.com/user-attachments/assets/282633e9-acdc-4526-9ff5-853d5fcf41ae)
![WhatsApp Görsel 2025-10-26 saat 11 57 27_6de32355](https://github.com/user-attachments/assets/421c8565-dc70-4f28-88f9-1d2c2a2690f5)
![WhatsApp Görsel 2025-10-26 saat 11 57 27_078b2f49](https://github.com/user-attachments/assets/aabfd2e9-ba00-4de2-bb4f-9e6ab9d1ce15)
![WhatsApp Görsel 2025-10-26 saat 11 57 28_365ed608](https://github.com/user-attachments/assets/4c297643-fa11-4f3d-ad57-ec4f98a3a24a)
![WhatsApp Görsel 2025-10-26 saat 11 57 28_6d0cf6b8](https://github.com/user-attachments/assets/890dfe85-1720-43ad-9baa-8fc72d58441b)


---
## 🧠 4. Technologies Used  

| Katman | Teknoloji |
|--------|------------|
| **Frontend** | React, Tailwind CSS |
| **Backend** | FastAPI (Python) |
| **Database** | Firebase (Firestore / Realtime Database) |
| **AI Platform** | Google Cloud (VM / GKE) |
| **AI Model** | Ollama (Llama 3) |

---

## 👥 5. Team Members  

- Seçkin Alp Kargı  
- Mert Çetin  
- Toprak Necat Gök  
- Ali Furkan Kaya  

# App Diagram
![WhatsApp Görsel 2025-10-26 saat 11 31 31_b3b71f04](https://github.com/user-attachments/assets/906467a0-4d8d-4dcd-a6fb-5ba9375f32b8)

# Teknik readme dosyaları için frontend/readme, AI/readme, backend/readme dosyalarına bakabilirsiniz.
