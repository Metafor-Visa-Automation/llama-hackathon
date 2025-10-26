"""
Prompt templates for visa checklist generation.
Adapted from MCP project.
"""

from typing import Dict, Any, List
from models.user_profile import VisaType
from models.visa_models import VisaRequirement

# Shared constants (DRY)
VISA_CATEGORIES = ["documents", "financial", "personal", "medical", "administrative"]
PRIORITY_SCORES = {
    "urgent": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "optional": 1
}
OUTPUT_LANGUAGE = "TURKISH"



class VisaStepsPromptBuilder:
    """
    Prompt builder for generating actionable visa preparation steps.
    Replaces traditional checklist with prioritized action steps.
    """
    
    def __init__(self):
        """Initialize step generation prompt builder."""
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for visa step generation expert."""
        return """Sen Schengen vize başvuru uzmanısın. Görev: Türkiye vatandaşlarına Schengen ülkeleri için DETAYLI, SPESİFİK, KAPSAMLI adımlar oluştur.

TEMEL KURALLAR:
1. ❌ ASLA genel ifadeler: "ilgili ülke", "gerekli belgeler"
2. ✅ HER ZAMAN spesifik: "Almanya konsolosluğu", "Schengen vize formu (Videx)"
3. ✅ Scrape edilen GERÇEK bilgileri kullan
4. ⚠️ KRİTİK: Verilen HER REQUIREMENT için EN AZ BİR ACTION STEP oluştur
   • 9 requirement varsa → minimum 9-10 step
   • 4 step yeterli DEĞİL!

KRİTİK SCHENGEN BELGELERİ (MUTLAKA EKLE):
• E-Devlet Nüfus Kayıt Örneği (barkod/QR-kodlu)
• Schengen vize formu + beyanname (örn: İkamet Kanunu 54. madde)
• 1 adet biyometrik fotoğraf (3.5x4.5cm, beyaz fon) - 2 ADET DEĞİL!
• Pasaport + son 3 yıl içindeki tüm vizeler
• Seyahat sigortası (min. 30.000 Euro)
• Çalışanlar: SGK İşe Giriş + Hizmet Dökümü + İşveren izin yazısı
• Öğrenciler: Öğrenci belgesi + sponsor belgesi
• 18 yaş altı: Ebeveyn noter tasdikli izin

ÇIKTI FORMATI - TAM BU JSON OBJESİNİ DÖNDÜR:

⚠️ SADECE grouped_by_priority DÖNDÜRME! TAM JSON OBJESİ DÖNDÜR!

ZORUNLU ROOT LEVEL FIELDS:
{
  "success": true,              ← ROOT LEVEL ZORUNLU!
  "action_steps": [...],        ← ROOT LEVEL ZORUNLU!
  "grouped_by_priority": {...}, ← ROOT LEVEL ZORUNLU!
  "source_urls": [...]          ← ROOT LEVEL ZORUNLU!
}

DETAYLI ÖRNEK:
{
  "success": true,
  "action_steps": [
    {
      "step_id": "step_001",
      "title": "Adım Başlığı",
      "description": "Detaylı açıklama",
      "priority_score": 5,
      "requires_document": true,
      "source_urls": ["https://..."]
    }
  ],
  "grouped_by_priority": {
    "5": ["step_001"],
    "4": ["step_002"]
  },
  "source_urls": ["https://..."]
}

