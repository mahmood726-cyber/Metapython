"""
Accessibility and Internationalization - Phase 8
Language hooks, ARIA roles, keyboard navigation, contrast checks
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass
from pathlib import Path
import re
from datetime import datetime

# Web framework support (optional)
try:
    from fastapi import Request
    from fastapi.responses import HTMLResponse
    from jinja2 import Environment, FileSystemLoader
    HAS_WEB_FRAMEWORK = True
except ImportError:
    HAS_WEB_FRAMEWORK = False

# Color analysis for contrast (optional)
try:
    from colorsys import rgb_to_hls, hls_to_rgb
    HAS_COLOR_ANALYSIS = True
except ImportError:
    HAS_COLOR_ANALYSIS = False

logger = logging.getLogger(__name__)

@dataclass
class AccessibilityConfig:
    """Accessibility configuration"""
    enable_screen_reader: bool = True
    enable_keyboard_navigation: bool = True
    enable_high_contrast: bool = False
    enable_large_text: bool = False
    default_language: str = "en"
    supported_languages: List[str] = None
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["en", "es", "fr", "de", "zh", "ja"]

class LanguageManager:
    """Internationalization and localization manager"""
    
    def __init__(self, default_language: str = "en"):
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.pluralization_rules: Dict[str, Callable] = {}
        
        self._load_default_translations()
        self._setup_pluralization_rules()
    
    def _load_default_translations(self):
        """Load default translations for common meta-analysis terms"""
        
        # English (base language)
        self.translations["en"] = {
            # General terms
            "meta_analysis": "Meta-Analysis",
            "effect_size": "Effect Size",
            "confidence_interval": "Confidence Interval",
            "standard_error": "Standard Error",
            "study": "Study",
            "studies": "Studies",
            "heterogeneity": "Heterogeneity",
            "publication_bias": "Publication Bias",
            "forest_plot": "Forest Plot",
            "funnel_plot": "Funnel Plot",
            
            # Statistical terms
            "fixed_effects": "Fixed Effects",
            "random_effects": "Random Effects",
            "pooled_estimate": "Pooled Estimate",
            "tau_squared": "Tau²",
            "i_squared": "I²",
            "q_statistic": "Q Statistic",
            "p_value": "P-value",
            "significant": "Significant",
            "not_significant": "Not Significant",
            
            # Methods
            "dersimonian_laird": "DerSimonian-Laird",
            "restricted_maximum_likelihood": "Restricted Maximum Likelihood",
            "mantel_haenszel": "Mantel-Haenszel",
            "peto_method": "Peto Method",
            
            # UI elements
            "analyze": "Analyze",
            "results": "Results",
            "download": "Download",
            "upload": "Upload",
            "configure": "Configure",
            "settings": "Settings",
            "help": "Help",
            "about": "About",
            
            # Accessibility
            "skip_to_content": "Skip to main content",
            "menu": "Menu",
            "search": "Search",
            "next": "Next",
            "previous": "Previous",
            "close": "Close",
            "expand": "Expand",
            "collapse": "Collapse",
            
            # Status messages
            "loading": "Loading...",
            "error_occurred": "An error occurred",
            "analysis_complete": "Analysis complete",
            "no_data": "No data available",
            "invalid_input": "Invalid input",
            "success": "Success",
            "warning": "Warning",
            "information": "Information"
        }
        
        # Spanish translations
        self.translations["es"] = {
            "meta_analysis": "Meta-Análisis",
            "effect_size": "Tamaño del Efecto",
            "confidence_interval": "Intervalo de Confianza",
            "standard_error": "Error Estándar",
            "study": "Estudio",
            "studies": "Estudios",
            "heterogeneity": "Heterogeneidad",
            "publication_bias": "Sesgo de Publicación",
            "forest_plot": "Gráfico de Bosque",
            "funnel_plot": "Gráfico de Embudo",
            "fixed_effects": "Efectos Fijos",
            "random_effects": "Efectos Aleatorios",
            "pooled_estimate": "Estimación Combinada",
            "p_value": "Valor P",
            "significant": "Significativo",
            "not_significant": "No Significativo",
            "analyze": "Analizar",
            "results": "Resultados",
            "download": "Descargar",
            "upload": "Subir",
            "settings": "Configuración",
            "help": "Ayuda",
            "loading": "Cargando...",
            "error_occurred": "Ocurrió un error",
            "analysis_complete": "Análisis completo",
            "skip_to_content": "Saltar al contenido principal",
            "menu": "Menú",
            "search": "Buscar"
        }
        
        # French translations
        self.translations["fr"] = {
            "meta_analysis": "Méta-Analyse",
            "effect_size": "Taille d'Effet",
            "confidence_interval": "Intervalle de Confiance",
            "standard_error": "Erreur Standard",
            "study": "Étude",
            "studies": "Études",
            "heterogeneity": "Hétérogénéité",
            "publication_bias": "Biais de Publication",
            "forest_plot": "Graphique en Forêt",
            "funnel_plot": "Graphique en Entonnoir",
            "fixed_effects": "Effets Fixes",
            "random_effects": "Effets Aléatoires",
            "pooled_estimate": "Estimation Combinée",
            "p_value": "Valeur P",
            "significant": "Significatif",
            "not_significant": "Non Significatif",
            "analyze": "Analyser",
            "results": "Résultats",
            "download": "Télécharger",
            "upload": "Téléverser",
            "settings": "Paramètres",
            "help": "Aide",
            "loading": "Chargement...",
            "error_occurred": "Une erreur s'est produite",
            "analysis_complete": "Analyse terminée",
            "skip_to_content": "Aller au contenu principal",
            "menu": "Menu",
            "search": "Rechercher"
        }
        
        # German translations
        self.translations["de"] = {
            "meta_analysis": "Meta-Analyse",
            "effect_size": "Effektstärke",
            "confidence_interval": "Konfidenzintervall",
            "standard_error": "Standardfehler",
            "study": "Studie",
            "studies": "Studien",
            "heterogeneity": "Heterogenität",
            "publication_bias": "Publikationsbias",
            "forest_plot": "Forest Plot",
            "funnel_plot": "Funnel Plot",
            "fixed_effects": "Feste Effekte",
            "random_effects": "Zufällige Effekte",
            "pooled_estimate": "Gepoolte Schätzung",
            "p_value": "P-Wert",
            "significant": "Signifikant",
            "not_significant": "Nicht Signifikant",
            "analyze": "Analysieren",
            "results": "Ergebnisse",
            "download": "Herunterladen",
            "upload": "Hochladen",
            "settings": "Einstellungen",
            "help": "Hilfe",
            "loading": "Wird geladen...",
            "error_occurred": "Ein Fehler ist aufgetreten",
            "analysis_complete": "Analyse abgeschlossen",
            "skip_to_content": "Zum Hauptinhalt springen",
            "menu": "Menü",
            "search": "Suchen"
        }
    
    def _setup_pluralization_rules(self):
        """Setup pluralization rules for different languages"""
        
        # English pluralization
        def english_plural(count: int, singular: str, plural: str = None) -> str:
            if count == 1:
                return singular
            return plural or f"{singular}s"
        
        # Spanish pluralization
        def spanish_plural(count: int, singular: str, plural: str = None) -> str:
            if count == 1:
                return singular
            if plural:
                return plural
            if singular.endswith(('a', 'e', 'i', 'o', 'u')):
                return f"{singular}s"
            return f"{singular}es"
        
        # French pluralization
        def french_plural(count: int, singular: str, plural: str = None) -> str:
            if count <= 1:
                return singular
            return plural or f"{singular}s"
        
        # German pluralization (simplified)
        def german_plural(count: int, singular: str, plural: str = None) -> str:
            if count == 1:
                return singular
            return plural or f"{singular}e"
        
        self.pluralization_rules = {
            "en": english_plural,
            "es": spanish_plural,
            "fr": french_plural,
            "de": german_plural
        }
    
    def set_language(self, language_code: str) -> bool:
        """Set current language"""
        if language_code in self.translations:
            self.current_language = language_code
            logger.info(f"Language set to: {language_code}")
            return True
        else:
            logger.warning(f"Language {language_code} not supported")
            return False
    
    def translate(self, key: str, language: Optional[str] = None) -> str:
        """Translate a key to current or specified language"""
        target_language = language or self.current_language
        
        # Try target language first
        if target_language in self.translations:
            translation = self.translations[target_language].get(key)
            if translation:
                return translation
        
        # Fallback to default language
        if self.default_language in self.translations:
            translation = self.translations[self.default_language].get(key)
            if translation:
                return translation
        
        # Return key if no translation found
        logger.debug(f"No translation found for key: {key}")
        return key
    
    def pluralize(self, count: int, singular_key: str, plural_key: Optional[str] = None,
                 language: Optional[str] = None) -> str:
        """Get pluralized translation"""
        target_language = language or self.current_language
        
        singular = self.translate(singular_key, target_language)
        plural = self.translate(plural_key, target_language) if plural_key else None
        
        if target_language in self.pluralization_rules:
            return self.pluralization_rules[target_language](count, singular, plural)
        else:
            # Default English-like pluralization
            return singular if count == 1 else (plural or f"{singular}s")
    
    def format_number(self, number: float, decimal_places: int = 3,
                     language: Optional[str] = None) -> str:
        """Format number according to language conventions"""
        target_language = language or self.current_language
        
        # Language-specific number formatting
        if target_language in ["de", "fr"]:
            # European formatting (comma as decimal separator)
            formatted = f"{number:.{decimal_places}f}".replace('.', ',')
        else:
            # Default formatting (period as decimal separator)
            formatted = f"{number:.{decimal_places}f}"
        
        return formatted
    
    def add_translations(self, language_code: str, translations: Dict[str, str]) -> None:
        """Add or update translations for a language"""
        if language_code not in self.translations:
            self.translations[language_code] = {}
        
        self.translations[language_code].update(translations)
        logger.info(f"Added {len(translations)} translations for {language_code}")
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages with their names"""
        language_names = {
            "en": "English",
            "es": "Español",
            "fr": "Français", 
            "de": "Deutsch",
            "zh": "中文",
            "ja": "日本語"
        }
        
        return [
            {
                "code": lang_code,
                "name": language_names.get(lang_code, lang_code),
                "native_name": language_names.get(lang_code, lang_code)
            }
            for lang_code in self.translations.keys()
        ]

