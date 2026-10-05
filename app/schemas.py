from pydantic import BaseModel
from typing import List


class KeyDate(BaseModel):
    label: str
    date: str
    source: str


class Amount(BaseModel):
    label: str
    value: str
    source: str


class WhereToAct(BaseModel):
    portal: str
    office: str


class Confidence(BaseModel):
    overall: float
    low_fields: List[str]


class DocumentData(BaseModel):
    doc_type: str
    issuer: str
    audience: str
    requires_user_action: bool
    key_dates: List[KeyDate]
    amounts: List[Amount]
    obligations: List[dict]
    required_documents: List[str]
    consequence_if_ignored: str
    where_to_act: WhereToAct
    confidence: Confidence