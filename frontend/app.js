const API_BASE = "http://127.0.0.1:8000";

const fileInput = document.getElementById("fileInput");
const cameraInput = document.getElementById("cameraInput");
const cameraButton = document.getElementById("cameraButton");
const uploadCard = document.getElementById("uploadCard");
const fileTitle = document.getElementById("fileTitle");
const fileHint = document.getElementById("fileHint");
const modeCards = [...document.querySelectorAll(".mode-card")];
const continueButton = document.getElementById("continueButton");
const continueText = document.getElementById("continueText");
const language = document.getElementById("language");
const result = document.getElementById("result");
const resultTitle = document.getElementById("resultTitle");
const resultBody = document.getElementById("resultBody");
const newDocument = document.getElementById("newDocument");
const loading = document.getElementById("loading");
const loadingTitle = document.getElementById("loadingTitle");
const loadingText = document.getElementById("loadingText");
const toast = document.getElementById("toast");

let selectedFile = null;
let selectedMode = "verify";


/* =========================================================
   TOAST
   ========================================================= */

function showToast(message) {

  if (!toast) return;

  toast.textContent = message;

  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 2600);

}


/* =========================================================
   FILE HANDLING
   ========================================================= */

function setFile(file) {

  if (!file) return;

  const allowed = [
    "application/pdf",
    "image/jpeg",
    "image/png"
  ];

  if (!allowed.includes(file.type)) {

    showToast(
      "Please choose a PDF, JPG or PNG."
    );

    return;
  }

  if (file.size > 20 * 1024 * 1024) {

    showToast(
      "That file is larger than 20 MB."
    );

    return;
  }

  selectedFile = file;

  if (fileTitle) {
    fileTitle.textContent = file.name;
  }

  if (fileHint) {
    fileHint.textContent =
      `${(file.size / 1024 / 1024).toFixed(2)} MB · ready to process`;
  }

  if (uploadCard) {
    uploadCard.classList.add("has-file");
  }

  if (continueButton) {
    continueButton.disabled = false;
  }

  if (continueText) {
    continueText.textContent =
      selectedMode === "verify"
        ? "Check this document"
        : "Understand this document";
  }

}


if (fileInput) {

  fileInput.addEventListener(
    "change",
    e => {
      setFile(e.target.files[0]);
    }
  );

}


if (cameraInput) {

  cameraInput.addEventListener(
    "change",
    e => {
      setFile(e.target.files[0]);
    }
  );

}


if (cameraButton && cameraInput) {

  cameraButton.addEventListener(
    "click",
    () => {
      cameraInput.click();
    }
  );

}


/* =========================================================
   MODE SELECTION
   ========================================================= */

modeCards.forEach(card => {

  card.addEventListener(
    "click",
    () => {

      modeCards.forEach(c => {
        c.classList.remove("selected");
        c.setAttribute("aria-pressed", "false");
      });

      card.classList.add("selected");
      card.setAttribute("aria-pressed", "true");

      selectedMode = card.dataset.mode;

      if (continueText) {

        if (!selectedFile) {
          continueText.textContent = "Select a document";
        } 
        else if (selectedMode === "verify") {
          continueText.textContent = "Check this document";
        } 
        else if (selectedMode === "understand") {
          continueText.textContent = "Understand this document";
        } 
        else if (selectedMode === "fill-form") {
          continueText.textContent = "Help me fill this form";
        }

      }

    }
  );

});


/* =========================================================
   DRAG & DROP
   ========================================================= */

if (uploadCard) {

  uploadCard.addEventListener(
    "dragover",
    e => {

      e.preventDefault();

      uploadCard.style.borderColor =
        "#7565df";

    }
  );


  uploadCard.addEventListener(
    "dragleave",
    () => {

      uploadCard.style.borderColor = "";

    }
  );


  uploadCard.addEventListener(
    "drop",
    e => {

      e.preventDefault();

      uploadCard.style.borderColor = "";

      setFile(
        e.dataTransfer.files[0]
      );

    }
  );

}


/* =========================================================
   LOADING
   ========================================================= */

function showLoading(title, text) {

  if (loadingTitle) {
    loadingTitle.textContent = title;
  }

  if (loadingText) {
    loadingText.textContent = text;
  }

  if (loading) {
    loading.classList.remove("hidden");
  }

}


function hideLoading() {

  if (loading) {
    loading.classList.add("hidden");
  }

}


/* =========================================================
   HELPERS
   ========================================================= */

   function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function prettyKey(key) {

  return String(key)
    .replaceAll("_", " ")
    .replace(/\b\w/g, c => c.toUpperCase());

}


function escapeHTML(value) {

  return String(value).replace(
    /[&<>"']/g,
    ch => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    }[ch])
  );

}


/* =========================================================
   DOCUMENT VERIFICATION
   ========================================================= */

