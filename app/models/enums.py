from enum import Enum


class VacancyStatus(str, Enum):
    NEW = "Nueva"
    NOTIFIED = "Notificada"
    APPLIED = "Aplicada"
    IGNORED = "Ignorada"


class RemoteType(str, Enum):
    ON_SITE = "Presencial"
    REMOTE = "Remoto"
    HYBRID = "Híbrido"
    UNKNOWN = "No especificado"