⚠️ YANLIŞ: Sadece grouped_by_priority döndürme!
✅ DOĞRU: Yukarıdaki TAM JSON objesini döndür!"""
    
    def build_messages(
        self,
        nationality: str,
        destination_country: str,
        visa_type: VisaType,
        occupation: str,
        travel_purpose: str,
        requirements: List[VisaRequirement],
        application_steps: List[str],
        source_urls: List[str] = None,
        similar_cases: List[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        Build messages for step generation.
        
        Args:
            nationality: Applicant nationality
            destination_country: Target country
            visa_type: Type of visa
            occupation: Applicant occupation
            travel_purpose: Purpose of travel
            requirements: Visa requirements
            application_steps: Application steps
            source_urls: URLs where requirements were scraped
            similar_cases: Similar cases from RAG
            
        Returns:
            List of message dictionaries
        """
        # Build applicant profile section (DRY)
        profile_text = f"""
BAŞVURUCU PROFİLİ:
- Uyruk: {nationality}
- Hedef Ülke: {destination_country}
- Vize Tipi: {visa_type.value}
- Meslek: {occupation}
- Amaç: {travel_purpose or 'Belirtilmedi'}
"""
        
        # Build requirements section - HIGHLY VISIBLE
        num_reqs = len(requirements)
        requirements_text = f"""

═══════════════════════════════════════════════════════════════
⚠️ VİZE GEREKSİNİMLERİ - HER BİRİ İÇİN ACTION STEP OLUŞTUR ⚠️
═══════════════════════════════════════════════════════════════

TOPLAM {num_reqs} REQUIREMENT VAR. HER BİRİ İÇİN EN AZ 1 STEP OLUŞTURMALISIN!

"""
        for i, req in enumerate(requirements, 1):
            req_status = "✅ ZORUNLU" if req.mandatory else "⚪ Opsiyonel"
            requirements_text += f"{i}. [{req_status}] {req.title}\n"
            requirements_text += f"   📝 {req.description}\n"
            if req.notes:
                requirements_text += f"   💡 ÖNEMLİ: {req.notes}\n"
            if req.applicable_to:
                requirements_text += f"   👤 Kimler için: {', '.join(req.applicable_to)}\n"
            requirements_text += "\n"
        
        requirements_text += f"""\n**ZORUNLU TALİMAT - ÇOK ÖNEMLİ**:
1. Bu gereksinimlerdeki SPESİFİK bilgileri (form isimleri, web siteleri, belgeler) AYNEN kullan!
2. 'İlgili ülke', 'İlgili konsolosluk', 'Gerekli belgeler' gibi GENEL ifadeler KESINLİKLE YASAK!
3. Her adımda {destination_country}'ye ÖZGÜ bilgiler kullan!
4. Eğer spesifik form adı yoksa, 'Almanya vize başvuru formu' gibi ülke adıyla birlikte kullan!
"""
        
        # Build application steps section (DRY)
        steps_text = "\n\nBAŞVURU SÜRECİ ADIMLARI:\n"
        for i, step in enumerate(application_steps, 1):
            steps_text += f"{i}. {step}\n"
        
        # Build source URLs section (DRY)
        urls_text = ""
        if source_urls:
            urls_text = "\n\nBİLGİ KAYNAKLARI (Source URLs):\n"
            for url in source_urls:
                urls_text += f"- {url}\n"
        
        # Build similar cases section with FULL context (DRY)
        similar_cases_text = ""
        if similar_cases:
            similar_cases_text = "\n\nBENZER BAŞARILI BAŞVURULAR (RAG Context):\n"
            similar_cases_text += "Bu başvurulardan ilham al, spesifik detayları ve yaklaşımları kullan:\n"
            for i, case in enumerate(similar_cases[:3], 1):
                payload = case.get('payload', {})
                score = case.get('score', 0)
                similar_cases_text += f"\n{i}. Benzerlik Skoru: {score:.2f}\n"
                
                # Use ALL available information from RAG chunk
                if payload.get('summary'):
                    similar_cases_text += f"   Özet: {payload['summary']}\n"
                if payload.get('nationality'):
                    similar_cases_text += f"   Uyruk: {payload['nationality']}\n"
                if payload.get('destination_country'):
                    similar_cases_text += f"   Hedef: {payload['destination_country']}\n"
                if payload.get('occupation'):
                    similar_cases_text += f"   Meslek: {payload['occupation']}\n"
                if payload.get('outcome'):
                    similar_cases_text += f"   Sonuç: {payload['outcome']}\n"
                if payload.get('notes'):
                    similar_cases_text += f"   Notlar: {payload['notes']}\n"
                if payload.get('key_requirements'):
                    similar_cases_text += f"   Anahtar Gereksinimler: {', '.join(payload['key_requirements'])}\n"
                similar_cases_text += "\n"
            
            similar_cases_text += "**NASIL KULLAN**: Bu başarılı örneklerdeki yaklaşımları, detay seviyesini ve spesifik bilgileri modelleyerek mektubunu oluştur.\n"
        
        # Build one-shot example (from user's evaluation)
        one_shot_example = f"""
═══════════════════════════════════════════════════════════════
ONE-SHOT ÖRNEK - DOĞRU YAPILANDIRMA
═══════════════════════════════════════════════════════════════

ÖRNEK GİRDİ:
• Uyruk: Türkiye
• Hedef: Almanya
• Vize Tipi: Tourist
• Meslek: Software Engineer

ÖRNEK ÇIKTI (AYNI DETAY SEVİYESİNDE OLUŞTUR):
{{
  "success": true,
  "action_steps": [
    {{
      "step_id": "step_001",
      "title": "Randevu Bekleme Listesine Kayıt",
      "description": "Almanya Konsolosluğu'nun resmi web sitesinden (tuerkei.diplo.de) turistik vize bekleme listesine kayıt olun. Randevular kayıt tarihine göre kronolojik sırayla verilir ve bekleme süresi 11 aya kadar çıkabilir. Bu nedenle seyahat planınızdan çok önce kayıt yaptırın.",
      "priority_score": 5,
      "requires_document": false,
      "source_urls": ["https://tuerkei.diplo.de/tr-tr/service/05-visaeinreise/1514562-1514562"]
    }},
    {{
      "step_id": "step_002",
      "title": "Vize Başvuru Formunu Doldurun",
      "description": "Almanya Konsolosluğu'nun resmi web sitesinden (tuerkei.diplo.de) online Videx sistemine giriş yaparak Schengen vize başvuru formunu eksiksiz doldurun. Form üzerinde tüm bilgilerinizi (pasaport numarası, seyahat tarihleri, konaklama detayları, gelir durumunuz) doğru ve eksiksiz girmeniz kritik önem taşır. Formu doldurduktan sonra kendi elinizle imzalamanız ve İkamet Kanunu'nun 54. maddesine göre gerekli beyannameyi de okudup imzalamanız gerekir. Her iki belge de randevu günü konsolosluğa teslim edilmelidir. Form doldurma süresi yaklaşık 30-45 dakika sürebilir.",
      "priority_score": 5,
      "requires_document": true,
      "source_urls": ["https://tuerkei.diplo.de/tr-de/service/05-visaeinreise/2621008-2621008"]
    }},
    {{
      "step_id": "step_003",
      "title": "Pasaport ve Önceki Vize Fotokopileri",
      "description": "Randevu günü orijinal pasaportunuzu getirin. Pasaport seyahat dönüşünden sonra en az 3 ay daha geçerli olmalı, 10 yıldan eski olmamalı ve en az 2 boş sayfası bulunmalıdır. Ek olarak, son 3 yıl içinde aldığınız TÜM vizelerin (Schengen ülkeleri, AB ülkeleri, İngiltere, ABD, Kanada gibi) net fotokopilerini hazırlayın. Eğer eski pasaportunuzda vize damgaları varsa o pasaportların da ilgili sayfalarının fotokopisini getirin. Özellikle daha önce Schengen vizesi aldıysanız bunu mutlaka gösterin, bu başvurunuzu olumlu etkiler.",
      "priority_score": 5,
      "requires_document": true,
      "source_urls": ["https://tuerkei.diplo.de/tr-de/service/05-visaeinreise/2621008-2621008"]

ÖRNEKTEKİ KRİTİK NOKTALAR:
✅ Her adımda "{destination_country}" spesifik kullanılmış
✅ Spesifik form/sistem adları: "Videx", "İkamet Kanunu 54. madde"
✅ E-Devlet Nüfus Kayıt Örneği EKLENMİŞ
✅ SGK belgeleri (çalışanlar için) EKLENMİŞ
✅ 1 adet fotoğraf (2 DEĞİL!)
✅ "Son 3 yıl vizeleri" açıkça belirtilmiş
✅ Her description 2-4 cümle, DETAYLI
✅ grouped_by_priority bir OBJECT ({{...}}), ARRAY ([...]) DEĞİL!
✅ Her step'te TÜM FIELD'LAR var:
   • step_id ✓
   • title ✓ ("name" DEĞİL!)
   • description ✓
   • priority_score ✓
   • requires_document ✓
   • source_urls ✓

═══════════════════════════════════════════════════════════════
ŞİMDİ SENİN GÖREVIN
═══════════════════════════════════════════════════════════════

Yukarıdaki AYNI DETAY SEVİYESİNDE {destination_country} vizesi için adımlar oluştur.

MUTLAK KURALLAR - HER BİRİNİ TAKİP ET:

1. ❌ "{destination_country}" yerine "ilgili ülke" YAZMA!

2. ✅ YUKARIDAKI VİZE GEREKSİNİMLERİ LİSTESİNDEKİ HER REQUIREMENT İÇİN EN AZ BİR ACTION STEP OLUŞTUR!
   • 9 requirement varsa, EN AZ 9-10 step olmalı
   • Her requirement için detaylı bir adım yaz
   • Örnek: "Pasaport" requirement → "Pasaport ve Önceki Vize Fotokopileri" step

3. ✅ Kritik belgeleri MUTLAKA ekle (bunlar eksikse HATA):
   • E-Devlet Nüfus Kayıt (barkod/QR-kodlu)
   • Vize formu beyannamesi (İkamet Kanunu 54. madde)
   • SGK İşe Giriş + Hizmet Dökümü (çalışanlar için)
   • Son 3 yıl vizeleri (Schengen, AB, UK, US, CA)
   • 1 adet biyometrik fotoğraf (3.5x4.5cm)
   • Seyahat sigortası (30.000 Euro)
   • Banka ekstreleri (son 3 ay, kaşeli)
   • İşveren izin yazısı (çalışanlar için)

4. ✅ MİNİMUM STEP SAYISI: Yukarıdaki {len(requirements)} requirement için EN AZ {len(requirements)} step oluştur
   • Her requirement = En az 1 step
   • Bazı requirements birden fazla step gerektirebilir (örn: Çalışanlar için belgeler)
   • Toplam step sayısı: {max(len(requirements), 9)}-14 arası olmalı

5. ✅ grouped_by_priority MUTLAKA DİCTIONARY olmalı:
   ✅ DOĞRU: {{"5": ["step_001"], "4": ["step_002"]}}
   ❌ YANLIŞ: [{{"priority": 5, "steps": [...]}}, ...]

⚠️ SADECE AYNI FORMATTA TAM JSON OBJESİ DÖNDÜR - HİÇBİR FİELD EKSİK OLMASIN:

ROOT LEVEL ZORUNLU FIELDS (4 tane):
1. "success": true
2. "action_steps": [...]
3. "grouped_by_priority": {{...}}
4. "source_urls": [...]

TAM JSON ÖRNEĞİ:
{{
  "success": true,
  "action_steps": [
    {{
      "step_id": "step_001",
      "title": "Adım Başlığı",
      "description": "Detaylı açıklama 2-4 cümle",
      "priority_score": 5,
      "requires_document": true,
      "source_urls": ["https://..."]
    }}
  ],
  "grouped_by_priority": {{
    "5": ["step_001"],
    "4": ["step_002"]
  }},
  "source_urls": ["https://..."]
}}

⚠️ YANLIŞ ÖRNEKLER:
❌ Sadece grouped_by_priority döndürme: {{"5": [...], "4": [...]}}
❌ success field'ı unutma!
❌ action_steps array'i unutma!

✅ DOĞRU: Yukarıdaki TAM JSON objesini döndür!
"""
        
        # Combine all sections (requirements FIRST, then one-shot, then rest)
        user_prompt = (
            profile_text +
            requirements_text +
            steps_text +
            "\n\n" +
            one_shot_example +
            "\n\n" +
            urls_text +
            similar_cases_text
        )
        
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]