function renderVerification(data) {

  const verification =
    data.verification || {};

  const status =
    verification.status || "uncertain";

  const checks =
    verification.checks || {};

  const warnings =
    verification.warnings || [];


  const statusLabel =
    status === "verified"
      ? "Looks official"
      : status === "suspicious"
        ? "Needs caution"
        : "Unable to fully verify";


  const displayChecks = [

    ["File type", checks.file_type],

    ["File structure", checks.file_structure],

    ["Document identity", checks.document_identity],

    ["Issuer", checks.issuer],

    ["Document number", checks.document_number],

    ["QR code", checks.qr_code],

    ["Digital signature", checks.digital_signature],

    ["Official source", checks.official_source]

  ].filter(
    ([, value]) =>
      value !== undefined &&
      value !== null
  );


  const formatValue = (key, value) => {

    const text = String(value);


    if (key === "File structure") {

      return text === "passed"
        ? "Passed"
        : text === "failed"
          ? "Failed"
          : prettyKey(text);

    }


    if (
      key === "QR code" ||
      key === "Digital signature"
    ) {

      return (
        text === "detected" ||
        text === "present"
      )
        ? "Present"
        : text === "not_present"
          ? "Not present"
          : text === "not_applicable"
            ? "Not applicable"
            : text === "not_checked"
              ? "Not checked"
              : prettyKey(text);

    }


    if (key === "Official source") {

      const labels = {

        official_domain_found:
          "Found",

        non_official_domain:
          "Non-official source",

        mixed_domains:
          "Mixed sources",

        not_found:
          "Not found",

        not_checked:
          "Not checked"

      };

      return (
        labels[text] ||
        prettyKey(text)
      );

    }


    return escapeHTML(text);

  };


  const checkHTML =
    displayChecks
      .map(
        ([key, value]) => `

          <div class="check">

            <span>
              ${escapeHTML(key)}
            </span>

            <b>
              ${formatValue(key, value)}
            </b>

          </div>

        `
      )
      .join("");


  const warningHTML =
    warnings.length

      ? `

        <div class="warning">

          ⚠

          ${warnings
            .map(w => escapeHTML(w))
            .join("<br>")}

        </div>

      `

      : `

        <div
          class="warning"
          style="
            background:#10211d;
            border-color:#1d4a3e;
            color:#8bd9c2
          "
        >

          ✓ No suspicious warning signals
          were found by the current checks.

        </div>

      `;


  return `

    <div class="status-card">

      <div class="status-row">

        <div
          class="status-badge status-${escapeHTML(status)}"
        >

          ${statusLabel}

        </div>


        <div>

          <strong>
            ${escapeHTML(
              data.filename || "Document"
            )}
          </strong>


          <div
            style="
              color:#747c8d;
              font-size:11px;
              margin-top:4px
            "
          >

            What DocuSaathi found while
            checking this document.

          </div>

        </div>

      </div>


      <div class="check-grid">

        ${checkHTML}

      </div>


      ${warningHTML}

    </div>

  `;

}


/* =========================================================
   DOCUMENT UNDERSTANDING
   ========================================================= */

function renderUnderstand(data) {

  const doc =
    data.document || {};

  const plan =
    data.action_plan || {};

  const dates =
    plan.important_dates || [];

  const amounts =
    plan.amounts || [];

  const actions =
    plan.actions || [];


  const actionsHTML =
    actions.length

      ? `

        <div class="action-list">

          ${actions
            .map(
              a => `

                <div class="action">

                  <strong>
                    ✓
                    ${escapeHTML(
                      a.action || "Action"
                    )}
                  </strong>


                  <small>

                    Priority:
                    ${escapeHTML(
                      a.priority || "normal"
                    )}

                    · Status:

                    ${escapeHTML(
                      a.status || "to do"
                    )}

                  </small>

                </div>

              `
            )
            .join("")}

        </div>

      `

      : `

        <div class="info-card">

          <div class="value">

            No direct user action
            was detected.

          </div>

        </div>

      `;


  const datesHTML =
    dates
      .map(
        d => `

          <div class="action">

            <strong>
              ${escapeHTML(
                d.label || "Date"
              )}
            </strong>


            <small>
              ${escapeHTML(
                d.date || ""
              )}
            </small>

          </div>

        `
      )
      .join("");


  const amountsHTML =
    amounts
      .map(
        a => `

          <div class="action">

            <strong>
              ${escapeHTML(
                a.label || "Amount"
              )}
            </strong>


            <small>
              ${escapeHTML(
                a.value || ""
              )}
            </small>

          </div>

        `
      )
      .join("");


  return `

    ${renderVerification(data)}


    <div class="summary-grid">

      <div class="info-card">

        <div class="label">
          Document type
        </div>

        <div class="value">

          ${escapeHTML(
            doc.doc_type ||
            "Not identified"
          )}

        </div>

      </div>


      <div class="info-card">

        <div class="label">
          Issuer
        </div>

        <div class="value">

          ${escapeHTML(
            doc.issuer ||
            "Not identified"
          )}

        </div>

      </div>


      <div class="info-card">

        <div class="label">
          What it means
        </div>

        <div class="value">

          ${escapeHTML(
            plan.summary ||
            "No summary returned."
          )}

        </div>

      </div>


      <div class="info-card">

        <div class="label">
          Where to act
        </div>

        <div class="value">

          ${escapeHTML(

            (
              plan.where_to_act &&
              (
                plan.where_to_act.portal ||
                plan.where_to_act.office
              )
            )

            || "Not specified"

          )}

        </div>

      </div>

    </div>


    <div class="summary-grid">

      <div class="info-card">

        <div class="label">
          Actions
        </div>

        ${actionsHTML}

      </div>


      <div class="info-card">

        <div class="label">
          Important dates
        </div>

        ${
          datesHTML ||
          '<div class="value">None detected</div>'
        }

      </div>

    </div>


    <div class="summary-grid">

      <div class="info-card">

        <div class="label">
          Amounts
        </div>

        ${
          amountsHTML ||
          '<div class="value">None detected</div>'
        }

      </div>


      <div class="info-card">

        <div class="label">
          If ignored
        </div>

        <div class="value">

          ${escapeHTML(
            plan.if_ignored ||
            "Not specified"
          )}

        </div>

      </div>

    </div>

  `;

}

