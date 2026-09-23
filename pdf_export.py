from fpdf import FPDF
import os

class KundliPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 20, 60)
        self.cell(0, 10, "AstroKundli - Birth Chart Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

def generate_kundli_pdf(filepath, name, place, dob_str, tob_str, tz_info,
                         ascendant, planets, houses, navamsa_result,
                         manglik_result, sadesati_result, lucky_info):
    pdf = KundliPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Name: {name}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Date of Birth: {dob_str}   Time: {tob_str}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Place: {place}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Timezone: {tz_info}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Ascendant (Lagna): {ascendant['sign']} {ascendant['degree']}°", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Planetary Positions", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    for planet, data in planets.items():
        r = " (R)" if data.get('retrograde') else ""
        pdf.cell(0, 6, f"  {planet}: {data['sign']} {data['degree']}°{r}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Houses (Bhavas)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    for h, data in houses.items():
        pdf.cell(0, 6, f"  House {h}: {data['sign']} {data['degree']}°", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Navamsa (D9) Ascendant: {navamsa_result['ascendant']}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    for planet, sign in navamsa_result['planets'].items():
        pdf.cell(0, 6, f"  {planet}: {sign}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Doshas & Notes", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"  Manglik Dosha: {'Yes' if manglik_result['is_manglik'] else 'No'} (Mars in house {manglik_result['mars_house']})", new_x="LMARGIN", new_y="NEXT")
    sade_text = f"Active - {sadesati_result['phase']}" if sadesati_result['is_active'] else "Not active"
    pdf.cell(0, 6, f"  Sade Sati: {sade_text}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    if lucky_info:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Lucky Info", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"  Numbers: {', '.join(map(str, lucky_info['number']))}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"  Color: {lucky_info['color']}   Day: {lucky_info['day']}", new_x="LMARGIN", new_y="NEXT")

    pdf.output(filepath)
    return filepath
