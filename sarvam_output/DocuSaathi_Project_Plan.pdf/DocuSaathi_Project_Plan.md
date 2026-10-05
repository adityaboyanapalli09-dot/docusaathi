## DocuSaathi

Government document-to-action assistant, built on Sarvam AI

<table><tr><td>Hackathon track</td><td>Applied AI</td></tr><tr><td>Problem statement</td><td>PS 41: use at least one Sarvam API to solve a problem that matters</td></tr><tr><td>Duration</td><td>24 hours</td></tr><tr><td>One-line pitch</td><td>Photograph any confusing official document and get, in your own language and by voice, what it is, what you must do, and by when.</td></tr></table>

## 1. The problem

Official notices, bank letters, scheme forms and land records are dense and usually written in formal English or bureaucratic language. Millions of people in India cannot easily read them, so they miss deadlines, skip benefits or depend on middlemen. Most AI tools are built for English speakers, which leaves exactly these users behind.

## 2. The solution

DocuSaathi converts a photo or PDF of an official document into an action plan. It does not just translate. It answers three questions:

• What is this? The document type and who sent it.

• What do I have to do? A prioritized checklist of actions.

• By when, and what happens if I don't? Deadlines, amounts and consequences.

The answer is given in the user's language as text and as voice, and the user can ask follow-up questions by speaking.

## 3. Target users

• Elderly citizens and first-generation literate users who struggle with formal English.

• Rural and semi-urban users who prefer voice over typing.

• Small business owners handling tax, GST and bank notices.

• Family members and community workers helping others with paperwork.

Page 1

DocuSaathi | Applied AI | PS 41 (Sarvam API)

---

## 4. End-to-end workflow

Seven stages run in sequence. Each stage has a clear input and output, so team members can build and test them in parallel.

<table><tr><td>#</td><td>Stage</td><td>Input</td><td>Output</td></tr><tr><td>1</td><td>Input</td><td>Photo / PDF, language choice</td><td>Image or PDF in a session</td></tr><tr><td>2</td><td>Document reading</td><td>Image / PDF</td><td>Clean text with layout and page regions</td></tr><tr><td>3</td><td>Classification and extraction</td><td>Text</td><td>Structured JSON with confidence</td></tr><tr><td>4</td><td>Action engine</td><td>Structured JSON</td><td>Prioritized checklist</td></tr><tr><td>5</td><td>Plain-language explanation</td><td>Checklist and JSON</td><td>Simple explanation in user's language</td></tr><tr><td>6</td><td>Voice layer</td><td>Spoken question</td><td>Grounded spoken answer</td></tr><tr><td>7</td><td>Output and handoff</td><td>All results</td><td>Card view, PDF / WhatsApp-ready share, reminders</td></tr></table>

## 5. Stage-by-stage detail

<table><tr><td>STAGE 1</td><td>Input</td></tr><tr><td>What happens</td><td>The user uploads a photo or PDF, or forwards one from the phone. They choose a language, or the system detects it from their first voice question. A quality check warns about blur, glare or cut-off edges and asks for a retake.</td></tr><tr><td>Tech used</td><td>Web app (mobile first), image preprocessing (rotate, deskew, contrast).</td></tr><tr><td>Output</td><td>A clean document image tied to a session ID.</td></tr></table>

<table><tr><td>STAGE 2</td><td>Document reading</td></tr><tr><td>What happens</td><td>Extracts text, tables, stamps and layout from the scan. Handles low-quality phone photos and pages that mix English with a regional language. Keeps page and region references for later highlighting.</td></tr><tr><td>Tech used</td><td>Sarvam Vision (document intelligence).</td></tr><tr><td>Output</td><td>Clean text plus coordinates for each block.</td></tr></table>

<table><tr><td>STAGE 3</td><td>Classification and extraction</td></tr><tr><td>What happens</td><td>Identifies the document type (tax notice, scheme application, bank KYC letter, legal notice, utility bill, etc.) and fills a fixed schema. Each field carries a confidence level and the source snippet it came from.</td></tr><tr><td>Tech used</td><td>Sarvam chat model with a strict JSON schema prompt, plus code-based validation (regex for dates, amounts, IDs).</td></tr><tr><td>Output</td><td>Structured JSON (see schema in section 6).</td></tr></table>

Page 2

DocuSaathi | Applied AI | PS 41 (Sarvam API)

---

<table><tr><td>STAGE 4</td><td>Action engine</td></tr><tr><td>What happens</td><td>Converts extracted fields into a checklist: what to do (pay, reply, visit, submit), the deadline and consequence, documents to carry, and where to go. Ranks items by urgency. Rule-based checks run alongside the LLM, for example marking a past deadline as overdue.</td></tr><tr><td>Tech used</td><td>Sarvam chat model for reasoning, deterministic rules in code for dates and priorities.</td></tr><tr><td>Output</td><td>Ordered checklist with urgency labels.</td></tr></table>

<table><tr><td>STAGE 5</td><td>Plain-language explanation</td></tr><tr><td>What happens</td><td>Rewrites the content at a simple reading level in the user's language. Official terms are kept with a short meaning next to them so the user can still use them at the office.</td></tr><tr><td>Tech used</td><td>Sarvam chat model, Sarvam translation and transliteration for script handling.</td></tr><tr><td>Output</td><td>Short explanation and checklist in the chosen language.</td></tr></table>