/* =========================================================
   FORM FILLING ASSISTANT
   ========================================================= */

function renderFillForm(data) {

  const form = data?.form || {};
  const fields = Array.isArray(form.fields)
    ? form.fields
    : [];

  if (!fields.length) {
    return `
      <div class="form-helper">
        <div class="form-helper-header">
          <div>
            <div class="form-eyebrow">
              FORM FILLING ASSISTANT
            </div>

            <h2>No fillable fields detected</h2>

            <p>
              I couldn't identify any fields that need to be filled in this document.
            </p>
          </div>
        </div>
      </div>
    `;
  }

  /* =========================================================
     SECTION INFORMATION
     ========================================================= */

  const sectionDescriptions = {

    "1":
      "Enter your name exactly as it should appear on your PAN card.",

    "2":
      "Enter the abbreviated version of your name if required.",

    "3":
      "Complete this section only if you have been known by another name.",

    "4":
      "Select the gender applicable to the applicant.",

    "5":
      "Enter the applicable date requested by the form.",

    "6":
      "Provide the required details of your parents. Follow the form's instructions about the parent whose name should appear on the PAN card.",

    "7":
      "Enter the applicant's residential and office address details requested by the form.",

    "8":
      "Choose whether communication should be sent to the residence or office address.",

    "9":
      "Enter your telephone, mobile number and email details.",

    "10":
      "Select the status that applies to the applicant.",

    "11":
      "Enter the registration number when it applies to the applicant.",

    "12":
      "Enter the Aadhaar number or Aadhaar Enrolment ID and the name as per Aadhaar.",

    "13":
      "Select the applicable source of income. Enter the business or profession code when applicable.",

    "14":
      "Complete this section only when a Representative Assessee is applicable.",

    "15":
      "Provide the documents being submitted as proof of identity, address and date of birth.",

    "16":
      "Complete the declaration with the place and date requested by the form."
  };


  /* =========================================================
     HELPERS
     ========================================================= */

  function getSectionInfo(field) {

    const raw =
      String(field.section || "Other Information");

    const match =
      raw.match(/^(\d+)\.\s*(.*)$/);

    if (match) {

      return {
        number: match[1],
        name: match[2]
      };

    }

    return {
      number: "",
      name: raw
    };
  }


  function getExplanation(field) {

    const label =
      String(field.label || "").toLowerCase();


    if (
      label.includes("representative assessee") ||
      label.includes("(ra)")
    ) {

      return {
        what_is_it:
          "A Representative Assessee is a person who acts on behalf of the applicant for tax-related matters when applicable.",

        what_do_i_enter:
          "Enter the details of the person who is officially acting as the Representative Assessee.",

        where_can_i_find_it:
          "Use the official details of the person representing the applicant.",

        warning:
          "Do not complete this section unless a Representative Assessee is applicable."
      };
    }


    if (
      label.includes("aadhaar")
    ) {

      return {
        what_is_it:
          "This field asks for the applicant's Aadhaar number or Aadhaar Enrolment ID.",

        what_do_i_enter:
          "Enter the Aadhaar number or Enrolment ID exactly as shown on the relevant document.",

        where_can_i_find_it:
          "You can find it on your Aadhaar document or Aadhaar enrolment acknowledgement.",

        warning:
          "Check every digit carefully."
      };
    }


    if (
      label.includes("proof of identity") ||
      label.includes("poi")
    ) {

      return {
        what_is_it:
          "POI means Proof of Identity.",

        what_do_i_enter:
          "Enter or select the document being submitted as proof of identity.",

        where_can_i_find_it:
          "Use an identity document accepted by the form.",

        warning:
          ""
      };
    }


    if (
      label.includes("proof of address") ||
      label.includes("poa")
    ) {

      return {
        what_is_it:
          "POA means Proof of Address.",

        what_do_i_enter:
          "Enter or select the document being submitted as proof of address.",

        where_can_i_find_it:
          "Use an address document accepted by the form.",

        warning:
          ""
      };
    }


    if (
      label.includes("proof of date of birth") ||
      label.includes("pob")
    ) {

      return {
        what_is_it:
          "POB refers to Proof of Date of Birth.",

        what_do_i_enter:
          "Enter or select the document being submitted as proof of date of birth.",

        where_can_i_find_it:
          "Use an accepted document that establishes the applicant's date of birth.",

        warning:
          ""
      };
    }


    if (
      label === "place" ||
      label.includes("place")
    ) {

      return {
        what_is_it:
          "This is the place where the declaration is being completed or signed.",

        what_do_i_enter:
          "Enter the city or place where you are signing the declaration.",

        where_can_i_find_it:
          "Use the location where you are completing the declaration.",

        warning:
          ""
      };
    }


    if (
      label === "date" ||
      label.includes("date")
    ) {

      return {
        what_is_it:
          "This field asks for the relevant date required by the form.",

        what_do_i_enter:
          "Enter the correct day, month and year.",

        where_can_i_find_it:
          "Use the applicable official date requested by the form.",

        warning:
          "Check the date carefully before submitting."
      };
    }


    if (
      label.includes("capacity")
    ) {

      return {
        what_is_it:
          "Capacity means the role in which the person is signing the declaration.",

        what_do_i_enter:
          "Enter or select the capacity in which you are signing.",

        where_can_i_find_it:
          "Use the role that applies to the person signing the declaration.",

        warning:
          ""
      };
    }


    if (
      label.includes("ao code")
    ) {

      return {
        what_is_it:
          "AO Code identifies the Assessing Officer jurisdiction associated with the PAN application.",

        what_do_i_enter:
          "Enter the Area Code, AO Type, Range Code and AO Number required by the form.",

        where_can_i_find_it:
          "Use the official AO Code applicable to your jurisdiction.",

        warning:
          "Do not guess an AO Code."
      };
    }


    return {
      what_is_it:
        "This is information that the form asks the applicant to provide.",

      what_do_i_enter:
        "Enter the information requested by the field.",

      where_can_i_find_it:
        "Use your relevant official records or documents.",

      warning:
        ""
    };
  }


  /* =========================================================
     GROUP FIELDS INTO SECTIONS
     ========================================================= */

  const sections = [];
  const sectionMap = new Map();


  fields.forEach((field, index) => {

    const info =
      getSectionInfo(field);

    const key =
      info.number
        ? `section-${info.number}`
        : `section-${info.name}`;


    if (!sectionMap.has(key)) {

      const section = {

        key,

        number: info.number,

        name: info.name,

        fields: []

      };

      sectionMap.set(
        key,
        section
      );

      sections.push(
        section
      );
    }


    sectionMap
      .get(key)
      .fields
      .push({
        ...field,
        __index: index
      });

  });


  /* =========================================================
     INPUT RENDERING
     ========================================================= */

  function renderInput(field) {

    const index =
      field.__index;

    const id =
      `form-field-${index}`;

    const label =
      field.label || "Field";

    const type =
      String(
        field.type || "text"
      ).toLowerCase();

    const options =
      Array.isArray(field.options)
        ? field.options
        : [];


    /* SELECT */

    if (
      type === "select" ||
      type === "dropdown"
    ) {

      return `
        <select
          id="${id}"
          data-form-input="true"
        >

          <option value="">
            Select an option
          </option>

          ${options.map(option => `
            <option value="${escapeHtml(option)}">
              ${escapeHtml(option)}
            </option>
          `).join("")}

        </select>
      `;
    }


    /* RADIO */

    if (
      type === "radio"
    ) {

      return `
        <div class="form-options">

          ${options.map(
            (option, optionIndex) => {

              const optionId =
                `${id}-${optionIndex}`;

              return `
                <label
                  class="form-option"
                  for="${optionId}"
                >

                  <input
                    type="radio"
                    id="${optionId}"
                    name="field-${index}"
                    value="${escapeHtml(option)}"
                  >

                  <span>
                    ${escapeHtml(option)}
                  </span>

                </label>
              `;

            }
          ).join("")}

        </div>
      `;
    }


    /* CHECKBOX */

    if (
      type === "checkbox" ||
      type === "checkboxes"
    ) {

      return `
        <div class="form-options">

          ${options.map(
            (option, optionIndex) => {

              const optionId =
                `${id}-${optionIndex}`;

              return `
                <label
                  class="form-option"
                  for="${optionId}"
                >

                  <input
                    type="checkbox"
                    id="${optionId}"
                    name="field-${index}"
                    value="${escapeHtml(option)}"
                  >

                  <span>
                    ${escapeHtml(option)}
                  </span>

                </label>
              `;

            }
          ).join("")}

        </div>
      `;
    }


    /* DATE */

    if (
      type === "date"
    ) {

      return `
        <input
          type="date"
          id="${id}"
          data-form-input="true"
        >
      `;
    }


    /* EMAIL */

    if (
      type === "email"
    ) {

      return `
        <input
          type="email"
          id="${id}"
          data-form-input="true"
          placeholder="Enter ${escapeHtml(label)}"
        >
      `;
    }


    /* FILE */

    if (
      type === "file"
    ) {

      return `
        <input
          type="file"
          id="${id}"
          data-form-input="true"
        >
      `;
    }


    /* TEXTAREA */

    if (
      type === "textarea" ||
      type === "long_text"
    ) {

      return `
        <textarea
          id="${id}"
          data-form-input="true"
          rows="3"
          placeholder="Enter ${escapeHtml(label)}"
        ></textarea>
      `;
    }


    /* DEFAULT TEXT */

    return `
      <input
        type="text"
        id="${id}"
        data-form-input="true"
        placeholder="Enter ${escapeHtml(label)}"
      >
    `;
  }


  /* =========================================================
     FIELD RENDERING
     ========================================================= */

  function renderField(field) {

    const explanation =
      getExplanation(field);

    return `
      <div
        class="form-field-wrapper"
        data-form-field="${escapeHtml(field.id)}"
      >

        <div class="form-field">

          <div class="form-field-title">
            ${escapeHtml(field.label || "Field")}
          </div>

          ${renderInput(field)}

        </div>


        <div class="field-help">

          <div class="field-help-item">

            <div class="field-help-label">
              What is it?
            </div>

            <div>
              ${escapeHtml(
                explanation.what_is_it
              )}
            </div>

          </div>


          <div class="field-help-item">

            <div class="field-help-label">
              What do I enter?
            </div>

            <div>
              ${escapeHtml(
                explanation.what_do_i_enter
              )}
            </div>

          </div>


          <div class="field-help-item">

            <div class="field-help-label">
              Where can I find it?
            </div>

            <div>
              ${escapeHtml(
                explanation.where_can_i_find_it
              )}
            </div>

          </div>


          ${
            explanation.warning
              ? `
                <div
                  class="field-help-item field-help-warning"
                >

                  <div class="field-help-label">
                    ⚠️ Important
                  </div>

                  <div>
                    ${escapeHtml(
                      explanation.warning
                    )}
                  </div>

                </div>
              `
              : ""
          }

        </div>

      </div>
    `;
  }


  /* =========================================================
     NAVIGATION
     ========================================================= */

  const navigationHTML = `

    <div class="form-section-nav">

      ${sections.map(
        (section, index) => {

          const sectionId =
            `form-section-${index}`;

          return `
            <button
              type="button"
              class="form-section-nav-button ${
                index === 0
                  ? "active"
                  : ""
              }"
              data-section-target="${sectionId}"
            >

              ${
                section.number
                  ? `${section.number}. `
                  : ""
              }

              ${escapeHtml(
                section.name
              )}

            </button>
          `;

        }
      ).join("")}

    </div>

  `;


  /* =========================================================
     SECTIONS
     ========================================================= */

  const sectionsHTML =
    sections.map(
      (section, index) => {

        const sectionId =
          `form-section-${index}`;

        const description =
          sectionDescriptions[
            section.number
          ] || "";


        return `
          <section
            id="${sectionId}"
            class="form-section"
          >

            <div class="form-section-header">

              <div>

                <h3>

                  ${
                    section.number
                      ? `${section.number}. `
                      : ""
                  }

                  ${escapeHtml(
                    section.name
                  )}

                </h3>


                ${
                  description
                    ? `
                      <p>
                        ${escapeHtml(
                          description
                        )}
                      </p>
                    `
                    : ""
                }

              </div>

            </div>


            <div class="form-field-grid">

              ${section.fields
                .map(field =>
                  renderField(field)
                )
                .join("")}

            </div>

          </section>
        `;

      }
    ).join("");


  /* =========================================================
     FINAL UI
     ========================================================= */

  return `

    <div class="form-helper">

      <div class="form-helper-header">

        <div>

          <div class="form-eyebrow">
            FORM FILLING ASSISTANT
          </div>

          <h2>
            Let's fill this form together
          </h2>

          <p>
            I've identified the fields in your document.
            I'll explain what each field means,
            what you should enter and where you can
            find the information.
          </p>

        </div>


        <div class="form-total">

          ${fields.length}

          detected fields

        </div>

      </div>


      ${navigationHTML}


      <div class="form-sections">

        ${sectionsHTML}

      </div>


      <div class="form-review">

        <button
          type="button"
          class="form-review-button"
          id="review-form-answers"
        >
          Review my answers
        </button>


        <div
          id="form-answer-review"
          class="form-answer-review"
        ></div>

      </div>

    </div>

  `;
}

