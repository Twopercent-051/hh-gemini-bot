import base64

from config import config


def encode_pair() -> str:
    resume_ids = {"backend": config.hh.backend_resume_id, "devops": config.hh.devops_resume_id}
    for resume_id, resume_title in resume_ids.items():
        print(resume_id, resume_title, sep=":")


def decode_pair(encoded_data: str) -> tuple:
    decoded_data = base64.urlsafe_b64decode(encoded_data.encode()).decode()
    resume_id, vacancy_id = decoded_data.split(":")
    return resume_id, vacancy_id


# Пример использования
encoded = encode_pair()
print("Encoded:", encoded)