class AccessibilityChecker:
    """Accessibility compliance checker"""
    
    def __init__(self):
        self.wcag_guidelines = {
            "contrast_ratio": {
                "normal_text": 4.5,
                "large_text": 3.0,
                "ui_components": 3.0
            },
            "font_sizes": {
                "minimum_body": 16,
                "minimum_large": 18
            }
        }
    
    def check_color_contrast(self, foreground_rgb: tuple, background_rgb: tuple) -> Dict[str, Any]:
        """Check color contrast ratio compliance"""
        if not HAS_COLOR_ANALYSIS:
            return {"available": False, "reason": "Color analysis not available"}
        
        try:
            # Calculate relative luminance
            def get_luminance(rgb):
                def linearize(c):
                    c = c / 255.0
                    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                
                r, g, b = rgb
                return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)
            
            l1 = get_luminance(foreground_rgb)
            l2 = get_luminance(background_rgb)
            
            # Ensure l1 is the lighter color
            if l1 < l2:
                l1, l2 = l2, l1
            
            contrast_ratio = (l1 + 0.05) / (l2 + 0.05)
            
            return {
                "contrast_ratio": contrast_ratio,
                "meets_normal_text": contrast_ratio >= self.wcag_guidelines["contrast_ratio"]["normal_text"],
                "meets_large_text": contrast_ratio >= self.wcag_guidelines["contrast_ratio"]["large_text"],
                "meets_ui_components": contrast_ratio >= self.wcag_guidelines["contrast_ratio"]["ui_components"],
                "wcag_aa_compliant": contrast_ratio >= 4.5,
                "wcag_aaa_compliant": contrast_ratio >= 7.0
            }
        
        except Exception as e:
            logger.error(f"Contrast check failed: {e}")
            return {"error": str(e)}
    
    def suggest_color_improvements(self, foreground_rgb: tuple, background_rgb: tuple) -> List[str]:
        """Suggest color improvements for better accessibility"""
        suggestions = []
        
        contrast_result = self.check_color_contrast(foreground_rgb, background_rgb)
        
        if not contrast_result.get("meets_normal_text", True):
            suggestions.append("Increase contrast for better text readability")
            suggestions.append("Consider using darker text on light background or vice versa")
        
        if not contrast_result.get("meets_ui_components", True):
            suggestions.append("Improve contrast for UI components and controls")
        
        # Specific suggestions based on colors
        fg_brightness = sum(foreground_rgb) / 3
        bg_brightness = sum(background_rgb) / 3
        
        if abs(fg_brightness - bg_brightness) < 50:
            suggestions.append("Colors are too similar - increase brightness difference")
        
        return suggestions
    
    def validate_html_accessibility(self, html_content: str) -> Dict[str, Any]:
        """Basic HTML accessibility validation"""
        issues = []
        recommendations = []
        
        # Check for alt text on images
        img_without_alt = re.findall(r'<img(?![^>]*alt=)[^>]*>', html_content, re.IGNORECASE)
        if img_without_alt:
            issues.append(f"Found {len(img_without_alt)} images without alt text")
            recommendations.append("Add descriptive alt text to all images")
        
        # Check for heading structure
        headings = re.findall(r'<h([1-6])[^>]*>', html_content, re.IGNORECASE)
        if headings:
            heading_levels = [int(h) for h in headings]
            if heading_levels and heading_levels[0] != 1:
                issues.append("Page does not start with h1 heading")
                recommendations.append("Start page with a single h1 heading")
            
            # Check for skipped heading levels
            for i in range(1, len(heading_levels)):
                if heading_levels[i] - heading_levels[i-1] > 1:
                    issues.append("Heading levels are skipped")
                    recommendations.append("Use heading levels sequentially (h1, h2, h3, etc.)")
                    break
        
        # Check for form labels
        inputs = re.findall(r'<input[^>]*>', html_content, re.IGNORECASE)
        labels = re.findall(r'<label[^>]*>', html_content, re.IGNORECASE)
        if len(inputs) > len(labels):
            issues.append("Some form inputs may be missing labels")
            recommendations.append("Ensure all form inputs have associated labels")
        
        # Check for skip links
        if 'skip' not in html_content.lower() or 'main' not in html_content.lower():
            recommendations.append("Consider adding a 'skip to main content' link")
        
        # Check for ARIA landmarks
        landmarks = ['main', 'nav', 'banner', 'contentinfo', 'complementary']
        found_landmarks = [landmark for landmark in landmarks if landmark in html_content.lower()]
        if len(found_landmarks) < 2:
            recommendations.append("Add ARIA landmarks for better navigation")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "accessibility_score": max(0, 100 - len(issues) * 10),
            "compliant": len(issues) == 0
        }

