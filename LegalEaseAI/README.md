# LegalEase

## AI-Powered Legal Document Generator

LegalEase is an AI-powered application for generating customizable legal
documents such as contracts, agreements, NDAs, lease agreements and
employment-related documents.

The application uses:

- Streamlit for the frontend
- FastAPI for the backend
- Google Gemini for AI generation
- python-docx for DOCX generation
- fpdf2 for PDF generation
- TXT export for plain-text documents

---

## Project Architecture

```text
User
  |
  v
Streamlit Frontend
  |
  v
FastAPI Backend
  |
  v
Gemini AI Generator
  |
  v
Generated Legal Document
  |
  +------> TXT
  |
  +------> DOCX
  |
  +------> PDF