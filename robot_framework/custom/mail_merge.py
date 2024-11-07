from mailmerge import MailMerge
from robot_framework import config


def data_to_template(data: dict) -> dict:
    files_saved = {}
    with MailMerge('test/Welcome letter to internationals.docx', keep_fields="all") as document:
        print(f"Writing {len(data)} documents...")
        for cpr, name in data.items():
            files_saved[cpr] = write_document(name, cpr, document)
    return files_saved


def write_document(name: str, cpr: str, document: MailMerge) -> str:
    filename = f'{config.SAVE_FOLDER}/{cpr}.docx'
    document.merge(Fornavn=name,
                   CPR=cpr)
    document.write(filename)
    return filename