class ARIAHelper:
    """ARIA (Accessible Rich Internet Applications) helper"""
    
    @staticmethod
    def generate_aria_attributes(element_type: str, **kwargs) -> Dict[str, str]:
        """Generate appropriate ARIA attributes for elements"""
        aria_attrs = {}
        
        if element_type == "button":
            if kwargs.get("expanded") is not None:
                aria_attrs["aria-expanded"] = str(kwargs["expanded"]).lower()
            if kwargs.get("controls"):
                aria_attrs["aria-controls"] = kwargs["controls"]
            if kwargs.get("describedby"):
                aria_attrs["aria-describedby"] = kwargs["describedby"]
        
        elif element_type == "table":
            aria_attrs["role"] = "table"
            if kwargs.get("caption"):
                aria_attrs["aria-label"] = kwargs["caption"]
        
        elif element_type == "chart":
            aria_attrs["role"] = "img"
            aria_attrs["aria-label"] = kwargs.get("title", "Chart")
            if kwargs.get("description"):
                aria_attrs["aria-describedby"] = f"chart-desc-{kwargs.get('id', 'default')}"
        
        elif element_type == "menu":
            aria_attrs["role"] = "menu"
            if kwargs.get("orientation"):
                aria_attrs["aria-orientation"] = kwargs["orientation"]
        
        elif element_type == "dialog":
            aria_attrs["role"] = "dialog"
            aria_attrs["aria-modal"] = "true"
            if kwargs.get("title"):
                aria_attrs["aria-labelledby"] = f"dialog-title-{kwargs.get('id', 'default')}"
        
        elif element_type == "alert":
            aria_attrs["role"] = "alert"
            aria_attrs["aria-live"] = "assertive"
        
        elif element_type == "status":
            aria_attrs["role"] = "status"
            aria_attrs["aria-live"] = "polite"
        
        return aria_attrs
    
    @staticmethod
    def create_accessible_table_html(data: List[List[str]], headers: List[str],
                                   caption: str = None) -> str:
        """Create accessible HTML table"""
        html = ['<table role="table"']
        
        if caption:
            html[0] += f' aria-label="{caption}"'
        
        html.append('>')
        
        if caption:
            html.append(f'  <caption>{caption}</caption>')
        
        # Headers
        html.append('  <thead>')
        html.append('    <tr>')
        for header in headers:
            html.append(f'      <th scope="col">{header}</th>')
        html.append('    </tr>')
        html.append('  </thead>')
        
        # Body
        html.append('  <tbody>')
        for row in data:
            html.append('    <tr>')
            for cell in row:
                html.append(f'      <td>{cell}</td>')
            html.append('    </tr>')
        html.append('  </tbody>')
        html.append('</table>')
        
        return '\n'.join(html)
    
    @staticmethod
    def create_accessible_chart_description(chart_type: str, data_summary: Dict[str, Any]) -> str:
        """Create accessible description for charts"""
        if chart_type == "forest_plot":
            desc = f"Forest plot showing {data_summary.get('n_studies', 0)} studies. "
            desc += f"Overall effect size: {data_summary.get('pooled_effect', 'N/A')}. "
            desc += f"Confidence interval: {data_summary.get('ci_low', 'N/A')} to {data_summary.get('ci_high', 'N/A')}."
            
        elif chart_type == "funnel_plot":
            desc = f"Funnel plot showing {data_summary.get('n_studies', 0)} studies plotted by effect size and standard error. "
            if data_summary.get('asymmetry_detected'):
                desc += "Visual inspection suggests possible publication bias."
            else:
                desc += "Studies appear symmetrically distributed."
        
        else:
            desc = f"{chart_type.replace('_', ' ').title()} chart with {data_summary.get('n_points', 0)} data points."
        
        return desc

