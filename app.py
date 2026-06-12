import customtkinter as ctk
import threading
import pdfplumber
import groq
import tkinter as tk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_COLOR = "#000000"
CARD_COLOR = "#111111"
ACCENT_COLOR = "#FFFFFF"
ACCENT_HOVER = "#CCCCCC"
TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#888888"
BORDER_COLOR = "#2A2A2A"
SUCCESS_COLOR = "#AAAAAA"
WARNING_COLOR = "#888888"

ANALYSIS_PROMPT = """You are a medical billing expert. Analyze the following medical bill and provide:

1. **BILL BREAKDOWN**
   - List each charge with description and amount
   - Total billed amount
   - Insurance adjustments (if any)
   - Patient responsibility

2. **RED FLAGS** 🚩
   - Identify any suspicious, duplicate, or overcharged items
   - Highlight unbundling or upcoding concerns
   - Note any charges that seem unusually high
   - Flag any services that may not have been rendered

3. **DISPUTE LETTER**
   Write a professional dispute letter addressing the red flags found, ready to send to the billing department.

Here is the medical bill text:

"""

class MedicalBillAnalyzer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Medical Bill Analyzer")
        self.geometry("950x850")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)

        self.pdf_path = None
        self.is_analyzing = False

        self._build_ui()

    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(20, 0))

        ctk.CTkLabel(
            header_frame,
            text="⚕  Medical Bill Analyzer",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text="AI-powered billing review",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).pack(side="left", padx=(10, 0), pady=(6, 0))

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=24, pady=(14, 0))

        # API Key Card
        api_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12)
        api_card.pack(fill="x", padx=24, pady=(16, 0))

        ctk.CTkLabel(
            api_card,
            text="GROQ API KEY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", padx=16, pady=(14, 4))

        self.api_key_entry = ctk.CTkEntry(
            api_card,
            placeholder_text="Enter your Groq API key  •  Get one free at console.groq.com",
            show="•",
            height=40,
            fg_color="#000000",
            border_color=BORDER_COLOR,
            border_width=1,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_SECONDARY,
            font=ctk.CTkFont(size=13),
            corner_radius=8,
        )
        self.api_key_entry.pack(fill="x", padx=16, pady=(0, 14))

        # PDF Picker Card
        pdf_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12)
        pdf_card.pack(fill="x", padx=24, pady=(12, 0))

        ctk.CTkLabel(
            pdf_card,
            text="MEDICAL BILL PDF",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", padx=16, pady=(14, 4))

        pdf_row = ctk.CTkFrame(pdf_card, fg_color="transparent")
        pdf_row.pack(fill="x", padx=16, pady=(0, 14))

        self.pdf_label = ctk.CTkLabel(
            pdf_row,
            text="No file selected",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.pdf_label.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            pdf_row,
            text="Browse PDF",
            width=110,
            height=36,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=8,
            command=self._pick_pdf,
        ).pack(side="right")

        # Analyze Button
        self.analyze_btn = ctk.CTkButton(
            self,
            text="Analyze My Bill",
            height=48,
            fg_color=ACCENT_COLOR,
            hover_color=ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=10,
            command=self._start_analysis,
        )
        self.analyze_btn.pack(fill="x", padx=24, pady=(16, 0))

        # Progress bar (hidden initially)
        self.progress = ctk.CTkProgressBar(
            self,
            fg_color=CARD_COLOR,
            progress_color=ACCENT_COLOR,
            height=4,
            corner_radius=2,
        )
        self.progress.pack(fill="x", padx=24, pady=(8, 0))
        self.progress.set(0)
        self.progress.pack_forget()

        # Results Card
        result_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12)
        result_card.pack(fill="both", expand=True, padx=24, pady=(12, 0))

        result_header = ctk.CTkFrame(result_card, fg_color="transparent")
        result_header.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            result_header,
            text="ANALYSIS RESULT",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_SECONDARY,
        ).pack(side="left")

        self.copy_btn = ctk.CTkButton(
            result_header,
            text="Copy to Clipboard",
            width=130,
            height=28,
            fg_color="transparent",
            border_color=BORDER_COLOR,
            border_width=1,
            hover_color="#334155",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            corner_radius=6,
            command=self._copy_result,
        )
        self.copy_btn.pack(side="right")

        self.result_text = ctk.CTkTextbox(
            result_card,
            fg_color="#0F172A",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Courier", size=12),
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=8,
            wrap="word",
            scrollbar_button_color=BORDER_COLOR,
            scrollbar_button_hover_color=ACCENT_COLOR,
        )
        self.result_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.result_text.insert("1.0", "Your bill analysis will appear here after you upload a PDF and click Analyze.")
        self.result_text.configure(state="disabled")

        # Footer
        ctk.CTkLabel(
            self,
            text="Not a substitute for professional legal or medical advice",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_SECONDARY,
        ).pack(pady=(6, 12))

    def _pick_pdf(self):
        path = filedialog.askopenfilename(
            title="Select Medical Bill PDF",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if path:
            self.pdf_path = path
            filename = path.split("/")[-1].split("\\")[-1]
            display = filename if len(filename) <= 45 else "..." + filename[-42:]
            self.pdf_label.configure(text=display, text_color=SUCCESS_COLOR)

    def _start_analysis(self):
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("Missing API Key", "Please enter your Groq API key.")
            return
        if not self.pdf_path:
            messagebox.showwarning("No PDF Selected", "Please select a medical bill PDF first.")
            return

        self.is_analyzing = True
        self.analyze_btn.configure(text="Analyzing…", state="disabled")
        self.progress.pack(fill="x", padx=24, pady=(8, 0))
        self.progress.configure(mode="indeterminate")
        self.progress.start()

        self._set_result("Extracting text from PDF…")
        thread = threading.Thread(target=self._run_analysis, args=(api_key,), daemon=True)
        thread.start()

    def _run_analysis(self, api_key):
        try:
            text = self._extract_pdf_text()
            if not text.strip():
                self._finish("Could not extract text from this PDF. It may be a scanned image. Please try a text-based PDF.")
                return

            self._set_result("Sending to Groq AI for analysis…")

            client = groq.Groq(api_key=api_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": ANALYSIS_PROMPT + text,
                    }
                ],
                max_tokens=3000,
                temperature=0.3,
            )
            result = response.choices[0].message.content
            self._finish(result)

        except groq.AuthenticationError:
            self._finish("Authentication failed. Please check your Groq API key.")
        except groq.RateLimitError:
            self._finish("Rate limit reached. Please wait a moment and try again.")
        except Exception as e:
            self._finish(f"Error during analysis:\n\n{str(e)}")

    def _extract_pdf_text(self):
        text_parts = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)

    def _set_result(self, text):
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.configure(state="disabled")

    def _finish(self, result_text):
        self.after(0, lambda: self._update_ui_after_analysis(result_text))

    def _update_ui_after_analysis(self, result_text):
        self._set_result(result_text)
        self.analyze_btn.configure(text="Analyze My Bill", state="normal")
        self.progress.stop()
        self.progress.pack_forget()
        self.is_analyzing = False

    def _copy_result(self):
        self.result_text.configure(state="normal")
        content = self.result_text.get("1.0", "end").strip()
        self.result_text.configure(state="disabled")
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.copy_btn.configure(text="Copied!", text_color=SUCCESS_COLOR)
            self.after(2000, lambda: self.copy_btn.configure(text="Copy to Clipboard", text_color=TEXT_SECONDARY))


if __name__ == "__main__":
    app = MedicalBillAnalyzer()
    app.mainloop()