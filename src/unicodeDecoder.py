from urllib.parse import unquote


def unicodeDecoder(text: str) -> str:
	text = unquote(text, "utf-8")
	return text
