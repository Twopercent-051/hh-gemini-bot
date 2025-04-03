from bs4 import BeautifulSoup
from pydantic import BaseModel, field_validator


def clean_text_with_bs4(text):
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text()
    return " ".join(clean.split())


class HhAuthModel(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"

    @staticmethod
    @field_validator("expires_in", mode="before")
    def adjust_expires_in(v):
        return int(v * 0.8) if v else 0


class HhResumeModel(BaseModel):
    id: str
    title: str
    description: str
    skills: list[str]

    @staticmethod
    @field_validator("skills", mode="before")
    def convert_list(v):
        if isinstance(v, list):
            return ", ".join(v) if v else ""
        return v if v else ""

    @staticmethod
    @field_validator("description", mode="before")
    def clean_description(v):
        return clean_text_with_bs4(v) if v else ""


class HhVacancyModel(BaseModel):
    id: int
    title: str
    employer: str
    description: str
    url: str

    @staticmethod
    @field_validator("title", mode="before")
    def clean_title(v):
        return clean_text_with_bs4(v) if v else ""

    @staticmethod
    @field_validator("description", mode="before")
    def clean_description(v):
        return clean_text_with_bs4(v) if v else ""