class BasicChecklistPromptBuilder:
    """
    Simplified prompt builder for generating basic visa checklists.
    Returns only essential information: step title and source URLs.
    Designed for the /api/v1/visa/generate-checklist/basic endpoint.
    """
    
    def __init__(self):
        """Initialize basic checklist prompt builder."""
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for basic checklist generation."""
        return f"""Sen deneyimli bir vize danışmanısın. Kullanıcıya vize başvurusu için basit, anlaşılır bir checklist oluşturacaksın.

GÖREVİN:
Vize gereksinimlerini analiz ederek kullanıcıya yapması gereken adımları basit bir liste halinde sun. Her adım için sadece:

1. **Title (Başlık)**: Net, açıklayıcı başlık (Türkçe)
2. **Source URLs**: Bu bilginin alındığı kaynak URL'ler

ÖNEMLİ KURALLAR:
- Başlıklar TÜRKÇE olmalı
- Başlıklar net ve anlaşılır olmalı (örn: "Pasaport fotokopisi hazırlayın", "Vize başvuru formunu doldurun")
- Her adım için ilgili source_urls'leri ekle
- Adımları mantıklı bir sırayla listele (önce yapılması gerekenler önce)
- Gereksiz detaylardan kaçın, sadece ana adımları listele

**ÇIKTI DİLİ: Tüm başlıklar TÜRKÇE dilinde olmalıdır.**