/* =========================================================
   FORM NAVIGATION + ANSWER REVIEW
   ========================================================= */

if (resultBody) {

  resultBody.addEventListener("click", event => {

    /* -------------------------------------------------------
       SECTION NAVIGATION
       ------------------------------------------------------- */

    const navButton =
      event.target.closest(
        ".form-section-nav-button"
      );

    if (navButton) {

      const targetId =
        navButton.dataset.sectionTarget;

      const target =
        document.getElementById(targetId);

      if (target) {

        document
          .querySelectorAll(
            ".form-section-nav-button"
          )
          .forEach(button => {
            button.classList.remove("active");
          });

        navButton.classList.add("active");

        target.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }

      return;
    }

    /* -------------------------------------------------------
       REVIEW ANSWERS
       ------------------------------------------------------- */

    const reviewButton =
      event.target.closest(
        "#review-form-answers"
      );

    if (!reviewButton) return;

    const reviewBox =
      document.getElementById(
        "form-answer-review"
      );

    if (!reviewBox) return;

    const fieldWrappers =
      resultBody.querySelectorAll(
        "[data-form-field]"
      );

    const answers = [];

    fieldWrappers.forEach(wrapper => {

      const label =
        wrapper
          .querySelector(
            ".form-field-title"
          )
          ?.textContent
          ?.trim();

      if (!label) return;

      /* RADIO */

      const checkedRadio =
        wrapper.querySelector(
          'input[type="radio"]:checked'
        );

      if (checkedRadio) {

        answers.push({
          label,
          value: checkedRadio.value
        });

        return;
      }

      /* CHECKBOXES */

      const checkedBoxes =
        wrapper.querySelectorAll(
          'input[type="checkbox"]:checked'
        );

      if (checkedBoxes.length) {

        answers.push({
          label,
          value: Array.from(
            checkedBoxes
          )
            .map(box => box.value)
            .join(", ")
        });

        return;
      }

      /* FILE */

      const fileInput =
        wrapper.querySelector(
          'input[type="file"]'
        );

      if (fileInput) {

        answers.push({
          label,
          value:
            fileInput.files.length
              ? fileInput.files[0].name
              : "No file selected"
        });

        return;
      }

      /* NORMAL INPUT */

      const input =
        wrapper.querySelector(
          "input:not([type='radio']):not([type='checkbox']):not([type='file']), select, textarea"
        );

      if (!input) return;

      const value =
        input.value.trim();

      answers.push({
        label,
        value:
          value || "Not filled"
      });
    });

    /* -------------------------------------------------------
       SHOW REVIEW
       ------------------------------------------------------- */

    reviewBox.innerHTML = `

      <div class="form-review-card">

        <h3>
          Answer Review
        </h3>

        <p>
          Check your answers before continuing.
        </p>

        <div class="form-review-list">

          ${
            answers.length
              ? answers.map(answer => `

                  <div class="form-review-item">

                    <div class="form-review-label">
                      ${escapeHtml(answer.label)}
                    </div>

                    <div class="form-review-value">
                      ${escapeHtml(answer.value)}
                    </div>

                  </div>

                `).join("")
              : `
                <div class="form-review-empty">
                  No answers entered yet.
                </div>
              `
          }

        </div>

      </div>

    `;

    reviewBox.scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });

  });

}


