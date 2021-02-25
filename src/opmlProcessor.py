import re
from aqt.qt import *
from aqt.utils import showInfo
from .unicodeDecoder import unicodeDecoder
from .imageLocalizer import getMedia
from aqt import mw
import aqt


styles = {
	"codespan": "<code>¡¡¡</code>",
	"bold": "<b>¡¡¡</b>",
	"italic": "<i>¡¡¡</i>",
	"underline": "<u>¡¡¡</u>",
	"strikethrough": "<del>¡¡¡</del>",
	"tag": "¡¡¡",
	"formula": "\\(¡¡¡\\)",
	"text-color-red": "<label style = \"color: #DC3C36;\">¡¡¡</label>",
	"text-color-green": "<label style = \"color: #6DB24C;\">¡¡¡</label>",
	"text-color-yellow": "<label style = \"color: #D48830;\">¡¡¡</label>",
	"text-color-blue": "<label style = \"color: #408FF7;\">¡¡¡</label>",
	"text-color-purple": "<label style = \"color: #7660F6;\">¡¡¡</label>",
	"content-link-text": "¡¡¡"
}


def processOpml(fileContent: list) -> list:
	allNodes = []
	# progressBar = OPMLProgress(mw, len(fileContent))
	# progressNum = 0
	for line in fileContent:
		# progressNum = progressNum + 1
		matchObject = re.match(
			r"( *)<outline (?:_complete=\"true\" )?text=\"(.*?)\" _mubu_text=\"(.*?)\" _note=\"(.*?)\" _mubu_note=\"(.*?)\"( _heading=\"(\d+)\")?",
			line
		)
		if matchObject is not None:
			indentLevel = int(len(matchObject.group(1)) / 2 + 1)
			tagIters = re.finditer(r"#(\S+)", matchObject.group(2))
			tags = []
			for tagIter in tagIters:
				tags.append(tagIter.group(1))
			mainContent = getContent(matchObject.group(3))
			noteContent = getContent(matchObject.group(5))
			try:
				headingLevel = int(matchObject.group(7))
				if headingLevel == 4:
					headingLevel = -1
			except TypeError:
				headingLevel = -1
			allNodes.append({
				"il": indentLevel,
				"mc": mainContent,
				"nc": noteContent,
				"hl": headingLevel,
				"tg": tags
			})
		# progressBar.updateProgress(progressNum)
	return allNodes


def getContent(content: str) -> str:
	content = unicodeDecoder(content)
	content = content.replace("\n", "<br>")
	content = re.sub(r"<span>(.*?)</span>", r"\1", content)
	images = re.finditer(r"!\[(.*?)]\((?:<a class=.*?><span class=.*?>(\S+?)\)</span></a>)", content)
	for image in images:
		formattedImage = "<img alt=\"" + image.group(1) + "\" src = \"" + getMedia(image.group(2)) + "\" />"
		content = content.replace(image.group(), formattedImage)
	content = re.sub(r"<a(?:[^>]*?)href=(\"\S+\")(?:[^>]*?)>", r"<a href=\1>", content)
	allStyles = re.finditer(r"<span class=\"(.*?)\"(?: data-raw=\"(\S*?)\" contenteditable=\"false\")?>(.*?)</span>",
							content)
	for singleStyle in allStyles:
		singleStyleContents = singleStyle.group(1).split(" ")
		styleFormatter = "¡¡¡"
		for singleStyleContent in singleStyleContents:
			if singleStyleContent:
				styleFormatter = styleFormatter.replace("¡¡¡", styles[singleStyleContent])
		if singleStyleContents.count("tag") > 0:
			formattedContent = ""
		elif singleStyleContents.count("formula") > 0:
			formattedContent = styleFormatter.replace("¡¡¡", unicodeDecoder(singleStyle.group(2)))
			formattedContent = formattedContent.replace("{{", "{ {")
			formattedContent = formattedContent.replace("}}", "} }")
		else:
			formattedContent = styleFormatter.replace("¡¡¡", singleStyle.group(3))
		content = content.replace(singleStyle.group(), formattedContent)
	content = re.sub(r"((?:<br>|^)(?:<(?:[^>/]*?)>)*)\\\((.*?)\\\)((?:</(?:[^>]*?)>)*(?:<br>|$))", r"\1\\[\2\\]\3", content)
	content = re.sub(r"((?:<br>|^)(?:<(?:[^>/]*?)>)*)\\\((.*?)\\\)((?:</(?:[^>]*?)>)*(?:<br>|$))", r"\1\\[\2\\]\3", content)
	return content


# class OPMLProgress(QDialog):
# 	def __init__(self, mw, maxValue: int):
# 		super().__init__(mw)
# 		grid = QGridLayout(self)
# 		grid.setSpacing(10)
# 		self.progress = QProgressBar(self)
# 		grid.addWidget(QLabel("Processing OPML"), 0, 0)
# 		grid.addWidget(self.progress, 0, 1)
# 		self.progress.setMinimum(0)
# 		self.progress.setMaximum(maxValue)
# 		self.progress.setTextVisible(True)
# 		self.progress.setValue(0)
# 		self.maxValue = maxValue
# 		self.show()
# 		self.setFocus()
#
# 	def updateProgress(self, toValue: int):
# 		self.progress.setValue(toValue)
# 		self.progress.update()
# 		self.update()
# 		if toValue == self.maxValue:
# 			self.close()
# 			aqt.mw.setFocus()
