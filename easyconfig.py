
import configparser

class EasyConfig:

    SECTION_DEFAULT = 'DEFAULT'
    configFileName = None

    # set config filename
    def setFileName(self, fileName):
        self.configFileName = fileName

    # load config from file
    def loadConfig(self, configParam):
        if not self.configFileName:
            return
        
        configFile = configparser.ConfigParser()
        configFile.read(self.configFileName)
        
        for key in configParam.keys():
            if key in configFile[self.SECTION_DEFAULT]:
                if type(configParam[key]) == int:
                    try:
                        val = int(configFile[self.SECTION_DEFAULT][key])
                        configParam[key] = val
                    except:
                        pass
                elif type(configParam[key]) == float:
                    try:
                        val = float(configFile[self.SECTION_DEFAULT][key])
                        configParam[key] = val
                    except:
                        pass
                elif type(configParam[key]) == bool:
                    if configFile[self.SECTION_DEFAULT][key] == 'True':
                        configParam[key] = True
                    else:
                        configParam[key] = False
                else:
                    configParam[key] = configFile[self.SECTION_DEFAULT][key]

    # save config to file
    def saveConfig(self, configParam):
        if not self.configFileName:
            return
        
        configFile = configparser.ConfigParser()
        
        for key in configParam:
            val = None
            if type(configParam[key]) == int:
                val = "%d" % configParam[key]
            elif type(configParam[key]) == float:
                val = "%f" % configParam[key]
            elif type(configParam[key]) == bool:
                if configParam[key]:
                    val = 'True'
                else:
                    val = 'False'
            elif type(configParam[key]) == str:
                val = configParam[key]

            if val != None:
                configFile[self.SECTION_DEFAULT][key] = val
        
        with open(self.configFileName, 'w') as writeFile:
            configFile.write(writeFile)

    def dumpConfig(self, configParam):
        for key in configParam:
            if type(configParam[key]) == int:
                print("%s = %d[int]" % (key, configParam[key]))
            elif type(configParam[key]) == float:
                print("%s = %f[float]" % (key, configParam[key]))
            elif type(configParam[key]) == bool:
                if configParam[key]:
                    print("%s = True[bool]" % key)
                else:
                    print("%s = False[bool]" % key)
            elif type(configParam[key]) == str:
                print("%s = %s[str]" % (key, configParam[key]))

    def process(self, configParam):
        self.loadConfig(configParam)
        self.saveConfig(configParam)
