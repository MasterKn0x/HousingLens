import io
import datetime
from fpdf import FPDF

def format_lkr(val):
    """Format large numbers into Millions (M) for the PDF."""
    if val >= 1_000_000:
        return f"Rs {val/1_000_000:.2f}M"
    return f"Rs {val:,.0f}"

class HousingLensPDF(FPDF):
    def header(self):
        # Brand Header
        self.set_font("helvetica", "B", 22)
        self.set_text_color(14, 165, 233)  # Sky blue variant
        self.cell(0, 10, "HousingLens", border=0, new_x="LMARGIN", new_y="NEXT", align="C")
        
        self.set_font("helvetica", "I", 11)
        self.set_text_color(100, 116, 139) # Slate 500
        self.cell(0, 6, "AI Property Valuation Platform - Scenario Report", border=0, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Page {self.page_no()}", border=0, align="C")

def generate_scenario_pdf(base_data, base_price, base_iri, mod_data, mod_price, mod_iri, price_delta, pct_change):
    """
    Generates a PDF using fpdf2 containing side-by-side scenario data.
    Returns the PDF as a byte string.
    """
    pdf = HousingLensPDF()
    pdf.add_page()
    
    # Metadata
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 6, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", border=0, new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(5)

    # ── DELTA SUMMARY ──
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 10, "Snapshot: Delta Analysis", border=0, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    dir_word = "Gain" if price_delta >= 0 else "Loss"
    pdf.set_text_color(52, 211, 153) if price_delta >= 0 else pdf.set_text_color(248, 113, 113)
    
    pdf.cell(0, 8, f"Net Value {dir_word}: {format_lkr(abs(price_delta))} ({pct_change:.1f}%)", border=0, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 8, f"Base IRI: {base_iri}/100  ->  Mod IRI: {mod_iri}/100", border=0, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # Helper for rendering tables
    def render_scenario_table(title, data, price, iri):
        pdf.set_font("helvetica", "B", 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, title, border=0, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(14, 165, 233)
        pdf.cell(0, 8, f"Predicted Value: {format_lkr(price)} (IRI: {iri}/100)", border=0, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(71, 85, 105)
        
        for k, v in data.items():
            pdf.cell(60, 8, str(k), border=1, fill=True)
            pdf.cell(130, 8, str(v), border=1, new_x="LMARGIN", new_y="NEXT")
            
        pdf.ln(8)

    # ── BASE SCENARIO ──
    render_scenario_table("Base Scenario", base_data, base_price, base_iri)

    # ── MODIFIED SCENARIO ──
    render_scenario_table("What-If Scenario", mod_data, mod_price, mod_iri)

    return bytes(pdf.output())