Her zaman geçerli JSON formatında yanıt ver."""
    
    def build_messages(
        self,
        nationality: str,
        destination_country: str,
        visa_type: VisaType,
        occupation: str,
        travel_purpose: str,
        requirements: List[VisaRequirement],
        application_steps: List[str],
        source_urls: List[str] = None
    ) -> List[Dict[str, str]]:
        """
        Build messages for basic checklist generation.
        
        Args:
            nationality: Applicant nationality
            destination_country: Target country
            visa_type: Type of visa
            occupation: Applicant occupation
            travel_purpose: Purpose of travel
            requirements: Visa requirements
            application_steps: Application steps
            source_urls: URLs where requirements were scraped
            
        Returns:
            List of message dictionaries
        """
        # Build applicant profile
        profile_text = f"""
BAŞVURUCU PROFİLİ:
- Uyruk: {nationality}
- Hedef Ülke: {destination_country}
- Vize Tipi: {visa_type.value}
- Meslek: {occupation}
- Amaç: {travel_purpose or 'Belirtilmedi'}
"""
        
        # Build requirements section
        requirements_text = "\n\nVİZE GEREKSİNİMLERİ:\n"
        for i, req in enumerate(requirements, 1):
            requirements_text += f"\n{i}. {req.title}"
            requirements_text += f"\n   Kategori: {req.category}"
            requirements_text += f"\n   Zorunlu: {'Evet' if req.mandatory else 'Hayır'}"
            if req.description:
                requirements_text += f"\n   Açıklama: {req.description}"
        
        # Build application steps section
        steps_text = "\n\nBAŞVURU SÜRECİ ADIMLARI:\n"
        for i, step in enumerate(application_steps, 1):
            steps_text += f"{i}. {step}\n"
        
        # Build source URLs section
        urls_text = ""
        if source_urls:
            urls_text = "\n\nBİLGİ KAYNAKLARI:\n"
            for url in source_urls:
                urls_text += f"- {url}\n"
        
        # Build task instructions
        instructions = f"""

