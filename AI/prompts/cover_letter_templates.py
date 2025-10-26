"""
ENHANCED Cover Letter Prompt Templates with Visa Requirements RAG Context.

KEY INNOVATION:
- Includes actual visa requirements in prompts
- Cover letters specifically address what consulates want to see
- Uses both visa requirements AND example letters for optimal results
"""

from typing import Dict, Any, List, Optional
from models.user_profile import UnifiedUserProfile
from models.cover_letter_models import ExampleCoverLetter
from utils import logger
from utils.helpers import format_list_as_bullets


class CoverLetterPromptBuilder:
    """
    Enhanced cover letter prompt builder with visa requirements context.
    
    This is the KEY INNOVATION of the unified system:
    - Cover letters now address specific visa requirements
    - Uses RAG from visa_documents_rag collection
    - Combines requirements + examples for optimal generation
    """
    
    def __init__(self):
        """Initialize prompt builder."""
        self.base_system_prompt = self._build_base_system_prompt()
    
    def _build_base_system_prompt(self) -> str:
        """Build base system prompt."""
        return """Sen deneyimli bir vize danışmanı ve profesyonel mektup yazarısın. Vize başvuruları için etkili, ikna edici ve profesyonel niyat mektupları (cover letter) oluşturacaksın.

GÖREVİN:
Vize başvurusu için kapsamlı, detaylı ve ikna edici bir niyat mektubu oluştur.

KRİTİK İLKELER:
1. **Özgünlük**: Samimi, dürüst ve başvurucunun gerçek durumunu yansıtan bir ton kullan
2. **Profesyonellik**: Resmi, diplomatik dil kullan
3. **Netlik**: Açık ve öz ol - belirsizlikten kaçın
4. **İkna Edicil**: Ülkeye güçlü bağları ve gerçek seyahat amacını göster
5. **Detay**: Genel ifadeler değil, SPESIFIK ve SOMUT bilgiler ver

MEKTUP İÇERİĞİ - ÇOK ÖNEMLİ:
Her paragraf DETAYLI, SPESİFİK ve BİLGİLENDİRİCİ olmalı:

❌ KÖTÜ: "Ben çalışan bir insanım ve seyahat etmeyi seviyorum."
✅ İYİ: "X Şirketinde 5 yıldır Yazılım Mühendisi olarak çalışıyorum (aylık 50.000 TL maaş). Daha önce Almanya, İtalya ve İspanya'yı ziyaret ettim (2022-2024 arası Schengen vizeleri)."

❌ KÖTÜ: "Ailem Türkiye'de."
✅ İYİ: "Eşim ve 2 çocuğum İstanbul'da yaşamaktadır. Ayrıca Kadıköy'de 800.000 TL değerinde bir ev sahibiyim ve şirketimde yönetici pozisyonundayım - bu nedenle kesinlikle ülkeme döneceğim."

❌ KÖTÜ: "Paris'i gezmek istiyorum."
✅ İYİ: "15-28 Haziran 2025 tarihleri arasında Paris'te 14 gün kalacağım. Rezervasyonunu yaptığım Hotel Le Marais'de (onay no: ABC123) konaklayacağım. Louvre Müzesi, Eyfel Kulesi ve Versailles Sarayı'nı ziyaret etmeyi planlıyorum."

PARAGRAF KURALLARI:
- **Introduction**: Kimsin, ne iş yapıyorsun, neden başvuruyorsun (SPESİFİK)
- **Travel Purpose**: DETAYLI seyahat planı (tarihler, yerler, aktiviteler, konaklama)
- **Financial Proof**: MALİ durumunu SOMUT rakamlarla göster (maaş, tasarruf, sponsorluk)
- **Ties to Home**: Ülkeye dönüş nedenlerini SPESIFIK örneklerle açıkla (iş, aile, emlak, eğitim)
- **Conclusion**: Profesyonel kapanış ve teşekkür

ZORUNLU ÇIKTI FORMATI:
Sadece geçerli JSON döndür. Markdown, açıklama ekleme.

{{
  "title": "Fransa Turist Vizesi Başvurusu - Niyat Mektubu",
  "salutation": "Sayın Vize Görevlisi,",
  "introduction": "Giriş paragrafı...",
  "body_paragraphs": [
    "Detaylı paragraf 1...",
    "Detaylı paragraf 2...",
    "Detaylı paragraf 3..."
  ],
  "conclusion": "Kapanış paragrafı...",
  "closing": "Saygılarımla,",
  "key_points": ["Nokta 1", "Nokta 2"],
  "tone": "Profesyonel ve saygılı",
  "word_count": 450
}}

**DİL ZORUNLULUĞU: TÜM içerik (title, salutation, introduction, body_paragraphs, conclusion, closing, key_points, tone) TÜRKÇE dilinde olmalıdır. Profesyonel, resmi Türkçe kullan.**"""
    
    def build_messages_with_visa_context(
        self,
        user_profile: UnifiedUserProfile,
        visa_requirements: List[Dict[str, Any]],
        example_letters: List[ExampleCoverLetter],
        max_word_count: int = 500
    ) -> List[Dict[str, str]]:
        """
        Build messages with BOTH visa requirements AND example letters context.
        
        This is the KEY METHOD - combines all context sources for optimal generation.
        
        Args:
            user_profile: Complete user profile
            visa_requirements: Visa requirements from RAG (visa_docs_rag collection)
            example_letters: Example letters from RAG (cover_letters collection)
            max_word_count: Maximum word count
            
        Returns:
            List of message dictionaries for LLM
        """
        # Build enhanced system prompt with visa requirements
        system_prompt = self._build_enhanced_system_prompt(visa_requirements)
        
        # Build user prompt with all context
        user_prompt = self._build_user_prompt(
            user_profile=user_profile,
            visa_requirements=visa_requirements,
            example_letters=example_letters,
            max_word_count=max_word_count
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _build_enhanced_system_prompt(
        self,
        visa_requirements: List[Dict[str, Any]]
    ) -> str:
        """
        Build enhanced system prompt with visa requirements.
        
        KEY INNOVATION: System prompt now includes actual visa requirements!
        """
        enhanced_prompt = self.base_system_prompt
        
        if visa_requirements:
            requirements_section = "\n\n## ÖNEMLİ: MEKTUPTA ADRESLENMESİ GEREKEN VİZE GEREKSİNİMLERİ (RAG Context)\n"
            requirements_section += "Niyat mektubunuz bu gereksinimleri DOĞAL BİR ŞEKİLDE içermeli:\n\n"
            
            for i, req in enumerate(visa_requirements[:5], 1):  # Top 5 requirements
                payload = req.get('payload', {})
                score = req.get('score', 0)
                title = payload.get('title', 'N/A')
                description = payload.get('description', '')
                category = payload.get('category', '')
                mandatory = payload.get('mandatory', False)
                notes = payload.get('notes', '')
                
                status = "**ZORUNLU**" if mandatory else "Opsiyonel"
                requirements_section += f"{i}. **{title}** ({status}) - Kategori: {category}\n"
                requirements_section += f"   Benzerlik: {score:.2f}\n"
                if description:
                    requirements_section += f"   Açıklama: {description}\n"
                if notes:
                    requirements_section += f"   Önemli Not: {notes}\n"
                requirements_section += "\n"
            
            requirements_section += "\n**KRİTİK**: Bu gereksinimleri mekanik olarak listeleme. Bunları mektubun akışı içinde DOĞAL olarak dokuyun. Her gereksinimi SPESİFİK örnekler ve detaylarla gösterin. RAG'den gelen notları ve açıklamaları kullanarak daha zengin içerik oluşturun.\n"
            
            enhanced_prompt += requirements_section
        
        return enhanced_prompt
    
    def _build_user_prompt(
        self,
        user_profile: UnifiedUserProfile,
        visa_requirements: List[Dict[str, Any]],
        example_letters: List[ExampleCoverLetter],
        max_word_count: int
    ) -> str:
        """Build complete user prompt with all context."""
        
        # Build profile section
        profile_section = f"""## BAŞVURUCU BİLGİLERİ
- **Ad Soyad**: {user_profile.full_name}
- **Uyruk**: {user_profile.nationality}
- **Meslek**: {user_profile.occupation}
- **Eğitim**: {user_profile.education or "Belirtilmemiş"}

## VİZE BAŞVURU DETAYLARI
- **Hedef Ülke**: {user_profile.destination_country}
- **Vize Tipi**: {user_profile.visa_type.value}
- **Seyahat Amacı**: {user_profile.travel_purpose}
- **Seyahat Tarihleri**: {user_profile.travel_dates.start} - {user_profile.travel_dates.end}

## BAŞVURUCU ARKA PLAN
**Meslek**: {user_profile.occupation}
"""
        
        # Travel history
        if user_profile.previous_travel_history:
            countries = ", ".join(user_profile.previous_travel_history)
            profile_section += f"\n**Önceki Seyahat Geçmişi**: {countries}\n"
        
        # Financial status
        if user_profile.financial_status:
            profile_section += f"\n**Mali Durum**: {user_profile.financial_status}\n"
        
        # Ties to home country
        if user_profile.ties_to_home_country:
            ties_list = format_list_as_bullets(user_profile.ties_to_home_country)
            profile_section += f"\n**Ülkeye Bağlar ({user_profile.nationality})**:\n{ties_list}\n"
        
        # Visa requirements section with FULL RAG context (KEY INNOVATION!)
        visa_req_section = "\n## MEKTUPTA ADRESLENMESİ GEREKEN VİZE GEREKSİNİMLERİ (RAG Context)\n"
        if visa_requirements:
            visa_req_section += "**ÖNEMLİ**: Niyat mektubunuz bu gereksinimleri SPESİFİK olarak ele almalı:\n\n"
            for i, req in enumerate(visa_requirements[:5], 1):
                payload = req.get('payload', {})
                score = req.get('score', 0)
                title = payload.get('title', 'N/A')
                description = payload.get('description', '')
                category = payload.get('category', '')
                mandatory = payload.get('mandatory', False)
                notes = payload.get('notes', '')
                
                visa_req_section += f"{i}. **{title}** ({category}) - {'ZORUNLU' if mandatory else 'Opsiyonel'}\n"
                visa_req_section += f"   RAG Benzerlik: {score:.2f}\n"
                if description:
                    visa_req_section += f"   Açıklama: {description}\n"
                if notes:
                    visa_req_section += f"   Önemli Notlar: {notes}\n"
                visa_req_section += "\n"
            
            visa_req_section += "**NASIL KULLANILMALI**: \n"
            visa_req_section += "- Bu gereksinimleri mektubun akışı içinde DOĞAL olarak dokuyun\n"
            visa_req_section += "- Başvurucunun her gereksinimi nasıl karşıladığını SPESİFİK örnekler ve detaylarla gösterin\n"
            visa_req_section += "- RAG'den gelen açıklamaları ve notları kullanarak zengin, bilgilendirici paragraflar oluşturun\n"
            visa_req_section += "- Listeleme yapmayın, anlatı içinde işleyin\n"
        else:
            visa_req_section += "Spesifik gereksinim sağlanmadı. Genel en iyi uygulamaları kullan.\n"
        
        # Examples section with FULL context
        examples_section = "\n## REFERANS ÖRNEKLER (RAG Context)\n"
        if example_letters:
            examples_section += f"İşte {len(example_letters)} benzer onaylanmış niyat mektubu. Bunları yapısal ve ton referansı olarak kullan ama DİREKT KOPYALAMA:\n\n"
            
            for idx, example in enumerate(example_letters[:2], 1):  # Top 2 examples
                status = "✓ ONAYLANDI" if example.approved else "Referans"
                examples_section += f"### Örnek {idx} - {example.country} {example.visa_type} {status}\n"
                
                # Add metadata
                if hasattr(example, 'nationality'):
                    examples_section += f"**Uyruk**: {example.nationality} | "
                if hasattr(example, 'occupation'):
                    examples_section += f"**Meslek**: {example.occupation} | "
                if hasattr(example, 'word_count'):
                    examples_section += f"**Kelime**: {example.word_count}\n"
                else:
                    examples_section += "\n"
                
                # Content preview
                examples_section += f"```\n{example.content[:800]}...\n```\n"
                
                # Key points if available
                if hasattr(example, 'key_points') and example.key_points:
                    examples_section += f"**Anahtar Noktalar**: {', '.join(example.key_points[:3])}\n"
                
                examples_section += "\n"
            
            examples_section += "**NASIL KULLAN**: Bu örneklerdeki yapı, ton, detay seviyesi ve ikna tekniklerini modelleyerek kendi mektubunu oluştur. İçeriği kopyalama, yaklaşımı adapte et.\n"
        else:
            examples_section += "Benzer örnek bulunamadı. En iyi uygulamalar ve vize gereksinimlerine göre üret.\n"
        
        # Final instructions
        instructions = f"""

## ÇIKTI TALİMATLARI
İkna edici bir niyat mektubu oluştur:

1. **Yukarıdaki vize gereksinimlerini SPESİFİK olarak ele al** (ANAHTAR!)
2. Seyahat amacını NET belirt ve gerçek niyeti göster
3. Başvurucunun niteliklerini ve geçmişini vurgula - SOMUT detaylarla
4. {user_profile.nationality} ülkesine güçlü bağları vurgula - SPESİFİK örneklerle
5. Yaklaşık {max_word_count} kelime uzunluğunda olsun
6. SPESİFİK detaylar ve tarihler kullan (genel ifadeler değil)
7. Profesyonel, özgüvenli ama saygılı bir ton koru
8. Başvurucunun her gereksinimi nasıl karşıladığını göster

**PARAGRAF KURALLARI (ÇOK ÖNEMLİ)**:
❌ KÖTÜ: "Ben iyi bir insanım ve gezmeyi severim."
✅ İYİ: "5 yıldır X Şirketinde Yazılım Mühendisi olarak çalışıyorum (aylık 50.000 TL). Daha önce Schengen bölgesini 3 kez ziyaret ettim (2022-2024)."

❌ KÖTÜ: "Mali durumum iyidir."
✅ İYİ: "Banka hesabımda 150.000 TL tasarrufum var (Garanti Bankası hesap ekstresi ekli). Ayrıca aylık 50.000 TL net maaş alıyorum ve seyahatim için toplam 30.000 TL bütçe ayırdım."

❌ KÖTÜ: "Paris'i görmek istiyorum."
✅ İYİ: "15-28 Haziran 2025 tarihleri arasında 14 gün Paris'te kalacağım. Hotel Le Marais'te (rezervasyon no: ABC123, gecesi 120 EUR) konaklayacağım. Louvre Müzesi, Eyfel Kulesi ve Versailles Sarayı'nı ziyaret edeceğim."

**KRİTİK**: SADECE geçerli JSON döndür. {{ ile başla }} ile bitir. Markdown veya açıklama ekleme.

**DİL ZORUNLULUĞU: Niyat mektubu TÜRKÇE dilinde yazılmalıdır. Tüm alanlar (title, salutation, introduction, body_paragraphs, conclusion, closing, key_points, tone) Türkçe metin içermelidir. Profesyonel, resmi Türkçe kullan.**"""
        
        # Combine all sections
        complete_prompt = (
            profile_section +
            visa_req_section +
            examples_section +
            instructions
        )
        
        logger.info("Built enhanced prompt with visa requirements context")
        return complete_prompt


__all__ = ['CoverLetterPromptBuilder']

