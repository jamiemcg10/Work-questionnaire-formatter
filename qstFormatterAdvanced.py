import re

## DEFINE FUNCTION TO ADD SCALE OPTIONS TO SCALE QUESTIONS
def scaleQ(text,nextText,file):
	scale = re.search('\d-\d+\sscale',text)
	if scale:
		print nextText
		#print "match: " + scale.group()
		match = scale.group()
		sStart = int(match[:1])
		sEnd = int(match[match.find("-")+1:match.find(" ")])
		if nextText.lower().find("familiar") == -1:
			for i in range(sStart,sEnd+1):
				file.write(str(i)+"\n")
		if re.match('[a-z]\.',nextText) is not None or re.match('a-z\)',nextText) is not None or text.find("on the following") >=0:
			#print nextText	## FOR TESTING
			file.write("\n")
			file.write("[[Answers]]\n")	


## IMPORT TKINTER AND OPEN WINDOW TO SELECT QST OR PROMPT FOR FILE NAME OF PLAIN TEXT QST
try:
	from Tkinter import Tk
	from tkFileDialog import askopenfilename

	## OPEN FILE DIRECTORY
	Tk().withdraw()
	qstFileName = askopenfilename(title="Please select your .txt questionnaire...")
except ImportError:
	qstFileName = raw_input("Please enter the full path and name of your .txt questionnaire without using quotation marks.\nExample: C:\Users\Jamie Smart\Documents\questionnaire.txt\nQuestionnaire location: ")


## CREATE NEW TEXT FILE FOR QST. PROMPT FOR A VALID FILE NAME IF THE FILE NAME GIVEN CAN'T BE OPENED.
try:
	file = open(qstFileName,"r+")
except:
	invalid = True
	while invalid:
		invalid = False
		qstFileName = raw_input("Please enter a valid file name. Remember to include the file extension.\nExample: C:\Users\Jamie Smart\Documents\questionnaire.txt\nQuestionnaire location: ")
		try:
			file = open(qstFileName,"r+")
		except:
			invalid = True


## CREATE AND OPEN FILE FOR FORMATTED QST
print "PROCESSING QUESTIONNAIRE..."
newFileName = qstFileName[:-4] + "_FORMATTED FOR QUALTRICS-ADVANCED.txt"
newFile = open(newFileName,"w")


## SPECIFY ADVANCED FORMAT FILE
newFile.write("[[AdvancedFormat]]\n\n")

## INITIALIZE BEGINNING EMBEDDED DATA VARIABLES
newFile.write("[[ED:Marker:0]]\n")
newFile.write("[[ED:Halfway_point:0]]\n")
newFile.write("[[ED:UserAgent]]\n")
newFile.write("[[ED:Q_TotalDuration]]\n")

## CREATE FIRST BLOCK AND COUNTER FOR INTRO VARIABLES
newFile.write("\n[[Block:Introduction]]\n[[Question:DB]]\n[[ID:INTRO1]]\n")
introCount = 2

## ITERATE THROUGH THE LINES IN THE QST AND SAVE TO A LIST
qstList = []
for line in file.readlines():
	qstList.append(line)
#print qstList ## FOR TESTING


