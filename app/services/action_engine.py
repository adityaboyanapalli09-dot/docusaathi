from datetime import datetime, date


def parse_date(value):
    """
    Try to convert common date formats into a Python date.
    Returns None if the date cannot be understood.
    """

    if not value:
        return None

    value = str(value).strip()

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%B %d, %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%d %b %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None


def build_action_plan(document):

    actions = []

    # -----------------------------------------
    # 1. Check whether this document requires
    #    action from the person who uploaded it
    # -----------------------------------------

    if document.requires_user_action:

        for obligation in document.obligations:

            actor = obligation.get("actor", "unknown")
            action = obligation.get("action", "")

            if actor in {"beneficiary", "both"}:

                actions.append({
                    "action": action,
                    "priority": "normal",
                    "status": "to_do"
                })

    # -----------------------------------------
    # 2. Required documents
    # -----------------------------------------

    documents_to_keep_ready = []

    if document.requires_user_action:

        for item in document.required_documents:

            documents_to_keep_ready.append(item)

    # -----------------------------------------
    # 3. Important dates + overdue detection
    # -----------------------------------------

    deadlines = []

    today = date.today()

    for item in document.key_dates:

        parsed_date = parse_date(item.date)

        status = "upcoming"

        if parsed_date:

            if parsed_date < today:
                status = "overdue"

            elif parsed_date == today:
                status = "due_today"

            else:
                status = "upcoming"

        deadlines.append({
            "label": item.label,
            "date": item.date,
            "status": status
        })

        # -----------------------------------------
        # Automatically increase priority if a
        # deadline has already passed
        # -----------------------------------------

        if status == "overdue":

            actions.append({
                "action": f"{item.label}: {item.date}",
                "priority": "urgent",
                "status": "overdue"
            })

        elif status == "due_today":

            actions.append({
                "action": f"{item.label}: {item.date}",
                "priority": "urgent",
                "status": "due_today"
            })

    # -----------------------------------------
    # 4. Amounts
    # -----------------------------------------

    amounts = []

    for item in document.amounts:

        amounts.append({
            "label": item.label,
            "value": item.value
        })

    # -----------------------------------------
    # 5. Where to act
    # -----------------------------------------

    where_to_act = {
        "portal": document.where_to_act.portal,
        "office": document.where_to_act.office
    }

    # -----------------------------------------
    # 6. What to carry
    #
    # For now, this is based on the documents
    # explicitly mentioned by the document.
    # -----------------------------------------

    what_to_carry = []

    for item in documents_to_keep_ready:

        what_to_carry.append({
            "document": item,
            "status": "required"
        })

    # -----------------------------------------
    # 7. Consequence
    # -----------------------------------------

    consequence = document.consequence_if_ignored

    # -----------------------------------------
    # 8. Final action plan
    # -----------------------------------------

    if document.requires_user_action:

        summary = (
            f"This document is a {document.doc_type} "
            f"issued by {document.issuer}."
        )

    else:

        summary = (
            f"This document is a {document.doc_type} "
            f"issued by {document.issuer}. "
            f"It does not appear to require direct action from you."
        )

    # -----------------------------------------
    # 9. Sort actions
    #
    # urgent → normal
    # -----------------------------------------

    priority_order = {
        "urgent": 0,
        "normal": 1
    }

    actions.sort(
        key=lambda x: priority_order.get(
            x["priority"],
            2
        )
    )

    # -----------------------------------------
    # 10. Return complete action plan
    # -----------------------------------------

    return {

        "summary": summary,

        "audience": document.audience,

        "requires_user_action":
            document.requires_user_action,

        "actions": actions,

        "documents_to_keep_ready":
            documents_to_keep_ready,

        "what_to_carry":
            what_to_carry,

        "important_dates":
            deadlines,

        "amounts":
            amounts,

        "where_to_act":
            where_to_act,

        "if_ignored":
            consequence,

        "confidence":
            document.confidence.overall
    }