/* =========================================================
   DOCUMENT SUBMISSION
   ========================================================= */

async function submit() {

  if (!selectedFile) {

    showToast(
      "Choose a document first."
    );

    return;
  }


  // -----------------------------
  // CHOOSE BACKEND FLOW
  // -----------------------------

  const endpoint =

  selectedMode === "verify"

    ? "/verify"

    : selectedMode === "fill-form"

      ? "/fill-form"

      : "/process-document";

  const formData =
    new FormData();

  formData.append(
    "file",
    selectedFile
  );


  // -----------------------------
  // LOADING MESSAGE
  // -----------------------------

  if (selectedMode === "verify") {

    showLoading(
      "Checking your document",
      "Running verification checks…"
    );

  } else if (selectedMode === "understand") {

    showLoading(
      "Understanding your document",
      "Verifying first, then reading the document with Sarvam AI…"
    );

  } else if (selectedMode === "fill-form") {

    showLoading(
      "Looking for fields to fill",
      "Checking the document and finding anything you need to enter…"
    );

  }


  try {

    const response =
      await fetch(
        API_BASE +
        endpoint +
        (
  selectedMode === "verify" ||
  selectedMode === "fill-form"
    ? ""
    : "?language=" +
      encodeURIComponent(
        language.value
      )
      ),
        {
          method: "POST",
          body: formData
        }
      );


    const data =
      await response.json();


    if (!response.ok) {

      throw new Error(
        data.detail ||
        "The backend returned an error."
      );

    }


    // -----------------------------
    // SHOW RESULT
    // -----------------------------

    if (result) {
      result.classList.remove("hidden");
    }


    // -----------------------------
    // RESULT TITLE
    // -----------------------------

    if (resultTitle) {

      if (selectedMode === "verify") {

        resultTitle.textContent =
          "Verification result";

      } else if (selectedMode === "understand") {

        resultTitle.textContent =
          "Your document, simplified";

      } else if (selectedMode === "fill-form") {

        resultTitle.textContent =
          "Form filling assistant";

      }

    }


    // -----------------------------
    // RESULT CONTENT
    // -----------------------------

    if (resultBody) {

      if (selectedMode === "verify") {

        resultBody.innerHTML =
          renderVerification(data);

      }

      else if (selectedMode === "understand") {

        resultBody.innerHTML =
          renderUnderstand(data);

      }

     else if (selectedMode === "fill-form") {

  resultBody.innerHTML =
    renderFillForm(data);

    } 

    }


    // -----------------------------
    // SCROLL TO RESULT
    // -----------------------------

    if (result) {

      result.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });

    }


  } catch (error) {

    showToast(
      "Could not reach the backend. Make sure FastAPI is running."
    );

    console.error(error);


  } finally {

    hideLoading();

  }

}


