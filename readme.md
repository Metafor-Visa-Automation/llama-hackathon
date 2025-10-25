# Visa Flow

**VisaPrep AI** (veya projenizin adı), vize başvuru sürecini otomatikleştirmek için tasarlanmış, yapay zeka destekli bir verimlilik aracıdır. Bu proje, karmaşık, stresli ve zaman alıcı bürokratik süreci; basit, rehberli ve verimli bir dijital iş akışına dönüştürür.

Platformumuz, kullanıcıların saatler süren manuel form doldurma, belge araştırma ve profil denetleme yükünü ortadan kaldırarak kişisel verimliliklerini en üst düzeye çıkarmayı hedefler.

## 🚀 The Problem We Solve

Geleneksel vize başvuru süreci bozuktur. Kullanıcılar şu sorunlarla boğuşur:

* **Muazzam Zaman Kaybı:** Karmaşık formları doldurmak ve forumlarda/konsolosluk sitelerinde doğru belge listesini aramak saatler, hatta günler sürer.
* **Yüksek Hata Riski:** Manuel veri girişinde (yanlış tarih, tutarsız bilgi) yapılan basit hatalar, başvurunun doğrudan reddedilmesine ve tüm sürecin başa sarmasına neden olabilir.
* **Gizli Stres Faktörü:** Vize memurlarının sosyal medya profillerini kontrol edebileceği endişesi, kullanıcıların yıllar süren sosyal medya geçmişlerini manuel olarak denetleme gibi verimsiz bir çabaya girmesine yol açar.

**VisaPrep AI, tüm bu süreci otomatize eder.**

## ✨ Core Features

Platformumuz, vize başvurusunun her aşamasını otomatize ederek verimliliği artırır:

### 1. Vize Süreci Otomasyonu

* **🤖 AI-Powered Form Filling:** 1-2 saatlik karmaşık form (DS-160, Schengen vb.) doldurma işlemini 5 dakikaya indirir. Yapay zekamız, sohbet arayüzünde basit sorular sorar ve cevapları doğrudan resmi formdaki doğru alanlara yerleştirir.
* **📋 Dynamic Document Checklist:** Kullanıcının profiline (öğrenci, çalışan), seyahat amacına ve gideceği ülkeye göre %100 kişiselleştirilmiş bir belge kontrol listesini saniyeler içinde oluşturur. Forumlarda saatlerce araştırma yapmayı engeller.
* **📄 Document OCR & Validation:** Kullanıcılar belgelerini (banka dökümü, maaş bordrosu, davetiye) yükler; yapay zekamız bu belgeleri okur (OCR), eksik imza, yanlış tarih veya formdaki bilgilerle tutarsızlık (örn: farklı bakiye) gibi basit ama kritik hataları anında tespit eder.
* **✍️ AI Letter of Intent Generator:** Kullanıcının seyahat planına ve profiline göre profesyonel, ikna edici bir dille niyet mektubu/vize dilekçesi taslağı oluşturur. Yazma stresini ve harcanan zamanı sıfıra indirir.

### 2. Sosyal Medya Profili Denetimi (Risk Audit)

* **🕵️ Automated Social Media Audit:** Kullanıcının 10 yıllık sosyal medya geçmişini manuel olarak (post post) incelemesi için harcayacağı onlarca saati birkaç dakikaya indirir.
* **💡 Actionable Insights:** Sadece sorunlu içeriği (nefret söylemi, yasa dışı faaliyet imaları, başvuruyla çelişen ifadeler) bulmakla kalmaz, aynı zamanda kullanıcıya **ne yapması gerektiğini (Sil, Gizle, Düzenle)** söyleyerek karar verme sürecini otomatikleştirir.

### 3. Yönetim Paneli (Productivity Dashboard)

* **📈 Centralized Task Management:** Başvuru sürecini (Belge Topla, Formu Doldur, Sosyal Medyayı İncele, Randevu Al) Trello benzeri basit bir arayüzde tek bir yerden yönetmeyi sağlar. Otomatik hatırlatıcılar kurar.
* **👨‍👩‍👧‍👦 Team & Family Application:** Sadece bireysel değil, bir şirket (İK departmanı) veya aile olarak başvuru yapılıyorsa, İK'nın veya aile reisinin tüm ekibin profil uyumluluğunu ve başvuru durumunu tek bir panelden yönetmesini sağlar.

## 🛠️ Tech Stack

* **Frontend:** React, Tailwind CSS
* **Backend:** FastAPI (Python)
* **Database:** Firebase (Kullanıcı verileri, ülke bazlı gereksinimler ve dinamik kontrol listeleri için Firestore/Realtime Database)
* **AI Platform:** Google Cloud (VM/GKE)
* **AI Model:** Ollama (Llama 3 modelini sunmak için)
  
## 🛠️ Arch (Edit from here: https://www.mermaidchart.com/d/529a48fe-299c-40cf-944e-bae6994234a7)

<img width="1246" height="1500" alt="Untitled diagram-2025-10-24-175128" src="https://github.com/user-attachments/assets/a1b88361-ba43-4ef7-8d16-6b85429a3f50" />

## 🛠️ Database (Edit from here: https://www.mermaidchart.com/d/965a71e2-ca92-43d9-8cd8-8d9d7ef0283b )

<img width="4390" height="2943" alt="image" src="https://github.com/user-attachments/assets/c69ca404-d3b4-4aa7-b923-7bc4b259174a" />