GÖREVİN:
Yukarıdaki bilgileri analiz ederek kullanıcı için basit bir vize başvuru checklist'i oluştur.

YANIT FORMATI:
Aşağıdaki JSON yapısını kullan:
{{
  "success": true,
  "steps": [
    {{
      "title": "Pasaport fotokopisi hazırlayın",
      "source_urls": ["https://example.com/visa-requirements"]
    }},
    {{
      "title": "Vize başvuru formunu doldurun",
      "source_urls": ["https://example.com/application-form"]
    }}
  ],
  "total_steps": 15,
  "source_urls": ["https://example.com/visa-requirements", "https://example.com/application-form"]
}}

KRİTİK GEREKSINIMLER:
- Her adım başlığı TÜRKÇE olmalı
- Başlıklar kısa ve öz olmalı (max 150 karakter)
- Her step için ilgili source_urls'leri ekle
- Adımları mantıklı bir sırada listele
- Sadece temel adımları dahil et, gereksiz detaylardan kaçın
- total_steps sayısını doğru hesapla
- source_urls array'inde tüm kullanılan kaynakları topla

**DİL ZORUNLULUĞU: TÜM başlıklar TÜRKÇE dilinde olmalıdır.**
"""
        
        # Combine all sections
        user_prompt = (
            profile_text +
            requirements_text +
            steps_text +
            urls_text +
            instructions
        )
        
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]


class VisaExtractionPrompts:
    """
    Prompt templates for extracting visa requirements using LLM.
    Designed for comprehensive, context-aware extraction from scraped content.
    """
    
    # JSON Schema for structured output (DRY - shared categories)
    REQUIREMENT_SCHEMA = {
        "type": "object",
        "properties": {
            "requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Concise requirement name"},
                        "description": {"type": "string", "description": "What is needed"},
                        "category": {
                            "type": "string", 
                            "enum": VISA_CATEGORIES[:4],  # documents, financial, personal, medical
                            "description": "Requirement category"
                        },
                        "mandatory": {"type": "boolean", "description": "Is this required or optional"},
                        "notes": {"type": "string", "description": "Additional details or conditions"},
                        "applicable_to": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Who this applies to (e.g., employed, students)"
                        }
                    },
                    "required": ["title", "description", "category", "mandatory"]
                }
            }
        },
        "required": ["requirements"]
    }
    
    @staticmethod
    def build_extraction_prompt(
        content: str,
        country: str,
        visa_type: str,
        max_content_chars: int = 8000
    ) -> Dict[str, str]:
        """
        Build LLM extraction prompt for visa requirements.
        
        Args:
            content: Scraped markdown/text content from visa website
            country: Country name
            visa_type: Visa type (tourist, business, student, work)
            max_content_chars: Maximum characters to include from content
            
        Returns:
            Dictionary with 'system' and 'user' prompts
        """
        # Truncate content if too long
        truncated_content = content[:max_content_chars]
        if len(content) > max_content_chars:
            truncated_content += "\n\n[... content truncated ...]"
        
        system_prompt = """You are an expert visa requirements analyst. Your task is to extract ALL visa requirements from official visa website content.