if (continueButton) {

  continueButton.addEventListener(
    "click",
    submit
  );

}


/* =========================================================
   NEW DOCUMENT
   ========================================================= */

if (newDocument) {

  newDocument.addEventListener(
    "click",
    () => {

      selectedFile = null;

      if (fileInput) {
        fileInput.value = "";
      }

      if (cameraInput) {
        cameraInput.value = "";
      }


      if (fileTitle) {

        fileTitle.textContent =
          "Drop your document here";

      }


      if (fileHint) {

        fileHint.textContent =
          "PDF, JPG or PNG · up to 20 MB";

      }


      if (continueButton) {

        continueButton.disabled = true;

      }


      if (continueText) {

        continueText.textContent =
          "Select a document";

      }


      if (result) {

        result.classList.add(
          "hidden"
        );

      }


      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });

    }
  );

}


/* =========================================================
   GOVERNMENT SCHEMES
   ========================================================= */

async function loadSchemeCategories() {

  try {

    const response =
      await fetch(
        API_BASE +
        "/schemes/categories"
      );


    if (!response.ok) {

      throw new Error(
        "Could not load scheme categories."
      );

    }


    const data =
      await response.json();


    const categories =
      data.categories || [];


    /*
      Prevent duplicate Government Support
      sections if this function is called again.
    */

    const oldSection =
      document.querySelector(
        ".schemes-section"
      );

    if (oldSection) {
      oldSection.remove();
    }


    const section =
      document.createElement(
        "section"
      );


    section.className =
      "schemes-section";


    section.innerHTML = `

      <div class="schemes-heading">

        <div>

          <span class="eyebrow">
            GOVERNMENT SUPPORT
          </span>

          <h2>
            Find a government scheme
          </h2>

          <p>
            Browse schemes and programmes
            available across different areas.
          </p>

        </div>

      </div>


      <!-- SEARCH BAR -->

      <div class="scheme-search">

        <input
          type="text"
          id="schemeSearchInput"
          placeholder="Search schemes, benefits, eligibility..."
          aria-label="Search government schemes"
        />

        <button
          id="schemeSearchBtn"
          type="button"
        >
          Search
        </button>

      </div>


      <!-- CATEGORY CARDS -->

      <div class="scheme-categories">

        ${categories
          .map(
            category => `

              <button
                class="scheme-category"
                type="button"
                data-category="${escapeHTML(
                  category
                )}"
              >

                <span>
                  ${escapeHTML(
                    category
                  )}
                </span>

                <span class="arrow">
                  →
                </span>

              </button>

            `
          )
          .join("")}

      </div>


      <!-- SCHEME RESULTS -->

      <div
        id="schemeResults"
        class="scheme-results"
      ></div>

    `;


    const main =
      document.querySelector(
        "main"
      );


    if (main) {

      main.appendChild(
        section
      );

    } else {

      document.body.appendChild(
        section
      );

    }


    /*
      CATEGORY CLICK EVENTS
    */

    section
      .querySelectorAll(
        ".scheme-category"
      )
      .forEach(button => {

        button.addEventListener(
          "click",
          () => {

            loadSchemesByCategory(
              button.dataset.category
            );

          }
        );

      });


    /*
      SEARCH EVENTS
    */

    const searchInput =
      section.querySelector(
        "#schemeSearchInput"
      );

    const searchButton =
      section.querySelector(
        "#schemeSearchBtn"
      );


    if (searchButton) {

      searchButton.addEventListener(
        "click",
        performSchemeSearch
      );

    }


    if (searchInput) {

      searchInput.addEventListener(
        "keydown",
        event => {

          if (event.key === "Enter") {

            performSchemeSearch();

          }

        }
      );

    }


    /*
      Store section reference for search.
    */

    window.docuSaathiSchemeSection =
      section;


  } catch (error) {

    console.error(
      "Could not load scheme categories:",
      error
    );

  }

}


