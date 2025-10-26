# 🖥️ Oto Vize Frontend

Oto Vize, vize başvuru sürecini kolaylaştırmak için geliştirilmiş yapay zeka destekli bir otomasyon platformudur.  
Bu repo, projenin **kullanıcı arayüzü (frontend)** kısmını içerir ve React + Tailwind CSS teknolojileriyle geliştirilmiştir.  

---

## 🚀 1. Overview

Oto Vize Frontend, kullanıcıların:  
- Kişisel bilgilerini kolayca girmesini,  
- Otomatik form doldurma sürecini başlatmasını,  
- Belgelerini yüklemesini ve kontrol etmesini,  
- Niyet mektubu oluşturmasını,  
- Tüm başvuru adımlarını tek bir panel üzerinden yönetmesini sağlar.  

Modern, hızlı ve sezgisel bir kullanıcı deneyimi hedeflenmiştir.  

---

## ⚙️ 2. Installation & Setup

### 🧩 Prerequisites
- Node.js 18+  
- npm veya yarn  
- Backend API’nin çalışır durumda olması (FastAPI servisi)  

### 💡 Steps

1. **Projeyi klonlayın:**  
   ```bash
   git clone https://github.com/Metafor-Visa-Automation/llama-hackathon.git
   cd llama-hackathon/frontend
   ```

2. **Bağımlılıkları yükleyin:**  
   ```bash
   npm install
   ```
   veya  
   ```bash
   yarn install
   ```

3. **Ortam değişkenlerini tanımlayın:**  
   `.env` dosyası oluşturun ve aşağıdaki örneği kullanın:  
   ```env
   VITE_API_URL=http://localhost:8000
   VITE_FIREBASE_API_KEY=...
   VITE_GCP_API_KEY=...
   VITE_OLLAMA_MODEL=llama3
   ```

4. **Geliştirme sunucusunu başlatın:**  
   ```bash
   npm run dev
   ```

5. **Uygulamayı açın:**  
   ```
   http://localhost:5173
   ```

---

## 🧠 3. Tech Stack

| Alan | Teknoloji |
|------|------------|
| Framework | React (Vite) |
| UI | Tailwind CSS |
| State Management | Context API |
| HTTP İstekleri | Axios |
| Authentication | Firebase Auth |
| Deployment | Vercel / Netlify |

---

## 📁 4. Folder Structure

```
frontend/
│
├── src/
│   ├── assets/           # Görseller, ikonlar
│   ├── components/       # Tekil UI bileşenleri
│   ├── pages/            # Sayfalar (Home, Dashboard, Form, Documents, vs.)
│   ├── context/          # Global state yönetimi
│   ├── services/         # API çağrıları
│   ├── utils/            # Yardımcı fonksiyonlar
│   └── App.jsx           # Uygulama kökü
│
├── public/
├── package.json
└── vite.config.js
```

---

## 🧩 5. Features

- 🪄 **Akıllı Form Otomasyonu** – Kullanıcı bilgilerini alır ve formlara otomatik işler.  
- 📑 **Belge Yükleme & Kontrol** – OCR destekli belge doğrulama.  
- ✍️ **Niyet Mektubu Üretimi** – AI destekli içerik oluşturucu.  
- 👀 **Canlı Önizleme & Geribildirim** – Anlık form validasyonu ve öneriler.  
- 🔐 **Güvenli Oturum Yönetimi** – Firebase kimlik doğrulama sistemiyle koruma.  

---

## 👨‍💻 6. Development Scripts

| Komut | Açıklama |
|-------|-----------|
| `npm run dev` | Geliştirme sunucusunu başlatır |
| `npm run build` | Üretim için derleme yapar |
| `npm run preview` | Derlenmiş uygulamayı önizler |
| `npm run lint` | Kod kalitesini kontrol eder |

---

## 🌍 7. Deployment

1. **Build alın:**  
   ```bash
   npm run build
   ```
2. **Vercel / Netlify / Firebase Hosting** üzerinden dağıtım yapabilirsiniz.  

---

## 🤝 8. Contributing

Katkıda bulunmak isteyenler için:  

1. Fork oluşturun  
2. Yeni bir branch açın  
3. Değişikliklerinizi yapın  
4. Pull request gönderin  

---

## 👥 9. Team

- Seçkin Alp Kargı  
- Mert Çetin  
- Toprak Necat Gök  
- Ali Furkan Kaya  