## ITERATE THROUGH THE QST LIST
for i in range(0,len(qstList)):
	txt = qstList[i].lstrip()
	## SAVE NEXT LINE TEXT IN A VARIABLE
	try:
		nextTxt = qstList[i+1]
		if nextTxt == "\n":
			nextTxt = qstList[i+2]
	except IndexError:
		nextTxt = qstList[i]


	## ESCAPE LOOP AND END QST BEFORE DEMOGRAPHIC QUESTIONS.
	if txt.lower()[:24] == "these last few questions" or txt.lower()[:12] == "demographics":
		print "QUESTIONNAIRE PROCESSING COMPLETE"
		break

	## REMOVE THE MUST ANSWER INSTRUCTION AND LOGIC ENCLOSED IN BRACKETS
	if txt.lower()[:11] == "must answer" or txt.lower()[:12] == "must answer:" or txt[:1] == "[":
		pass
	else:
		print txt 

		## REGEX FOR QUESTIONS
		newQ = re.match('\d(?=.)', txt) ## MATCHES NUMBERS FOLLOWED BY A PERIOD 
		## REGEX FOR ANSWERS
		newL1 = re.match('[a-z]+\.', txt) ## MATCHES LETTERS FOLLOWED BY A PERIOD
		newL2 = re.match('[a-z]+\)', txt) ## MATCHES LETTERS FOLLOWED BY A PARENTHESIS
		newL3 = re.match('\W',txt) ## MATCHES NON-ALPHANUMERIC CHARACTERS

		## CREATE NEW QUESTIONS
		if newQ:
			sliderQ = 0
			textQ = 0
			qNumber = txt[:txt.find(".")]
			newFile.write("\n")	
			## MARK MULTIPLE ANSWER QUESTIONS
			if txt.lower().find("select all that apply.") >= 0 or txt.find("select up to") >= 0:
				newFile.write("[[Question:MC:MultipleAnswer]]\n")
			## MARK CONSTANT SUM QUESTIONS
			elif txt.find("Please sum") >= 0:
				newFile.write("[[Question:ConstantSum]]\n")
			## MARK TEXT ENTRY QUESTIONS
			elif txt.find("numeric characters") >= 0 or nextTxt.lower().find("open-ended") >= 0:
				newFile.write("[[Question:TextEntry]]\n")
				textQ = 1
			## IDENTIFY SLIDER QUESTIONS (WILL NOT MARK IN QST)
			elif nextTxt.lower().find("slider") >= 0:
				newFile.write("[[Question:DB]]\n")
				sliderQ = 1
			## MARK SOME MATRIX QUESTIONS
			elif txt.find("on the following attributes") >= 0 and txt.find("scale where") >=0:
				newFile.write("[[Question: Matrix]]\n")
			else:
				newFile.write("[[Question:MC]]\n")
			newFile.write("[[ID:Q%s]]\n" %(qNumber))
			newFile.write(txt[txt.find('.')+1:].lstrip()+"\n")
		
			if not sliderQ and not textQ:
				newFile.write("[[Choices]]\n")
				scaleQ(txt,nextTxt,newFile)			


		## REMOVE VARIOUS BULLETS FROM BEGINNING OF LINE AND WRITE RESPONSE OPTION TO FORMATTED FILE
		elif txt[:1] == "*" or txt[:1] == "-":
			newFile.write(txt[1:].lstrip())		
		elif newL1:
			newFile.write(txt[newL1.end():].lstrip())
		elif newL2:
			newFile.write(txt[newL2.end():].lstrip()) 
		elif newL3:
			newFile.write(txt[3:].lstrip())	


		## CREATES NEW BLOCKS USING KEY WORDS
		elif txt.lower().find("the following questions") >=0:		
			newFile.write("\n[[Block]]\n[[Question:DB]]\n[[ID:INTRO%d]]\n%s" %(introCount,txt))
			introCount += 1
		elif txt.lower().find("in this section") >=0:		
			newFile.write("\n[[Block]]\n[[Question:DB]]\n[[ID:INTRO%d]]\n%s" %(introCount,txt))
			introCount += 1
		elif txt.lower().find("like to ask") >=0:		
			newFile.write("\n[[Block]]\n[[Question:DB]]\n[[ID:INTRO%d]]\n%s" %(introCount,txt))
			introCount += 1
		elif txt.lower().find("section") >=0:		
			newFile.write("\n[[Block]]\n%s"%(txt))	
	
		## INSERTS BLANK LINE BETWEEN QUESTIONS AND ANSWER CHOICES FOR MATRIX QUESTIONS
		elif txt.lower().find("answer choices") >=0:
			newFile.write("\n")
		else: 
			pass
			#newFile.write(txt) ## WRITE LINE TO FILE IF NONE OF THE ABOVE CRITERIA ARE MET





## SAVE AS .TXT FILE.
file.close()
newFile.close()
