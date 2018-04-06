import os
import time
import json
import sys
import shutil

global propertiesFile
global deployModules
global defsDeploy

propertiesFile = "pyBuild.properties"
deployModules = ['frontend.ear', 'webservice.ear']
#modulesMaxLen = max([len(f) for f in deployModules])
defsDeploy = {"PRD_CRQ":"CRQ0009999999", "release":1}
maxDeployLagMins = 10

def loadDefs():
	if not os.path.isfile(propertiesFile):
		print(f"\nArquivo de propriedades '{propertiesFile}' inexistente.\n"
		f'Criando um novo com parametros default.\n')
		with open(propertiesFile,'w') as f:
			json.dump(defsDeploy,f)
		#input('>')
		#sys.exit()
	print(f'\nArquivo de propriedades "{propertiesFile}" encontrado.')
	with open(propertiesFile) as f:
		defsDeploy = json.load(f)
	print(f'Deploy properties: {defsDeploy}\n')

def initDeployDir():
	if not os.path.isdir("c:\\deploy"):
		print("\nDiretório c:\\deploy inexistente.\n")
		input('>')
		sys.exit()
	binDir = "c:\\deploy\\"+defsDeploy["PRD_CRQ"]+"\\bin\\exe"
	os.makedirs(binDir,exist_ok=True)

def copyDeployFiles():
	binDir = "c:\\deploy\\"+defsDeploy["PRD_CRQ"]+"\\bin\\exe\\"
	for f in deployModules:
		shutil.copy2('bin\\exe\\'+f,binDir+f)
	print(f'Arquivos copiados\n')
	
def buildModules():
	mintty_exe = os.environ['LOCALAPPDATA']+'\\Atlassian\\SourceTree\\git_local\\usr\\bin\\mintty.exe'
	if not os.path.isfile(mintty_exe):
		print(f'\nArquivo "{mintty_exe}" nao encontrado!')
		input('>')
		sys.exit()
	print('Invocando build.sh ...\n')
	ret = os.system(mintty_exe+' /usr/bin/bash --login -i -c ./build.sh')
	return ret

def callSonar():
	mintty_exe = os.environ['LOCALAPPDATA']+'\\Atlassian\\SourceTree\\git_local\\usr\\bin\\mintty.exe'
	if not os.path.isfile(mintty_exe):
		print(f'\nArquivo "{mintty_exe}" nao encontrado!')
		input('>')
		sys.exit()
	os.chdir('sourcecode')
	print('Dir: %s' % (os.getcwd()))
	print('Invocando sonar.sh ...\n')
	ret = os.system(mintty_exe+' /usr/bin/bash --login -i -c ./sonar.sh')
	os.chdir('..')
	print('Dir: %s' % (os.getcwd()))
	return ret

def checkDeployFiles():
	if not os.path.isdir('bin\\exe'):
		print('Diretorio bin\\exe nao encontrado')
		return False
	allModsOk = True
	for f in deployModules:
		if not os.path.isfile('bin\\exe\\'+f):
			print(f'\Arquivo "bin\\exe\\{f}" inexistente')
			allModsOk = False
		else:
			fStat = os.stat('bin\\exe\\'+f)
			if (fStat.st_size<=0):
				print(f'Arquivo bin\\exe\\{f:18} inexistente')
				allModsOk = False
			elif ( (time.time()-fStat.st_mtime) / 60 >maxDeployLagMins):
				print(f'Arquivo bin\\exe\\{f:18} antigo - {int((time.time()-fStat.st_mtime) // 60)} mins - '\
				f'{time.ctime(fStat.st_mtime)}')
				allModsOk = False
			#
	#dirFiles = os.listdir('bin\\exe')
	if allModsOk: print('Arquivos de build ok')
	else: 
		print('\nArquivos nao gerados no build!')
		input('>')
		sys.exit()

print('\n### Init\n')
print(f'propertiesFile={propertiesFile}\n')
print(f'deployModules={deployModules}\n')
loadDefs()
initDeployDir()
print('\n### Build\n')
buildModules()
print('\n### Check build files\n')
checkDeployFiles()
copyDeployFiles()

print('\n### Update Sonar\n')
callSonar()

print('\n### Script ok\n')
input('>')
