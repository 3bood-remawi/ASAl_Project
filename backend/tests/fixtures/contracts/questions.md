# Retrieval Eval Q&A (Task 853)

Plain-language questions with expected answers, drawn from the fixtures in
this directory. Seed set for retrieval evaluation - checks whether the
system finds the right contract and returns the right answer.

1. **File**: `ECsample.pdf`
   **Q**: What is the minimum rest day entitlement for the employee?
   **A**: Not less than 1 rest day in every period of 7 days.

2. **File**: `ECsample.pdf`
   **Q**: What is the minimum notice period for terminating the employment contract?
   **A**: Not less than 7 days, or an equivalent amount of payment in lieu of notice . 
3. **File**: `ECsample-scan.pdf`
   **Q**: Can the system extract text from this contract?
   **A**: No - it's a scanned, image-only PDF with no text layer, so it should trigger the "not supported yet" / OCR-required error path instead of returning extracted text.

4. **File**: `Example-Mutual-Non-Disclosure-Agreement.pdf`
   **Q**: What must the Recipient do with Confidential Information if the other party asks for it back?
   **A**: Return all copies and records of it, and not retain any.

5. **File**: `Example-Mutual-Non-Disclosure-Agreement.pdf`
   **Q**: Which law governs this NDA, and where are disputes handled?
   **A**: English law, with non-exclusive jurisdiction of the English Courts.

6. **File**: `NDA__contractors__draft.pdf`
   **Q**: Who are the two parties to this NDA?
   **A**: Highways England Company Limited (HECL) and the contractor named in the agreement.

7. **File**: `NDA__contractors__draft.pdf`
   **Q**: Is the receiving party allowed to send Confidential Information outside the UK?
   **A**: No - the agreement prohibits transferring Confidential Information outside the United Kingdom.

8. **File**: `g-cloud-8-framework-agreement.pdf`
   **Q**: How many service Lots does the G-Cloud 8 framework cover, and what are they?
   **A**: Four - Infrastructure as a Service (IaaS), Platform as a Service (PaaS), Software as a Service (SaaS), and Specialist Cloud Services.

9. **File**: `g-cloud-8-framework-agreement.pdf`
   **Q**: What is the maximum duration of a Call-Off Contract under this framework?
   **A**: 24 months.

10. **File**: `g-cloud-8-framework-agreement.pdf`
    **Q**: What Management Charge rate does the Supplier pay CCS?
    **A**: Up to 1% of Charges invoiced to Buyers, currently set at 0.5%.

11. **File**: `scottish-government-model-private-residential-tenancy-agreement-private-rented-sector.pdf`
    **Q**: How much notice must a tenant give to end the tenancy?
    **A**: At least 28 days' written notice.

12. **File**: `scottish-government-model-private-residential-tenancy-agreement-private-rented-sector.pdf`
    **Q**: How much notice must the landlord give if the tenant has lived there over six months and the eviction ground isn't a "behaviour" ground?
    **A**: 84 days' notice.

13. **File**: `scottish-government-model-private-residential-tenancy-agreement-private-rented-sector.pdf`
    **Q**: What is the maximum deposit a landlord can charge?
    **A**: No more than two months' rent.

14. **File**: `dz-agreement-037-nara-dickinson-signed.pdf`
    **Q**: How long does this digitization agreement last?
    **A**: Five years, or one year after completion of any Project Plan, whichever is longer - then it auto-renews for additional one-year periods.

15. **File**: `dz-agreement-037-nara-dickinson-signed.pdf`
    **Q**: What is the standard image resolution assumed for digitization projects?
    **A**: 300ppi is the assumed resolution, although NARA may require a different ppi depending on the project and records.