class KeyboardNavigation:
    """Keyboard navigation helpers"""
    
    @staticmethod
    def generate_keyboard_shortcuts() -> Dict[str, str]:
        """Generate standard keyboard shortcuts"""
        return {
            "alt+m": "Open main menu",
            "alt+s": "Search",
            "alt+h": "Help",
            "ctrl+enter": "Submit form/Run analysis",
            "escape": "Close dialog/Cancel",
            "tab": "Next element",
            "shift+tab": "Previous element",
            "enter": "Activate button/link",
            "space": "Select checkbox/radio button",
            "arrow_keys": "Navigate menus/tables",
            "home": "Go to beginning",
            "end": "Go to end",
            "page_up": "Page up",
            "page_down": "Page down"
        }
    
    @staticmethod
    def create_skip_links_html() -> str:
        """Create skip navigation links"""
        return '''
        <div class="skip-links" aria-label="Skip navigation">
            <a href="#main-content" class="skip-link">Skip to main content</a>
            <a href="#main-nav" class="skip-link">Skip to navigation</a>
            <a href="#search" class="skip-link">Skip to search</a>
        </div>
        '''
    
    @staticmethod
    def create_keyboard_shortcuts_help() -> str:
        """Create keyboard shortcuts help text"""
        shortcuts = KeyboardNavigation.generate_keyboard_shortcuts()
        
        html = ['<div class="keyboard-shortcuts" role="region" aria-labelledby="shortcuts-title">']
        html.append('<h3 id="shortcuts-title">Keyboard Shortcuts</h3>')
        html.append('<dl>')
        
        for key, description in shortcuts.items():
            html.append(f'  <dt><kbd>{key.replace("_", " ").title()}</kbd></dt>')
            html.append(f'  <dd>{description}</dd>')
        
        html.append('</dl>')
        html.append('</div>')
        
        return '\n'.join(html)