/* =========================================================
   SEARCH GOVERNMENT SCHEMES
   ========================================================= */

async function performSchemeSearch() {

  const section =
    window.docuSaathiSchemeSection;


  if (!section) return;


  const searchInput =
    section.querySelector(
      "#schemeSearchInput"
    );


  const results =
    section.querySelector(
      "#schemeResults"
    );


  if (!searchInput || !results) {
    return;
  }


  const query =
    searchInput.value.trim();


  if (!query) {

    showToast(
      "Type something to search."
    );

    return;
  }


  try {

    results.innerHTML = `

      <div class="scheme-empty">

        <h3>
          Searching...
        </h3>

        <p>
          Looking through government schemes.
        </p>

      </div>

    `;


    const response =
      await fetch(

        API_BASE +
        "/schemes/search?q=" +
        encodeURIComponent(
          query
        )

      );


    if (!response.ok) {

      throw new Error(
        "Scheme search failed."
      );

    }


    const data =
      await response.json();


    const schemes =
      data.schemes || [];


    if (!schemes.length) {

      results.innerHTML = `

        <div class="scheme-empty">

          <h3>
            No schemes found
          </h3>

          <p>
            Try a different scheme name,
            benefit or eligibility keyword.
          </p>

        </div>

      `;


      results.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });


      return;

    }


    results.innerHTML = `

      <div class="scheme-search-heading">

        <h3>
          Search results
        </h3>

        <p>
          ${schemes.length}
          scheme${schemes.length === 1 ? "" : "s"}
          found for
          “${escapeHTML(query)}”
        </p>

      </div>


      <div class="scheme-cards">

        ${schemes
          .map(
            (scheme, index) => `

              <article
                class="scheme-card"
                data-search-index="${index}"
              >

                <div class="scheme-card-top">

                  <span>

                    ${escapeHTML(
                      scheme.government_level ||
                      ""
                    )}

                  </span>

                </div>


                <h4>

                  ${escapeHTML(
                    scheme.name ||
                    ""
                  )}

                </h4>


                <p>

                  ${escapeHTML(
                    scheme.short_description ||
                    ""
                  )}

                </p>


                <strong>
                  Who is it for?
                </strong>


                <p>

                  ${escapeHTML(
                    scheme.who_is_it_for ||
                    ""
                  )}

                </p>


                <div class="scheme-open">

                  Explore this programme

                  <span>
                    →
                  </span>

                </div>

              </article>

            `
          )
          .join("")}

      </div>

    `;


    results
      .querySelectorAll(
        ".scheme-card"
      )
      .forEach(
        (card, index) => {

          card.addEventListener(
            "click",
            () => {

              showSchemeDetail(
                schemes[index],
                "Search results"
              );

            }
          );

        }
      );


    results.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });


  } catch (error) {

    console.error(
      "Could not search schemes:",
      error
    );


    results.innerHTML = `

      <div class="scheme-empty">

        <h3>
          Search unavailable
        </h3>

        <p>
          Could not connect to the scheme database.
        </p>

      </div>

    `;

  }

}


