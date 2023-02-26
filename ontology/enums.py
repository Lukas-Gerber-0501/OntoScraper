from enum import Enum


class ImageTypes(Enum):
    PNG = ".png"
    JPG = ".jpg"
    JPEG = ".jpeg"
    GIF = ".gif"
    BMP = ".bmp"
    TIFF = ".tiff"
    TIF = ".tif"
    ICO = ".ico"
    SVG = ".svg"
    WEBP = ".webp"


class DocumentTypes(Enum):
    PDF = ".pdf"
    DOC = ".doc"
    DOCX = ".docx"
    ODT = ".odt"
    TXT = ".txt"
    XLS = ".xls"
    XLSX = ".xlsx"
    PPT = ".ppt"
    PPTX = ".pptx"
    CSV = ".csv"
    XML = ".xml"
    JSON = ".json"
    ZIP = ".zip"
    RAR = ".rar"


class VideoTypes(Enum):
    MP4 = ".mp4"
    WEBM = ".webm"
    OGG = ".ogg"
    AVI = ".avi"
    MOV = ".mov"
    WMV = ".wmv"
    FLV = ".flv"
    MKV = ".mkv"


class AudioTypes(Enum):
    MP3 = ".mp3"
    OGG = ".ogg"
    WAV = ".wav"
    FLAC = ".flac"


class OtherTypes(Enum):
    OTHER = "other"