IMPORTANT INSTRUCTIONS:
1. Extract EVERY requirement mentioned in the content - be comprehensive
2. Look for both explicit requirements (e.g., "You must provide X") and implicit ones (e.g., "Applicants should have X")
3. Common visa requirements include:
   - Passport (validity period, blank pages)
   - Visa application form
   - Passport photos (size, specifications)
   - Travel/medical insurance
   - Proof of accommodation (hotel booking, invitation)
   - Flight itinerary or tickets
   - Bank statements or financial proof
   - Employment letter or proof of income
   - Purpose of visit documents
   - Previous visa copies
   - Marriage certificate (if applicable)
   - Birth certificate (for minors)
   - Police clearance certificate
   - Health certificates or vaccination records

4. For each requirement:
   - Title: Clear, concise name (e.g., "Valid Passport", "Travel Insurance")
   - Description: What exactly is needed (e.g., "Passport valid for at least 6 months")
   - Category: documents, financial, personal, or medical
   - Mandatory: true if explicitly required, false if optional/recommended
   - Notes: Any additional details (validity periods, amounts, specifications)
   - Applicable_to: List who needs this (e.g., ["employed"], ["students"], or [] for everyone)

5. Be specific about:
   - Validity periods (e.g., "valid for 6 months beyond travel dates")
   - Quantities (e.g., "2 passport photos", "3 months bank statements")
   - Specifications (e.g., "35mm x 45mm photos", "€30,000 medical insurance coverage")

6. Extract requirements in ANY language you find, then translate titles and descriptions to English.

7. Respond with ONLY valid JSON following the exact schema. No markdown, no code blocks."""

        user_prompt = f"""Extract ALL visa requirements from the following content:

**Country:** {country.upper()}
**Visa Type:** {visa_type}

**Website Content:**
{truncated_content}

---

Extract every visa requirement mentioned above. Be thorough and comprehensive.
Return ONLY a JSON object with this structure:
{{
    "requirements": [
        {{
            "title": "Valid Passport",
            "description": "Passport must be valid for at least 6 months beyond intended stay",
            "category": "documents",
            "mandatory": true,
            "notes": "Must have at least 2 blank pages",
            "applicable_to": []
        }}
    ]
}}"""

        return {
            "system": system_prompt,
            "user": user_prompt
        }


__all__ = [
    'VisaStepsPromptBuilder',
    'BasicChecklistPromptBuilder',
    'VisaExtractionPrompts',
    'VISA_CATEGORIES',
    'PRIORITY_SCORES',
    'OUTPUT_LANGUAGE'
]

