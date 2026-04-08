"""training/pdf_export.py – PDF daily synthesis export with fpdf2.

Generates a professional PDF with:
  - Header: title + date
  - Trainee info (prenom, niveau, session)
  - Course summary (from synthesis AI)
  - Quiz + WhatsApp scores
  - Score comparison (Jour 2+)
  - A faire demain (3 actions)
  - Progress bar (session/104)
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from fpdf import FPDF

from training.content import TOTAL_SESSIONS

# --- Constants ---
_ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = _ROOT / "data" / "pdfs"


def _sanitize(text: str) -> str:
    """Sanitize text for latin-1 PDF output (replace unsupported chars)."""
    replacements = {
        "\u2014": "-",   # em dash
        "\u2013": "-",   # en dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u00ab": '"',   # left guillemet
        "\u00bb": '"',   # right guillemet
        "\u2022": "-",   # bullet
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    # Encode to latin-1, replacing anything else
    return text.encode("latin-1", errors="replace").decode("latin-1")


class _SessionPDF(FPDF):
    """Custom FPDF subclass with header/footer for session synthesis."""

    def __init__(self, session_number: int, theme_title: str) -> None:
        super().__init__()
        self.set_margins(left=15, top=15, right=15)
        self.set_auto_page_break(auto=True, margin=15)
        self._session_number = session_number
        self._theme_title = _sanitize(theme_title)

    def header(self) -> None:
        eff_w = self.w - self.l_margin - self.r_margin
        self.set_font("Helvetica", "B", 16)
        self.set_x(self.l_margin)
        self.multi_cell(eff_w, 10, _sanitize("Synthese de session"), align="C")
        self.set_font("Helvetica", "", 10)
        self.set_x(self.l_margin)
        self.multi_cell(
            eff_w, 6,
            f"Session {self._session_number}/{TOTAL_SESSIONS} - {self._theme_title}",
            align="C",
        )
        self.set_x(self.l_margin)
        self.multi_cell(eff_w, 5, f"Date : {date.today().strftime('%d/%m/%Y')}", align="R")
        self.ln(4)
        # Separator line respecting margins
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def _eff_w(self) -> float:
        """Effective page width respecting left+right margins."""
        return self.w - self.l_margin - self.r_margin

    def section_title(self, title: str) -> None:
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(7, 94, 84)  # dark teal
        self.set_x(self.l_margin)
        self.multi_cell(self._eff_w(), 8, _sanitize(title))
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body_text(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        clean = _sanitize(text)
        self.set_x(self.l_margin)
        try:
            self.multi_cell(self._eff_w(), 6, clean)
        except Exception:
            self.set_x(self.l_margin)
            self.multi_cell(self._eff_w(), 6, clean[:400] + "...")
        self.ln(3)

    def bullet_list(self, items: list[str]) -> None:
        self.set_font("Helvetica", "", 10)
        for item in items:
            clean = _sanitize(item.lstrip("- "))
            if len(clean) > 500:
                clean = clean[:500] + "..."
            self.set_x(self.l_margin)
            try:
                self.multi_cell(self._eff_w(), 6, f"- {clean}")
            except Exception:
                self.set_x(self.l_margin)
                self.multi_cell(self._eff_w(), 6, f"- {clean[:200]}...")
        self.ln(2)

    def score_box(self, label: str, value: str) -> None:
        """Label en gras sur une ligne, valeur indentée sur la suivante si longue."""
        self.set_font("Helvetica", "B", 10)
        label_w = min(65, self.w - self.l_margin - self.r_margin)
        self.cell(label_w, 7, _sanitize(label), border=0)
        self.set_font("Helvetica", "", 10)
        val_clean = _sanitize(value)
        # Valeur courte : même ligne ; longue : multi_cell sur ligne suivante
        remaining_w = self.w - self.l_margin - self.r_margin - label_w
        if len(val_clean) <= 40:
            self.cell(remaining_w, 7, val_clean, new_x="LMARGIN", new_y="NEXT")
        else:
            self.ln()
            self.set_x(self.l_margin + 8)
            self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 6, val_clean)
        self.ln(1)

    def progress_bar(self, session_number: int, total: int) -> None:
        """Draw a visual progress bar."""
        self.section_title("Progression du parcours")
        pct = min(session_number / total, 1.0) if total else 0.0

        bar_x = 10
        bar_y = self.get_y()
        bar_w = 190
        bar_h = 8

        # Background
        self.set_fill_color(230, 230, 230)
        self.rect(bar_x, bar_y, bar_w, bar_h, "F")

        # Filled portion
        self.set_fill_color(7, 94, 84)
        self.rect(bar_x, bar_y, bar_w * pct, bar_h, "F")

        # Label
        self.set_xy(bar_x, bar_y)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(255, 255, 255)
        self.cell(bar_w, bar_h, f"Session {session_number}/{total} ({pct:.0%})", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(bar_h + 4)


def generate_session_pdf(
    session_number: int,
    theme_title: str,
    prenom: str,
    niveau: str,
    synthesis: Dict[str, str],
    quiz_data: Dict[str, Any],
    wa_data: Optional[Dict[str, Any]],
    is_jour1: bool,
) -> bytes:
    """Generate the daily session PDF.

    Returns:
        PDF content as bytes.
    """
    pdf = _SessionPDF(session_number, theme_title)
    pdf.add_page()

    # --- Trainee info ---
    pdf.section_title("Stagiaire")
    pdf.score_box("Prenom :", prenom or "Non renseigne")
    pdf.score_box("Niveau :", niveau or "Non renseigne")
    pdf.ln(2)

    # --- Course summary ---
    resume = synthesis.get("resume_cours", "")
    if resume:
        pdf.section_title("Resume du cours")
        pdf.body_text(resume)

    # --- Scores ---
    pdf.section_title("Scores de la session")

    if quiz_data:
        score = quiz_data.get("score", 0)
        total = quiz_data.get("total", 0)
        score_pct = quiz_data.get("score_pct", 0)
        speed = quiz_data.get("speed_bonuses", 0)
        pdf.score_box("Quiz :", f"{score}/{total} ({score_pct}%)")
        if speed:
            pdf.score_box("Bonus rapidite :", str(speed))
    else:
        pdf.score_box("Quiz :", "Non effectue")

    if not is_jour1:
        if wa_data and not wa_data.get("placeholder"):
            wa_score = wa_data.get("score", 0)
            pdf.score_box("WhatsApp :", f"{wa_score}/100")
            criteria = wa_data.get("criteria", [])
            for c in criteria:
                name = c.get("name", "?")
                cscore = c.get("score", 0)
                weight = c.get("weight", 0)
                pdf.score_box(f"  {name} :", f"{cscore}/10 (poids {weight}%)")
        else:
            pdf.score_box("WhatsApp :", "Non effectue")

    pdf.ln(2)

    # --- Comparison Jour 2+ ---
    if not is_jour1 and quiz_data and wa_data and not wa_data.get("placeholder"):
        pdf.section_title("Comparaison Quiz / WhatsApp")
        quiz_pct = quiz_data.get("score_pct", 0)
        wa_score = wa_data.get("score", 0)
        pdf.score_box("Quiz :", f"{quiz_pct}%")
        pdf.score_box("WhatsApp :", f"{wa_score}/100")
        if quiz_pct > wa_score:
            pdf.body_text(
                "Tu es plus a l'aise sur les connaissances (quiz) "
                "que sur la mise en pratique (WhatsApp). "
                "Travaille les mises en situation."
            )
        elif wa_score > quiz_pct:
            pdf.body_text(
                "Tu es plus a l'aise en situation (WhatsApp) "
                "qu'en connaissances pures (quiz). "
                "Revois les points cles du cours."
            )
        else:
            pdf.body_text(
                "Vos scores quiz et WhatsApp sont equilibres. Continuez comme ca."
            )

    # --- Points forts ---
    points_forts = synthesis.get("points_forts", "")
    if points_forts:
        pdf.section_title("Points forts")
        lines = [l.strip() for l in points_forts.split("\n") if l.strip()]
        if lines:
            pdf.bullet_list(lines)
        else:
            pdf.body_text(points_forts)

    # --- Axes d'amelioration ---
    axes = synthesis.get("axes_amelioration", "")
    if axes:
        pdf.section_title("Axes d'amelioration")
        lines = [l.strip() for l in axes.split("\n") if l.strip()]
        if lines:
            pdf.bullet_list(lines)
        else:
            pdf.body_text(axes)

    # --- A faire demain ---
    a_faire = synthesis.get("a_faire_demain", "")
    if a_faire:
        pdf.section_title("A faire demain")
        lines = [l.strip() for l in a_faire.split("\n") if l.strip()]
        if lines:
            pdf.bullet_list(lines)
        else:
            pdf.body_text(a_faire)

    # --- Progress bar ---
    pdf.progress_bar(session_number, TOTAL_SESSIONS)

    return bytes(pdf.output())


def generate_memo_pdf(theme_title: str, content: str) -> bytes:
    """Generate a simple PDF for a fiche mémo.

    Returns:
        PDF content as bytes.
    """
    pdf = FPDF()
    pdf.add_page()

    eff_w = pdf.w - pdf.l_margin - pdf.r_margin

    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(eff_w, 10, _sanitize("Fiche memo"), align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(eff_w, 7, _sanitize(theme_title), align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(eff_w, 5, f"Date : {date.today().strftime('%d/%m/%Y')}", align="R")
    pdf.ln(6)

    # Separator
    pdf.set_draw_color(200, 200, 200)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(6)

    # Content
    pdf.set_font("Helvetica", "", 10)
    for line in content.split("\n"):
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(eff_w, 5, _sanitize(line))
        pdf.ln(1)

    return bytes(pdf.output())


def save_pdf(pdf_bytes: bytes, session_number: int) -> Path:
    """Save PDF to data/pdfs/ and return the file path."""
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    filename = f"session_{session_number:03d}_{today}.pdf"
    path = PDF_DIR / filename
    path.write_bytes(pdf_bytes)
    return path