/* =========================================================
   LOAD SCHEMES IN A CATEGORY
   ========================================================= */

async function loadSchemesByCategory(
  category
) {

  try {

    const response =
      await fetch(

        API_BASE +
        "/schemes/category/" +
        encodeURIComponent(
          category
        )

      );


    if (!response.ok) {

      throw new Error(
        "Could not load schemes."
      );

    }


    const data =
      await response.json();


    const schemes =
      data.schemes || [];


    const section =
      window.docuSaathiSchemeSection;


    if (!section) return;


    const results =
      section.querySelector(
        "#schemeResults"
      );


    if (!results) return;


    results.innerHTML = `

      <div class="scheme-search-heading">

        <h3>
          ${escapeHTML(category)}
        </h3>

        <p>
          ${schemes.length}
          programmes available
        </p>

      </div>


      <div class="scheme-cards">

        ${schemes
          .map(
            (scheme, index) => `

              <article
                class="scheme-card"
                data-scheme-index="${index}"
              >

                <div class="scheme-card-top">

                  <span>

                    ${escapeHTML(
                      scheme.government_level ||
                      ""
                    )}

                  </span>

                </div>


                <h4>

                  ${escapeHTML(
                    scheme.name ||
                    ""
                  )}

                </h4>


                <p>

                  ${escapeHTML(
                    scheme.short_description ||
                    ""
                  )}

                </p>


                <strong>
                  Who is it for?
                </strong>


                <p>

                  ${escapeHTML(
                    scheme.who_is_it_for ||
                    ""
                  )}

                </p>


                <div class="scheme-open">

                  Explore this programme

                  <span>
                    →
                  </span>

                </div>

              </article>

            `
          )
          .join("")}

      </div>

    `;


    results
      .querySelectorAll(
        ".scheme-card"
      )
      .forEach(
        (card, index) => {

          card.addEventListener(
            "click",
            () => {

              showSchemeDetail(
                schemes[index],
                category
              );

            }
          );

        }
      );


    results.scrollIntoView({
      behavior: "smooth",
      block: "start"
    });


  } catch (error) {

    console.error(
      "Could not load schemes:",
      error
    );


    showToast(
      "Could not load schemes."
    );

  }

}


/* =========================================================
   INDIVIDUAL SCHEME / PROGRAMME
   ========================================================= */

function showSchemeDetail(
  scheme,
  category
) {

  const section =
    window.docuSaathiSchemeSection;


  if (!section) return;


  const results =
    section.querySelector(
      "#schemeResults"
    );


  if (!results) return;


  results.innerHTML = `

    <div class="scheme-detail">

      <button
        type="button"
        class="scheme-detail-back"
        id="schemeBackButton"
      >

        ← Back to
        ${escapeHTML(category)}

      </button>


      <div class="scheme-detail-level">

        ${escapeHTML(
          scheme.government_level ||
          "Government Programme"
        )}

      </div>


      <h3>

        ${escapeHTML(
          scheme.name ||
          ""
        )}

      </h3>


      <p class="scheme-detail-intro">

        ${escapeHTML(
          scheme.short_description ||
          ""
        )}

      </p>


      <div class="scheme-detail-grid">

        <div class="scheme-detail-box">

          <div class="label">
            Who is it for?
          </div>

          <div class="value">

            ${escapeHTML(
              scheme.who_is_it_for ||
              "Not specified"
            )}

          </div>

        </div>


        <div class="scheme-detail-box">

          <div class="label">
            Eligibility
          </div>

          <div class="value">

            ${escapeHTML(
              scheme.eligibility ||
              "Not specified"
            )}

          </div>

        </div>


        <div class="scheme-detail-box">

          <div class="label">
            Benefits
          </div>

          <div class="value">

            ${escapeHTML(
              scheme.benefits ||
              "Not specified"
            )}

          </div>

        </div>


        <div class="scheme-detail-box">

          <div class="label">
            How to apply
          </div>

          <div class="value">

            ${escapeHTML(
              scheme.how_to_apply ||
              "See official source"
            )}

          </div>

        </div>

      </div>


      <a
        class="scheme-detail-link"
        href="${escapeHTML(
          scheme.official_application_link ||
          "#"
        )}"
        target="_blank"
        rel="noopener noreferrer"
      >

        Visit official programme →

      </a>

    </div>

  `;


  const backButton =
    section.querySelector(
      "#schemeBackButton"
    );


  if (backButton) {

    backButton.addEventListener(
      "click",
      () => {

        if (category === "Search results") {

          /*
            Return to the main scheme section
            instead of creating another section.
          */

          const searchInput =
            section.querySelector(
              "#schemeSearchInput"
            );

          if (searchInput) {
            searchInput.value = "";
          }


          const results =
            section.querySelector(
              "#schemeResults"
            );

          if (results) {
            results.innerHTML = "";
          }


          section
            .querySelectorAll(
              ".scheme-category"
            )
            .forEach(card => {
              card.style.display = "";
            });


          section.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });


        } else {

          loadSchemesByCategory(
            category
          );

        }

      }
    );

  }


  results.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });

}


/* =========================================================
   START GOVERNMENT SCHEME SECTION
   ========================================================= */

loadSchemeCategories();