"""
Report Generator Module for TalentRank AI
Generates professional enterprise PDF reports using ReportLab and CSV summaries.
Includes Candidate Ranking Reports, Individual Candidate Deep Dives, and Skill Gap Overviews.
"""

import io
from typing import List, Dict, Any, Optional
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds professional page numbering and confidentiality footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header rule
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(40, 755, 572, 755)
        self.drawString(40, 760, "TalentRank AI — Candidate Screening Intelligence Report")

        # Footer
        self.line(40, 45, 572, 45)
        self.drawString(40, 32, "CONFIDENTIAL — STRICTLY FOR INTERNAL HIRING USE ONLY")
        self.drawRightString(572, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        self.title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=6
        )
        self.subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=14
        )
        self.section_heading = ParagraphStyle(
            'ReportSection',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=colors.HexColor('#0369a1'),
            spaceBefore=12,
            spaceAfter=8
        )
        self.body_style = ParagraphStyle(
            'ReportBody',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#1e293b')
        )
        self.body_bold = ParagraphStyle(
            'ReportBodyBold',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#0f172a')
        )

    def generate_candidate_ranking_pdf(
        self,
        job_title: str,
        company: str,
        ranked_candidates: List[Dict[str, Any]],
        session_date: str = "Today"
    ) -> bytes:
        """Generates a multi-page Candidate Ranking Report in PDF format."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=55,
            bottomMargin=55
        )

        story = []

        # Title Banner
        story.append(Paragraph(f"Candidate Ranking Report: {job_title}", self.title_style))
        story.append(Paragraph(f"Company: {company} | Screening Date: {session_date} | Total Screened: {len(ranked_candidates)}", self.subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=14))

        # Executive Summary Table
        strong_cnt = sum(1 for c in ranked_candidates if c.get("recommendation") == "Strong Match")
        good_cnt = sum(1 for c in ranked_candidates if c.get("recommendation") == "Good Match")
        partial_cnt = sum(1 for c in ranked_candidates if c.get("recommendation") == "Partial Match")
        review_cnt = sum(1 for c in ranked_candidates if c.get("recommendation") == "Needs Review")

        summary_data = [
            [
                Paragraph("<b>Total Candidates</b>", self.body_style),
                Paragraph("<b>Strong Matches (>=80%)</b>", self.body_style),
                Paragraph("<b>Good Matches (65-79%)</b>", self.body_style),
                Paragraph("<b>Partial Matches (45-64%)</b>", self.body_style),
                Paragraph("<b>Needs Review (&lt;45%)</b>", self.body_style)
            ],
            [
                Paragraph(f"<b>{len(ranked_candidates)}</b>", self.title_style),
                Paragraph(f"<b>{strong_cnt}</b>", self.title_style),
                Paragraph(f"<b>{good_cnt}</b>", self.title_style),
                Paragraph(f"<b>{partial_cnt}</b>", self.title_style),
                Paragraph(f"<b>{review_cnt}</b>", self.title_style)
            ]
        ]
        summary_table = Table(summary_data, colWidths=[105] * 5)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 16))

        # Main Candidate Table
        story.append(Paragraph("Ranked Candidates Breakdown", self.section_heading))

        headers = ["Rank", "Candidate Name", "Match Score", "Recommendation", "Req Skills", "Sim %", "Exp"]
        table_rows = [[Paragraph(f"<b>{h}</b>", self.body_bold) for h in headers]]

        for c in ranked_candidates:
            rec = c.get("recommendation", "Review")
            score = c.get("final_score", 0.0)

            rec_color = "#15803d" if rec == "Strong Match" else ("#0369a1" if rec == "Good Match" else ("#b45309" if rec == "Partial Match" else "#b91c1c"))

            req_matched_str = f"{len(c.get('matched_required', []))} Matched"
            exp_val = c.get("candidate_exp", c.get("experience", 0.0))

            table_rows.append([
                Paragraph(f"#{c.get('rank', '-')}", self.body_bold),
                Paragraph(c.get('candidate_name', 'Unknown')[:22], self.body_style),
                Paragraph(f"<b>{score:.1f}%</b>", self.body_bold),
                Paragraph(f"<font color='{rec_color}'><b>{rec}</b></font>", self.body_style),
                Paragraph(req_matched_str, self.body_style),
                Paragraph(f"{c.get('similarity_score', 0):.1f}%", self.body_style),
                Paragraph(f"{exp_val:.1f}y", self.body_style)
            ])

        cand_table = Table(table_rows, colWidths=[40, 140, 70, 95, 75, 55, 50])
        cand_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER')
        ]))
        story.append(cand_table)

        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_candidate_report_pdf(
        self,
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any],
        explanation: Dict[str, Any]
    ) -> bytes:
        """Generates an in-depth individual candidate profile and scorecard in PDF format."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=55,
            bottomMargin=55
        )

        story = []
        name = candidate_data.get("candidate_name", "Candidate Profile")
        final_score = candidate_data.get("final_score", 0.0)
        rec = candidate_data.get("recommendation", "Review")

        # Header Banner
        story.append(Paragraph(f"Candidate Intelligence Report: {name}", self.title_style))
        story.append(Paragraph(f"Target Role: {job_data.get('job_title', 'General')} | Status: {rec}", self.subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=14))

        # Profile Overview Table
        info_data = [
            [
                Paragraph("<b>Email:</b>", self.body_bold),
                Paragraph(candidate_data.get("email", "Not Found"), self.body_style),
                Paragraph("<b>Overall Match:</b>", self.body_bold),
                Paragraph(f"<b><font size='12' color='#0284c7'>{final_score:.1f}%</font></b>", self.body_bold)
            ],
            [
                Paragraph("<b>Phone:</b>", self.body_bold),
                Paragraph(candidate_data.get("phone", "Not Found"), self.body_style),
                Paragraph("<b>Recommendation:</b>", self.body_bold),
                Paragraph(f"<b>{rec}</b>", self.body_bold)
            ],
            [
                Paragraph("<b>Education:</b>", self.body_bold),
                Paragraph(candidate_data.get("education", "Not Specified"), self.body_style),
                Paragraph("<b>Experience:</b>", self.body_bold),
                Paragraph(f"{candidate_data.get('candidate_exp', candidate_data.get('experience', 0.0)):.1f} Years", self.body_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[80, 180, 100, 160])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 14))

        # Scorecard Breakdown
        story.append(Paragraph("Multi-Dimensional Score Breakdown", self.section_heading))
        score_data = [
            ["Metric", "Score", "Weight", "Contribution"],
            ["Required Skills Match", f"{candidate_data.get('skill_score', 0):.1f}%", "40%", f"{explanation['contributions'].get('Required Skills', 0):.1f} pts"],
            ["TF-IDF Text Similarity", f"{candidate_data.get('similarity_score', 0):.1f}%", "25%", f"{explanation['contributions'].get('Text Similarity', 0):.1f} pts"],
            ["Preferred Skills Match", f"{candidate_data.get('preferred_skill_score', 0):.1f}%", "15%", f"{explanation['contributions'].get('Preferred Skills', 0):.1f} pts"],
            ["Experience Alignment", f"{candidate_data.get('experience_score', 0):.1f}%", "10%", f"{explanation['contributions'].get('Experience', 0):.1f} pts"],
            ["Education Alignment", f"{candidate_data.get('education_score', 0):.1f}%", "5%", f"{explanation['contributions'].get('Education', 0):.1f} pts"],
            ["Keyword Relevance", f"{candidate_data.get('keyword_score', 0):.1f}%", "5%", f"{explanation['contributions'].get('Keyword Relevance', 0):.1f} pts"],
            ["Final Weighted Total", f"{final_score:.1f}%", "100%", f"{final_score:.1f} pts"]
        ]
        score_table = Table(score_data, colWidths=[180, 110, 110, 120])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8fafc')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0f2fe')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER')
        ]))
        story.append(score_table)
        story.append(Spacer(1, 14))

        # Explainability & Insights
        story.append(Paragraph("Explainable AI Insights & Decision Support", self.section_heading))
        story.append(Paragraph(f"<b>Key Takeaway:</b> {explanation.get('summary_narrative', '')}", self.body_style))
        story.append(Spacer(1, 8))

        # Strengths & Gaps
        sg_data = [
            [
                Paragraph("<b>Demonstrated Strengths</b>", self.body_bold),
                Paragraph("<b>Identified Skill & Qualification Gaps</b>", self.body_bold)
            ],
            [
                Paragraph("<br/>".join([f"• {s}" for s in explanation.get("strengths", [])]), self.body_style),
                Paragraph("<br/>".join([f"• {g}" for g in explanation.get("gaps", [])]), self.body_style)
            ]
        ]
        sg_table = Table(sg_data, colWidths=[260, 260])
        sg_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#ecfdf5')),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#fef2f2')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(sg_table)

        doc.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer.getvalue()


report_generator = ReportGenerator()
