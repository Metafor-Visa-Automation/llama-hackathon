"""
Country to visa information URLs mapping.
Maps destination countries to their official visa information websites.
"""

from typing import Dict, List

# Country code -> URLs mapping
COUNTRY_VISA_URLS: Dict[str, List[str]] = {
    "Almanya": [
        "https://www.auswaertiges-amt.de/en/visa-service",
        "https://digital.diplo.de/Visa",
        "https://www.germany.info/us-en/service/visa",
    ],
    "Germany": [
        "https://www.auswaertiges-amt.de/en/visa-service",
        "https://digital.diplo.de/Visa",
        "https://www.germany.info/us-en/service/visa",
    ],
    "Fransa": [
        "https://france-visas.gouv.fr",
        "https://www.diplomatie.gouv.fr/en/coming-to-france/",
        "https://www.welcometofrance.com/en/fiche/short-stay-visa",
    ],
    "France": [
        "https://france-visas.gouv.fr",
        "https://www.diplomatie.gouv.fr/en/coming-to-france/",
        "https://www.welcometofrance.com/en/fiche/short-stay-visa",
    ],
    "İtalya": [
        "https://vistoperitalia.esteri.it/home/en",
        "https://www.esteri.it/en/servizi-consolari-e-visti/",
        "https://www.schengenvisainfo.com/italy-visa/",
    ],
    "Italy": [
        "https://vistoperitalia.esteri.it/home/en",
        "https://www.esteri.it/en/servizi-consolari-e-visti/",
        "https://www.schengenvisainfo.com/italy-visa/",
    ],
    "İspanya": [
        "https://www.exteriores.gob.es/en/ServiciosAlCiudadano/Paginas/Visados.aspx",
        "https://blsspainvisa.com",
        "https://www.schengenvisainfo.com/spain-visa/",
    ],
    "Spain": [
        "https://www.exteriores.gob.es/en/ServiciosAlCiudadano/Paginas/Visados.aspx",
        "https://blsspainvisa.com",
        "https://www.schengenvisainfo.com/spain-visa/",
    ],
    "Hollanda": [
        "https://www.netherlandsworldwide.nl/visa-the-netherlands",
        "https://www.government.nl/topics/immigration-to-the-netherlands",
        "https://ind.nl/en",
    ],
    "Netherlands": [
        "https://www.netherlandsworldwide.nl/visa-the-netherlands",
        "https://www.government.nl/topics/immigration-to-the-netherlands",
        "https://ind.nl/en",
    ],
    "Portekiz": [
        "https://vistos.mne.gov.pt/en/",
        "https://www.gov.pt/en/migrantes-viver-e-trabalhar-em-portugal",
        "https://eportugal.gov.pt/en/inicio",
    ],
    "Portugal": [
        "https://vistos.mne.gov.pt/en/",
        "https://www.gov.pt/en/migrantes-viver-e-trabalhar-em-portugal",
        "https://eportugal.gov.pt/en/inicio",
    ],
    "Avusturya": [
        "https://www.oesterreich.gv.at/en/themen/menschen_aus_anderen_staaten/visum_fuer_oesterreich",
        "https://www.migration.gv.at/en/",
        "https://www.bmeia.gv.at/en/",
    ],
    "Austria": [
        "https://www.oesterreich.gv.at/en/themen/menschen_aus_anderen_staaten/visum_fuer_oesterreich",
        "https://www.migration.gv.at/en/",
        "https://www.bmeia.gv.at/en/",
    ],
    "Belçika": [
        "https://visaonweb.diplomatie.be",
        "http://diplomatie.belgium.be/en/travel-belgium/visa-belgium",
        "https://dofi.ibz.be/en",
    ],
    "Belgium": [
        "https://visaonweb.diplomatie.be",
        "http://diplomatie.belgium.be/en/travel-belgium/visa-belgium",
        "https://dofi.ibz.be/en",
    ],
    "İsveç": [
        "https://www.migrationsverket.se/en/you-want-to-apply/visiting-sweden.html",
        "https://www.government.se/government-policy/migration-and-asylum/",
        "https://www.swedenabroad.se/en/",
    ],
    "Sweden": [
        "https://www.migrationsverket.se/en/you-want-to-apply/visiting-sweden.html",
        "https://www.government.se/government-policy/migration-and-asylum/",
        "https://www.swedenabroad.se/en/",
    ],
    "Yunanistan": [
        "https://www.mfa.gr/usa/en/visas.html",
        "https://evisa.gr",
        "https://migration.gov.gr/en/",
    ],
    "Greece": [
        "https://www.mfa.gr/usa/en/visas.html",
        "https://evisa.gr",
        "https://migration.gov.gr/en/",
    ],
}



def get_country_urls(country: str) -> List[str]:
    """
    Get visa information URLs for a given country.
    
    Args:
        country: Country name (can be in Turkish or English)
        
    Returns:
        List of URLs for the country, or empty list if not found
    """
    # Try exact match first
    if country in COUNTRY_VISA_URLS:
        return COUNTRY_VISA_URLS[country]
    
    # Try case-insensitive match
    country_lower = country.lower()
    for key, urls in COUNTRY_VISA_URLS.items():
        if key.lower() == country_lower:
            return urls
    
    return []


def is_country_supported(country: str) -> bool:
    """
    Check if a country has predefined URLs.
    
    Args:
        country: Country name
        
    Returns:
        True if country is supported, False otherwise
    """
    return len(get_country_urls(country)) > 0


__all__ = ['COUNTRY_VISA_URLS', 'get_country_urls', 'is_country_supported']