<table><tr><td>STAGE 6</td><td>Voice layer</td></tr><tr><td>What happens</td><td>The user asks follow-ups by voice, for example "Can I pay this online?" or "What happens if I am late?". The answer is generated only from the document content, with a clear "not mentioned in this document" fallback, and is spoken back.</td></tr><tr><td>Tech used</td><td>Saaras (speech-to-text), Sarvam chat model with document-grounded prompting, Bulbul (text-to-speech).</td></tr><tr><td>Output</td><td>Spoken and written answer in the user's language.</td></tr></table>

<table><tr><td>STAGE 7</td><td>Output and handoff</td></tr><tr><td>What happens</td><td>Shows a card-style summary: document type, deadline, steps, documents. The user can share it as a WhatsApp-ready message or PDF with a family member. Optional deadline reminders. Documents are deleted after the session.</td></tr><tr><td>Tech used</td><td>Frontend rendering, PDF export, share links.</td></tr><tr><td>Output</td><td>Summary card, shareable file, optional reminder.</td></tr></table>

Page 3

DocuSaathi | Applied AI | PS 41 (Sarvam API)

---

## 6. Data schema (the backbone)

Every stage after reading works on this schema. Agreeing on it in the first two hours lets the whole team build in parallel.

```json
{"doc_type": "income_tax_notice", "issuer": "...", "key_dates": [ {"label": "Reply by", "date": "...", "source": "page1 line4"} ], "amounts": [ {"label": "Amount due", "value": "...", "source": "..."} ], "obligations": ["Respond to notice", "Pay difference"], "required_documents": ["PAN copy", "..."], "consequence_if_ignored": "...", "where_to_act": {"portal": "...", "office": "..."}, "confidence": {"overall": 0.0, "low_fields": []}}
```

## 7. System layout

<table><tr><td>Layer</td><td>Responsibility</td></tr><tr><td>Frontend</td><td>Mobile-friendly web app: upload, language selector, mic button, checklist view, highlighted original document.</td></tr><tr><td>Backend API</td><td>Pipeline orchestration (Vision, extraction, action engine, explanation, TTS) and session storage so follow-up questions keep context.</td></tr><tr><td>Sarvam services</td><td>Vision for reading, chat model for extraction and reasoning, Saaras for speech-to-text, Bulbul for text-to-speech, translation APIs.</td></tr><tr><td>Validation module</td><td>Code checks for dates, amounts and ID formats against the extracted text, to catch hallucinations.</td></tr><tr><td>Evaluation script</td><td>10 to 15 realistic documents with expected fields, producing accuracy numbers for the demo.</td></tr></table>

## 8. Trust and safety

• Evidence: every extracted field links to the highlighted region of the original document.

• Confidence flags: blurry scans or uncertain fields are marked instead of guessed.

• Grounded answers: follow-up answers use only the document, with a not-mentioned fallback.

- Not legal advice: the app explains documents and points users to the official office or helpline for decisions.

- **Privacy:** documents are not stored beyond the session and are deleted afterward; this is stated in the pitch.

Page 4

DocuSaathi | Applied AI | PS 41 (Sarvam API)

---

## 9. 24-hour build plan

<table><tr><td>Hours</td><td>Work</td></tr><tr><td>0-2</td><td>Lock scope, get API keys, finalize the JSON schema, collect 10 to 15 sample documents (include blurry phone photos).</td></tr><tr><td>2-10</td><td>Backend pipeline (reading, extraction, action engine, explanation) in parallel with the frontend shell and share/export.</td></tr><tr><td>10-16</td><td>Voice layer, evidence highlighting, second language, validation checks, error handling.</td></tr><tr><td>16-20</td><td>Integration, run the evaluation set, fix the weakest outputs.</td></tr><tr><td>20-24</td><td>Demo script, slides, backup recorded demo, README.</td></tr></table>

## 10. Scope

<table><tr><td>Must have</td><td>Nice to have</td><td>Skip</td></tr><tr><td>Upload to checklist to explanation in 2 languages Voice question and spoken answer Evidence highlighting on the original</td><td>WhatsApp-style share Deadline reminders Third language</td><td>User accounts Real government integrations Payments</td></tr></table>

## 11. Demo script (about 2 minutes)

• Show a dense English notice and explain who gets confused by it.

• Upload a phone photo and watch the checklist appear in the chosen language.

- Tap a requirement and show it highlighted on the original page.

• Ask a voice question in the local language and play the spoken answer.

• Close with the accuracy numbers from the test set.

## 12. Risks and mitigations

<table><tr><td>Risk</td><td>Mitigation</td></tr><tr><td>Poor OCR on bad photos</td><td>Test early with real phone pictures; add a retake prompt and preprocessing.</td></tr><tr><td>Hallucinated dates or amounts</td><td>Validate with code against the extracted text; show confidence flags.</td></tr><tr><td>Sensitive personal data</td><td>No storage beyond the session; delete after use; state this clearly.</td></tr><tr><td>Scope creep</td><td>Freeze features at hour 16; polish one flow instead of adding more.</td></tr><tr><td>Voice latency in demo</td><td>Pre-test audio, keep answers short, have a recorded backup.</td></tr></table>

## 13. Judging angles to highlight

- Clear user and real-world problem: citizens who cannot read official documents.

- Sarvam used where it matters: vision, speech, language and voice together.

- Measurable quality: accuracy on a test set, not just a nice demo.

• Responsible design: evidence, confidence flags, grounded answers, privacy.

Page 5

DocuSaathi | Applied AI | PS 41 (Sarvam API)