class AccessibilityManager:
    """Central accessibility and i18n management"""
    
    def __init__(self, config: AccessibilityConfig = None):
        self.config = config or AccessibilityConfig()
        self.language_manager = LanguageManager(self.config.default_language)
        self.accessibility_checker = AccessibilityChecker()
        self.aria_helper = ARIAHelper()
        
        # Set initial language
        self.language_manager.set_language(self.config.default_language)
    
    def get_localized_content(self, content_key: str, **format_args) -> str:
        """Get localized content with formatting"""
        translated = self.language_manager.translate(content_key)
        
        if format_args:
            try:
                return translated.format(**format_args)
            except KeyError as e:
                logger.warning(f"Missing format argument {e} for key {content_key}")
                return translated
        
        return translated
    
    def format_analysis_results(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Format meta-analysis results with localization"""
        formatted = {}
        
        # Effect size
        if "pooled_effect" in results:
            effect = results["pooled_effect"]
            formatted["pooled_effect"] = f"{self.get_localized_content('pooled_estimate')}: {self.language_manager.format_number(effect)}"
        
        # Confidence interval
        if "ci_low" in results and "ci_high" in results:
            ci_low = self.language_manager.format_number(results["ci_low"])
            ci_high = self.language_manager.format_number(results["ci_high"])
            formatted["confidence_interval"] = f"{self.get_localized_content('confidence_interval')}: [{ci_low}, {ci_high}]"
        
        # P-value
        if "p_value" in results:
            p_val = results["p_value"]
            if p_val < 0.001:
                p_formatted = "< 0.001"
            else:
                p_formatted = self.language_manager.format_number(p_val)
            formatted["p_value"] = f"{self.get_localized_content('p_value')}: {p_formatted}"
        
        # Heterogeneity
        if "heterogeneity" in results:
            het = results["heterogeneity"]
            if "I2" in het:
                i2 = self.language_manager.format_number(het["I2"], 1)
                formatted["i_squared"] = f"{self.get_localized_content('i_squared')}: {i2}%"
        
        return formatted
    
    def create_accessible_report_html(self, results: Dict[str, Any],
                                    title: str = None) -> str:
        """Create accessible HTML report"""
        title = title or self.get_localized_content("meta_analysis")
        
        html = [
            '<!DOCTYPE html>',
            '<html lang="{}">'.format(self.language_manager.current_language),
            '<head>',
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'  <title>{title}</title>',
            '  <style>',
            self._get_accessible_css(),
            '  </style>',
            '</head>',
            '<body>',
            self.aria_helper.create_skip_links_html(),
            f'  <header role="banner">',
            f'    <h1 id="main-title">{title}</h1>',
            '  </header>',
            '  <main id="main-content" role="main" aria-labelledby="main-title">',
        ]
        
        # Add formatted results
        formatted_results = self.format_analysis_results(results)
        
        html.append('    <section aria-labelledby="results-title">')
        html.append(f'      <h2 id="results-title">{self.get_localized_content("results")}</h2>')
        
        for key, value in formatted_results.items():
            html.append(f'      <p>{value}</p>')
        
        html.append('    </section>')
        
        # Add keyboard shortcuts
        html.append(self.aria_helper.create_keyboard_shortcuts_help())
        
        html.extend([
            '  </main>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html)
    
    def _get_accessible_css(self) -> str:
        """Get accessible CSS styles"""
        return '''
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 16px;
            line-height: 1.5;
            color: #212529;
            background-color: #ffffff;
            margin: 0;
            padding: 20px;
        }
        
        .skip-link {
            position: absolute;
            left: -9999px;
            top: auto;
            width: 1px;
            height: 1px;
            overflow: hidden;
        }
        
        .skip-link:focus {
            position: static;
            width: auto;
            height: auto;
            background: #000;
            color: #fff;
            padding: 8px 16px;
            text-decoration: none;
            z-index: 1000;
        }
        
        h1, h2, h3 {
            color: #495057;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }
        
        h1 { font-size: 2em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.25em; }
        
        .keyboard-shortcuts {
            margin-top: 2em;
            padding: 1em;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        kbd {
            background: #f8f9fa;
            border: 1px solid #adb5bd;
            border-radius: 3px;
            padding: 2px 4px;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        dl dt {
            font-weight: bold;
            margin-top: 0.5em;
        }
        
        dl dd {
            margin-left: 2em;
            margin-bottom: 0.5em;
        }
        
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        
        @media (prefers-contrast: high) {
            body {
                background: #000;
                color: #fff;
            }
            
            h1, h2, h3 {
                color: #fff;
            }
        }
        '''
    
    def validate_accessibility(self, html_content: str) -> Dict[str, Any]:
        """Validate accessibility of HTML content"""
        return self.accessibility_checker.validate_html_accessibility(html_content)
    
    def get_accessibility_status(self) -> Dict[str, Any]:
        """Get overall accessibility status"""
        return {
            "language": {
                "current": self.language_manager.current_language,
                "supported": self.language_manager.get_supported_languages()
            },
            "features": {
                "screen_reader_support": self.config.enable_screen_reader,
                "keyboard_navigation": self.config.enable_keyboard_navigation,
                "high_contrast": self.config.enable_high_contrast,
                "large_text": self.config.enable_large_text
            },
            "wcag_compliance": {
                "level": "AA",
                "guidelines_followed": [
                    "Keyboard accessible",
                    "Screen reader compatible", 
                    "Color contrast compliant",
                    "Semantic HTML structure",
                    "ARIA landmarks and labels"
                ]
            }
        }

# Global accessibility manager
_global_accessibility: Optional[AccessibilityManager] = None

def initialize_accessibility(config: AccessibilityConfig = None) -> AccessibilityManager:
    """Initialize global accessibility manager"""
    global _global_accessibility
    _global_accessibility = AccessibilityManager(config)
    return _global_accessibility

def get_accessibility() -> Optional[AccessibilityManager]:
    """Get global accessibility manager"""
    return _global_accessibility

# Convenience functions
def translate(key: str, language: Optional[str] = None) -> str:
    """Convenience function for translation"""
    accessibility = get_accessibility()
    if accessibility:
        return accessibility.language_manager.translate(key, language)
    return key

def format_localized_number(number: float, decimal_places: int = 3) -> str:
    """Convenience function for number formatting"""
    accessibility = get_accessibility()
    if accessibility:
        return accessibility.language_manager.format_number(number, decimal_places)
    return f"{number:.{decimal_places}f}"